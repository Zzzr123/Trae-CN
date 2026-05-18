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
├── practice04/
│   └── chat_client.py     # AnythingLLM文档仓库集成实现
├── practice05/
│   └── chat_skill_client.py # 技能系统集成实现
├── practice06/
│   └── chat_chained_client.py # 链式工具调用功能实现
├── practice07/
│   ├── chat_chained_client.py # 链式工具调用功能实现（多文件操作版）
│   ├── 1.txt              # 测试文件1（值为42）
│   └── 2.txt              # 测试文件2（值为58）
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

### Practice 04: AnythingLLM文档仓库集成

**文件**: `practice04/chat_client.py`

**功能用途**:
- 提供交互式终端聊天界面
- 支持流式输出（边生成边显示）
- 自动维护聊天历史记录
- 每五次聊天提取一次关键信息
- 按照5W规则（Who、What、When、Where、Why）提取关键信息
- 将关键信息记录到本地文件 `D:\chat-log\log.txt`
- 支持通过 `/search` 命令或表达"查找聊天历史"的意思来搜索聊天历史
- **集成AnythingLLM文档仓库**，支持通过自然语言查询文档内容
- 当用户提到"文档仓库"、"文件仓库"、"仓库"时自动触发AnythingLLM查询
- 支持Ctrl+C退出
- 实时显示性能指标

**实现的教学目标**:
1. **外部API集成**: 学习如何集成第三方API服务（如AnythingLLM）
2. **subprocess模块使用**: 掌握使用subprocess调用系统命令（如curl）的方法
3. **工具调用系统**: 深入理解如何设计和实现复杂的工具调用功能
4. **文档仓库查询**: 学会如何让AI助手查询本地文档知识库
5. **中文编码处理**: 掌握API调用中的中文编码问题处理

**核心知识点**:
- subprocess模块调用系统命令
- curl命令调用HTTP API
- 中文编码处理（ensure_ascii=False）
- AnythingLLM API集成
- OpenAI工具调用API
- 聊天历史管理和搜索

**环境配置**:
在 `.env` 文件中添加以下配置：
```
ANYTHINGLLM_API_KEY=your_api_key
ANYTHINGLLM_WORKSPACE_SLUG=your_workspace_slug
```

**运行方式**:
```bash
python practice04/chat_client.py
```

**使用示例**:
```
=== LLM Chat Interface with AnythingLLM Integration ===
Type your message and press Enter. Press Ctrl+C to exit.
Use '/search' to search chat history.
Mention '文档仓库'、'文件仓库'、'仓库' to query AnythingLLM.
========================================================

You: 你好
Assistant: 你好！有什么可以帮助你的吗？

[Token Usage: 20, Time: 1.50s, Speed: 13.33 tokens/s]
[Chat History Length: 2 messages, Context Length: 50 characters]
[Conversation Count: 1]

You: 查询一下文档仓库中关于Python入门的内容
执行工具: anythingllm_query
工具执行结果: {"success": true, "data": {"response": "根据文档仓库的查询结果，Python入门文档包含以下内容..."}}

Assistant: 根据文档仓库的查询结果，Python入门文档包含以下内容：
1. Python基础语法介绍
2. 变量和数据类型
3. 控制流程语句
...

[Token Usage: 180, Time: 2.30s, Speed: 78.26 tokens/s]
[Chat History Length: 4 messages, Context Length: 200 characters]
[Conversation Count: 2]
```

### Practice 05: 技能系统集成

**文件**: `practice05/chat_skill_client.py`

**功能用途**:
- 提供交互式终端聊天界面
- 支持流式输出（边生成边显示）
- 自动维护聊天历史记录
- 每五次聊天提取一次关键信息
- 按照5W规则（Who、What、When、Where、Why）提取关键信息
- 将关键信息记录到本地文件 `D:\chat-log\log.txt`
- 支持通过 `/search` 命令或表达"查找聊天历史"的意思来搜索聊天历史
- 集成AnythingLLM文档仓库，支持通过自然语言查询文档内容
- **集成技能系统**，支持动态加载和使用技能
- 自动读取并显示可用技能列表
- 当用户需要使用技能时，自动加载技能内容并遵照执行
- 支持Ctrl+C退出
- 实时显示性能指标

