#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ollama对话意图识别工具 - 入口文件

本程序用于调用Ollama本地模型API，对对话内容进行意图识别。
"""
import os
import sys
import logging
import argparse
from typing import List, Dict, Any, Optional

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
from src.config.settings import settings
from src.ollama_client import OllamaClient
from src.services.prompt_processor import PromptProcessorService
from src.services.report_service import ReportService
from src.utils.prompt_utils import (
    load_prompts_from_file, load_prompts_from_json, 
    load_prompts_from_inputs_folder, load_system_prompt,
    get_default_prompts
)

# 配置日志
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """配置日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径（可选）
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level = getattr(logging, log_level.upper())
    
    handlers = [logging.StreamHandler()]
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(description="Ollama对话意图识别工具")
    
    # API设置
    parser.add_argument("--api-url", type=str, default="http://localhost:11434", 
                      help="Ollama API URL")
    
    # 模型设置
    parser.add_argument("--model", type=str, default="qwen2.5-coder:3b", 
                      help="要使用的Ollama模型名称")
    parser.add_argument("--temperature", type=float, default=0.01, 
                      help="温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.01")
    
    # 输入设置
    parser.add_argument("--system-prompt-file", type=str, 
                      help="系统提示词文件路径")
    parser.add_argument("--prompts-file", type=str, 
                      help="提示词文件路径，每行一个提示词")
    parser.add_argument("--inputs-folder", type=str, 
                      help="包含JSON文件的inputs文件夹路径")
    parser.add_argument("--dataset-file", type=str, 
                      help="特定的数据集文件路径，例如data/数据集.json")
    
    # 输出设置
    parser.add_argument("--output-dir", type=str, default="outputs", 
                      help="输出目录")
    parser.add_argument("--delay", type=float, default=0.1, 
                      help="请求之间的延迟（秒）")
    
    # 功能开关
    parser.add_argument("--no-summary", action="store_true", 
                      help="不保存提示词和响应的摘要")
    parser.add_argument("--no-resume", action="store_true", 
                      help="不使用断点续传，重新处理所有提示词")
    parser.add_argument("--save-raw", action="store_true", 
                      help="保存原始API响应")
    parser.add_argument("--no-report", action="store_true", 
                      help="不生成HTML报告")
    
    # 日志设置
    parser.add_argument("--log-level", type=str, default="INFO", 
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="日志级别")
    parser.add_argument("--log-file", type=str, 
                      help="日志文件路径")
    
    # 测试连接
    parser.add_argument("--test-connection", action="store_true", 
                      help="测试与Ollama API的连接")
    
    return parser.parse_args()


def update_settings_from_args(args: argparse.Namespace) -> None:
    """从命令行参数更新设置
    
    Args:
        args: 命令行参数
    """
    # 更新API设置
    settings.api_url = args.api_url
    settings.api_endpoint = f"{args.api_url}/api/chat"
    
    # 更新模型设置
    settings.model_name = args.model
    settings.temperature = args.temperature
    
    # 更新输出设置
    if args.output_dir:
        settings.output_dir = args.output_dir
    settings.delay = args.delay
    
    # 更新功能开关
    settings.save_summary = not args.no_summary
    settings.resume_from_checkpoint = not args.no_resume
    settings.save_raw_response = args.save_raw
    settings.generate_report = not args.no_report
    
    # 设置输入文件夹路径（如果提供）
    if args.inputs_folder:
        settings.input_dir = args.inputs_folder


def test_ollama_connection(api_url: str, model_name: str) -> bool:
    """测试与Ollama API的连接
    
    Args:
        api_url: Ollama API URL
        model_name: 模型名称
        
    Returns:
        连接是否成功
    """
    logger = logging.getLogger(__name__)
    client = OllamaClient(api_url)
    
    logger.info(f"测试与Ollama API的连接: {api_url}")
    logger.info(f"测试模型: {model_name}")
    
    available, error_msg = client.check_model_available(model_name)
    
    if available:
        logger.info(f"成功连接到Ollama API，模型 {model_name} 可用")
        return True
    else:
        logger.error(f"无法连接到Ollama API: {error_msg}")
        return False


def main() -> None:
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 配置日志
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    # 更新设置
    update_settings_from_args(args)
    
    # 打印欢迎信息
    logger.info("=" * 50)
    logger.info("Ollama对话意图识别工具")
    logger.info("=" * 50)
    logger.info(f"当前配置: ")
    logger.info(f"  - API URL: {settings.api_url}")
    logger.info(f"  - 模型: {settings.model_name}")
    logger.info(f"  - 输出目录: {settings.output_dir}")
    logger.info("=" * 50)
    
    # 测试连接
    if args.test_connection:
        if test_ollama_connection(settings.api_url, settings.model_name):
            logger.info("连接测试成功")
        else:
            logger.error("连接测试失败，请检查Ollama服务是否正在运行")
            sys.exit(1)
        return
    
    # 加载系统提示词
    system_prompt = load_system_prompt(args.system_prompt_file)
    logger.info(f"系统提示词长度: {len(system_prompt)} 字符")
    
    # 加载提示词列表
    prompts = []
    
    # 根据不同的输入源加载提示词
    if args.dataset_file:
        # 直接从特定数据集文件加载
        prompts = load_prompts_from_json(args.dataset_file)
        if prompts:
            logger.info(f"已从数据集文件加载 {len(prompts)} 个提示词: {args.dataset_file}")
        else:
            logger.warning("从数据集文件加载提示词失败，使用默认提示词列表")
            prompts = get_default_prompts()
    elif args.inputs_folder:
        prompts = load_prompts_from_inputs_folder(args.inputs_folder)
        if not prompts:
            logger.warning("从inputs文件夹加载提示词失败，使用默认提示词列表")
            prompts = get_default_prompts()
        else:
            logger.info(f"已从inputs文件夹加载 {len(prompts)} 个提示词")
    elif args.prompts_file:
        prompts = load_prompts_from_file(args.prompts_file)
        if not prompts:
            logger.warning("从文件加载提示词失败，使用默认提示词列表")
            prompts = get_default_prompts()
        else:
            logger.info(f"已从文件加载 {len(prompts)} 个提示词: {args.prompts_file}")
    else:
        prompts = get_default_prompts()
        logger.info("使用默认提示词列表")
    
    # 创建处理服务
    processor_service = PromptProcessorService()
    
    # 处理提示词
    result = processor_service.process_prompts(
        settings.model_name, 
        system_prompt, 
        prompts, 
        settings.output_dir
    )
    
    # 输出处理结果
    logger.info("=" * 50)
    logger.info(f"处理完成，已处理 {result['processed_count']}/{result['total_count']} 个提示词")
    
    # 生成HTML报告
    if settings.generate_report and processor_service.summary:
        report_path = ReportService.generate_html_report(
            processor_service.summary, 
            settings.output_dir, 
            settings.model_name, 
            system_prompt
        )
        if report_path:
            logger.info(f"已生成HTML报告: {report_path}")
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main() 