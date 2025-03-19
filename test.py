import requests
import json
import os
import time
import argparse
import hashlib
import glob
import re
from typing import List, Dict, Any, Tuple
from html_report_generator import generate_html_report

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """初始化Ollama客户端

        Args:
            base_url: Ollama API的基础URL，默认为本地地址
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/chat"
        
    def generate(self, model: str, prompt: str, system_prompt: str = None, return_full_response: bool = False, temperature: float = 0.01, options: dict = None, keep_alive: str = "5m") -> Any:
        """调用Ollama模型生成回复

        Args:
            model: 要使用的模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词
            return_full_response: 是否返回完整的API响应
            temperature: 温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.01
            options: 额外的模型参数，如top_p、top_k等
            keep_alive: 模型在内存中保持加载的时间，默认为5分钟

        Returns:
            如果return_full_response为True，返回完整的API响应；否则只返回回复文本
        """
        # 构建消息列表
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加用户提示词
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # 构建请求负载
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive
        }

        # 添加温度参数
        if options is None:
            options = {}
        options["temperature"] = temperature
            
        # 如果有其他选项，添加到payload
        if options:
            payload["options"] = options
            
        try:
            response = requests.post(self.api_endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 根据参数决定返回内容
            if return_full_response:
                return result
            
            # 从响应中提取回复内容
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"]
            else:
                return ""
        except requests.exceptions.RequestException as e:
            print(f"API调用错误: {e}")
            if return_full_response:
                return {"error": str(e)}
            return ""


def get_existing_responses(output_dir: str) -> Dict[str, str]:
    """获取已存在的响应文件
    
    Args:
        output_dir: 输出目录
        
    Returns:
        已存在的响应文件字典，键为提示词哈希，值为文件路径
    """
    existing_responses = {}
    
    # 检查输出目录是否存在
    if not os.path.exists(output_dir):
        return existing_responses
    
    # 查找所有响应文件
    response_files = glob.glob(os.path.join(output_dir, "response_*_*.json"))
    
    for file_path in response_files:
        # 从文件名中提取哈希值
        file_name = os.path.basename(file_path)
        parts = file_name.split("_")
        if len(parts) >= 3:
            # 提取哈希值（去掉.json后缀）
            hash_value = parts[2].replace(".json", "")
            existing_responses[hash_value] = file_path
    
    return existing_responses

def process_prompts(model_name: str, system_prompt: str, prompts: List[str], output_dir: str = "outputs", 
                   delay: float = 0.5, api_url: str = "http://localhost:11434", save_summary: bool = True,
                   resume: bool = True, save_raw_response: bool = False, generate_report: bool = True,
                   temperature: float = 0.01):
    """处理提示词列表并将结果保存到文件

    Args:
        model_name: 要使用的模型名称
        system_prompt: 系统提示词
        prompts: 提示词列表
        output_dir: 输出目录
        delay: 请求之间的延迟（秒）
        api_url: Ollama API的URL
        save_summary: 是否保存提示词和响应的摘要
        resume: 是否断点续传，跳过已处理的提示词
        save_raw_response: 是否保存原始API响应
        generate_report: 是否生成HTML报告
        temperature: 温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.01
    """
    client = OllamaClient(api_url)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 如果需要保存原始响应，创建raw目录
    raw_dir = os.path.join(output_dir, "raw")
    if save_raw_response:
        os.makedirs(raw_dir, exist_ok=True)
    
    # 获取已存在的响应
    existing_responses = {}
    if resume:
        existing_responses = get_existing_responses(output_dir)
        if existing_responses:
            print(f"找到 {len(existing_responses)} 个已存在的响应文件")
    
    # 用于保存摘要的列表
    summary = []
    
    # 加载已有的摘要（如果存在）
    summary_file = os.path.join(output_dir, "summary.json")
    if resume and os.path.exists(summary_file):
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                summary = json.load(f)
            print(f"已加载现有摘要，包含 {len(summary)} 个条目")
        except Exception as e:
            print(f"加载摘要文件时出错: {e}")
    
    # 记录已处理的提示词ID
    processed_ids = {item["prompt_id"] for item in summary} if summary else set()
    
    for i, prompt in enumerate(prompts):
        prompt_id = i + 1
        
        # 如果已经处理过，则跳过
        if resume and prompt_id in processed_ids:
            print(f"跳过已处理的提示词 {prompt_id}/{len(prompts)}: {prompt[:50]}...")
            continue
        
        print(f"处理提示词 {prompt_id}/{len(prompts)}: {prompt[:50]}...")
        
        # 创建一个简短的哈希作为文件名的一部分
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()[:8]
        
        # 检查是否已经处理过这个提示词
        if resume and prompt_hash in existing_responses:
            print(f"已存在响应文件: {existing_responses[prompt_hash]}")
            
            # 尝试读取现有响应
            try:
                with open(existing_responses[prompt_hash], "r", encoding="utf-8") as f:
                    response = f.read()
                
                # 添加到摘要
                summary.append({
                    "prompt_id": prompt_id,
                    "prompt": prompt,
                    "response": response,
                    "output_file": existing_responses[prompt_hash]
                })
                
                continue
            except Exception as e:
                print(f"读取现有响应时出错: {e}")
        
        
        # 调用模型获取响应
        if save_raw_response:
            full_response = client.generate(model_name, prompt, system_prompt, return_full_response=True, temperature=temperature)
            response = full_response.get("message", {}).get("content", "")
        else:
            response = client.generate(model_name, prompt, system_prompt, temperature=temperature)
        
        # 检查响应是否为JSON格式
        try:
            # 尝试解析响应为JSON
            parsed_response = json.loads(response)
            formatted_response = json.dumps(parsed_response, ensure_ascii=False, indent=2)
            print("响应内容为有效的JSON格式")
        except json.JSONDecodeError:
            # 如果解析失败，尝试从响应中提取JSON内容
            print("尝试从响应中提取JSON格式的内容...")
            try:
                # 查找第一个'{'和最后一个'}'之间的JSON内容，更宽松的匹配
                match = re.search(r'\{[\s\S]*?\}', response, re.IGNORECASE)
                if match:
                    # 提取匹配的内容
                    json_content = match.group(0)
                    # 解析提取的内容
                    parsed_response = json.loads(json_content)
                    formatted_response = json.dumps(parsed_response, ensure_ascii=False, indent=2)
                    print("提取的JSON格式的内容有效")
                else:
                    raise ValueError("未找到有效的JSON内容")
            except (json.JSONDecodeError, ValueError) as e:
                # 如果仍然无法解析，打印错误信息并跳过保存
                print(f"错误: 响应内容不是有效的JSON格式 \n - {response[:100]}...")
                continue
        
        # 创建输出文件名 - 使用序号和哈希
        output_file = os.path.join(output_dir, f"response_{prompt_id}_{prompt_hash}.json")
        
        # 保存格式化后的JSON响应到文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_response)
            
        print(f"已保存响应到: {output_file} \n")
        
        # 添加到摘要
        summary.append({
            "prompt_id": prompt_id,
            "prompt": prompt,
            "response": formatted_response,
            "output_file": output_file
        })
        
        # 保存摘要（每次处理完一个提示词都保存，以便断点续传）
        if save_summary:
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 添加短暂延迟以避免API限制
        if i < len(prompts) - 1:  # 最后一个提示词后不需要延迟
            time.sleep(delay)
    
    # 最终保存摘要
    if save_summary and summary:
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"已保存摘要到: {summary_file}")
    
    # 生成HTML报告
    if generate_report and summary:
        generate_html_report(summary, output_dir, model_name, system_prompt)

def load_prompts_from_file(file_path: str) -> List[str]:
    """从文件加载提示词列表

    Args:
        file_path: 提示词文件路径

    Returns:
        提示词列表
    """
    if not os.path.exists(file_path):
        print(f"错误: 提示词文件 '{file_path}' 不存在")
        return []
        
    with open(file_path, "r", encoding="utf-8") as f:
        # 每行作为一个提示词
        return [line.strip() for line in f if line.strip()]

def load_prompts_from_json(json_file_path: str) -> List[str]:
    """从JSON文件加载提示词列表

    Args:
        json_file_path: JSON文件路径，支持数据集.json格式

    Returns:
        提示词列表
    """
    if not os.path.exists(json_file_path):
        print(f"错误: JSON文件 '{json_file_path}' 不存在")
        return []
        
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 处理数据集.json格式
        if isinstance(data, list) and all(isinstance(item, dict) and "dialog" in item for item in data):
            print(f"检测到对话数据集格式: {json_file_path}")
            prompts = []
            for item in data:
                # 将每个对话转换为JSON字符串作为提示词
                prompts.append(json.dumps(item, ensure_ascii=False))
            return prompts
        # 处理普通列表格式
        elif isinstance(data, list):
            return [str(item) for item in data if item]
        # 处理字典格式
        elif isinstance(data, dict) and "prompts" in data:
            prompts = data.get("prompts", [])
            return [str(item) for item in prompts if item]
        else:
            print(f"错误: JSON文件格式不正确，应为列表或包含'prompts'字段的字典")
            return []
    except json.JSONDecodeError:
        print(f"错误: 无法解析JSON文件 '{json_file_path}'")
        return []

def load_prompts_from_inputs_folder(folder_path: str) -> List[str]:
    """从inputs文件夹加载所有JSON文件的提示词列表

    Args:
        folder_path: inputs文件夹路径

    Returns:
        提示词列表
    """
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return []
    
    # 查找文件夹中的所有JSON文件
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    if not json_files:
        print(f"警告: 文件夹 '{folder_path}' 中未找到任何JSON文件")
        return []
    
    prompts = []
    for json_file in json_files:
        print(f"正在加载文件: {json_file}")
        prompts.extend(load_prompts_from_json(json_file))
    
    return prompts

def load_system_prompt() -> str:
    """加载默认的系统提示词

    Returns:
        系统提示词
    """
    return """
    Role: 对话意图识别模型
    Background: 用户需要一个能够识别对话中是否含有指令的小模型，这些指令可能与智能家居控制或大模型调用相关。
    Profile: 你是一个自然语言处理和对话模型，擅长理解复杂的对话内容，能够准确识别出对话中的显式和隐式指令意图。
    Skills: 你能精确识别对话中的指令意图，包括智能家居控制和大模型调用，并能发现多轮对话中的潜在需求。
    Goals: 准确识别对话中的指令意图，并以JSON格式输出结果。
    Constrains: 
    1. 仅输出JSON格式的结果，不包含任何额外的分析或解释。
    2. 能够识别多种对话场景，包括日常对话、带有唤醒词的直接命令、以及多文本对话中的潜在指令。
    3. 能理解对话中的隐喻、省略和场景暗示。
    4. 支持多用户对话场景分析。

    WakeupWord: {"小爱"}
    OutputFormat: JSON格式（仅包含has_command字段）

    Examples:
