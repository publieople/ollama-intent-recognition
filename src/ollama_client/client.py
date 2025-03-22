#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ollama API客户端实现
"""
import requests
from typing import Any, Dict, List, Optional, Union, Tuple
import json
import logging

# 配置日志
logger = logging.getLogger(__name__)


class OllamaException(Exception):
    """Ollama API调用异常类"""
    pass


class OllamaClient:
    """Ollama API客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """初始化Ollama客户端

        Args:
            base_url: Ollama API的基础URL，默认为本地地址
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/chat"
        
    def generate(self, 
                model: str, 
                prompt: str, 
                system_prompt: Optional[str] = None, 
                return_full_response: bool = False, 
                temperature: float = 0.01, 
                top_p: float = 0.9,
                precision_bias: float = 0.0,
                options: Optional[Dict[str, Any]] = None, 
                keep_alive: str = "5m") -> Any:
        """调用Ollama模型生成回复

        Args:
            model: 要使用的模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词
            return_full_response: 是否返回完整的API响应
            temperature: 温度参数，控制输出的随机性，较低的值使输出更确定，默认为0.01
            top_p: top-p参数，控制输出的多样性，较低的值会使模型更保守，默认为0.9
            precision_bias: 精确度偏差值，正值偏向非指令(降低假正例)，负值偏向指令，范围-1.0到1.0，默认为0
            options: 额外的模型参数，如top_p、top_k等
            keep_alive: 模型在内存中保持加载的时间，默认为5分钟

        Returns:
            如果return_full_response为True，返回完整的API响应；否则只返回回复文本
            
        Raises:
            OllamaException: 当API调用失败时抛出异常
        """
        # 构建消息列表
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加用户提示词
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # 构建请求负载
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive
        }

        # 添加温度参数
        if options is None:
            options = {}
        options["temperature"] = temperature
        options["top_p"] = top_p
            
        # 如果有其他选项，添加到payload
        if options:
            payload["options"] = options
        
        logger.debug(f"调用Ollama API，模型: {model}, 温度: {temperature}, top_p: {top_p}, 精确度偏差: {precision_bias}")
        
        try:
            response = requests.post(self.api_endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 根据参数决定返回内容
            if return_full_response:
                return result
            
            # 从响应中提取回复内容
            if "message" in result and "content" in result["message"]:
                content = result["message"]["content"]
                
                # 应用精确度偏差（如果设置）
                if precision_bias != 0.0 and content:
                    # 尝试解析JSON并应用偏差
                    try:
                        import json
                        content_json = json.loads(content)
                        if "has_command" in content_json:
                            # 如果precision_bias为正值，增加判定为非指令的可能性
                            # 如果为负值，增加判定为指令的可能性
                            if precision_bias > 0 and content_json["has_command"]:
                                # 将部分指令判定为非指令（降低假正例）
                                if precision_bias > 0.8 or (precision_bias > 0.3 and "dialog" in content_json):
                                    content_json["has_command"] = False
                                    content = json.dumps(content_json, ensure_ascii=False)
                                    logger.debug("应用精确度偏差，将指令重判为非指令")
                            elif precision_bias < 0 and not content_json["has_command"]:
                                # 将部分非指令判定为指令（降低假负例）
                                if precision_bias < -0.8 or (precision_bias < -0.3 and "dialog" in content_json):
                                    content_json["has_command"] = True
                                    content = json.dumps(content_json, ensure_ascii=False)
                                    logger.debug("应用精确度偏差，将非指令重判为指令")
                    except Exception as e:
                        logger.debug(f"应用精确度偏差失败: {e}")
                
                return content
            else:
                logger.warning("API响应中未找到预期的回复内容")
                return ""
                
        except requests.exceptions.RequestException as e:
            error_msg = f"API调用错误: {e}"
            logger.error(error_msg)
            
            if return_full_response:
                return {"error": str(e)}
                
            raise OllamaException(error_msg) from e
            
    def check_model_available(self, model_name: str) -> Tuple[bool, str]:
        """检查模型是否可用
        
        Args:
            model_name: 模型名称
            
        Returns:
            元组(是否可用, 错误信息)
        """
        try:
            # 简单请求测试模型是否可用
            test_payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "test"}],
                "stream": False,
                "options": {"num_predict": 1}  # 只预测一个token来快速检查
            }
            
            response = requests.post(self.api_endpoint, json=test_payload)
            
            if response.status_code == 200:
                return True, ""
            else:
                error_msg = f"模型不可用: HTTP {response.status_code}"
                if response.text:
                    try:
                        error_json = response.json()
                        if "error" in error_json:
                            error_msg = f"模型错误: {error_json['error']}"
                    except json.JSONDecodeError:
                        error_msg = f"模型不可用: {response.text[:100]}"
                        
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            return False, f"连接错误: {str(e)}" 