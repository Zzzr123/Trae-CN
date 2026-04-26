# AI智能体开发教学项目

这是一个基于Python的AI智能体开发教学项目，旨在通过实践练习帮助学习者掌握AI智能体的核心开发技能。

## 项目结构

```
.
├── practice01/
│   └── llm_client.py       # LLM客户端实现
├── practice02/
│   ├── chat_interface.py   # 终端聊天界面实现
│   ├── tool_caller.py      # 工具调用功能实现
│   └── tool_chat_client.py # 带curl网络访问功能的聊天客户端
├── practice03/
│   ├── chat_summary.py     # 聊天记录总结和压缩功能实现
│   └── chat_history_logger.py # 聊天历史记录和搜索功能实现
├── .gitignore             # Git忽略文件
├── env.example            # 环境变量配置模板
└── README.md              # 项目说明文档
```

## 环境配置

1. 复制 `env.example` 为 `.env` 文件
2. 填写正确的LLM API配置信息：
   - `BASE_URL`: OpenAI兼容的API地址
   - `MODEL`: 使用的模型名称
   - `TOKEN`: API访问令牌

## 练习说明

### Practice 01: LLM客户端基础

**文件**: `practice01/llm_client.py`

**功能用途**:
- 读取项目根目录的`.env`配置文件
- 使用Python标准HTTP库访问OpenAI兼容协议的LLM API
- 发送对话请求并获取响应
- 统计和显示性能指标

**实现的教学目标**:
1. **环境变量管理**: 学习如何安全地管理API密钥和配置信息
2. **HTTP客户端开发**: 掌握使用Python标准库进行HTTP请求的方法
3. **API集成**: 理解OpenAI兼容API的调用方式和数据格式
4. **性能监控**: 学会统计和计算API调用的性能指标
5. **错误处理**: 掌握基本的异常处理和错误提示

**核心知识点**:
- 文件操作（读取.env配置）
- URL解析和HTTP连接
- JSON数据处理
- 时间计算和性能统计
- Token消耗分析

**运行方式**:
```bash
python practice01/llm_client.py
```

**输出示例**:
```
Request completed successfully!
Model: gpt-3.5-turbo
Base URL: https://api.openai.com/v1
Prompt: Hello, how are you?
Response: I'm doing well, thank you for asking!

Token Usage:
  Prompt tokens: 10
  Completion tokens: 15
  Total tokens: 25

Performance:
  Total time: 1.23 seconds
  Tokens per second: 20.33
```

### Practice 02a: 终端聊天界面

**文件**: `practice02/chat_interface.py`

**功能用途**:
- 提供交互式终端聊天界面
- 支持流式输出（边生成边显示）
- 自动维护聊天历史记录
- 支持Ctrl+C退出
- 实时显示性能指标

**实现的教学目标**:
1. **交互式界面开发**: 学习如何创建命令行交互式应用
2. **流式API处理**: 掌握处理流式响应的方法
3. **状态管理**: 学习如何维护和管理聊天上下文
4. **用户体验优化**: 理解如何提供实时反馈和良好的用户体验
5. **异常处理与控制流**: 掌握键盘中断处理和错误恢复

**核心知识点**:
- 标准输入/输出处理
- 流式HTTP响应处理
- 聊天历史管理
- 性能实时计算
- 异常捕获和处理

**运行方式**:
```bash
python practice02/chat_interface.py
```

**使用示例**:
```
=== LLM Chat Interface ===
Type your message and press Enter. Press Ctrl+C to exit.
==========================

You: Hello
Assistant: Hi there! How can I help you today?

[Token Usage: 20, Time: 1.50s, Speed: 13.33 tokens/s]

You: What's the weather like today?
Assistant: I'm sorry, I don't have access to real-time weather information. But I can help you with many other topics!

[Token Usage: 45, Time: 2.10s, Speed: 21.43 tokens/s]

^C

Exiting chat interface. Goodbye!
```

### Practice 02b: 工具调用功能

**文件**: `practice02/tool_caller.py`

**功能用途**:
- 实现6个工具函数（5个文件操作工具 + 1个网络访问工具）
- 支持LLM工具调用能力
- 交互式命令行界面
- 工具执行结果处理

