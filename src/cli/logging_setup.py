"""
日志配置模块，提供日志系统的设置功能。
"""
import os
import logging
from typing import Optional, List


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """配置日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径（可选）
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level = getattr(logging, log_level.upper())
    
    handlers: List[logging.Handler] = [logging.StreamHandler()]
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