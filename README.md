# Ollama对话意图识别工具

这是一个用于调用Ollama本地模型API的Python应用程序，专门用于对话意图识别任务。应用程序可以处理提示词列表，将系统提示词与每个提示词结合作为输入，并将模型的响应保存到文件中。

## 项目结构

```
.
├── ollama_intent.py              # 新的主入口文件
├── html_report_generator.py      # HTML报告生成器工具
├── requirements.txt              # 依赖包列表
├── system.txt                    # 系统提示词文件
├── prompts.txt                   # 默认提示词文件
├── pytest.ini                    # pytest配置文件
├── mypy.ini                      # mypy配置文件
├── src/                          # 源代码目录
│   ├── cli/                      # 命令行接口模块
│   │   ├── __init__.py
│   │   ├── arguments.py          # 命令行参数处理
│   │   ├── logging_setup.py      # 日志配置
│   │   └── app.py                # 应用程序入口
│   ├── config/                   # 配置模块
│   │   ├── __init__.py
│   │   ├── .env.example          # 环境变量示例
│   │   ├── settings.py           # 应用程序配置
│   │   └── logging_config.py     # 日志配置
│   ├── ollama_client/            # Ollama客户端模块
│   │   ├── __init__.py
│   │   └── client.py             # Ollama API客户端
│   ├── services/                 # 服务模块
│   │   ├── __init__.py
│   │   ├── prompt_processor.py   # 提示词处理服务
│   │   └── report_service.py     # 报告生成服务
│   ├── templates/                # 模板模块
│   │   ├── __init__.py
│   │   └── report_template.py    # HTML报告模板
│   └── utils/                    # 工具函数模块
│       ├── __init__.py
│       ├── file_utils.py         # 文件处理工具
│       ├── prompt_utils.py       # 提示词处理工具
│       ├── evaluation_utils.py   # 评估工具
│       └── report_utils.py       # 报告生成工具
├── scripts/                      # 辅助脚本
│   └── run_tests.py              # 测试执行脚本
├── tests/                        # 测试目录
│   ├── __init__.py
│   └── test_ollama_client.py     # Ollama客户端测试
├── data/                         # 数据目录
│   └── ...                       # 各种数据集文件
├── inputs/                       # 输入目录
│   └── ...                       # 输入JSON文件
└── outputs/                      # 输出目录
    └── ...                       # 生成的响应和报告
```

## 最近更新 [0.5.0] - 2024-03-22

### 主要重构 - 项目结构优化

- 重构项目目录结构，使其更加模块化和易于维护
- 添加了中英双语说明文档
- 将主要功能从单一文件拆分为多个模块，增强代码复用性

### 新增模块

- **src/templates**: 新增模板模块，负责HTML报告生成
  - 添加`report_template.py`替代原有的HTML报告生成功能
- **src/cli**: 新增命令行接口模块，处理命令行参数和应用程序运行
  - 添加`arguments.py`处理命令行参数解析
  - 添加`logging_setup.py`配置日志系统
  - 添加`app.py`作为应用程序主要逻辑入口

### 入口文件优化

- 重构入口文件，创建`ollama_intent.py`作为主入口
- 将`html_report_generator.py`重构为独立工具入口

### 代码优化

- 改进代码组织，减少重复代码
- 增强类型标注，提高代码可读性
- 改进错误处理和日志记录
- 将相关功能组织到相应的模块中，遵循单一职责原则

## 版本升级指南 (0.4.x 到 0.5.0)

### 新的入口点

主入口文件已从`main.py`更改为`ollama_intent.py`。您需要更新调用方式：

**旧版本:**

```bash

python main.py [参数]
```

**新版本:**

```bash
python ollama_intent.py [参数]
```

### 命令行参数

所有命令行参数保持不变。您可以继续使用与0.4.x版本相同的参数。

### 输出目录

新版本保持与旧版本相同的输出目录结构。默认输出目录仍为`outputs/`。如果您使用的是自定义输出目录，可以继续使用`--output-dir`参数指定。

### HTML报告生成器

新版本提供了增强的命令行接口用于生成报告：

```bash
python html_report_generator.py --summary-file outputs/summary.json --output-file outputs/report.html
```

### 代码修改说明

如果您对代码进行了自定义修改，请注意以下变化：

1. HTML报告模板现在位于`src/templates/report_template.py`
2. 命令行参数处理代码现在位于`src/cli/arguments.py`
3. 主应用程序逻辑现在位于`src/cli/app.py`

### 数据兼容性

新版本完全兼容旧版本的数据格式。您可以继续使用之前生成的输出文件和摘要文件。

### 测试验证

升级后，建议测试基本功能：

1. 测试连接：

   ```bash
   python ollama_intent.py --test-connection
   ```

2. 使用默认提示词运行：

   ```bash
   python ollama_intent.py
   ```

## 新增特性

- **异步支持**：新增异步API调用支持，提高并发性能
- **流式生成**：支持流式响应生成，实时获取模型输出
- **环境变量配置**：支持通过环境变量和.env文件进行配置
- **更强大的错误处理**：重试机制和更详细的错误日志
- **上下文管理器支持**：客户端支持with语句和异步with语句
- **请求超时控制**：可配置API请求超时时间
- **更多单元测试**：包括异步功能的测试
- **类型检查增强**：更完善的类型标注
- **缓存支持**：使用lru_cache缓存常用结果
- **辅助脚本**：新增代码格式化、测试执行等辅助脚本

