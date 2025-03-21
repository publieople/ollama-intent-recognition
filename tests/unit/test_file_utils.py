#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件工具函数的单元测试
"""
import os
import sys
import unittest
import tempfile
import json

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.file_utils import compute_prompt_hash, extract_json_from_text, save_json_file, load_json_file


class TestFileUtils(unittest.TestCase):
    """文件工具函数测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        self.temp_dir.cleanup()
    
    def test_compute_prompt_hash(self):
        """测试提示词哈希计算函数"""
        # 测试空字符串
        self.assertEqual(len(compute_prompt_hash("")), 8)
        
        # 测试相同输入得到相同哈希
        prompt = "这是一个测试提示词"
        hash1 = compute_prompt_hash(prompt)
        hash2 = compute_prompt_hash(prompt)
        self.assertEqual(hash1, hash2)
        
        # 测试不同输入得到不同哈希
        prompt2 = "这是另一个测试提示词"
        hash3 = compute_prompt_hash(prompt2)
        self.assertNotEqual(hash1, hash3)
    
    def test_extract_json_from_text(self):
        """测试从文本中提取JSON内容函数"""
        # 测试有效的JSON
        text = '{"key": "value"}'
        result = extract_json_from_text(text)
        self.assertEqual(result, {"key": "value"})
        
        # 测试带有额外文本的JSON
        text = 'Some text before {"key": "value"} some text after'
        result = extract_json_from_text(text)
        self.assertEqual(result, {"key": "value"})
        
        # 测试无效的JSON
        text = "This is not a valid JSON"
        result = extract_json_from_text(text)
        self.assertIsNone(result)
    
    def test_save_and_load_json_file(self):
        """测试保存和加载JSON文件函数"""
        # 准备测试数据
        data = {"key": "value", "list": [1, 2, 3], "nested": {"a": 1}}
        file_path = os.path.join(self.temp_dir.name, "test.json")
        
        # 测试保存
        result = save_json_file(file_path, data)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(file_path))
        
        # 测试加载
        loaded_data = load_json_file(file_path)
        self.assertEqual(loaded_data, data)
        
        # 测试加载不存在的文件
        non_existent_file = os.path.join(self.temp_dir.name, "non_existent.json")
        default_value = {"default": True}
        result = load_json_file(non_existent_file, default_value)
        self.assertEqual(result, default_value)


if __name__ == "__main__":
    unittest.main() 