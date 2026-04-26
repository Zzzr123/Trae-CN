import os
import json
import time
import sys
from http.client import HTTPSConnection
from urllib.parse import urlparse

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def calculate_context_length(chat_history):
    """
    计算聊天上下文的长度
    """
    total_length = 0
    for message in chat_history:
        total_length += len(message.get('content', ''))
    return total_length

def summarize_chat_history(chat_history, host, path, headers, model):
    """
    使用LLM对聊天历史进行总结
    """
    # 准备总结请求
    summary_prompt = """
    请对以下聊天历史进行总结，提取关键信息和主要对话内容：
    
    {chat_history}
    
    总结要求：
    1. 简洁明了，抓住重点
    2. 保留重要的信息和决策
    3. 忽略无关细节
    """
    
    # 构建聊天历史文本
    chat_history_text = ""
    for message in chat_history:
        role = "用户" if message['role'] == 'user' else "助手"
        chat_history_text += f"{role}: {message['content']}\n"
    
    # 替换占位符
    summary_prompt = summary_prompt.format(chat_history=chat_history_text)
    
    # 准备请求 payload
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的对话总结助手，擅长提取对话的关键信息并进行简洁明了的总结。"},
            {"role": "user", "content": summary_prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        # 发送请求
        conn = HTTPSConnection(host)
        conn.request('POST', path, json.dumps(payload), headers)
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()
        
        # 解析响应
        result = json.loads(response_data)
        if result.get('choices'):
            summary = result['choices'][0].get('message', {}).get('content', '').strip()
            return summary
        else:
            return "聊天历史总结失败"
    except Exception as e:
        print(f"总结聊天历史时出错: {e}")
        return "聊天历史总结失败"

def compress_chat_history(chat_history, host, path, headers, model):
    """
    压缩聊天历史，前70%内容总结，后30%内容保留原文
    """
    if len(chat_history) <= 2:
        return chat_history
    
    # 计算分割点
    split_point = int(len(chat_history) * 0.7)
    
    # 前70%的内容
    early_history = chat_history[:split_point]
    # 后30%的内容
    recent_history = chat_history[split_point:]
    
    # 对前70%的内容进行总结
    summary = summarize_chat_history(early_history, host, path, headers, model)
    
    # 构建压缩后的聊天历史
    compressed_history = [
        {"role": "system", "content": f"以下是之前对话的总结：\n{summary}"}
    ] + recent_history
    
    return compressed_history

def extract_key_information(chat_history, host, path, headers, model):
    """
    按照5W规则提取关键信息
    """
    # 准备提取请求
    extract_prompt = """
    请对以下聊天历史按照5W规则提取关键信息：
    Who（谁）、What（做了什么事）、When（什么时候，可选）、Where（在何处，可选）、Why（为什么要做这个事，可选）
    
    {chat_history}
    
    提取要求：
    1. 每条关键信息都要按照5W规则进行提取
    2. 提取多条关键信息，确保覆盖主要内容
    3. 格式清晰，易于阅读
    """
    
    # 构建聊天历史文本
    chat_history_text = ""
    for message in chat_history:
        role = "用户" if message['role'] == 'user' else "助手"
        chat_history_text += f"{role}: {message['content']}\n"
    
    # 替换占位符
    extract_prompt = extract_prompt.format(chat_history=chat_history_text)
    
    # 准备请求 payload
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的信息提取助手，擅长按照5W规则从对话中提取关键信息。"},
            {"role": "user", "content": extract_prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        # 发送请求
        conn = HTTPSConnection(host)
        conn.request('POST', path, json.dumps(payload), headers)
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()
        
        # 解析响应
        result = json.loads(response_data)
        if result.get('choices'):
            key_info = result['choices'][0].get('message', {}).get('content', '').strip()
            return key_info
        else:
            return "关键信息提取失败"
    except Exception as e:
        print(f"提取关键信息时出错: {e}")
        return "关键信息提取失败"

def log_key_information(key_info):
    """
    将关键信息记录到D:\chat-log\log.txt
    """
    log_dir = "D:\chat-log"
    log_file = os.path.join(log_dir, "log.txt")
    
    # 确保目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 写入关键信息
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(key_info)
        f.write("\n" + "-" * 80 + "\n")
    
    print(f"关键信息已记录到: {log_file}")

def search_chat_history(query):
    """
    搜索聊天历史
    """
    log_file = "D:\chat-log\log.txt"
    
    # 检查文件是否存在
    if not os.path.exists(log_file):
        return {"success": False, "error": "聊天历史文件不存在"}
    
    # 读取文件内容
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {"success": True, "content": content, "query": query}

def execute_tool(tool_call):
    """
    执行工具调用
    """
    tool_name = tool_call.get('name')
    arguments = tool_call.get('arguments', {})
    
    if tool_name == "search_chat_history":
        return search_chat_history(arguments.get('query', ''))
    else:
        return {"success": False, "error": f"未知工具: {tool_name}"}

def main():
    env = load_env()
    base_url = env.get('BASE_URL', 'https://api.openai.com/v1')
    model = env.get('MODEL', 'gpt-3.5-turbo')
    token = env.get('TOKEN')
    
    if not token:
        print("Error: TOKEN not found in .env file")
        return
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    
    chat_history = []
    conversation_count = 0
    
    print("=== LLM Chat Interface with History Logger ===")
    print("Type your message and press Enter. Press Ctrl+C to exit.")
    print("Use '/search' to search chat history.")
    print("==============================================\n")
    
    try:
        while True:
            # 检查是否需要压缩聊天历史
            context_length = calculate_context_length(chat_history)
            if len(chat_history) >= 10 or context_length >= 3000:  # 5轮对话，每轮包含user和assistant，所以是10条消息
                print("检测到聊天历史过长，正在进行压缩...")
                
                # 准备请求头
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                
                # 压缩聊天历史
                chat_history = compress_chat_history(chat_history, host, path, headers, model)
                print("聊天历史压缩完成！")
            
            # 检查是否需要提取关键信息
            if conversation_count > 0 and conversation_count % 5 == 0:  # 每5轮对话提取一次关键信息
                print("正在提取关键信息...")
                
                # 准备请求头
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                
                # 提取关键信息
                key_info = extract_key_information(chat_history, host, path, headers, model)
                # 记录关键信息
                log_key_information(key_info)
            
            # Get user input
            user_input = input("You: ")
            
            # 检查是否是搜索命令
            if user_input.startswith('/search') or '查找聊天历史' in user_input:
                # 准备请求头
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                
                # 执行搜索
                search_result = search_chat_history(user_input)
                
                # 准备搜索请求
                search_payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "你是一个聊天历史搜索助手，根据用户的查询和聊天历史记录，提供相关的回答。"},
                        {"role": "user", "content": f"用户查询: {user_input}\n\n聊天历史记录:\n{search_result.get('content', '')}"}
                    ],
                    "temperature": 0.7
                }
                
                # 发送请求
                conn = HTTPSConnection(host)
                conn.request('POST', path, json.dumps(search_payload), headers)
                response = conn.getresponse()
                response_data = response.read().decode('utf-8')
                conn.close()
                
                # 解析响应
                result = json.loads(response_data)
                if result.get('choices'):
                    search_response = result['choices'][0].get('message', {}).get('content', '').strip()
                    print(f"\nAssistant: {search_response}\n")
                continue
            
            # Add user message to history
            chat_history.append({"role": "user", "content": user_input})
            
            # 准备工具调用配置
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "search_chat_history",
                        "description": "搜索聊天历史记录",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "搜索查询"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]
            
            # Prepare payload
            payload = {
                "model": model,
                "messages": chat_history,
                "temperature": 0.7,
                "stream": True,
                "tools": tools
            }
            
            # Send streaming request
            start_time = time.time()
            total_tokens = 0
            
            try:
                conn = HTTPSConnection(host)
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                
                conn.request('POST', path, json.dumps(payload), headers)
                response = conn.getresponse()
                
                print("Assistant: ", end="")
                sys.stdout.flush()
                
                assistant_response = ""
                tool_calls = []
                
                # Process streaming response
                for line in response:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content = delta['content']
                                    print(content, end="")
                                    sys.stdout.flush()
                                    assistant_response += content
                                elif 'tool_calls' in delta:
                                    tool_calls = delta['tool_calls']
                                
                            if 'usage' in chunk:
                                total_tokens = chunk['usage'].get('total_tokens', 0)
                        except json.JSONDecodeError:
                            pass
                
                conn.close()
                
                # 处理工具调用
                if tool_calls:
                    for tool_call in tool_calls:
                        tool_name = tool_call.get('function', {}).get('name')
                        arguments = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
                        
                        print(f"\n执行工具: {tool_name}")
                        tool_result = execute_tool({
                            'name': tool_name,
                            'arguments': arguments
                        })
                        
                        print(f"工具执行结果: {tool_result}")
                        
                        # 将工具执行结果发送给LLM
                        second_payload = {
                            "model": model,
                            "messages": chat_history + [
                                {"role": "assistant", "content": None, "tool_calls": tool_calls},
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.get('id'),
                                    "content": json.dumps(tool_result)
                                }
                            ],
                            "temperature": 0.7
                        }
                        
                        conn = HTTPSConnection(host)
                        conn.request('POST', path, json.dumps(second_payload), headers)
                        second_response = conn.getresponse()
                        second_response_data = second_response.read().decode('utf-8')
                        conn.close()
                        
                        second_result = json.loads(second_response_data)
                        if second_result.get('choices'):
                            second_choice = second_result['choices'][0]
                            tool_response = second_choice.get('message', {}).get('content', '').strip()
                            print(f"\nAssistant: {tool_response}")
                            assistant_response = tool_response
                
                # Add assistant response to history
                chat_history.append({"role": "assistant", "content": assistant_response})
                conversation_count += 1
                
                # Calculate performance
                end_time = time.time()
                total_time = end_time - start_time
                tokens_per_second = total_tokens / total_time if total_time > 0 else 0
                
                print(f"\n\n[Token Usage: {total_tokens}, Time: {total_time:.2f}s, Speed: {tokens_per_second:.2f} tokens/s]")
                print(f"[Chat History Length: {len(chat_history)} messages, Context Length: {calculate_context_length(chat_history)} characters]")
                print(f"[Conversation Count: {conversation_count}]\n")
                
            except Exception as e:
                print(f"\nError: {e}\n")
                # Remove the last user message from history to allow retry
                if chat_history and chat_history[-1]['role'] == 'user':
                    chat_history.pop()
    
    except KeyboardInterrupt:
        print("\n\nExiting chat interface. Goodbye!")

if __name__ == "__main__":
    main()