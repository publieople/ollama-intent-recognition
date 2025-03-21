#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件处理工具函数
"""
import os
import json
import glob
import hashlib
import logging
from typing import List, Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)


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
    
    logger.info(f"找到 {len(existing_responses)} 个已存在的响应文件")
    return existing_responses


def compute_prompt_hash(prompt: str) -> str:
    """计算提示词的哈希值
    
    Args:
        prompt: 提示词
        
    Returns:
        哈希值（8个字符）
    """
    return hashlib.md5(prompt.encode('utf-8')).hexdigest()[:8]


def load_json_file(file_path: str, default: Any = None) -> Any:
    """加载JSON文件
    
    Args:
        file_path: 文件路径
        default: 默认返回值（如果加载失败）
        
    Returns:
        JSON对象，或默认值（如果加载失败）
    """
    if not os.path.exists(file_path):
        logger.warning(f"文件不存在: {file_path}")
        return default
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"无法解析JSON文件: {file_path}")
        return default
    except Exception as e:
        logger.error(f"加载文件时出错: {file_path}, 错误: {e}")
        return default


def save_json_file(file_path: str, data: Any, ensure_ascii: bool = False, indent: int = 2) -> bool:
    """保存数据到JSON文件
    
    Args:
        file_path: 文件路径
        data: 要保存的数据
        ensure_ascii: 是否确保ASCII编码（默认False，支持中文）
        indent: 缩进空格数
        
    Returns:
        保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
        return True
    except Exception as e:
        logger.error(f"保存JSON文件时出错: {file_path}, 错误: {e}")
        return False


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """从文本中提取JSON内容
    
    尝试两种方法：
    1. 直接解析整个文本
    2. 在文本中查找JSON块（{}之间的内容）
    
    Args:
        text: 输入文本
        
    Returns:
        解析后的JSON对象，如果无法解析则返回None
    """
    # 直接尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试从文本中提取JSON内容
    import re
    try:
        # 寻找第一个'{'和最后一个'}'之间的JSON内容
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            json_content = match.group(0)
            return json.loads(json_content)
    except (json.JSONDecodeError, AttributeError):
        pass
    
    # 如果都失败，返回None
    return None 