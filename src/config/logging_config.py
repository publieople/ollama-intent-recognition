#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志配置模块
"""
import os
import logging
import logging.config
from pathlib import Path
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """配置日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径（可选）
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level = getattr(logging, log_level.upper())
    
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": level,
        }
    }
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        handlers["file"] = {
            "class": "logging.FileHandler",
            "filename": log_file,
            "formatter": "standard",
            "level": level,
            "encoding": "utf-8",
        }
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format
            },
        },
        "handlers": handlers,
        "loggers": {
            "": {  # root logger
                "handlers": list(handlers.keys()),
                "level": level,
                "propagate": True
            },
            # 应用特定的日志器配置
            "src": {
                "level": level,
                "propagate": True
            },
            "src.ollama_client": {
                "level": level,
                "propagate": True
            },
            "src.services": {
                "level": level,
                "propagate": True
            },
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # 记录日志配置完成
    logger = logging.getLogger(__name__)
    logger.debug("日志系统配置完成")
    
    
def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器对象
    """
    return logging.getLogger(name) 