**实现的教学目标**:
1. **工具调用设计**: 学习如何设计和实现工具调用系统
2. **API集成**: 掌握OpenAI工具调用API的使用方法
3. **文件操作**: 学习Python文件系统操作
4. **函数式编程**: 理解函数设计和参数传递
5. **错误处理**: 掌握工具执行中的异常处理

**核心知识点**:
- 文件系统操作（列出、重命名、删除、创建、读取）
- 网络访问（HTTP/HTTPS请求）
- OpenAI工具调用API
- JSON数据处理
- 函数设计和参数验证
- 异常处理和错误恢复

**运行方式**:
```bash
python practice02/tool_caller.py
```

**使用示例**:
```
请输入你的请求: 列出当前目录下的文件
执行工具: list_files
工具执行结果: {"success": true, "data": [{"name": "chat_interface.py", "size": 3500, "modified_time": "2026-04-22 10:55:00", "type": "file"}, {"name": "tool_caller.py", "size": 8000, "modified_time": "2026-04-22 11:15:00", "type": "file"}]}

AI响应: 当前目录下有2个文件：
1. chat_interface.py (3500字节, 修改时间: 2026-04-22 10:55:00)
2. tool_caller.py (8000字节, 修改时间: 2026-04-22 11:15:00)

Token Usage: 150, Time: 2.30s, Speed: 65.22 tokens/s
--------------------------------------------------

请输入你的请求: 在当前目录创建一个test.txt文件，内容为Hello World
执行工具: create_file
工具执行结果: {"success": true, "message": "文件已创建: test.txt"}

AI响应: 已成功创建test.txt文件，内容为"Hello World"。

Token Usage: 180, Time: 1.90s, Speed: 94.74 tokens/s
--------------------------------------------------

请输入你的请求: 访问百度首页并返回内容
执行工具: curl_get
工具执行结果: {"success": true, "content": "<!DOCTYPE html>...", "status": 200, "reason": "OK"}

AI响应: 已成功访问百度首页，返回状态码200。

Token Usage: 200, Time: 1.50s, Speed: 133.33 tokens/s
--------------------------------------------------
```

### Practice 02c: 带curl网络访问功能的聊天客户端

**文件**: `practice02/tool_chat_client.py`

**功能用途**:
- 实现curl网络访问工具函数
- 支持LLM工具调用能力
- 交互式命令行界面
- 工具执行结果处理

**实现的教学目标**:
1. **网络访问实现**: 学习如何使用Python标准库进行HTTP/HTTPS请求
2. **工具调用设计**: 学习如何设计和实现工具调用系统
3. **API集成**: 掌握OpenAI工具调用API的使用方法
4. **函数式编程**: 理解函数设计和参数传递
5. **错误处理**: 掌握工具执行中的异常处理

**核心知识点**:
- 网络访问（HTTP/HTTPS请求）
- OpenAI工具调用API
- JSON数据处理
- 函数设计和参数验证
- 异常处理和错误恢复

**运行方式**:
```bash
python practice02/tool_chat_client.py
```

**使用示例**:
```
请输入你的请求: 访问GitHub首页并返回内容
执行工具: curl_get
工具执行结果: {"success": true, "content": "<!DOCTYPE html>...", "status": 200, "reason": "OK"}

AI响应: 已成功访问GitHub首页，返回状态码200。

Token Usage: 180, Time: 2.10s, Speed: 85.71 tokens/s
--------------------------------------------------
```

### Practice 03: 聊天记录总结和压缩功能

**文件**: `practice03/chat_summary.py`

**功能用途**:
- 提供交互式终端聊天界面
- 支持流式输出（边生成边显示）
- 自动维护聊天历史记录
- 聊天历史记录检测和压缩
- 支持Ctrl+C退出
- 实时显示性能指标

**实现的教学目标**:
1. **聊天历史管理**: 学习如何管理和维护聊天上下文
2. **自动总结功能**: 掌握使用LLM对聊天历史进行总结的方法
3. **上下文压缩**: 理解如何在保持对话连贯性的同时减少上下文长度
4. **性能优化**: 学习如何通过压缩上下文来提高LLM的响应速度和降低token消耗
5. **用户体验优化**: 理解如何在后台执行总结操作而不影响用户体验