**实现的教学目标**:
1. **技能系统设计**: 学习如何设计和实现一个可扩展的技能系统
2. **文件系统操作**: 掌握Python文件和目录的读取操作
3. **YAML解析**: 学会解析YAML front matter格式的内容
4. **动态技能加载**: 理解如何动态加载和使用技能
5. **工具调用系统**: 深入理解复杂的工具调用流程

**核心知识点**:
- 文件系统操作（os模块）
- YAML front matter解析
- 动态技能加载
- OpenAI工具调用API
- 聊天历史管理
- 流式API处理

**运行方式**:
```bash
python practice05/chat_skill_client.py
```

**使用示例**:

**示例1: 不指定部门，要求撰写五一节放假通知**
```
=== LLM Chat Interface with Skills Integration ===
Type your message and press Enter. Press Ctrl+C to exit.
Use '/search' to search chat history.
Mention '文档仓库'、'文件仓库'、'仓库' to query AnythingLLM.
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 请撰写一份关于五一节放假的通知
执行工具: load_skill_content
工具执行结果: {"success": true, "content": "# 通知撰写规则\n\n1. 通知不能以\"通知\"二字开头\n2. 必须冠以\"XX部\"的前缀，例如\"采购部通知\"、\"宣传部通知\"等\n3. 如果用户没有告知所在部门，就使用\"XX部\"代替\n4. 通知内容要正式、简洁、清晰\n5. 包含必要的信息：通知对象、通知事项、时间、相关要求等"}

Assistant: XX部通知
全体员工：

根据国家法定节假日规定，结合公司实际情况，现将2026年五一节放假安排通知如下：

一、放假时间：2026年5月1日（星期四）至5月5日（星期一），共5天。2026年4月27日（星期六）、4月28日（星期日）正常上班。

二、工作安排：
1. 各部门需在放假前做好安全检查工作，关闭门窗、电源等设施。
2. 值班人员要坚守岗位，保持通讯畅通，遇有突发事件及时报告。

三、注意事项：
1. 放假期间外出人员请注意安全，做好个人防护。
2. 请大家合理安排假期时间，保持良好的工作状态。

祝大家节日快乐！

XX部
2026年4月25日

[Token Usage: 200, Time: 3.50s, Speed: 57.14 tokens/s]
[Chat History Length: 4 messages, Context Length: 300 characters]
[Conversation Count: 1]
```

**示例2: 指定销售部，要求撰写五一节放假通知**
```
=== LLM Chat Interface with Skills Integration ===
Type your message and press Enter. Press Ctrl+C to exit.
Use '/search' to search chat history.
Mention '文档仓库'、'文件仓库'、'仓库' to query AnythingLLM.
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 我是销售部的，需要撰写一份关于五一节放假的通知
执行工具: load_skill_content
工具执行结果: {"success": true, "content": "# 通知撰写规则\n\n1. 通知不能以\"通知\"二字开头\n2. 必须冠以\"XX部\"的前缀，例如\"采购部通知\"、\"宣传部通知\"等\n3. 如果用户没有告知所在部门，就使用\"XX部\"代替\n4. 通知内容要正式、简洁、清晰\n5. 包含必要的信息：通知对象、通知事项、时间、相关要求等"}

Assistant: 销售部通知
全体销售部员工：

根据国家法定节假日规定，结合公司实际情况，现将2026年五一节放假安排通知如下：

一、放假时间：2026年5月1日（星期四）至5月5日（星期一），共5天。2026年4月27日（星期六）、4月28日（星期日）正常上班。

二、工作安排：
1. 各销售团队需在放假前与客户做好沟通工作，确保假期期间的业务顺利进行。
2. 值班人员要坚守岗位，保持通讯畅通，遇有客户咨询及时处理。

三、注意事项：
1. 放假期间外出人员请注意安全，做好个人防护。
2. 请大家合理安排假期时间，保持良好的工作状态。

祝大家节日快乐！

销售部
2026年4月25日

[Token Usage: 220, Time: 3.80s, Speed: 57.89 tokens/s]
[Chat History Length: 4 messages, Context Length: 350 characters]
[Conversation Count: 1]
```

