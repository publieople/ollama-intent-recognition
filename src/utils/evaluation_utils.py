#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型评估工具函数
"""
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

# 配置日志
logger = logging.getLogger(__name__)


def extract_prediction(response: str) -> Optional[bool]:
    """从模型响应中提取预测结果
    
    Args:
        response: 模型响应文本
        
    Returns:
        提取的预测结果 (True/False)，如果提取失败则返回None
    """
    try:
        # 尝试将响应解析为JSON
        if isinstance(response, str):
            json_data = json.loads(response)
        else:
            json_data = response
            
        # 检查是否包含has_command字段
        if "has_command" in json_data:
            return json_data["has_command"]
        
        # 对于可能嵌套的JSON结构
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key == "has_command":
                    return value
        
        logger.warning(f"无法从响应中提取预测结果: {response}")
        return None
    except Exception as e:
        logger.error(f"解析模型响应时出错: {e}")
        return None


def compute_confusion_matrix(
    predictions: List[bool], 
    ground_truth: List[bool]
) -> Dict[str, int]:
    """计算混淆矩阵
    
    Args:
        predictions: 预测结果列表
        ground_truth: 真实标签列表
        
    Returns:
        混淆矩阵字典 (TP, FP, TN, FN)
    """
    # 初始化混淆矩阵
    confusion_matrix = {
        "TP": 0,  # 真正例
        "FP": 0,  # 假正例
        "TN": 0,  # 真负例
        "FN": 0   # 假负例
    }
    
    # 填充混淆矩阵
    for pred, gt in zip(predictions, ground_truth):
        if pred is True and gt is True:
            confusion_matrix["TP"] += 1
        elif pred is True and gt is False:
            confusion_matrix["FP"] += 1
        elif pred is False and gt is False:
            confusion_matrix["TN"] += 1
        elif pred is False and gt is True:
            confusion_matrix["FN"] += 1
    
    return confusion_matrix


def compute_metrics(confusion_matrix: Dict[str, int]) -> Dict[str, float]:
    """计算评估指标
    
    Args:
        confusion_matrix: 混淆矩阵
        
    Returns:
        包含各项评估指标的字典
    """
    TP = confusion_matrix["TP"]
    FP = confusion_matrix["FP"]
    TN = confusion_matrix["TN"]
    FN = confusion_matrix["FN"]
    
    # 准确率 (Accuracy) = (TP + TN) / (TP + TN + FP + FN)
    total = TP + TN + FP + FN
    accuracy = (TP + TN) / total if total > 0 else 0
    
    # 精确率 (Precision) = TP / (TP + FP)
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    
    # 召回率 (Recall) = TP / (TP + FN)
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    
    # F1分数 = 2 * (precision * recall) / (precision + recall)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def evaluate_model_predictions(
    summary: List[Dict[str, Any]],
    dataset_file: Optional[str] = None
) -> Dict[str, Any]:
    """评估模型预测结果
    
    Args:
        summary: 包含提示词和响应的摘要列表
        dataset_file: 可选的数据集文件路径，用于获取真实标签
        
    Returns:
        评估结果字典
    """
    # 提取预测结果和真实标签
    predictions = []
    ground_truth = []
    valid_samples = []
    
    # 如果提供了数据集文件，则加载真实标签
    gt_map = {}
    dataset = []
    if dataset_file:
        try:
            with open(dataset_file, "r", encoding="utf-8") as f:
                dataset = json.load(f)
            
            logger.info(f"已加载原始数据集，包含 {len(dataset)} 个样本")
            
            # 为每个对话创建映射关系
            for item in dataset:
                if "dialog" in item and "has_command" in item:
                    dialog_key = json.dumps({"dialog": item["dialog"]}, ensure_ascii=False)
                    gt_map[dialog_key] = item.get("has_command", False)
            
            logger.info(f"已创建 {len(gt_map)} 个真实标签映射")
        except Exception as e:
            logger.error(f"加载数据集文件出错: {e}")
    
    # 处理每个样本
    for i, item in enumerate(summary):
        prompt = item.get("prompt", "")
        response = item.get("response", "")
        prompt_id = item.get("prompt_id", i+1)
        
        # 从响应中提取预测结果
        pred = extract_prediction(response)
        if pred is None:
            logger.warning(f"无法从响应中提取预测结果: prompt_id={prompt_id}")
            continue
            
        # 查找对应的真实标签
        gt = None
        
        # 首先尝试从提示词中解析（兼容旧格式）
        try:
            if isinstance(prompt, str):
                prompt_data = json.loads(prompt)
                if "has_command" in prompt_data:
                    gt = prompt_data["has_command"]
                    logger.debug(f"从提示词中解析到真实标签: {gt}")
        except Exception as e:
            logger.debug(f"从提示词解析真实标签失败: {e}")
        
        # 如果没有找到真实标签，则尝试从数据集映射中查找
        if gt is None and gt_map:
            try:
                # 查找对应的真实标签
                gt = gt_map.get(prompt)
                if gt is not None:
                    logger.debug(f"从映射表中找到真实标签: {gt}")
                else:
                    # 如果找不到，可能是由于JSON序列化的细微差异，尝试遍历比较
                    for orig_prompt, orig_gt in gt_map.items():
                        try:
                            orig_data = json.loads(orig_prompt)
                            prompt_data = json.loads(prompt)
                            if orig_data.get("dialog") == prompt_data.get("dialog"):
                                gt = orig_gt
                                logger.debug(f"通过对话内容匹配找到真实标签: {gt}")
                                break
                        except Exception:
                            continue
            except Exception as e:
                logger.debug(f"从映射表查找真实标签失败: {e}")
        
        # 如果仍然没有找到真实标签，则尝试根据prompt_id从原始数据集中获取
        if gt is None and dataset and prompt_id <= len(dataset):
            try:
                # 索引从1开始，但数组索引从0开始
                dataset_idx = prompt_id - 1
                if 0 <= dataset_idx < len(dataset):
                    dataset_item = dataset[dataset_idx]
                    if "has_command" in dataset_item:
                        gt = dataset_item["has_command"]
                        logger.debug(f"从原始数据集（按ID）中获取真实标签: {gt}")
            except Exception as e:
                logger.debug(f"从原始数据集获取真实标签失败: {e}")
        
        # 如果找到了真实标签，则添加到评估集合
        if gt is not None:
            predictions.append(pred)
            ground_truth.append(gt)
            valid_samples.append(item)
        else:
            logger.warning(f"无法获取真实标签: prompt_id={prompt_id}")
    
    # 如果没有有效样本，返回空结果
    if not predictions:
        logger.warning("没有找到有效的评估样本")
        return {
            "metrics": {},
            "confusion_matrix": {},
            "valid_samples": 0,
            "total_samples": len(summary)
        }
    
    # 输出匹配统计信息
    logger.info(f"总样本数: {len(summary)}, 有效评估样本数: {len(valid_samples)}")
    
    # 计算混淆矩阵
    confusion_matrix = compute_confusion_matrix(predictions, ground_truth)
    
    # 计算评估指标
    metrics = compute_metrics(confusion_matrix)
    
    return {
        "metrics": metrics,
        "confusion_matrix": confusion_matrix,
        "valid_samples": len(valid_samples),
        "total_samples": len(summary)
    } 