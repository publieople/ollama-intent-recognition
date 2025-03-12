import os
import json
import datetime

def generate_html_report(summary: list, output_dir: str, model_name: str, system_prompt: str):
    """生成HTML报告文件
    
    Args:
        summary: 摘要数据
        output_dir: 输出目录
        model_name: 模型名称
        system_prompt: 系统提示词
    """
    if not summary:
        return
    
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
        
        html_content += f"""
    <div class="result-item">
        <h3>提示词 #{prompt_id}</h3>
        <div class="prompt">{prompt}</div>
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
    
    # 写入HTML文件
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"已生成HTML报告: {html_file}")