### Practice 06: 链式工具调用（Chained Tool Calls）

**文件**: `practice06/chat_chained_client.py`

**功能用途**:
- 提供交互式终端聊天界面
- 支持流式输出（边生成边显示）
- 自动维护聊天历史记录
- 每五次聊天提取一次关键信息
- 按照5W规则（Who、What、When、Where、Why）提取关键信息
- 将关键信息记录到本地文件 `D:\chat-log\log.txt`
- 支持通过 `/search` 命令或表达"查找聊天历史"的意思来搜索聊天历史
- 集成AnythingLLM文档仓库，支持通过自然语言查询文档内容
- 集成技能系统，支持动态加载和使用技能
- **实现链式工具调用功能**，前一个工具的输出可以作为后一个工具的输入
- 支持文件搜索、内容读取、网页访问、文件写入等工具的组合使用
- 支持Ctrl+C退出
- 实时显示性能指标

**实现的教学目标**:
1. **链式调用设计**: 学习如何设计和实现链式工具调用系统
2. **上下文管理**: 掌握如何在多个工具调用之间传递数据和状态
3. **循环控制**: 学会如何设置最大迭代次数防止无限循环
4. **响应解析**: 掌握如何解析LLM返回的JSON格式和tool_calls格式响应
5. **错误处理**: 学会处理JSON解析失败、工具执行异常等情况

**核心知识点**:
- ChainedCallContext类设计和实现
- 链式调用执行流程
- JSON响应解析（支持markdown代码块标记）
- OpenAI标准Function Calling格式支持
- 上下文变量管理
- 最大迭代次数控制

**运行方式**:
```bash
python practice06/chat_chained_client.py
```

**测试场景**:

**测试1: 文件搜索链式调用**
```
=== LLM Chat Interface with Chained Tool Calls ===
Type your message and press Enter. Press Ctrl+C to exit.
支持链式工具调用，前一个工具的输出可以作为后一个工具的输入
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 请查找practice05目录下所有包含'def'关键词的文件，并总结这些文件的主要内容
检测到复杂请求，启动链式工具调用...

--- 迭代 1/10 ---
LLM响应: {"done":false,"tool_call":{"name":"search_files_with_keyword","arguments":{"directory":"practice05","keyword":"def"}}}
执行工具: search_files_with_keyword
参数: {'directory': 'practice05', 'keyword': 'def'}
工具执行结果: 成功

--- 迭代 2/10 ---
LLM响应: {"done":false,"tool_call":{"name":"read_file_content","arguments":{"filepath":"practice05/chat_skill_client.py"}}}
执行工具: read_file_content
参数: {'filepath': 'practice05/chat_skill_client.py'}
工具执行结果: 成功

--- 迭代 3/10 ---
LLM响应: {"done":true,"answer":"practice05目录下包含'def'关键词的文件是chat_skill_client.py。该文件主要包含以下功能：\n\n1. **环境变量加载**: load_env()函数用于从.env文件加载配置\n2. **上下文管理**: calculate_context_length()计算聊天上下文长度\n3. **聊天总结**: summarize_chat_history()对聊天历史进行总结\n4. **聊天压缩**: compress_chat_history()压缩聊天历史\n5. **信息提取**: extract_key_information()按5W规则提取关键信息\n6. **技能管理**: list_available_skills()和load_skill_content()管理技能系统\n7. **工具执行**: execute_tool()执行各种工具调用\n8. **链式调用**: execute_chained_tool_call()实现链式工具调用\n\n该文件是一个完整的AI聊天客户端，支持技能系统和链式工具调用功能。"}
任务完成！最终回答: practice05目录下包含'def'关键词的文件是chat_skill_client.py...

Assistant: practice05目录下包含'def'关键词的文件是chat_skill_client.py。该文件主要包含以下功能：

1. **环境变量加载**: load_env()函数用于从.env文件加载配置
2. **上下文管理**: calculate_context_length()计算聊天上下文长度
3. **聊天总结**: summarize_chat_history()对聊天历史进行总结
4. **聊天压缩**: compress_chat_history()压缩聊天历史
5. **信息提取**: extract_key_information()按5W规则提取关键信息
6. **技能管理**: list_available_skills()和load_skill_content()管理技能系统
7. **工具执行**: execute_tool()执行各种工具调用
8. **链式调用**: execute_chained_tool_call()实现链式工具调用

该文件是一个完整的AI聊天客户端，支持技能系统和链式工具调用功能。
```

