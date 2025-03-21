#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
应用程序配置模块
"""
import os
from typing import Dict, Any, Optional, List


class Settings:
    """应用程序配置类"""
    
    def __init__(self):
        """初始化配置对象"""
        # API设置
        self.api_url: str = "http://localhost:11434"
        self.api_endpoint: str = f"{self.api_url}/api/chat"
        
        # 模型设置
        self.model_name: str = "qwen2.5-coder:3b"
        self.temperature: float = 0.01
        self.keep_alive: str = "5m"
        self.model_options: Dict[str, Any] = {}
        
        # 输入/输出设置
        self.output_dir: str = "outputs"
        self.input_dir: str = "inputs"
        self.delay: float = 0.1
        
        # 功能开关
        self.save_summary: bool = True
        self.resume_from_checkpoint: bool = True
        self.save_raw_response: bool = False
        self.generate_report: bool = True
    
    def update(self, **kwargs) -> None:
        """更新配置参数
        
        Args:
            **kwargs: 关键字参数，用于更新配置
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
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