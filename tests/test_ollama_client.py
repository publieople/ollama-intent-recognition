#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ollama客户端测试
"""
import json
import unittest
from unittest.mock import patch, MagicMock

import pytest
import requests

from src.ollama_client import OllamaClient, OllamaException


class TestOllamaClient(unittest.TestCase):
    """Ollama客户端测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.client = OllamaClient(base_url="http://test-ollama:11434", timeout=10)
        
    @patch('requests.post')
    def test_generate(self, mock_post):
        """测试生成方法"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "测试回复"}
        }
        mock_post.return_value = mock_response
        
        # 执行方法
        result = self.client.generate(
            model="test-model", 
            prompt="测试提示词",
            system_prompt="系统提示词"
        )
        
        # 验证结果
        self.assertEqual(result, "测试回复")
        
        # 验证请求内容
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        payload = json.loads(kwargs['json'])
        
        self.assertEqual(payload['model'], "test-model")
        self.assertEqual(len(payload['messages']), 2)
        self.assertEqual(payload['messages'][0]['role'], "system")
        self.assertEqual(payload['messages'][0]['content'], "系统提示词")
        self.assertEqual(payload['messages'][1]['role'], "user")
        self.assertEqual(payload['messages'][1]['content'], "测试提示词")
        
    @patch('requests.post')
    def test_generate_error(self, mock_post):
        """测试生成方法错误处理"""
        # 模拟异常
        mock_post.side_effect = requests.exceptions.ConnectionError("连接错误")
        
        # 验证异常
        with self.assertRaises(OllamaException):
            self.client.generate(
                model="test-model", 
                prompt="测试提示词",
                retry_count=1  # 设置只重试一次，加快测试速度
            )
    
    @patch('requests.post')
    def test_check_model_available(self, mock_post):
        """测试模型可用性检查"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 执行方法
        available, _ = self.client.check_model_available("test-model")
        
        # 验证结果
        self.assertTrue(available)
        
    @patch('requests.post')
    def test_check_model_not_available(self, mock_post):
        """测试模型不可用性检查"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "找不到模型"
        mock_post.return_value = mock_response
        
        # 执行方法
        available, error_msg = self.client.check_model_available("test-model")
        
        # 验证结果
        self.assertFalse(available)
        self.assertIn("模型不可用", error_msg)
        
    def test_apply_precision_bias(self):
        """测试精确度偏差应用"""
        content = json.dumps({"has_command": True, "dialog": "测试对话"})
        
        # 测试正偏差值
        result = self.client._apply_precision_bias(content, 0.9)
        result_json = json.loads(result)
        self.assertFalse(result_json["has_command"])
        
        # 测试负偏差值
        content = json.dumps({"has_command": False, "dialog": "测试对话"})
        result = self.client._apply_precision_bias(content, -0.9)
        result_json = json.loads(result)
        self.assertTrue(result_json["has_command"])
        
        # 测试零偏差值
        content = json.dumps({"has_command": True})
        result = self.client._apply_precision_bias(content, 0.0)
        self.assertEqual(result, content)
        
    @patch('requests.get')
    def test_get_models(self, mock_get):
        """测试获取模型列表"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "model1"},
                {"name": "model2"}
            ]
        }
        mock_get.return_value = mock_response
        
        # 执行方法
        result = self.client.get_models()
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "model1")
        self.assertEqual(result[1]["name"], "model2")


@pytest.mark.asyncio
async def test_generate_async():
    """测试异步生成方法"""
    client = OllamaClient(base_url="http://test-ollama:11434")
    
    # 使用补丁装饰器模拟异步会话的post方法
    with patch('aiohttp.ClientSession.post') as mock_post:
        # 创建模拟响应
        mock_response = MagicMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock()
        mock_response.json.return_value = {"message": {"content": "异步测试回复"}}
        
        # 设置mock返回值
        mock_post.return_value = mock_response
        
        # 调用异步方法
        result = await client.generate_async(
            model="test-model", 
            prompt="异步测试提示词"
        )
        
        # 验证结果
        assert result == "异步测试回复"
        
        # 关闭会话
        await client.close_session()


@pytest.mark.asyncio
async def test_generate_stream():
    """测试流式生成方法"""
    client = OllamaClient(base_url="http://test-ollama:11434")
    
    # 使用补丁装饰器模拟异步会话的post方法
    with patch('aiohttp.ClientSession.post') as mock_post:
        # 创建模拟响应
        mock_response = MagicMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        
        # 模拟流式内容
        mock_content = MagicMock()
        # 模拟异步迭代器
        async def mock_aiter():
            for text in [
                b'{"message": {"content": "segment1"}}',
                b'{"message": {"content": "segment2"}}',
                b'{"done": true}'
            ]:
                yield text
        mock_content.__aiter__.return_value = mock_aiter()
        mock_response.content = mock_content
        
        # 设置mock返回值
        mock_post.return_value = mock_response
        
        # 调用流式方法
        chunks = []
        async for chunk in client.generate_stream(
            model="test-model", 
            prompt="流式测试提示词"
        ):
            chunks.append(chunk)
        
        # 验证结果
        assert chunks == ["segment1", "segment2"]
        
        # 关闭会话
        await client.close_session()


if __name__ == "__main__":
    unittest.main() 