**测试2: 技能查询链式调用**
```
=== LLM Chat Interface with Chained Tool Calls ===
Type your message and press Enter. Press Ctrl+C to exit.
支持链式工具调用，前一个工具的输出可以作为后一个工具的输入
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 我想了解notice技能的详细规则
检测到复杂请求，启动链式工具调用...

--- 迭代 1/10 ---
LLM响应: {"done":false,"tool_call":{"name":"load_skill_content","arguments":{"skill_name":"notice"}}}
执行工具: load_skill_content
参数: {'skill_name': 'notice'}
工具执行结果: 成功

--- 迭代 2/10 ---
LLM响应: {"done":true,"answer":"notice技能的详细规则如下：\n\n1. **标题规则**: 通知不能以\"通知\"二字开头\n2. **部门前缀**: 必须冠以\"XX部\"的前缀，例如\"采购部通知\"、\"宣传部通知\"等\n3. **默认部门**: 如果用户没有告知所在部门，就使用\"XX部\"代替\n4. **内容要求**: 通知内容要正式、简洁、清晰\n5. **必要信息**: 包含通知对象、通知事项、时间、相关要求等\n\n使用示例：\n- 用户未指定部门：输出\"XX部通知\"开头的内容\n- 用户指定部门为\"销售部\"：输出\"销售部通知\"开头的内容"}
任务完成！最终回答: notice技能的详细规则如下：...

Assistant: notice技能的详细规则如下：

1. **标题规则**: 通知不能以"通知"二字开头
2. **部门前缀**: 必须冠以"XX部"的前缀，例如"采购部通知"、"宣传部通知"等
3. **默认部门**: 如果用户没有告知所在部门，就使用"XX部"代替
4. **内容要求**: 通知内容要正式、简洁、清晰
5. **必要信息**: 包含通知对象、通知事项、时间、相关要求等

使用示例：
- 用户未指定部门：输出"XX部通知"开头的内容
- 用户指定部门为"销售部"：输出"销售部通知"开头的内容
```

