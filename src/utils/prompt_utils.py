#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提示词处理工具函数
"""
import os
import json
import glob
import re
import logging
from typing import List, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)


def load_prompts_from_file(file_path: str) -> List[str]:
    """从文件加载提示词列表

    Args:
        file_path: 提示词文件路径

    Returns:
        提示词列表
    """
    if not os.path.exists(file_path):
        logger.error(f"错误: 提示词文件 '{file_path}' 不存在")
        return []
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # 每行作为一个提示词，去除空行
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"加载提示词文件时出错: {file_path}, 错误: {e}")
        return []


def load_prompts_from_json(json_file_path: str) -> List[str]:
    """从JSON文件加载提示词列表

    Args:
        json_file_path: JSON文件路径，支持数据集.json格式

    Returns:
        提示词列表
    """
    if not os.path.exists(json_file_path):
        logger.error(f"错误: JSON文件 '{json_file_path}' 不存在")
        return []
        
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 处理数据集.json格式
        if isinstance(data, list) and all(isinstance(item, dict) and "dialog" in item for item in data):
            logger.info(f"检测到对话数据集格式: {json_file_path}")
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
            logger.error(f"错误: JSON文件格式不正确，应为列表或包含'prompts'字段的字典")
            return []
    except json.JSONDecodeError:
        logger.error(f"错误: 无法解析JSON文件 '{json_file_path}'")
        return []
    except Exception as e:
        logger.error(f"加载JSON文件时出错: {json_file_path}, 错误: {e}")
        return []


def load_prompts_from_inputs_folder(folder_path: str) -> List[str]:
    """从inputs文件夹加载所有JSON文件的提示词列表

    Args:
        folder_path: inputs文件夹路径

    Returns:
        提示词列表
    """
    if not os.path.exists(folder_path):
        logger.error(f"错误: 文件夹 '{folder_path}' 不存在")
        return []
    
    # 查找文件夹中的所有JSON文件
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    if not json_files:
        logger.warning(f"警告: 文件夹 '{folder_path}' 中未找到任何JSON文件")
        return []
    
    prompts = []
    for json_file in json_files:
        logger.info(f"正在加载文件: {json_file}")
        prompts.extend(load_prompts_from_json(json_file))
    
    return prompts


def load_system_prompt(system_prompt_file: str = None) -> str:
    """加载系统提示词
    
    Args:
        system_prompt_file: 系统提示词文件路径
    
    Returns:
        系统提示词文本
    """
    # 如果提供了文件路径且文件存在，从文件加载
    if system_prompt_file and os.path.exists(system_prompt_file):
        try:
            with open(system_prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"从文件加载系统提示词时出错: {e}")
            # 发生错误时返回默认系统提示词
    
    # 返回默认系统提示词
    return get_default_system_prompt()


def get_default_system_prompt() -> str:
    """获取默认的系统提示词

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