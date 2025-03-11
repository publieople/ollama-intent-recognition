import requests
import json
import os
import time
import argparse
import hashlib
import glob
import datetime
from typing import List, Dict, Any, Tuple

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """初始化Ollama客户端

        Args:
            base_url: Ollama API的基础URL，默认为本地地址
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/chat"
        
    def generate(self, model: str, prompt: str, system_prompt: str = None, return_full_response: bool = False, temperature: float = 0.1, options: dict = None, keep_alive: str = "5m") -> Any:
        """调用Ollama模型生成回复

        Args:
            model: 要使用的模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词
            return_full_response: 是否返回完整的API响应
            temperature: 温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.1
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

def format_multi_turn_prompt(prompt: str) -> str:
    """格式化多轮对话提示词
    
    将多行对话格式化为更清晰的格式，便于模型理解
    
    Args:
        prompt: 原始提示词，可能包含多行对话
        
    Returns:
        格式化后的提示词
    """
    # 检查是否是多轮对话（包含用户A/B标识）
    if "用户A" in prompt or "用户B" in prompt:
        # 已经是多轮对话格式，保持不变
        return prompt
    
    # 检查是否有多行但没有用户标识
    lines = prompt.strip().split('\n')
    if len(lines) > 1:
        # 添加用户标识
        formatted_lines = []
        for i, line in enumerate(lines):
            user = "用户A" if i % 2 == 0 else "用户B"
            formatted_lines.append(f"{user}：{line}")
        return "\n".join(formatted_lines)
    
    # 单行提示词，保持不变
    return prompt

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

def generate_html_report(summary: List[Dict], output_dir: str, model_name: str, system_prompt: str):
    """生成HTML报告文件
    
    Args:
        summary: 摘要数据
        output_dir: 输出目录
        model_name: 模型名称
        system_prompt: 系统提示词
    """
    if not summary:
        return
    
    # 创建HTML文件路径
    html_file = os.path.join(output_dir, "report.html")
    
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建HTML内容
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>对话意图识别结果报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .header {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 5px solid #007bff;
        }}
        .system-prompt {{
            background-color: #f0f7ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            white-space: pre-wrap;
            border: 1px solid #cce5ff;
        }}
        .result-item {{
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .prompt {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            white-space: pre-wrap;
            border-left: 3px solid #6c757d;
        }}
        .response {{
            background-color: #f0fff0;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
            border-left: 3px solid #28a745;
        }}
        .json {{
            font-family: monospace;
        }}
        .meta {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #eee;
            color: #6c757d;
            font-size: 0.9em;
        }}
        .toggle-btn {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            margin-bottom: 10px;
        }}
        .toggle-btn:hover {{
            background-color: #0069d9;
        }}
        .hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>对话意图识别结果报告</h1>
        <p>生成时间: {now}</p>
        <p>模型: {model_name}</p>
        <p>处理提示词数量: {len(summary)}</p>
    </div>
    
    <h2>系统提示词</h2>
    <div class="system-prompt">{system_prompt}</div>
    
    <h2>处理结果</h2>
    <button class="toggle-btn" onclick="toggleAllResponses()">展开/折叠所有响应</button>
    
    <div id="results">
"""
    
    # 添加每个提示词和响应
    for item in summary:
        prompt_id = item.get("prompt_id", "")
        prompt = item.get("prompt", "")
        response = item.get("response", "")
        output_file = item.get("output_file", "")
        
        # 尝试解析响应为JSON
        try:
            response_json = json.loads(response)
            response_formatted = json.dumps(response_json, ensure_ascii=False, indent=2)
            is_json = True
        except:
            response_formatted = response
            is_json = False
        
        html_content += f"""
    <div class="result-item">
        <h3>提示词 #{prompt_id}</h3>
        <div class="prompt">{prompt}</div>
        <button class="toggle-btn" onclick="toggleResponse('response-{prompt_id}')">显示/隐藏响应</button>
        <div id="response-{prompt_id}" class="response {'hidden' if prompt_id > 5 else ''}">
            <div class="{'json' if is_json else ''}">{response_formatted}</div>
        </div>
        <div class="meta">输出文件: {os.path.basename(output_file)}</div>
    </div>
"""
    
    # 添加页脚和JavaScript
    html_content += """
    </div>
    
    <div class="footer">
        <p>由Ollama对话意图识别工具生成</p>
    </div>
    
    <script>
        function toggleResponse(id) {
            const element = document.getElementById(id);
            if (element.classList.contains('hidden')) {
                element.classList.remove('hidden');
            } else {
                element.classList.add('hidden');
            }
        }
        
        function toggleAllResponses() {
            const responses = document.querySelectorAll('.response');
            const allHidden = Array.from(responses).every(el => el.classList.contains('hidden'));
            
            responses.forEach(el => {
                if (allHidden) {
                    el.classList.remove('hidden');
                } else {
                    el.classList.add('hidden');
                }
            });
        }
    </script>
