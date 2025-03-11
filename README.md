# Ollama对话意图识别工具

这是一个用于调用Ollama本地模型API的Python脚本，专门用于对话意图识别任务。脚本可以处理提示词列表，将系统提示词与每个提示词结合作为输入，并将模型的响应保存到文件中。

## 功能特点

- 调用本地Ollama API进行对话意图识别
- 支持自定义系统提示词
- 支持从文件加载提示词列表
- 可配置输出目录和请求延迟
- 命令行参数支持灵活配置
- 自动格式化多轮对话提示词
- 生成包含提示词和响应的摘要文件
- 支持断点续传，可以从上次中断的地方继续处理
- 以系统身份发送系统提示词，以用户身份发送提示词
- 可选保存原始API响应，便于调试

## 安装要求

1. 安装Python 3.6+
2. 安装依赖包：
   ```
   pip install requests
   ```
3. 安装并运行[Ollama](https://ollama.ai/)
4. 下载所需的模型，例如：
   ```
   ollama pull llama3.2
   ```

## 使用方法

### 基本用法

```bash
python test.py
```

这将使用默认配置运行脚本，使用llama3模型和内置的提示词列表。

### 高级用法

```bash
python test.py --model llama3.2 --prompts-file prompts.txt --output-dir results --delay 1.0
```

### 命令行参数

- `--model`: 要使用的Ollama模型名称（默认：llama3.2）
- `--prompts-file`: 提示词文件路径，每行一个提示词
- `--output-dir`: 输出目录（默认：outputs）
- `--system-prompt-file`: 系统提示词文件路径
- `--delay`: 请求之间的延迟（秒）（默认：0.5）
- `--api-url`: Ollama API URL（默认：http://localhost:11434）
- `--no-summary`: 不保存提示词和响应的摘要
- `--no-resume`: 不使用断点续传，重新处理所有提示词
- `--save-raw`: 保存原始API响应，便于调试

## 提示词文件格式

提示词文件应为纯文本文件，每行包含一个提示词。例如：

```
打开客厅的灯。
贾维斯，明天的天气怎么样。
今天天气真好。
```

对于多轮对话，可以使用以下格式：

```
用户A："哇，外面好亮啊。"
用户B："是啊，该起床了。"
```

## 系统提示词

系统提示词用于指导模型如何处理输入的提示词。默认系统提示词配置为对话意图识别任务，识别对话中是否含有指令，以及指令的类型。

如果需要自定义系统提示词，可以创建一个文本文件并使用`--system-prompt-file`参数指定。

## 输出格式

脚本将模型的响应保存为JSON文件，每个提示词对应一个输出文件。输出文件命名为`response_1_[哈希值].json`、`response_2_[哈希值].json`等，其中哈希值是根据提示词内容生成的唯一标识。

此外，脚本还会生成一个`summary.json`文件，包含所有提示词和响应的对应关系，便于后续分析和处理。如果不需要生成摘要文件，可以使用`--no-summary`参数。

对于对话意图识别任务，输出的JSON格式如下：

```json
{"call": true, "type": "NoAwakeWord", "instruction_type": "智能家居"}
```

## 示例

1. 使用默认配置运行：
   ```bash
   python test.py
   ```

2. 使用自定义提示词文件：
   ```bash
   python test.py --prompts-file my_prompts.txt
   ```

3. 使用不同的模型和输出目录：
   ```bash
   python test.py --model llama3.2 --output-dir results
   ```

4. 完整自定义配置：
   ```bash
   python test.py --model llama3.2 --prompts-file prompts.txt --output-dir results --system-prompt-file system.txt --delay 1.0 --api-url http://localhost:11434
   ```

## 断点续传

脚本支持断点续传功能，可以从上次中断的地方继续处理提示词。这对于处理大量提示词或者在处理过程中遇到中断的情况非常有用。

断点续传功能通过以下方式实现：
1. 每处理完一个提示词，立即更新摘要文件
2. 重新启动脚本时，会检查输出目录中是否存在已处理的响应文件
3. 如果找到已处理的响应文件，会跳过对应的提示词，继续处理未处理的提示词

如果不需要使用断点续传功能，可以使用`--no-resume`参数。

## API调用方式

脚本使用Ollama的Chat API，以系统身份发送系统提示词，以用户身份发送提示词列表中的提示词。这种方式更符合大语言模型的对话模式，可以获得更好的响应效果。

具体来说，脚本会构建如下格式的请求：

```json
{
  "model": "llama3.2",
  "messages": [
    {
      "role": "system",
      "content": "系统提示词内容..."
    },
    {
      "role": "user",
      "content": "用户提示词内容..."
    }
  ],
  "stream": false
}
```

## 原始API响应

如果使用`--save-raw`参数，脚本会在输出目录下创建一个`raw`子目录，用于保存原始的API响应。这对于调试和分析模型行为非常有用。

原始响应文件命名为`raw_response_1_[哈希值].json`、`raw_response_2_[哈希值].json`等。 