#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提示词处理服务
"""
import os
import time
import json
import logging
from typing import List, Dict, Any, Optional

from ..ollama_client import OllamaClient
from ..config.settings import settings
from ..utils.file_utils import get_existing_responses, compute_prompt_hash, save_json_file, extract_json_from_text

# 配置日志
logger = logging.getLogger(__name__)


class PromptProcessorService:
    """提示词处理服务类"""
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """初始化提示词处理服务
        
        Args:
            client: 可选的Ollama客户端实例，如果未提供则创建新实例
        """
        self.client = client or OllamaClient(settings.api_url)
        self.summary = []
        self.processed_ids = set()
        
    def process_prompts(
        self, 
        model_name: str, 
        system_prompt: str, 
        prompts: List[str], 
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理提示词列表
        
        Args:
            model_name: 要使用的模型名称
            system_prompt: 系统提示词
            prompts: 提示词列表
            output_dir: 可选的输出目录，如果不提供则使用配置中的默认值
            
        Returns:
            包含处理结果的摘要信息
        """
        # 设置输出目录
        if output_dir:
            settings.output_dir = output_dir
        
        # 确保输出目录存在
        os.makedirs(settings.output_dir, exist_ok=True)
        
        # 如果需要保存原始响应，创建raw目录
        if settings.save_raw_response:
            os.makedirs(settings.raw_output_dir, exist_ok=True)
        
        # 获取已存在的响应
        existing_responses = {}
        if settings.resume_from_checkpoint:
            existing_responses = get_existing_responses(settings.output_dir)
        
        # 加载已有的摘要（如果存在）
        summary_file = os.path.join(settings.output_dir, "summary.json")
        if settings.resume_from_checkpoint and os.path.exists(summary_file):
            try:
                with open(summary_file, "r", encoding="utf-8") as f:
                    self.summary = json.load(f)
                logger.info(f"已加载现有摘要，包含 {len(self.summary)} 个条目")
                
                # 记录已处理的提示词ID
                self.processed_ids = {item["prompt_id"] for item in self.summary}
            except Exception as e:
                logger.error(f"加载摘要文件时出错: {e}")
        
        # 处理每个提示词
        for i, prompt in enumerate(prompts):
            prompt_id = i + 1
            
            # 如果已经处理过，则跳过
            if settings.resume_from_checkpoint and prompt_id in self.processed_ids:
                logger.info(f"跳过已处理的提示词 {prompt_id}/{len(prompts)}: {prompt[:50]}...")
                continue
            
            logger.info(f"处理提示词 {prompt_id}/{len(prompts)}: {prompt[:50]}...")
            
            # 创建提示词哈希
            prompt_hash = compute_prompt_hash(prompt)
            
            # 检查是否已经处理过这个提示词
            if settings.resume_from_checkpoint and prompt_hash in existing_responses:
                logger.info(f"已存在响应文件: {existing_responses[prompt_hash]}")
                
                # 尝试读取现有响应
                try:
                    with open(existing_responses[prompt_hash], "r", encoding="utf-8") as f:
                        response = f.read()
                    
                    # 添加到摘要
                    self.summary.append({
                        "prompt_id": prompt_id,
                        "prompt": prompt,
                        "response": response,
                        "output_file": existing_responses[prompt_hash]
                    })
                    self.processed_ids.add(prompt_id)
                    
                    # 保存摘要
                    if settings.save_summary:
                        self._save_summary(summary_file)
                        
                    continue
                except Exception as e:
                    logger.error(f"读取现有响应时出错: {e}")
            
            # 调用模型获取响应
            try:
                if settings.save_raw_response:
                    full_response = self.client.generate(
                        model_name, 
                        prompt, 
                        system_prompt, 
                        return_full_response=True, 
                        temperature=settings.temperature
                    )
                    response = full_response.get("message", {}).get("content", "")
                    
                    # 保存原始响应
                    raw_output_file = os.path.join(
                        settings.raw_output_dir, 
                        f"raw_response_{prompt_id}_{prompt_hash}.json"
                    )
                    save_json_file(raw_output_file, full_response)
                else:
                    response = self.client.generate(
                        model_name, 
                        prompt, 
                        system_prompt, 
                        temperature=settings.temperature
                    )
                
                # 处理响应内容，确保是JSON格式
                json_response = extract_json_from_text(response)
                
                if json_response:
                    formatted_response = json.dumps(json_response, ensure_ascii=False, indent=2)
                    logger.info("响应内容为有效的JSON格式")
                else:
                    logger.error(f"错误: 响应内容不是有效的JSON格式")
                    formatted_response = response  # 使用原始响应，后续可能需要人工检查
                
                # 创建输出文件名
                output_file = os.path.join(settings.output_dir, f"response_{prompt_id}_{prompt_hash}.json")
                
                # 保存格式化后的响应到文件
                with open(output_file, "w", encoding="utf-8") as f:
                    if json_response:
                        f.write(formatted_response)
                    else:
                        # 当不是有效JSON时，保存原始响应
                        f.write(response)
                    
                logger.info(f"已保存响应到: {output_file}")
                
                # 添加到摘要
                self.summary.append({
                    "prompt_id": prompt_id,
                    "prompt": prompt,
                    "response": formatted_response if json_response else response,
                    "output_file": output_file
                })
                self.processed_ids.add(prompt_id)
                
                # 保存摘要
                if settings.save_summary:
                    self._save_summary(summary_file)
                
                # 添加短暂延迟以避免API限制
                if i < len(prompts) - 1:  # 最后一个提示词后不需要延迟
                    time.sleep(settings.delay)
                    
            except Exception as e:
                logger.error(f"处理提示词时出错: {prompt_id}, 错误: {e}")
                continue
        
        # 最终保存摘要
        if settings.save_summary and self.summary:
            self._save_summary(summary_file)
        
        # 返回处理结果
        return {
            "processed_count": len(self.processed_ids),
            "total_count": len(prompts),
            "summary_file": summary_file if settings.save_summary else None,
            "output_dir": settings.output_dir
        }
    
    def _save_summary(self, summary_file: str) -> None:
        """保存摘要到文件
        
        Args:
            summary_file: 摘要文件路径
        """
        try:
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(self.summary, f, ensure_ascii=False, indent=2)
            logger.debug(f"已保存摘要到: {summary_file}")
        except Exception as e:
            logger.error(f"保存摘要文件时出错: {e}")
            
    def get_summary(self) -> List[Dict[str, Any]]:
        """获取处理摘要
        
        Returns:
            处理摘要列表
        """
        return self.summary 