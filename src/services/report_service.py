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
            # 处理每个条目的JSON有效性
            for item in summary:
                response = item.get("response", "")
                try:
                    if isinstance(response, str):
                        json.loads(response)
                        item['is_json'] = True
                    elif isinstance(response, (dict, list)):  # 如果已经是Python对象，也视为有效JSON
                        item['is_json'] = True
                    else:
                        item['is_json'] = False
                except:
                    item['is_json'] = False

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
            /* 基础样式 */
            :root {{
                --primary-color: #4361ee;
                --primary-light: #e7edff;
                --success-color: #2ecc71;
                --warning-color: #f39c12;
                --danger-color: #e74c3c;
                --grey-color: #6c757d;
                --bg-color: #f9fafb;
                --card-shadow: 0 4px 6px rgba(0,0,0,0.1);
                --border-radius: 8px;
            }}
            body {{
                font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                color: #2d3748;
                background-color: var(--bg-color);
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3, h4 {{
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.8em;
            }}
            h1 {{
                font-size: 2.2em;
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 10px;
                margin-top: 0.5em;
            }}
            h2 {{
                font-size: 1.8em;
                border-left: 4px solid var(--primary-color);
                padding-left: 10px;
            }}
            h3 {{
                font-size: 1.4em;
            }}
            
            /* 卡片样式 */
            .card {{
                background-color: white;
                border-radius: var(--border-radius);
                box-shadow: var(--card-shadow);
                padding: 20px;
                margin-bottom: 20px;
                overflow: hidden;
                transition: all 0.3s ease;
            }}
            .card:hover {{
                box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            }}
            
            /* 页眉样式 */
            .header-card {{
                background-color: white;
                background: linear-gradient(135deg, #4361ee, #3a0ca3);
                color: white;
                padding: 25px;
                border-radius: var(--border-radius);
                margin-bottom: 25px;
                position: relative;
                overflow: hidden;
            }}
            .header-card h1 {{
                color: white;
                border-bottom: none;
                margin-top: 0;
            }}
            .header-card p {{
                opacity: 0.9;
                margin: 8px 0;
            }}
            .header-card::before {{
                content: "";
                position: absolute;
                top: -50%;
                right: -50%;
                width: 100%;
                height: 100%;
                background: rgba(255,255,255,0.1);
                transform: rotate(30deg);
                pointer-events: none;
            }}
            
            /* 系统提示词样式 */
            .system-prompt {{
                background-color: var(--primary-light);
                padding: 20px;
                border-radius: var(--border-radius);
                white-space: pre-wrap;
                border-left: 4px solid var(--primary-color);
                font-size: 0.95em;
                overflow-x: auto;
                max-height: 200px;
                overflow-y: auto;
                transition: max-height 0.3s ease;
            }}
            .system-prompt.expanded {{
                max-height: 1000px;
            }}
            
            /* 统计信息样式 */
            .stats-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                flex: 1;
                min-width: 200px;
                padding: 20px;
                border-radius: var(--border-radius);
                box-shadow: var(--card-shadow);
                background-color: white;
                text-align: center;
                transition: transform 0.3s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            .stat-value {{
                font-size: 2.2em;
                font-weight: bold;
                color: var(--primary-color);
                margin-bottom: 10px;
            }}
            .stat-label {{
                color: var(--grey-color);
                font-size: 1em;
            }}
            
            /* 评估指标样式 */
            .metrics-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-top: 20px;
            }}
            .metrics-section {{
                flex: 1;
                min-width: 300px;
            }}
            .metrics-table {{
                width: 100%;
                border-collapse: collapse;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 0 0 1px #e2e8f0;
            }}
            .metrics-table th, .metrics-table td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
            }}
            .metrics-table th {{
                background-color: #f8fafc;
                font-weight: 600;
            }}
            .metrics-table tr:last-child td {{
                border-bottom: none;
            }}
            .metrics-table tr:hover {{
                background-color: #f8fafc;
            }}
            .metrics-table td:last-child {{
                font-weight: 600;
                color: var(--primary-color);
            }}
            
            /* 混淆矩阵样式 */
            .confusion-matrix {{
                border-collapse: separate;
                border-spacing: 0;
                border-radius: var(--border-radius);
                overflow: hidden;
                box-shadow: var(--card-shadow);
                margin: 15px 0;
                width: 100%;
            }}
            .confusion-matrix th, .confusion-matrix td {{
                padding: 15px;
                text-align: center;
                border: 1px solid #e2e8f0;
            }}
            .confusion-matrix th {{
                background-color: #f8fafc;
                font-weight: 600;
            }}
            .cm-header {{
                background-color: #f1f5f9 !important;
                color: #1e293b;
            }}
            .cm-tp {{
                background-color: rgba(46, 204, 113, 0.15);
            }}
            .cm-fp {{
                background-color: rgba(231, 76, 60, 0.15);
            }}
            .cm-fn {{
                background-color: rgba(243, 156, 18, 0.15);
            }}
            .cm-tn {{
                background-color: rgba(52, 152, 219, 0.15);
            }}
            
            /* 结果列表样式 */
            .result-item {{
                background-color: white;
                padding: 20px;
                border-radius: var(--border-radius);
                margin-bottom: 20px;
                box-shadow: var(--card-shadow);
                border-top: 4px solid var(--primary-color);
                transition: all 0.3s ease;
            }}
            .result-item:hover {{
                box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            }}
            .result-item h3 {{
                margin-top: 0;
                color: var(--primary-color);
                display: flex;
                align-items: center;
            }}
            .prompt {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 15px;
                white-space: pre-wrap;
                border-left: 3px solid var(--grey-color);
                font-size: 0.95em;
                overflow-x: auto;
            }}
            .response {{
                background-color: #f0fff4;
                padding: 15px;
                border-radius: 6px;
                white-space: pre-wrap;
                border-left: 3px solid var(--success-color);
                font-size: 0.95em;
                overflow-x: auto;
                transition: max-height 0.3s ease;
            }}
            .json {{
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                line-height: 1.5;
            }}
            .meta {{
                margin-top: 15px;
                color: var(--grey-color);
                font-size: 0.9em;
                display: flex;
                align-items: center;
            }}
            .meta i {{
                margin-right: 5px;
            }}
            
            /* 按钮样式 */
            .btn {{
                display: inline-block;
                background-color: var(--primary-color);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.2s ease;
                text-decoration: none;
                margin-right: 10px;
                margin-bottom: 10px;
            }}
            .btn:hover {{
                background-color: #3651d3;
                transform: translateY(-2px);
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }}
            .btn-group {{
                margin: 15px 0;
            }}
            
            /* 底部样式 */
            .footer {{
                margin-top: 40px;
                padding: 20px 0;
                border-top: 1px solid #e2e8f0;
                color: var(--grey-color);
                font-size: 0.9em;
                text-align: center;
            }}
            
            /* 隐藏类 */
            .hidden {{
                display: none;
            }}
            
            /* 响应式设计 */
            @media (max-width: 768px) {{
                .stats-container,
                .metrics-container {{
                    flex-direction: column;
                }}
                .stat-card {{
                    width: 100%;
                }}
                .confusion-matrix {{
                    font-size: 0.85em;
                }}
            }}
            
            /* 标签样式 */
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 50px;
                font-size: 0.8em;
                margin-left: 10px;
            }}
            .badge-success {{
                background-color: rgba(46, 204, 113, 0.15);
                color: #27ae60;
            }}
            .badge-error {{
                background-color: rgba(231, 76, 60, 0.15);
                color: #c0392b;
            }}
            
            /* 图标样式 */
            .icon {{
                display: inline-block;
                width: 18px;
                height: 18px;
                margin-right: 5px;
                vertical-align: middle;
            }}
            
            /* 目录样式 */
            .toc {{
                background-color: white;
                border-radius: var(--border-radius);
                box-shadow: var(--card-shadow);
                padding: 20px;
                margin-bottom: 20px;
                width: 280px;
                position: fixed;
                top: 20px;
                left: -240px;
                z-index: 100;
                max-height: calc(100vh - 40px);
                overflow-y: auto;
                transition: all 0.3s ease;
            }}
            .toc.visible {{
                left: 20px;
            }}
            .toc::after {{
                content: "≡";
                position: absolute;
                right: 15px;
                top: 10px;
                font-size: 24px;
                color: var(--primary-color);
                cursor: pointer;
                border: 1px solid var(--primary-color);
                border-radius: 4px;
                padding: 0 8px;
                line-height: 24px;
            }}
            
            .toc h3 {{
                margin-top: 0;
                margin-bottom: 15px;
                color: var(--primary-color);
            }}
            .toc-list {{
                list-style-type: none;
                padding: 0;
                margin: 0;
            }}
            .toc-item {{
                padding: 5px 0;
                border-bottom: 1px solid #f0f0f0;
            }}
            .toc-item:last-child {{
                border-bottom: none;
            }}
            .toc-link {{
                color: #333;
                text-decoration: none;
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: all 0.2s ease;
            }}
            .toc-link:hover {{
                color: var(--primary-color);
            }}
            .toc-link .badge {{
                margin-left: 10px;
                font-size: 0.7em;
            }}
            .toc-link.active {{
                color: var(--primary-color);
                font-weight: bold;
            }}
            
            /* 页面左侧区域，用于触发目录显示 */
            .page-edge-trigger {{
                position: fixed;
                left: 0;
                top: 0;
                width: 5%;
                height: 100%;
                z-index: 90;
            }}
            
            /* 主内容区域 */
            .main-content {{
                margin-left: 80px;
                transition: margin-left 0.3s ease;
            }}
            .main-content.toc-expanded {{
                margin-left: 320px;
            }}
            
            /* 响应式布局 */
            @media (max-width: 1200px) {{
                .main-content {{
                    margin-left: 0;
                }}
                .toc {{
                    left: -280px;
                }}
                .toc.visible {{
                    left: 0;
                }}
                .main-content.toc-expanded {{
                    margin-left: 0;
                }}
            }}
            
            /* 动画效果 */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .animate-fade-in {{
                animation: fadeIn 0.5s ease forwards;
            }}
        </style>
    </head>
    <body>
        <div class="page-edge-trigger" id="page-trigger"></div>
        
        <div class="toc" id="report-toc">
            <h3>报告目录</h3>
            <ul class="toc-list">
                <li class="toc-item"><a href="#header" class="toc-link">报告头部</a></li>
                <li class="toc-item"><a href="#system-prompt" class="toc-link">系统提示词</a></li>
                <li class="toc-item"><a href="#stats-summary" class="toc-link">摘要统计</a></li>
                <li class="toc-item"><a href="#model-metrics" class="toc-link">模型评估指标</a></li>
                <li class="toc-item"><a href="#results" class="toc-link">处理结果 <span class="badge badge-success">{len(summary)}</span></a></li>
            </ul>
        </div>
        
        <div class="main-content">
            <div class="header-card" id="header">
                <h1>对话意图识别结果报告</h1>
                <p><strong>生成时间:</strong> {now}</p>
                <p><strong>模型:</strong> {model_name}</p>
                <p><strong>处理提示词数量:</strong> {len(summary)}</p>
            </div>
            
            <div class="card" id="system-prompt">
                <h2>系统提示词
                    <button class="btn" onclick="toggleSystemPrompt()">展开/折叠</button>
                </h2>
                <div class="system-prompt" id="system-prompt-content">{system_prompt}</div>
            </div>
            
            <h2 id="stats-summary">摘要统计</h2>
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-value">{len(summary)}</div>
                    <div class="stat-label">总处理数量</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{valid_samples}</div>
                    <div class="stat-label">有效评估样本</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{success_rate}%</div>
                    <div class="stat-label">成功率</div>
                </div>
            </div>
            
            <div class="card" id="model-metrics">
                <h2>模型评估指标</h2>
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
                                <th class="cm-header"></th>
                                <th class="cm-header" colspan="2"><strong>实际值</strong></th>
                            </tr>
                            <tr>
                                <th class="cm-header" rowspan="2"><strong>预测值</strong></th>
                                <td class="cm-tp">真正例 (TP): {tp}</td>
                                <td class="cm-fp">假正例 (FP): {fp}</td>
                            </tr>
                            <tr>
                                <td class="cm-fn">假负例 (FN): {fn}</td>
                                <td class="cm-tn">真负例 (TN): {tn}</td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
            
            <h2 id="results">处理结果</h2>
            <div class="btn-group">
                <button class="btn" onclick="toggleAllResponses()">展开/折叠所有响应</button>
                <button class="btn" onclick="filterResults('all')">显示全部</button>
                <button class="btn" onclick="filterResults('json')">仅显示有效JSON</button>
                <button class="btn" onclick="filterResults('non-json')">仅显示无效JSON</button>
            </div>
            
            <div id="results-container">
    """
            
            # 处理summary中的每个响应
            valid_json_responses = []
            invalid_json_responses = []
            
            for i, entry in enumerate(summary):
                prompt = entry['prompt']
                response = entry['response']
                # 确保latency和tokens有默认值，并转换为字符串显示
                latency = str(entry.get('latency', 'N/A'))
                tokens = str(entry.get('tokens', 'N/A'))
                is_json = entry.get('is_json', False)
                
                if is_json:
                    badge_class = "badge-success"
                    badge_text = "有效JSON"
                    valid_json_responses.append(i)
                else:
                    badge_class = "badge-error"
                    badge_text = "无效JSON"
                    invalid_json_responses.append(i)
                
                html_content += f"""
                <div class="result-item" id="result-{i}" data-type="{('json' if is_json else 'non-json')}">
                    <h3>提示词 #{i+1} <span class="badge {badge_class}">{badge_text}</span></h3>
                    <div class="prompt">{prompt}</div>
                    <h3>
                        响应
                        <button class="btn" onclick="toggleResponse('response-{i}')">展开/折叠</button>
                    </h3>
                    <div class="response hidden" id="response-{i}">{response}</div>
                    <div class="meta">
                        <span><strong>延迟:</strong> {latency}秒</span> | 
                        <span><strong>Tokens:</strong> {tokens}</span>
                    </div>
                </div>
                """
            
            # 添加目录项目
            toc_script = """
            // 动态生成目录中的结果项
            const tocList = document.querySelector('.toc-list');
            const validResSection = document.createElement('li');
            validResSection.className = 'toc-item';
            validResSection.innerHTML = '<strong>有效JSON响应:</strong>';
            tocList.appendChild(validResSection);
            
            """
            
            # 添加有效JSON响应到目录
            for i in valid_json_responses:
                toc_script += f"""
                const validItem{i} = document.createElement('li');
                validItem{i}.className = 'toc-item';
                validItem{i}.innerHTML = '<a href="#result-{i}" class="toc-link">提示词 #{i+1} <span class="badge badge-success">有效</span></a>';
                tocList.appendChild(validItem{i});
                """
            
            # 添加无效JSON响应到目录
            toc_script += """
            const invalidResSection = document.createElement('li');
            invalidResSection.className = 'toc-item';
            invalidResSection.innerHTML = '<strong>无效JSON响应:</strong>';
            tocList.appendChild(invalidResSection);
            
            """
            
            for i in invalid_json_responses:
                toc_script += f"""
                const invalidItem{i} = document.createElement('li');
                invalidItem{i}.className = 'toc-item';
                invalidItem{i}.innerHTML = '<a href="#result-{i}" class="toc-link">提示词 #{i+1} <span class="badge badge-error">无效</span></a>';
                tocList.appendChild(invalidItem{i});
                """
            
            # 关闭HTML并添加JavaScript功能
            html_content += f"""
            </div>

        </div>

        <script>
            // 功能: 切换响应显示/隐藏
            function toggleResponse(id) {{
                const element = document.getElementById(id);
                element.classList.toggle('hidden');
            }}
            
            // 功能: 切换系统提示词显示/隐藏
            function toggleSystemPrompt() {{
                const element = document.getElementById('system-prompt-content');
                element.classList.toggle('expanded');
            }}
            
            // 功能: 展开/折叠所有响应
            function toggleAllResponses() {{
                const responses = document.querySelectorAll('.response');
                const allHidden = Array.from(responses).every(r => r.classList.contains('hidden'));
                
                responses.forEach(response => {{
                    if(allHidden) {{
                        response.classList.remove('hidden');
                    }} else {{
                        response.classList.add('hidden');
                    }}
                }});
            }}
            
            // 功能: 筛选结果
            function filterResults(filter) {{
                const results = document.querySelectorAll('.result-item');
                
                results.forEach(result => {{
                    if(filter === 'all') {{
                        result.style.display = 'block';
                    }} else if(filter === 'json' && result.dataset.type === 'json') {{
                        result.style.display = 'block';
                    }} else if(filter === 'non-json' && result.dataset.type === 'non-json') {{
                        result.style.display = 'block';
                    }} else {{
                        result.style.display = 'none';
                    }}
                }});
            }}
            
            // 功能: 目录控制
            document.addEventListener('DOMContentLoaded', function() {{
                const toc = document.getElementById('report-toc');
                const mainContent = document.querySelector('.main-content');
                const pageTrigger = document.getElementById('page-trigger');
                
                // 鼠标进入左侧区域时展开目录
                pageTrigger.addEventListener('mouseenter', function() {{
                    toc.classList.add('visible');
                    if(window.innerWidth > 1200) {{
                        mainContent.classList.add('toc-expanded');
                    }}
                }});
                
                // 鼠标离开目录区域时折叠目录
                toc.addEventListener('mouseleave', function(e) {{
                    // 确保鼠标真的离开了目录区域
                    if (e.relatedTarget !== pageTrigger) {{
                        toc.classList.remove('visible');
                        mainContent.classList.remove('toc-expanded');
                    }}
                }});
                
                // 点击目录中的菜单图标固定/取消固定目录显示
                toc.addEventListener('click', function(e) {{
                    // 识别点击的是否是菜单图标区域
                    const rect = toc.getBoundingClientRect();
                    if (e.clientX > rect.right - 40) {{
                        toc.classList.toggle('visible');
                        mainContent.classList.toggle('toc-expanded');
                    }}
                }});
                
                // 滚动监听，高亮当前位置的目录项
                const sections = document.querySelectorAll('h2[id], .result-item[id]');
                const tocLinks = document.querySelectorAll('.toc-link');
                
                window.addEventListener('scroll', function() {{
                    let current = '';
                    
                    sections.forEach(section => {{
                        const sectionTop = section.offsetTop;
                        const sectionHeight = section.clientHeight;
                        if(pageYOffset >= (sectionTop - 150)) {{
                            current = section.getAttribute('id');
                        }}
                    }});
                    
                    tocLinks.forEach(link => {{
                        link.classList.remove('active');
                        if(link.getAttribute('href') === `#${{current}}`) {{
                            link.classList.add('active');
                        }}
                    }});
                }});
                
                // 平滑滚动到锚点
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                    anchor.addEventListener('click', function (e) {{
                        e.preventDefault();
                        
                        const targetId = this.getAttribute('href');
                        const targetElement = document.querySelector(targetId);
                        
                        if (targetElement) {{
                            window.scrollTo({{
                                top: targetElement.offsetTop - 20,
                                behavior: 'smooth'
                            }});
                        }}
                    }});
                }});
                
                {toc_script}
            }});
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
                elif isinstance(response, (dict, list)):  # 如果已经是Python对象，也视为有效JSON
                    valid_json_count += 1
            except:
                continue
                
        # 计算成功率百分比
        return round((valid_json_count / len(summary)) * 100, 2) 