"""
报告模板模块，提供HTML报告生成功能。
"""
import os
import json
import datetime
from typing import List, Optional, Dict, Any


def generate_html_report_content(
    summary: list, 
    model_name: str, 
    system_prompt: str,
    metrics: Optional[Dict[str, Any]] = None
) -> str:
    """生成HTML报告内容
    
    Args:
        summary: 摘要数据
        model_name: 模型名称
        system_prompt: 系统提示词
        metrics: 评估指标（可选）
        
    Returns:
        HTML内容字符串
    """
    if not summary:
        return ""
    
    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建HTML内容
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>对话意图识别结果报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        .metrics-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .metric-label {{
            color: #6c757d;
            margin-top: 5px;
        }}
        .chart-container {{
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 30px;
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
        .confusion-matrix {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }}
        .matrix-cell {{
            padding: 10px;
            text-align: center;
            border-radius: 3px;
            font-weight: bold;
        }}
        .matrix-header {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .matrix-tp {{
            background-color: #d4edda;
        }}
        .matrix-fp {{
            background-color: #f8d7da;
        }}
        .matrix-tn {{
            background-color: #d4edda;
        }}
        .matrix-fn {{
            background-color: #f8d7da;
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
    
    {f'''
    <h2>评估指标</h2>
    <div class="metrics-container">
        <div class="metric-card">
            <div class="metric-value">{metrics.get('accuracy', 0):.2%}</div>
            <div class="metric-label">准确率 (Accuracy)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('precision', 0):.2%}</div>
            <div class="metric-label">精确率 (Precision)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('recall', 0):.2%}</div>
            <div class="metric-label">召回率 (Recall)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{metrics.get('f1', 0):.2%}</div>
            <div class="metric-label">F1分数</div>
        </div>
    </div>
    
    <div class="chart-container">
        <h3>混淆矩阵</h3>
        <div class="confusion-matrix">
            <div class="matrix-cell matrix-header">预测值</div>
            <div class="matrix-cell matrix-header">真实值</div>
            <div class="matrix-cell matrix-tp">TP: {metrics.get('confusion_matrix', {}).get('TP', 0)}</div>
            <div class="matrix-cell matrix-fp">FP: {metrics.get('confusion_matrix', {}).get('FP', 0)}</div>
            <div class="matrix-cell matrix-tn">TN: {metrics.get('confusion_matrix', {}).get('TN', 0)}</div>
            <div class="matrix-cell matrix-fn">FN: {metrics.get('confusion_matrix', {}).get('FN', 0)}</div>
        </div>
    </div>
    ''' if metrics else ''}
    
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
            response_json = json.loads(response)
            response_formatted = json.dumps(response_json, ensure_ascii=False, indent=2)
            is_json = True
        except:
            response_formatted = response
            is_json = False
        
        # 尝试解析提示词为JSON（如果是对话格式）
        try:
            prompt_json = json.loads(prompt)
            if isinstance(prompt_json, dict) and "dialog" in prompt_json:
                prompt_formatted = json.dumps(prompt_json, ensure_ascii=False, indent=2)
                is_dialog = True
            else:
                prompt_formatted = prompt
                is_dialog = False
        except:
            prompt_formatted = prompt
            is_dialog = False
        
        html_content += f"""
    <div class="result-item">
        <h3>提示词 #{prompt_id}</h3>
        <div class="prompt {'json' if is_dialog else ''}">{prompt_formatted}</div>
        <button class="toggle-btn" onclick="toggleResponse('response-{prompt_id}')">显示/隐藏响应</button>
        <div id="response-{prompt_id}" class="response {'hidden' if prompt_id > 5 else ''}">
            <div class="{'json' if is_json else ''}">{response_formatted}</div>
        </div>
        <div class="meta">输出文件: {os.path.basename(output_file)}</div>
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
    
    return html_content


def generate_html_report(
    summary: list, 
    output_dir: str, 
    model_name: str, 
    system_prompt: str,
    metrics: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """生成HTML报告文件
    
    Args:
        summary: 摘要数据
        output_dir: 输出目录
        model_name: 模型名称
        system_prompt: 系统提示词
        metrics: 评估指标（可选）
        
    Returns:
        生成的HTML文件路径，如果失败则返回None
    """
    if not summary:
        return None
    
    # 创建HTML文件路径
    html_file = os.path.join(output_dir, "report.html")
    
    # 生成HTML内容
    html_content = generate_html_report_content(summary, model_name, system_prompt, metrics)
    
    # 写入HTML文件
    try:
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"已生成HTML报告: {html_file}")
        return html_file
    except Exception as e:
        print(f"生成HTML报告失败: {e}")
        return None 