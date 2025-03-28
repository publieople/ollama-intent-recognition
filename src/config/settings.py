#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
应用程序配置模块
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable, TypeVar, cast

from dotenv import load_dotenv

# 配置日志
logger = logging.getLogger(__name__)

# 定义类型变量
T = TypeVar('T')


def _parse_bool(value: str) -> bool:
    """解析字符串为布尔值
    
    Args:
        value: 字符串值
        
    Returns:
        布尔值
    """
    return value.lower() in ('true', 'yes', '1', 'y', 'on')


def _get_env(key: str, default: T, parser: Optional[Callable[[str], T]] = None) -> T:
    """从环境变量获取值
    
    Args:
        key: 环境变量名
        default: 默认值
        parser: 解析函数(可选)
        
    Returns:
        环境变量值或默认值
    """
    value = os.environ.get(key)
    if value is None:
        return default
        
    if parser is None:
        if isinstance(default, bool):
            parser = _parse_bool  # type: ignore
        elif isinstance(default, int):
            parser = int  # type: ignore
        elif isinstance(default, float):
            parser = float  # type: ignore
        else:
            return cast(T, value)
            
    try:
        return parser(value)
    except Exception as e:
        logger.warning(f"解析环境变量 {key} 失败: {e}，使用默认值 {default}")
        return default


class Settings:
    """应用程序配置类"""
    
    def __init__(self):
        """初始化配置对象"""
        # 加载环境变量
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"从 {env_file} 加载环境变量")
        else:
            load_dotenv()  # 尝试从默认位置加载
            
        # API设置
        self.api_url: str = _get_env('OLLAMA_API_URL', "http://localhost:11434")
        self.api_endpoint: str = f"{self.api_url}/api/chat"
        self.timeout: int = _get_env('OLLAMA_TIMEOUT', 60, int)
        
        # 模型设置
        self.model_name: str = _get_env('OLLAMA_MODEL', "qwen2.5-coder:3b")
        self.temperature: float = _get_env('MODEL_TEMPERATURE', 0.01, float)
        self.top_p: float = _get_env('MODEL_TOP_P', 0.9, float)
        self.precision_bias: float = _get_env('PRECISION_BIAS', 0.0, float)
        self.keep_alive: str = _get_env('KEEP_ALIVE', "5m")
        self.model_options: Dict[str, Any] = {}
        
        # 输入/输出设置
        self.output_dir: str = _get_env('OUTPUT_DIR', "outputs")
        self.input_dir: str = _get_env('INPUT_DIR', "inputs")
        self.delay: float = _get_env('DELAY', 0.1, float)
        self.dataset_file: Optional[str] = _get_env('DATASET_FILE', "data/dataset.json")
        
        # 功能开关
        self.save_summary: bool = _get_env('SAVE_SUMMARY', True, _parse_bool)
        self.resume_from_checkpoint: bool = _get_env('RESUME_FROM_CHECKPOINT', True, _parse_bool)
        self.save_raw_response: bool = _get_env('SAVE_RAW_RESPONSE', False, _parse_bool)
        self.generate_report: bool = _get_env('GENERATE_REPORT', True, _parse_bool)
        self.open_report: bool = _get_env('OPEN_REPORT', False, _parse_bool)
        
        # 日志设置
        self.log_level: str = _get_env('LOG_LEVEL', "INFO")
        self.log_file: Optional[str] = _get_env('LOG_FILE', None)
    
    def update(self, **kwargs) -> None:
        """更新配置参数
        
        Args:
            **kwargs: 关键字参数，用于更新配置
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"更新配置: {key} = {value}")
            else:
                logger.warning(f"未知配置参数: {key}")
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典
        
        Returns:
            包含所有配置的字典
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def save_to_file(self, file_path: str) -> None:
        """将当前配置保存到文件
        
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Settings':
        """从文件加载配置
        
        Args:
            file_path: 文件路径
            
        Returns:
            配置对象
        """
        settings = cls()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
                settings.update(**config_dict)
            logger.info(f"从 {file_path} 加载配置")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
        return settings
    
    def get_output_path(self, sub_path: Optional[str] = None) -> str:
        """获取输出路径
        
        Args:
            sub_path: 可选的子路径
            
        Returns:
            完整的输出路径
        """
        path = self.output_dir
        if sub_path:
            path = os.path.join(path, sub_path)
        
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        return path
    
    @property
    def raw_output_dir(self) -> str:
        """获取原始响应的输出目录
        
        Returns:
            原始响应的输出目录路径
        """
        return self.get_output_path("raw")


# 全局设置实例
settings = Settings() 