**测试3: 网页处理链式调用**
```
=== LLM Chat Interface with Chained Tool Calls ===
Type your message and press Enter. Press Ctrl+C to exit.
支持链式工具调用，前一个工具的输出可以作为后一个工具的输入
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 访问https://www.nsu.edu/HTML/news/2024/06/article_3974.html并总结页面内容，保存到practice06/summary.txt
检测到复杂请求，启动链式工具调用...

--- 迭代 1/10 ---
LLM响应: {"done":false,"tool_call":{"name":"curl_get","arguments":{"url":"https://www.nsu.edu/HTML/news/2024/06/article_3974.html"}}}
执行工具: curl_get
参数: {'url': 'https://www.nsu.edu/HTML/news/2024/06/article_3974.html'}
工具执行结果: 成功

--- 迭代 2/10 ---
LLM响应: {"done":false,"tool_call":{"name":"write_file","arguments":{"filepath":"practice06/summary.txt","content":"【页面内容总结】\n\n根据网页内容，这是一篇关于...的新闻文章。\n\n主要内容：\n1. ...\n2. ...\n3. ...\n\n总结：..."}}}
执行工具: write_file
参数: {'filepath': 'practice06/summary.txt', 'content': '【页面内容总结】\n\n根据网页内容...'}
工具执行结果: 成功

--- 迭代 3/10 ---
LLM响应: {"done":true,"answer":"已成功访问网页并总结内容，保存到practice06/summary.txt文件中。\n\n总结内容：\n【页面内容总结】\n\n根据网页内容，这是一篇关于...的新闻文章。\n\n主要内容：\n1. ...\n2. ...\n3. ...\n\n总结：..."}
任务完成！最终回答: 已成功访问网页并总结内容，保存到practice06/summary.txt文件中...

Assistant: 已成功访问网页并总结内容，保存到practice06/summary.txt文件中。

总结内容：
【页面内容总结】

根据网页内容，这是一篇关于...的新闻文章。

主要内容：
1. ...
2. ...
3. ...

总结：...
```

### Practice 07: 链式工具调用（多文件操作版）

**文件**: `practice07/chat_chained_client.py`

**功能用途**:
- 提供交互式终端聊天界面
- 支持流式输出（边生成边显示）
- 自动维护聊天历史记录
- 每五次聊天提取一次关键信息
- 按照5W规则（Who、What、When、Where、Why）提取关键信息
- 将关键信息记录到本地文件 `D:\chat-log\log.txt`
- 支持通过 `/search` 命令或表达"查找聊天历史"的意思来搜索聊天历史
- 集成AnythingLLM文档仓库，支持通过自然语言查询文档内容
- 集成技能系统，支持动态加载和使用技能
- **实现链式工具调用功能**，前一个工具的输出可以作为后一个工具的输入
- 支持文件搜索、内容读取、网页访问、文件写入等工具的组合使用
- **新增多文件操作支持**，能够读取多个文件并进行运算后写入结果
- 支持Ctrl+C退出
- 实时显示性能指标

**实现的教学目标**:
1. **链式调用设计**: 学习如何设计和实现链式工具调用系统
2. **上下文管理**: 掌握如何在多个工具调用之间传递数据和状态
3. **循环控制**: 学会如何设置最大迭代次数防止无限循环
4. **响应解析**: 掌握如何解析LLM返回的JSON格式和tool_calls格式响应
5. **错误处理**: 学会处理JSON解析失败、工具执行异常等情况
6. **多文件操作**: 学会使用链式调用读取多个文件并进行运算

**核心知识点**:
- ChainedCallContext类设计和实现
- 链式调用执行流程
- JSON响应解析（支持markdown代码块标记）
- OpenAI标准Function Calling格式支持
- 上下文变量管理
- 最大迭代次数控制
- 多文件读取和运算

**运行方式**:
```bash
python practice07/chat_chained_client.py
```

**测试场景**:

**测试1: 文件搜索链式调用**
```
=== LLM Chat Interface with Chained Tool Calls (Practice07) ===
Type your message and press Enter. Press Ctrl+C to exit.
支持链式工具调用，前一个工具的输出可以作为后一个工具的输入
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 请查找practice06目录下所有包含'def'关键词的文件，并总结这些文件的主要内容
检测到复杂请求，启动链式工具调用...

--- 迭代 1/10 ---
LLM响应: {"done":false,"tool_call":{"name":"search_files_with_keyword","arguments":{"directory":"practice06","keyword":"def"}}}
执行工具: search_files_with_keyword
参数: {'directory': 'practice06', 'keyword': 'def'}
工具执行结果: 成功

--- 迭代 2/10 ---
LLM响应: {"done":false,"tool_call":{"name":"read_file_content","arguments":{"filepath":"practice06/chat_chained_client.py"}}}
执行工具: read_file_content
参数: {'filepath': 'practice06/chat_chained_client.py'}
工具执行结果: 成功

--- 迭代 3/10 ---
LLM响应: {"done":true,"answer":"practice06目录下包含'def'关键词的文件是chat_chained_client.py。该文件主要实现了链式工具调用功能..."}
任务完成！最终回答: practice06目录下包含'def'关键词的文件是chat_chained_client.py...

Assistant: practice06目录下包含'def'关键词的文件是chat_chained_client.py。该文件主要实现了链式工具调用功能...
```

