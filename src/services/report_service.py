#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告服务模块，提供报告生成功能。
"""
import os
import json
import datetime
import logging
from typing import List, Dict, Any, Optional

# 导入评估工具
from ..utils.evaluation_utils import evaluate_model_predictions

from src.config.settings import settings
from src.templates.report_template import generate_html_report

# 配置日志
logger = logging.getLogger(__name__)


class ReportService:
    """报告服务类"""
    
    def __init__(self):
        """初始化报告服务"""
        self.output_dir = settings.output_dir
    
    def generate_html_report(
        self, 
        summary: List[Dict[str, Any]], 
        system_prompt: str,
        metrics: Optional[Dict[str, Any]] = None,
        dataset_file: Optional[str] = None
    ) -> Optional[str]:
        """生成HTML报告
        
        Args:
            summary: 提示词和响应摘要
            system_prompt: 系统提示词
            metrics: 评估指标（可选）
            dataset_file: 数据集文件路径（可选）
            
        Returns:
            生成的HTML文件路径，如果失败则返回None
        """
        if not summary:
            return None
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 如果没有提供评估指标但有数据集文件，则计算评估指标
        if metrics is None and dataset_file:
            try:
                metrics = evaluate_model_predictions(summary, dataset_file)
                logger.info("已计算评估指标")
            except Exception as e:
                logger.error(f"计算评估指标时出错: {e}")
        
        # 使用模板生成HTML报告
        return generate_html_report(
            summary=summary,
            output_dir=self.output_dir,
            model_name=settings.model_name,
            system_prompt=system_prompt,
            metrics=metrics
        )

    @staticmethod
    def _calculate_success_rate(summary: List[Dict[str, Any]]) -> float:
        """计算成功率
        
        Args:
            summary: 摘要数据
            
        Returns:
            成功率（百分比）
        """
        if not summary:
            return 0.0
            
        # 检查哪些响应是有效的JSON
        valid_json_count = 0
        for item in summary:
            response = item.get("response", "")
            try:
                if isinstance(response, str):
                    json.loads(response)
                    valid_json_count += 1
                elif isinstance(response, (dict, list)):  # 如果已经是Python对象，也视为有效JSON
                    valid_json_count += 1
            except:
                continue
                
        # 计算成功率百分比
        return round((valid_json_count / len(summary)) * 100, 2) 