[
    {
      "dialog": [
        {
          "speaker": "父亲",
          "content": "今天天气这么好，咱们把窗户打开通通风吧。"
        },
        {
          "speaker": "母亲",
          "content": "好主意，顺便把空气净化器关掉。"
        }
      ],
        "has_command": true
    },
    {
      "dialog": [
        {
          "speaker": "女儿",
          "content": "妈妈，我今天考试得了95分！"
        },
        {
          "speaker": "母亲",
          "content": "太棒了，宝贝！晚上给你做你最爱吃的红烧鸡翅。"
        }
      ],
        "has_command": false
    },
    {
      "dialog": [
        {
          "speaker": "父亲",
          "content": "明天早上有个重要的会议，我得早点出门。"
        },
        {
          "speaker": "母亲",
          "content": "几点呀？"
        },
        {
            "speaker":"父亲",
            "content":"早上七点吧"
        }
      ],
        "has_command": true
    },
    {
        "dialog": [
          {
            "speaker": "母亲",
            "content": "最近感觉眼睛有点干涩，是不是用眼过度了？"
          },
          {
            "speaker": "父亲",
            "content": "可能是，多休息休息，少看手机。"
          }
    ],
        "has_command": false
    },
    {
      "dialog": [
        {
          "speaker": "儿子",
          "content": "客厅的电视声音太小了，听不清。"
        },
        {
          "speaker": "父亲",
          "content": "那可以把音量调大一点。"
        }
      ],
      "has_command": true
    },
    {
        "dialog": [
          {
            "speaker": "父亲",
            "content": "最近新闻里说，那个新电影很不错。"
          },
          {
            "speaker": "儿子",
            "content": "是吗？我周末去看看。"
          }
        ],
        "has_command": false
    },
    {
      "dialog": [
        {
          "speaker": "女儿",
          "content": "卧室有点冷，能开一下暖气吗？"
        },
        {
          "speaker": "母亲",
          "content": "好的，我这就去开。"
        }
      ],
        "has_command": true
    },
    {
        "dialog": [
          {
            "speaker": "父亲",
            "content": "你觉得湖人今年能拿总冠军吗?"
          },
          {
            "speaker": "儿子",
            "content": "我觉得包可以的！"
          }
        ],
        "has_command": false
      },
    {
      "dialog": [
        {
          "speaker": "母亲",
          "content": "下周我们要去奶奶家，记得提前买点水果。"
        }
      ],
        "has_command": true
    },
    {
      "dialog": [
        {
          "speaker": "母亲",
          "content": "最近感觉腰酸背痛的，是不是该去做个按摩了？"
        },
        {
          "speaker": "父亲",
          "content": "可以呀，我帮你预约一下。"
        }
      ],
        "has_command": false
    },
    {
      "dialog": [
        {
          "speaker": "女儿",
          "content": "今天天气这么好，咱们把阳台的花浇一下吧。"
        },
        {
          "speaker": "母亲",
          "content": "可是前两天应该浇过了吧"
        }
      ],
        "has_command": true
    },
    {
      "dialog": [
        {
          "speaker": "父亲",
          "content": "最近小区里新开了一个健身房，我打算去办个卡。"
        },
        {
          "speaker": "母亲",
          "content": "挺好的，锻炼身体很重要。"
        }
      ],
        "has_command": false
    },
    {
      "dialog": [
        {
          "speaker": "儿子",
          "content": "卧室的空调风太大了，吹的人脑袋疼"
        }
      ],
        "has_command": true
    },
    {
      "dialog": [
        {
          "speaker": "女儿",
          "content": "我最近总是感觉肚子疼，是不是吃坏东西了？"
        },
        {
          "speaker": "父亲",
          "content": "要不咱们去医院看看吧。"
        }
    ],
        "has_command": false
    },
    {
      "dialog": [
        {
          "speaker": "母亲",
          "content": "今天天气不太好，记得把阳台的窗户关上。"
        }
      ],
        "has_command": true
    },
    {
      "dialog": [
        {
          "speaker": "父亲",
          "content": "最近新闻里说，那个新餐厅的菜很不错。"
        },
        {
          "speaker": "母亲",
          "content": "是吗？有空咱们去尝尝。"
        }
      ],
        "has_command": false
    },
    {
        "dialog": [
            {
                "speaker": "儿子",
                "content": "卧室的灯好像有点暗，这样看书有点伤眼睛"
            },
            {
                "speaker": "父亲",
                "content": "你也可以早点休息"
            }
        ],
        "has_command": true
    },
    {
        "dialog": [
            {
                "speaker": "女儿",
                "content": "客厅的音乐声音太吵了，能小声点吗？"
            },
            {
                "speaker": "父亲",
                "content": "好，我马上调低音量。"
            }
        ],
        "has_command": false
    },
    {
        "dialog": [
            {
                "speaker": "父亲",
                "content": "今天天气不错，把窗帘拉开吧。"
            }
        ],
        "has_command": true
    },
    {
        "dialog": [
            {
                "speaker": "母亲",
                "content": "今天超市打折，要不要一起去买东西？"
            },
            {
                "speaker": "儿子",
                "content": "好呀，我正好需要买点零食。"
            }
        ],
        "has_command": false
    }
]
    """

def get_default_prompts() -> List[str]:
    """获取默认的提示词列表

    Returns:
        默认提示词列表
    """
    return [
        "打开客厅的灯。",
        "贾维斯，明天的天气怎么样。",
        "今天天气真好。",
        "用户A：\"哇，外面好亮啊。\"\n用户B：\"是啊，该起床了。\"",
        "用户A：\"今天我出门了，家里只有猫。\"\n用户B：\"记得给它留点水和猫粮。\"",
        "用户A：\"电费又涨了，得省着点用。\"\n用户B：\"是啊，最近用电有点多。\"",
        "用户A：\"贾维斯，把健身房的温度调低点。\"\n用户B：\"顺便放点动感音乐。\"",
        "用户A：\"明天下雨唉！\"\n用户B：\"那明天早点出门吧。\"",
        "用户A：\"数学题太难了。\"\n用户B：\"用学习平板查下解题步骤。\""
    ]

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Ollama模型API调用脚本")
    parser.add_argument("--api-url", type=str, default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--model", type=str, default="qwen2.5-coder:3b", help="要使用的Ollama模型名称")
    parser.add_argument("--temperature", type=float, default=0.01, help="温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.01")
    parser.add_argument("--system-prompt-file", type=str, help="系统提示词文件路径")
    parser.add_argument("--prompts-file", type=str, help="提示词文件路径，每行一个提示词")
    parser.add_argument("--inputs-folder", type=str, help="包含JSON文件的inputs文件夹路径")
    parser.add_argument("--dataset-file", type=str, help="特定的数据集文件路径，例如data/数据集.json")
    parser.add_argument("--delay", type=float, default=0.1, help="请求之间的延迟（秒）")
    parser.add_argument("--no-summary", action="store_true", help="不保存提示词和响应的摘要")
    parser.add_argument("--no-resume", action="store_true", help="不使用断点续传，重新处理所有提示词")
    parser.add_argument("--save-raw", action="store_true", help="保存原始API响应")
    parser.add_argument("--no-report", action="store_true", help="不生成HTML报告")
    parser.add_argument("--output-dir", type=str, default="outputs", help="输出目录")

    args = parser.parse_args()
    
    # 加载系统提示词
    if args.system_prompt_file and os.path.exists(args.system_prompt_file):
        with open(args.system_prompt_file, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        print(f"已从文件加载系统提示词: {args.system_prompt_file}")
    else:
        system_prompt = load_system_prompt()
        print("使用默认系统提示词")
    
    # 加载提示词列表
    if args.dataset_file:
        # 直接从特定数据集文件加载
        prompts = load_prompts_from_json(args.dataset_file)
        if prompts:
            print(f"已从数据集文件加载 {len(prompts)} 个提示词: {args.dataset_file}")
        else:
            print("从数据集文件加载提示词失败，使用默认提示词列表")
            prompts = get_default_prompts()
    elif args.inputs_folder:
        prompts = load_prompts_from_inputs_folder(args.inputs_folder)
        if not prompts:
            print("使用默认提示词列表")
            prompts = get_default_prompts()
        else:
            print(f"已从inputs文件夹加载 {len(prompts)} 个提示词")
    elif args.prompts_file:
        prompts = load_prompts_from_file(args.prompts_file)
        if not prompts:
            print("使用默认提示词列表")
            prompts = get_default_prompts()
        else:
            print(f"已从文件加载 {len(prompts)} 个提示词: {args.prompts_file}")
    else:
        prompts = get_default_prompts()
        print("使用默认提示词列表")
    
    # 处理提示词并保存结果
    process_prompts(args.model, system_prompt, prompts, args.output_dir, args.delay, args.api_url, 
                   not args.no_summary, not args.no_resume, args.save_raw, not args.no_report,
                   args.temperature)

if __name__ == "__main__":
    main()