**测试2: 多文件操作**
```
=== LLM Chat Interface with Chained Tool Calls (Practice07) ===
Type your message and press Enter. Press Ctrl+C to exit.
支持链式工具调用，前一个工具的输出可以作为后一个工具的输入
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 读取practice07/1.txt和practice07/2.txt两个文件，文件内容的都是正整数，把两个数相加的和写入result.txt文件
检测到复杂请求，启动链式工具调用...

--- 迭代 1/10 ---
LLM响应: {"done":false,"tool_call":{"name":"read_file_content","arguments":{"filepath":"practice07/1.txt"}}}
执行工具: read_file_content
参数: {'filepath': 'practice07/1.txt'}
工具执行结果: 成功，内容: "42"

--- 迭代 2/10 ---
LLM响应: {"done":false,"tool_call":{"name":"read_file_content","arguments":{"filepath":"practice07/2.txt"}}}
执行工具: read_file_content
参数: {'filepath': 'practice07/2.txt'}
工具执行结果: 成功，内容: "58"

--- 迭代 3/10 ---
LLM响应: {"done":false,"tool_call":{"name":"write_file","arguments":{"filepath":"practice07/result.txt","content":"100"}}}
执行工具: write_file
参数: {'filepath': 'practice07/result.txt', 'content': '100'}
工具执行结果: 成功

--- 迭代 4/10 ---
LLM响应: {"done":true,"answer":"已成功读取practice07/1.txt（值为42）和practice07/2.txt（值为58），将两个数相加的结果100写入到practice07/result.txt文件中。"}
任务完成！最终回答: 已成功读取practice07/1.txt（值为42）和practice07/2.txt（值为58）...

Assistant: 已成功读取practice07/1.txt（值为42）和practice07/2.txt（值为58），将两个数相加的结果100写入到practice07/result.txt文件中。
```

**测试3: 网页处理链式调用**
```
=== LLM Chat Interface with Chained Tool Calls (Practice07) ===
Type your message and press Enter. Press Ctrl+C to exit.
支持链式工具调用，前一个工具的输出可以作为后一个工具的输入
Available skills:
- notice: 撰写、修改、润色通知
====================================================

You: 访问https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html并总结页面内容，保存到practice07/summary.txt
检测到复杂请求，启动链式工具调用...

--- 迭代 1/10 ---
LLM响应: {"done":false,"tool_call":{"name":"curl_get","arguments":{"url":"https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html"}}}
执行工具: curl_get
参数: {'url': 'https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html'}
工具执行结果: 成功

--- 迭代 2/10 ---
LLM响应: {"done":true,"answer":"已成功访问网页，内容是关于成都东软学院在ICAIBD 2024（第七届人工智能与大数据国际会议）上取得突破性学术进展的报道。我校共有4篇论文成功入选，收录数量位居第二，成为中西部地区唯一有论文入选的民办高校。"}
任务完成！最终回答: 已成功访问网页...

Assistant: 已成功访问网页并总结内容，保存到practice07/summary.txt文件中。

总结内容：
成都东软学院在ICAIBD 2024（第七届人工智能与大数据国际会议）上取得突破性学术进展。我校共有4篇论文成功入选，收录数量位居第二，成为中西部地区唯一有论文入选的民办高校。
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
