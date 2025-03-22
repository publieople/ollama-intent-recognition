#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告工具模块，提供报告查看和处理的辅助功能
"""
import os
import sys
import webbrowser
import time
from pathlib import Path
import logging

# 配置日志记录
logger = logging.getLogger(__name__)

def open_report_in_browser(report_path=None, output_dir="outputs"):
    """
    在浏览器中打开生成的报告
    
    Args:
        report_path: 报告文件的路径，如果为None则尝试在output_dir中查找
        output_dir: 输出目录，默认为"outputs"
        
    Returns:
        bool: 是否成功打开报告
    """
    if report_path is None:
        # 尝试在输出目录中查找report.html文件
        if not os.path.exists(output_dir):
            logger.error(f"输出目录 {output_dir} 不存在")
            return False
            
        report_path = os.path.join(output_dir, "report.html")
        
    # 验证报告文件是否存在
    if not os.path.exists(report_path):
        logger.error(f"报告文件 {report_path} 不存在")
        return False
        
    # 获取文件的绝对路径
    absolute_path = os.path.abspath(report_path)
    file_url = f"file://{absolute_path}"
    
    # 尝试在浏览器中打开
    try:
        logger.info(f"正在浏览器中打开报告: {file_url}")
        webbrowser.open(file_url)
        return True
    except Exception as e:
        logger.error(f"在浏览器中打开报告失败: {e}")
        return False

def monitor_report_changes(report_path=None, output_dir="outputs", interval=2.0):
    """
    监视报告文件的变化，并在变化时自动刷新浏览器
    
    Args:
        report_path: 报告文件的路径，如果为None则尝试在output_dir中查找
        output_dir: 输出目录，默认为"outputs"
        interval: 检查间隔时间（秒）
        
    Returns:
        None
    """
    if report_path is None:
        report_path = os.path.join(output_dir, "report.html")
        
    if not os.path.exists(report_path):
        logger.error(f"报告文件 {report_path} 不存在，无法监视变化")
        return
        
    # 获取初始修改时间
    last_modified = os.path.getmtime(report_path)
    
    # 首次打开报告
    open_report_in_browser(report_path)
    
    print(f"正在监视报告文件 {report_path} 的变化...")
    print("按 Ctrl+C 停止监视")
    
    try:
        while True:
            time.sleep(interval)
            current_modified = os.path.getmtime(report_path)
            
            if current_modified > last_modified:
                print(f"检测到报告文件变化，刷新浏览器...")
                open_report_in_browser(report_path)
                last_modified = current_modified
    except KeyboardInterrupt:
        print("\n停止监视报告文件")

if __name__ == "__main__":
    # 如果直接运行此脚本，尝试在浏览器中打开最新的报告
    default_output_dir = "outputs"
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--watch" or sys.argv[1] == "-w":
            # 监视模式
            output_dir = sys.argv[2] if len(sys.argv) > 2 else default_output_dir
            monitor_report_changes(output_dir=output_dir)
        else:
            # 将第一个参数视为报告路径或输出目录
            path = sys.argv[1]
            if os.path.isdir(path):
                open_report_in_browser(output_dir=path)
            else:
                open_report_in_browser(report_path=path)
    else:
        # 无参数，尝试打开默认位置的报告
        if open_report_in_browser(output_dir=default_output_dir):
            print(f"已在浏览器中打开报告")
        else:
            print(f"无法找到或打开报告，请检查 {default_output_dir} 目录是否存在报告文件")
            print("用法: python report_utils.py [报告文件路径 | 输出目录]")
            print("或使用监视模式: python report_utils.py --watch [输出目录]") 