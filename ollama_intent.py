#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ollama对话意图识别工具 - 入口文件

本程序用于调用Ollama本地模型API，对对话内容进行意图识别。
"""
import os
import sys
import logging

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
from src.cli.arguments import parse_arguments, update_settings_from_args
from src.cli.app import OllamaIntentApp


def main() -> int:
    """主函数
    
    Returns:
        退出代码
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 更新设置
    update_settings_from_args(args)
    
    # 创建并运行应用程序
    app = OllamaIntentApp(args)
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 