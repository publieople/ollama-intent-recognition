# Ollama对话意图识别工具

这是一个用于调用Ollama本地模型API的Python应用程序，专门用于对话意图识别任务。应用程序可以处理提示词列表，将系统提示词与每个提示词结合作为输入，并将模型的响应保存到文件中。

## 项目结构

```
.
├── main.py                 # 主入口文件
├── requirements.txt        # 依赖包列表
├── src/                    # 源代码目录
│   ├── config/             # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py     # 应用程序配置
│   ├── ollama_client/      # Ollama客户端模块
│   │   ├── __init__.py
│   │   └── client.py       # Ollama API客户端
│   ├── services/           # 服务模块
│   │   ├── __init__.py
│   │   ├── prompt_processor.py   # 提示词处理服务
│   │   └── report_service.py     # 报告生成服务
│   └── utils/              # 工具函数模块
│       ├── __init__.py
│       ├── file_utils.py   # 文件处理工具
│       └── prompt_utils.py # 提示词处理工具
├── tests/                  # 测试目录
│   ├── unit/               # 单元测试
│   │   └── test_file_utils.py   # 文件工具测试
│   └── integration/        # 集成测试
├── data/                   # 数据目录
│   └── ...                 # 各种数据集文件
├── inputs/                 # 输入目录
│   └── ...                 # 输入JSON文件
└── outputs/                # 输出目录
    └── ...                 # 生成的响应和报告
```

## 功能特点

- 调用本地Ollama API进行对话意图识别
- 支持自定义系统提示词
- 支持从文件、JSON文件或目录加载提示词列表
- 可配置输出目录和请求延迟
- 命令行参数支持灵活配置
- 自动格式化多轮对话提示词
- 生成包含提示词和响应的摘要文件
- 支持断点续传，可以从上次中断的地方继续处理
- 完整的日志记录
- 生成HTML报告，便于查看结果
- 支持测试API连接
- 单元测试支持

## 安装要求

1. 安装Python 3.6+
2. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```
3. 安装并运行[Ollama](https://ollama.ai/)
4. 下载所需的模型，例如：
   ```
   ollama pull qwen2.5-coder:3b
   ```

## 使用方法

### 基本用法

```bash
python main.py
```

这将使用默认配置运行脚本，使用qwen2.5-coder:3b模型和内置的提示词列表。

### 高级用法

```bash
python main.py --model llama3 --prompts-file prompts.txt --output-dir results --delay 1.0
```

### 测试API连接

```bash
python main.py --test-connection
```

### 从JSON数据集加载提示词

```bash
python main.py --dataset-file data/dataset.json
```

### 从inputs目录加载JSON文件

```bash
python main.py --inputs-folder inputs
```

### 自定义日志级别和保存日志文件

```bash
python main.py --log-level DEBUG --log-file logs/app.log
```

## 命令行参数

### API设置
- `--api-url`: Ollama API URL（默认：http://localhost:11434）

### 模型设置
- `--model`: 要使用的Ollama模型名称（默认：qwen2.5-coder:3b）
- `--temperature`: 温度参数，控制输出的随机性（默认：0.01）

### 输入设置
- `--system-prompt-file`: 系统提示词文件路径
- `--prompts-file`: 提示词文件路径，每行一个提示词
- `--inputs-folder`: 包含JSON文件的inputs文件夹路径
- `--dataset-file`: 特定的数据集文件路径

### 输出设置
- `--output-dir`: 输出目录（默认：outputs）
- `--delay`: 请求之间的延迟（秒）（默认：0.1）

### 功能开关
- `--no-summary`: 不保存提示词和响应的摘要
- `--no-resume`: 不使用断点续传，重新处理所有提示词
- `--save-raw`: 保存原始API响应
- `--no-report`: 不生成HTML报告

### 日志设置
- `--log-level`: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- `--log-file`: 日志文件路径

### 其他
- `--test-connection`: 测试与Ollama API的连接

## 提示词文件格式

提示词文件应为纯文本文件，每行包含一个提示词。例如：

```
打开客厅的灯。
贾维斯，明天的天气怎么样。
今天天气真好。
```

## 系统提示词

系统提示词用于指导模型如何处理输入的提示词。默认系统提示词配置为对话意图识别任务，用于识别对话中是否含有指令，以及指令的类型。

如果需要自定义系统提示词，可以创建一个文本文件并使用`--system-prompt-file`参数指定。

## 输出格式

应用程序将模型的响应保存为JSON文件，每个提示词对应一个输出文件。输出文件命名为`response_1_[哈希值].json`、`response_2_[哈希值].json`等，其中哈希值是根据提示词内容生成的唯一标识。

此外，应用程序还会生成一个`summary.json`文件，包含所有提示词和响应的对应关系，便于后续分析和处理。如果不需要生成摘要文件，可以使用`--no-summary`参数。

## HTML报告

应用程序会自动生成一个HTML报告，包含所有提示词和响应的可视化展示。报告文件保存为`outputs/report.html`。

HTML报告包含以下内容：
- 处理时间、使用的模型和提示词数量
- 系统提示词
- 摘要统计信息（包括成功率）
- 每个提示词和其对应的响应
- 可展开/折叠的响应视图

## 断点续传

应用程序支持断点续传功能，可以从上次中断的地方继续处理提示词。这对于处理大量提示词或者在处理过程中遇到中断的情况非常有用。如果不需要使用断点续传功能，可以使用`--no-resume`参数。

## 运行测试

运行单元测试：

```bash
python -m unittest discover -s tests/unit
```

## 项目特点

1. **模块化设计**：代码被组织为独立的模块，每个模块负责特定的功能，便于维护和扩展。
2. **配置管理**：使用集中式配置管理，便于调整应用程序行为。
3. **错误处理**：完善的错误处理和日志记录，便于调试和问题排查。
4. **单元测试**：包含单元测试示例，确保代码质量。
5. **类型标注**：使用Python类型标注，提高代码可读性和IDE支持。
6. **文档完善**：详细的函数文档和注释，便于理解代码。
7. **断点续传**：支持从上次中断的地方继续处理，提高效率。
8. **灵活配置**：通过命令行参数提供灵活的配置选项。

## 开发人员注意事项

1. **添加新功能**：在适当的模块中添加新功能，并更新相应的文档。
2. **修改配置**：在`src/config/settings.py`中添加新的配置项。
3. **添加测试**：为新功能添加单元测试和集成测试。
4. **日志记录**：使用`logging`模块记录日志，而不是直接使用`print`。
5. **异常处理**：适当处理异常，避免程序崩溃。 