</body>
</html>
"""
    
    # 写入HTML文件
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"已生成HTML报告: {html_file}")

def process_prompts(model_name: str, system_prompt: str, prompts: List[str], output_dir: str = "outputs", 
                   delay: float = 0.5, api_url: str = "http://localhost:11434", save_summary: bool = True,
                   resume: bool = True, save_raw_response: bool = False, generate_report: bool = True,
                   temperature: float = 0.1):
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
        temperature: 温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.1
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
        
        # 格式化多轮对话提示词
        formatted_prompt = format_multi_turn_prompt(prompt)
        
        # 调用模型
        if save_raw_response:
            # 获取完整响应
            full_response = client.generate(model_name, formatted_prompt, system_prompt, return_full_response=True, temperature=temperature)
            
            # 提取文本响应
            if isinstance(full_response, dict) and "message" in full_response and "content" in full_response["message"]:
                response = full_response["message"]["content"]
            else:
                response = ""
                
            # 保存原始响应
            raw_file = os.path.join(raw_dir, f"raw_response_{prompt_id}_{prompt_hash}.json")
            with open(raw_file, "w", encoding="utf-8") as f:
                json.dump(full_response, f, ensure_ascii=False, indent=2)
            print(f"已保存原始响应到: {raw_file}")
        else:
            # 只获取文本响应
            response = client.generate(model_name, formatted_prompt, system_prompt, temperature=temperature)
        
        # 创建输出文件名 - 使用序号和哈希
        output_file = os.path.join(output_dir, f"response_{prompt_id}_{prompt_hash}.json")
        
        # 保存响应到文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response)
            
        print(f"已保存响应到: {output_file} \n")
        
        # 添加到摘要
        summary.append({
            "prompt_id": prompt_id,
            "prompt": prompt,
            "response": response,
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
        json_file_path: JSON文件路径

    Returns:
        提示词列表
    """
    if not os.path.exists(json_file_path):
        print(f"错误: JSON文件 '{json_file_path}' 不存在")
        return []
        
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if isinstance(data, list):
            # 如果JSON是列表格式，直接使用
            return [str(item) for item in data if item]
        elif isinstance(data, dict) and "prompts" in data:
            # 如果JSON是字典格式且包含prompts字段
            prompts = data.get("prompts", [])
            return [str(item) for item in prompts if item]
        else:
            print(f"错误: JSON文件格式不正确，应为列表或包含'prompts'字段的字典")
            return []
    except json.JSONDecodeError:
        print(f"错误: 无法解析JSON文件 '{json_file_path}'")
        return []

def load_system_prompt() -> str:
    """加载默认的系统提示词

    Returns:
        系统提示词
    """
    return """
    Role: 对话意图识别模型
    Background: 用户需要一个能够识别对话中是否含有指令的模型，这些指令可能与智能家居控制或大模型调用相关。
    Profile: 你是一个自然语言处理和对话模型，擅长分析和理解复杂的对话内容，能够准确识别出对话中的显式和隐式指令意图。
    Skills: 你能精确识别对话中的指令意图，包括智能家居控制和大模型调用，并能解析多轮对话中的潜在需求。
    Goals: 准确识别对话中的指令意图，并以JSON格式输出结果。
    Constrains: 
    1. 能够处理多种对话场景，包括日常对话、带有唤醒词的直接命令、以及多文本对话中的潜在指令
    2. 能理解对话中的隐喻、省略和场景暗示
    3. 支持多用户对话场景分析

    Wake-upWord: {"贾维斯"}
    OutputFormat: JSON格式（包含call、type、instruction_type字段）

    Workflow:
    1. 输入对话内容
    2. 分析对话中的显式指令和隐式场景
    3. 识别唤醒词和指令类型
    4. 生成结构化JSON输出

    Examples:
    【基础示例】
    例子1：{打开客厅的灯。}
    输出：{"call": true , "type": "NoAwakeWord", "instruction_type": "智能家居"}

    例子2：{贾维斯，明天的天气怎么样。}
    输出：{"call": true , "type": "AwakeWord", "instruction_type":"大模型调用"}

    例子3：{今天天气真好。}
    输出：{"call": false , "type": "None", "instruction_type":"无指令"}

    【复杂场景示例】
    例子4：
    输入：
    - 用户A："哇，外面好亮啊。"
    - 用户B："是啊，该起床了。"
    输出：{"call": true, "type": "NoAwakeWord", "instruction_type": "智能家居"}

    例子5：
    输入：
    - 用户A："今天我出门了，家里只有猫。"
    - 用户B："记得给它留点水和猫粮。"
    输出：{"call": true, "type": "NoAwakeWord", "instruction_type": "智能家居"}

    例子6：
    输入：
    - 用户A："电费又涨了，得省着点用。"
    - 用户B："是啊，最近用电有点多。"
    输出：{"call": true, "type": "NoAwakeWord", "instruction_type": "智能家居"}

    例子7：
    输入：
    - 用户A："贾维斯，把健身房的温度调低点。"
    - 用户B："顺便放点动感音乐。"
    输出：{"call": true, "type": "AwakeWord", "instruction_type": "大模型调用"}

    例子8：
    输入：
    - 用户A："明天下雨唉！"
    - 用户B："那明天早点出门吧。"
    输出：{"call": true, "type": "NoAwakeWord", "instruction_type": "大模型调用"}

    例子9：
    输入:
    - 用户A："数学题太难了。"
    - 用户B："用学习平板查下解题步骤。"
    输出：{"call": false, "type": "NoAwakeWord", "instruction_type": "无指令"}
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
    parser.add_argument("--model", type=str, default="llama3.2", help="要使用的Ollama模型名称")
    parser.add_argument("--prompts-file", type=str, help="提示词文件路径，每行一个提示词")
    parser.add_argument("--output-dir", type=str, default="outputs", help="输出目录")
    parser.add_argument("--system-prompt-file", type=str, help="系统提示词文件路径")
    parser.add_argument("--delay", type=float, default=0.5, help="请求之间的延迟（秒）")
    parser.add_argument("--api-url", type=str, default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--no-summary", action="store_true", help="不保存提示词和响应的摘要")
    parser.add_argument("--no-resume", action="store_true", help="不使用断点续传，重新处理所有提示词")
    parser.add_argument("--save-raw", action="store_true", help="保存原始API响应")
    parser.add_argument("--no-report", action="store_true", help="不生成HTML报告")
    parser.add_argument("--temperature", type=float, default=0.1, help="温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.1")
    
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
    if args.prompts_file:
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
