#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML报告生成器 - 入口文件

该文件提供了一个命令行工具，用于生成HTML报告。
"""
import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
from src.templates.report_template import generate_html_report


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(description="HTML报告生成工具")
    
    # 输入设置
    parser.add_argument("--summary-file", type=str, required=True,
                      help="包含摘要数据的JSON文件路径")
    parser.add_argument("--system-prompt-file", type=str, required=True,
                      help="系统提示词文件路径")
    
    # 输出设置
    parser.add_argument("--output-dir", type=str, default="outputs",
                      help="输出目录")
    parser.add_argument("--model-name", type=str, default="未指定",
                      help="模型名称")
    
    return parser.parse_args()


def load_summary(summary_file: str) -> List[Dict[str, Any]]:
    """加载摘要数据
    
    Args:
        summary_file: 摘要文件路径
    
    Returns:
        摘要数据列表
    """
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载摘要文件失败: {e}")
        return []


def load_system_prompt(prompt_file: str) -> str:
    """加载系统提示词
    
    Args:
        prompt_file: 提示词文件路径
    
    Returns:
        系统提示词
    """
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"加载系统提示词文件失败: {e}")
        return ""


def main() -> int:
    """主函数
    
    Returns:
        退出代码
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载摘要数据
    summary = load_summary(args.summary_file)
    if not summary:
        print("摘要数据为空，无法生成报告")
        return 1
    
    # 加载系统提示词
    system_prompt = load_system_prompt(args.system_prompt_file)
    if not system_prompt:
        print("警告: 系统提示词为空")
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 生成HTML报告
    report_file = generate_html_report(
        summary=summary,
        output_dir=args.output_dir,
        model_name=args.model_name,
        system_prompt=system_prompt
    )
    
    if report_file:
        print(f"已生成HTML报告: {report_file}")
        return 0
    else:
        print("生成HTML报告失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())