**核心知识点**:
- 聊天历史管理和检测
- LLM总结功能实现
- 上下文长度计算和控制
- 流式API处理
- 性能实时计算

**运行方式**:
```bash
python practice03/chat_summary.py
```

**使用示例**:
```
=== LLM Chat Interface with Summary ===
Type your message and press Enter. Press Ctrl+C to exit.
=======================================

You: Hello
Assistant: Hi there! How can I help you today?

[Token Usage: 20, Time: 1.50s, Speed: 13.33 tokens/s]
[Chat History Length: 2 messages, Context Length: 50 characters]

... 多轮对话后 ...

检测到聊天历史过长，正在进行压缩...
聊天历史压缩完成！

You: What was our previous conversation about?
Assistant: Based on our previous conversation summary, we discussed...

[Token Usage: 150, Time: 2.30s, Speed: 65.22 tokens/s]
[Chat History Length: 5 messages, Context Length: 1200 characters]
```

### Practice 03b: 聊天历史记录和搜索功能

**文件**: `practice03/chat_history_logger.py`

**功能用途**:
- 提供交互式终端聊天界面
- 支持流式输出（边生成边显示）
- 自动维护聊天历史记录
- 每五次聊天提取一次关键信息
- 按照5W规则（Who、What、When、Where、Why）提取关键信息
- 将关键信息记录到本地文件 `D:\chat-log\log.txt`
- 支持通过 `/search` 命令或表达"查找聊天历史"的意思来搜索聊天历史
- 支持Ctrl+C退出
- 实时显示性能指标

**实现的教学目标**:
1. **关键信息提取**: 学习如何使用LLM按照特定规则提取关键信息
2. **本地文件操作**: 掌握Python文件和目录的创建、读写操作
3. **工具调用系统**: 学习如何设计和实现工具调用功能
4. **聊天历史管理**: 理解如何有效管理和利用聊天历史记录
5. **用户交互优化**: 学习如何通过命令和自然语言触发特定功能

**核心知识点**:
- 5W规则信息提取
- 本地文件系统操作
- OpenAI工具调用API
- 聊天历史管理和搜索
- 流式API处理

**运行方式**:
```bash
python practice03/chat_history_logger.py
```

**使用示例**:
```
=== LLM Chat Interface with History Logger ===
Type your message and press Enter. Press Ctrl+C to exit.
Use '/search' to search chat history.
==============================================

You: Hello
Assistant: Hi there! How can I help you today?

[Token Usage: 20, Time: 1.50s, Speed: 13.33 tokens/s]
[Chat History Length: 2 messages, Context Length: 50 characters]
[Conversation Count: 1]

... 多轮对话后 ...

正在提取关键信息...
关键信息已记录到: D:\chat-log\log.txt

You: /search 之前我们聊了什么
执行工具: search_chat_history
工具执行结果: {"success": true, "content": "[2026-04-26 22:30:00]\n1. Who: 用户\n   What: 向助手打招呼\n   When: 2026-04-26 22:30\n   Why: 开始对话\n\n2. Who: 助手\n   What: 回应用户并询问如何帮助\n   When: 2026-04-26 22:30\n   Why: 响应用户的问候\n------------------------------", "query": "/search 之前我们聊了什么"}

Assistant: 根据聊天历史记录，之前我们的对话内容是：
1. 用户向助手打招呼，开始对话
2. 助手回应用户并询问如何帮助

[Token Usage: 150, Time: 2.30s, Speed: 65.22 tokens/s]
[Chat History Length: 10 messages, Context Length: 1500 characters]
[Conversation Count: 5]
```

## 技术栈

- Python 3.6+
- 标准库: `os`, `json`, `time`, `http.client`, `urllib.parse`
- OpenAI兼容API

## 学习路径

1. 配置开发环境
2. 完成Practice 01，掌握基础的LLM API调用
3. 后续练习将逐步深入智能体开发的高级主题

## 注意事项

- 请勿将`.env`文件提交到版本控制系统
- API Token需要妥善保管，避免泄露
- 确保网络连接正常以访问LLM API
