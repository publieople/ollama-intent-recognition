"""
命令行参数处理模块。
"""
import argparse
from typing import Dict, Any

from src.config.settings import settings


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
    parser.add_argument("--top-p", type=float, default=0.9,
                      help="top-p参数，控制输出的多样性，较低的值会使模型更保守，默认为0.9")
    parser.add_argument("--precision-bias", type=float, default=0.0,
                      help="精确度偏差值，正值偏向非指令(降低假正例)，负值偏向指令，范围-1.0到1.0，默认为0")
    
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
    parser.add_argument("--open-report", action="store_true", 
                      help="生成报告后自动在浏览器中打开")
    
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
    """根据命令行参数更新全局设置
    
    Args:
        args: 解析后的命令行参数
    """
    # 更新API设置
    settings.api_url = args.api_url
    settings.api_endpoint = f"{args.api_url}/api/chat"
    
    # 更新模型设置
    settings.model_name = args.model
    settings.temperature = args.temperature
    settings.top_p = args.top_p
    settings.precision_bias = args.precision_bias
    
    # 更新输出设置
    if args.output_dir:
        settings.output_dir = args.output_dir
    settings.delay = args.delay
    
    # 更新数据集文件路径
    if args.dataset_file:
        settings.dataset_file = args.dataset_file
    
    # 更新功能开关
    settings.save_summary = not args.no_summary
    settings.resume_from_checkpoint = not args.no_resume
    settings.save_raw_response = args.save_raw
    settings.generate_report = not args.no_report
    settings.open_report = args.open_report
    
    # 设置输入文件夹路径（如果提供）
    if args.inputs_folder:
        settings.input_dir = args.inputs_folder


def get_cli_config() -> Dict[str, Any]:
    """获取从命令行解析的配置
    
    Returns:
        配置字典
    """
    args = parse_arguments()
    update_settings_from_args(args)
    
    return {
        "args": args,
        "settings": settings
    } 