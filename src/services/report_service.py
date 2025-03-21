#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告生成服务
"""
import os
import json
import datetime
import logging
from typing import List, Dict, Any, Optional

# 导入评估工具
from ..utils.evaluation_utils import evaluate_model_predictions

# 配置日志
logger = logging.getLogger(__name__)


class ReportService:
    """报告生成服务类"""
    
    @staticmethod
    def generate_html_report(
        summary: List[Dict[str, Any]], 
        output_dir: str, 
        model_name: str, 
        system_prompt: str,
        dataset_file: Optional[str] = None
    ) -> Optional[str]:
        """生成HTML报告文件
        
        Args:
            summary: 摘要数据
            output_dir: 输出目录
            model_name: 模型名称
            system_prompt: 系统提示词
            dataset_file: 可选的数据集文件路径，用于评估
            
        Returns:
            生成的HTML报告文件路径，如果生成失败则返回None
        """
        if not summary:
            logger.warning("摘要为空，无法生成报告")
            return None
        
        try:
            # 计算评估指标
            evaluation_results = evaluate_model_predictions(summary, dataset_file)
            metrics = evaluation_results.get("metrics", {})
            confusion_matrix = evaluation_results.get("confusion_matrix", {})
            valid_samples = evaluation_results.get("valid_samples", 0)
            total_samples = evaluation_results.get("total_samples", len(summary))
            
            # 格式化评估指标
            accuracy = metrics.get("accuracy", 0) * 100
            precision = metrics.get("precision", 0) * 100
            recall = metrics.get("recall", 0) * 100
            f1 = metrics.get("f1", 0) * 100
            
            # 格式化混淆矩阵
            tp = confusion_matrix.get("TP", 0)
            fp = confusion_matrix.get("FP", 0)
            tn = confusion_matrix.get("TN", 0)
            fn = confusion_matrix.get("FN", 0)
            
            # 计算成功率
            success_rate = ReportService._calculate_success_rate(summary)
            
            # 创建HTML文件路径
            html_file = os.path.join(output_dir, "report.html")
            
            # 获取当前时间
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 构建HTML内容
            html_content = f"""<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>对话意图识别结果报告</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .header {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 5px solid #007bff;
            }}
            .system-prompt {{
                background-color: #f0f7ff;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                white-space: pre-wrap;
                border: 1px solid #cce5ff;
            }}
            .result-item {{
                background-color: #fff;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .prompt {{
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
                white-space: pre-wrap;
                border-left: 3px solid #6c757d;
            }}
            .response {{
                background-color: #f0fff0;
                padding: 10px;
                border-radius: 5px;
                white-space: pre-wrap;
                border-left: 3px solid #28a745;
            }}
            .json {{
                font-family: monospace;
            }}
            .meta {{
                color: #6c757d;
                font-size: 0.9em;
                margin-top: 10px;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 10px;
                border-top: 1px solid #eee;
                color: #6c757d;
                font-size: 0.9em;
            }}
            .toggle-btn {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
                margin-bottom: 10px;
            }}
            .toggle-btn:hover {{
                background-color: #0069d9;
            }}
            .hidden {{
                display: none;
            }}
            .summary-info {{
                margin-top: 20px;
                background-color: #e9f7ef;
                padding: 10px;
                border-radius: 5px;
                border-left: 3px solid #27ae60;
            }}
            .metrics-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            .metrics-table th, .metrics-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .metrics-table th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .metrics-container {{
                background-color: #f0f8ff;
                padding: 15px;
                border-radius: 5px;
                margin-top: 15px;
                border-left: 3px solid #4169e1;
            }}
            .confusion-matrix {{
                display: inline-block;
                margin: 10px 0;
                border-collapse: collapse;
            }}
            .confusion-matrix th, .confusion-matrix td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            .confusion-matrix th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>对话意图识别结果报告</h1>
            <p>生成时间: {now}</p>
            <p>模型: {model_name}</p>
            <p>处理提示词数量: {len(summary)}</p>
        </div>
        
        <h2>系统提示词</h2>
        <div class="system-prompt">{system_prompt}</div>
        
        <div class="summary-info">
            <h3>摘要统计</h3>
            <p>总处理数量: {len(summary)}</p>
            <p>有效评估样本: {valid_samples}/{len(summary)}</p>
            <p>成功率: {success_rate}%</p>
        </div>
        
        <div class="metrics-container">
            <h3>模型评估指标</h3>
            <div class="section">
                <h2>统计信息</h2>
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-value">{len(summary)}</div>
                        <div class="stat-label">总样本数</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{success_rate}%</div>
                        <div class="stat-label">JSON格式有效率</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>评估指标</h2>
                <div class="eval-note">以下评估指标基于 {valid_samples}/{total_samples} 个有效样本计算</div>
                <div class="metrics-container">
                    <div class="metrics-section">
                        <h3>主要指标</h3>
                        <table class="metrics-table">
                            <tr>
                                <td>准确率 (Accuracy)</td>
                                <td>{accuracy:.2f}%</td>
                            </tr>
                            <tr>
                                <td>精确率 (Precision)</td>
                                <td>{precision:.2f}%</td>
                            </tr>
                            <tr>
                                <td>召回率 (Recall)</td>
                                <td>{recall:.2f}%</td>
                            </tr>
                            <tr>
                                <td>F1分数</td>
                                <td>{f1:.2f}%</td>
                            </tr>
                        </table>
                    </div>
                    <div class="metrics-section">
                        <h3>混淆矩阵</h3>
                        <table class="confusion-matrix">
                            <tr>
                                <td></td>
                                <td colspan="2"><strong>实际值</strong></td>
                            </tr>
                            <tr>
                                <td rowspan="2"><strong>预测值</strong></td>
                                <td>真正例 (TP): {tp}</td>
                                <td>假正例 (FP): {fp}</td>
                            </tr>
                            <tr>
                                <td>假负例 (FN): {fn}</td>
                                <td>真负例 (TN): {tn}</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <h2>处理结果</h2>
        <button class="toggle-btn" onclick="toggleAllResponses()">展开/折叠所有响应</button>
        
        <div id="results">
    """
            
            # 添加每个提示词和响应
            for item in summary:
                prompt_id = item.get("prompt_id", "")
                prompt = item.get("prompt", "")
                response = item.get("response", "")
                output_file = item.get("output_file", "")
                
                # 尝试解析响应为JSON
                try:
                    # 如果已经是字符串形式的JSON，解析它
                    if isinstance(response, str):
                        response_json = json.loads(response)
                    else:
                        response_json = response
                    
                    response_formatted = json.dumps(response_json, ensure_ascii=False, indent=2)
                    is_json = True
                except:
                    response_formatted = response if isinstance(response, str) else str(response)
                    is_json = False
                
                html_content += f"""
        <div class="result-item">
            <h3>提示词 #{prompt_id}</h3>
            <div class="prompt">{prompt}</div>
            <button class="toggle-btn" onclick="toggleResponse('response-{prompt_id}')">显示/隐藏响应</button>
            <div id="response-{prompt_id}" class="response {'hidden' if prompt_id > 5 else ''}">
                <div class="{'json' if is_json else ''}">{response_formatted}</div>
            </div>
            <div class="meta">输出文件: {os.path.basename(output_file) if output_file else '未保存'}</div>
        </div>
    """
            
            # 添加页脚和JavaScript
            html_content += """
        </div>
        
        <div class="footer">
            <p>由Ollama对话意图识别工具生成</p>
        </div>
        
        <script>
            function toggleResponse(id) {
                const element = document.getElementById(id);
                if (element.classList.contains('hidden')) {
                    element.classList.remove('hidden');
                } else {
                    element.classList.add('hidden');
                }
            }
            
            function toggleAllResponses() {
                const responses = document.querySelectorAll('.response');
                const allHidden = Array.from(responses).every(el => el.classList.contains('hidden'));
                
                responses.forEach(el => {
                    if (allHidden) {
                        el.classList.remove('hidden');
                    } else {
                        el.classList.add('hidden');
                    }
                });
            }
        </script>
    </body>
    </html>
    """
            
            # 写入HTML文件
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"已生成HTML报告: {html_file}")
            return html_file
            
        except Exception as e:
            logger.error(f"生成HTML报告时出错: {e}")
            return None
            
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
            except:
                continue
                
        # 计算成功率百分比
        return round((valid_json_count / len(summary)) * 100, 2) 