## 安装要求

1. 安装Python 3.8+
2. 安装依赖包：

   ```
   pip install -r requirements.txt
   ```
3. 安装并运行[Ollama](https://ollama.ai/)
4. 下载所需的模型，例如：
   ```
   ollama pull qwen2.5-coder:3b
   ```

## 环境变量配置

项目支持通过环境变量或.env文件进行配置。复制`src/config/.env.example`为`src/config/.env`，然后根据需要修改配置。

主要的环境变量包括：

```
# Ollama API设置
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:3b
OLLAMA_TIMEOUT=60

# 模型参数设置
MODEL_TEMPERATURE=0.01
MODEL_TOP_P=0.9
PRECISION_BIAS=0.0

# 输出设置
OUTPUT_DIR=outputs
DELAY=0.1

# 功能开关
SAVE_SUMMARY=true
RESUME_FROM_CHECKPOINT=true
```

## 使用方法

### 基本用法

```bash
python ollama_intent.py
```

这将使用默认配置运行脚本，使用qwen2.5-coder:3b模型和内置的提示词列表。

### 高级用法

```bash
python ollama_intent.py --model llama3 --prompts-file prompts.txt --output-dir results --delay 1.0
```

### 测试API连接

```bash
python ollama_intent.py --test-connection
```

### 从JSON数据集加载提示词

```bash
python ollama_intent.py --dataset-file data/dataset.json
```

### 从inputs目录加载JSON文件

```bash
python ollama_intent.py --inputs-folder inputs
```

### 自定义日志级别和保存日志文件

```bash
python ollama_intent.py --log-level DEBUG --log-file logs/app.log
```

## 开发者工具

项目包含了多个开发者工具脚本，方便开发和测试：

### 运行测试

```bash
python scripts/run_tests.py test
```

### 格式化代码

```bash
python scripts/run_tests.py format
```

### 类型检查

```bash
python scripts/run_tests.py typecheck
```

### 运行所有检查

```bash
python scripts/run_tests.py all
```

## Ollama客户端使用示例

### 基本用法

```python
from src.ollama_client import OllamaClient

# 创建客户端
client = OllamaClient(base_url="http://localhost:11434")

# 生成回复
response = client.generate(
    model="qwen2.5-coder:3b",
    prompt="你好，请介绍一下自己",
    system_prompt="你是一个AI助手"
)

print(response)
```

### 使用上下文管理器

```python
with OllamaClient() as client:
    response = client.generate(
        model="qwen2.5-coder:3b",
        prompt="你好，请介绍一下自己"
    )
    print(response)
```

### 异步调用

```python
import asyncio
from src.ollama_client import OllamaClient

async def main():
    client = OllamaClient()
    response = await client.generate_async(
        model="qwen2.5-coder:3b",
        prompt="你好，请介绍一下自己"
    )
    print(response)
    await client.close_session()

asyncio.run(main())
```

### 流式生成

```python
import asyncio
from src.ollama_client import OllamaClient

async def main():
    client = OllamaClient()
    async for chunk in client.generate_stream(
        model="qwen2.5-coder:3b",
        prompt="你好，请介绍一下自己"
    ):
        print(chunk, end="", flush=True)
    await client.close_session()

asyncio.run(main())
```

## 命令行参数

除了通过环境变量配置，也可以通过命令行参数进行配置：

### API设置
- `--api-url`: Ollama API URL（默认：http://localhost:11434）
- `--model`: 要使用的Ollama模型名称（默认：qwen2.5-coder:3b）

### 模型设置
- `--temperature`: 温度参数，控制输出的随机性（默认：0.01）
- `--top-p`: top-p参数，控制输出的多样性（默认：0.9）
- `--precision-bias`: 精确度偏差值（默认：0.0）

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
- `--open-report`: 生成报告后自动在浏览器中打开

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

## 项目特点

1. **模块化设计**：代码被组织为独立的模块，每个模块负责特定的功能，便于维护和扩展。
2. **配置管理**：使用集中式配置管理，支持环境变量和文件配置。
3. **错误处理**：完善的错误处理和重试机制，提高程序的健壮性。
4. **单元测试**：完整的单元测试和测试工具，确保代码质量。
5. **类型标注**：完善的Python类型标注，提高代码可读性和IDE支持。
6. **文档完善**：详细的函数文档和注释，便于理解代码。
7. **断点续传**：支持从上次中断的地方继续处理，提高效率。
8. **灵活配置**：通过环境变量和命令行参数提供灵活的配置选项。
9. **异步支持**：支持异步API调用和流式生成，提高程序性能。
10. **开发工具**：包含代码格式化、测试执行等辅助脚本，提高开发效率。

## 开发人员注意事项

1. **添加新功能**：在适当的模块中添加新功能，并更新相应的文档。
2. **修改配置**：在`src/config/settings.py`中添加新的配置项。
3. **添加测试**：为新功能添加单元测试。
4. **日志记录**：使用`logging`模块记录日志，而不是直接使用`print`。
5. **异常处理**：适当处理异常，避免程序崩溃。
6. **代码格式化**：使用`python scripts/run_tests.py format`格式化代码。
7. **类型检查**：使用`python scripts/run_tests.py typecheck`进行类型检查。
8. **环境变量**：更新`src/config/.env.example`文件，确保新的环境变量有文档说明。 