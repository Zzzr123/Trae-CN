import os
import json
import time
import sys
import subprocess
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
    total_length = 0
    for message in chat_history:
        total_length += len(message.get('content', ''))
    return total_length

def summarize_chat_history(chat_history, host, path, headers, model):
    summary_prompt = """
    请对以下聊天历史进行总结，提取关键信息和主要对话内容：

    {chat_history}

    总结要求：
    1. 简洁明了，抓住重点
    2. 保留重要的信息和决策
    3. 忽略无关细节
    """

    chat_history_text = ""
    for message in chat_history:
        role = "用户" if message['role'] == 'user' else "助手"
        chat_history_text += f"{role}: {message['content']}\n"

    summary_prompt = summary_prompt.format(chat_history=chat_history_text)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的对话总结助手，擅长提取对话的关键信息并进行简洁明了的总结。"},
            {"role": "user", "content": summary_prompt}
        ],
        "temperature": 0.3
    }

    try:
        conn = HTTPSConnection(host)
        conn.request('POST', path, json.dumps(payload), headers)
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()

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
    if len(chat_history) <= 2:
        return chat_history

    split_point = int(len(chat_history) * 0.7)
    early_history = chat_history[:split_point]
    recent_history = chat_history[split_point:]

    summary = summarize_chat_history(early_history, host, path, headers, model)

    compressed_history = [
        {"role": "system", "content": f"以下是之前对话的总结：\n{summary}"}
    ] + recent_history

    return compressed_history

def extract_key_information(chat_history, host, path, headers, model):
    extract_prompt = """
    请对以下聊天历史按照5W规则提取关键信息：
    Who（谁）、What（做了什么事）、When（什么时候，可选）、Where（在何处，可选）、Why（为什么要做这个事，可选）

    {chat_history}

    提取要求：
    1. 每条关键信息都要按照5W规则进行提取
    2. 提取多条关键信息，确保覆盖主要内容
    3. 格式清晰，易于阅读
    """

    chat_history_text = ""
    for message in chat_history:
        role = "用户" if message['role'] == 'user' else "助手"
        chat_history_text += f"{role}: {message['content']}\n"

    extract_prompt = extract_prompt.format(chat_history=chat_history_text)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的信息提取助手，擅长按照5W规则从对话中提取关键信息。"},
            {"role": "user", "content": extract_prompt}
        ],
        "temperature": 0.3
    }

    try:
        conn = HTTPSConnection(host)
        conn.request('POST', path, json.dumps(payload), headers)
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()

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
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chat-log')
    log_file = os.path.join(log_dir, "log.txt")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(key_info)
        f.write("\n" + "-" * 80 + "\n")

    print(f"关键信息已记录到: {log_file}")

def search_chat_history(query):
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chat-log', 'log.txt')

    if not os.path.exists(log_file):
        return {"success": False, "error": "聊天历史文件不存在"}

    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()

    return {"success": True, "content": content, "query": query}

def anythingllm_query(query):
    """
    使用curl访问AnythingLLM的聊天API
    """
    env = load_env()
    api_key = env.get('ANYTHINGLLM_API_KEY')
    workspace_slug = env.get('ANYTHINGLLM_WORKSPACE_SLUG')

    if not api_key or not workspace_slug:
        return {"success": False, "error": "ANYTHINGLLM_API_KEY 或 ANYTHINGLLM_WORKSPACE_SLUG 未配置"}

    url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"

    try:
        cmd = [
            'curl', '-X', 'POST', url,
            '-H', f'Authorization: Bearer {api_key}',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({"message": query}, ensure_ascii=False),
            '-s'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            return {"success": False, "error": f"Curl命令执行失败: {result.stderr}"}

        response_text = result.stdout

        try:
            response_data = json.loads(response_text)
            if response_data.get('error'):
                return {"success": False, "error": response_data.get('error')}
            return {"success": True, "data": response_data}
        except json.JSONDecodeError:
            return {"success": True, "content": response_text}

    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_tool(tool_call):
    tool_name = tool_call.get('name')
    arguments = tool_call.get('arguments', {})

    if tool_name == "search_chat_history":
        return search_chat_history(arguments.get('query', ''))
    elif tool_name == "anythingllm_query":
        return anythingllm_query(arguments.get('query', ''))
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

    print("=== LLM Chat Interface with AnythingLLM Integration ===")
    print("Type your message and press Enter. Press Ctrl+C to exit.")
    print("Use '/search' to search chat history.")
    print("Mention '文档仓库'、'文件仓库'、'仓库' to query AnythingLLM.")
    print("========================================================\n")

    system_prompt = """
    你是一个AI助手，具有以下工具调用能力：

    1. search_chat_history: 搜索聊天历史记录
       参数:
           query: 搜索查询

    2. anythingllm_query: 查询AnythingLLM文档仓库
       参数:
           query: 查询内容
       当用户提到"文档仓库"、"文件仓库"、"仓库"时使用此工具

    当用户的请求需要使用这些工具时，你应该生成tool_calls字段，包含工具调用的详细信息。
    """

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
        },
        {
            "type": "function",
            "function": {
                "name": "anythingllm_query",
                "description": "查询AnythingLLM文档仓库，获取相关文档内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "查询内容"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    try:
        while True:
            context_length = calculate_context_length(chat_history)
            if len(chat_history) >= 10 or context_length >= 3000:
                print("检测到聊天历史过长，正在进行压缩...")

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }

                chat_history = compress_chat_history(chat_history, host, path, headers, model)
                print("聊天历史压缩完成！")

            if conversation_count > 0 and conversation_count % 5 == 0:
                print("正在提取关键信息...")

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }

                key_info = extract_key_information(chat_history, host, path, headers, model)
                log_key_information(key_info)

            user_input = input("You: ")

            if user_input.startswith('/search') or '查找聊天历史' in user_input:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }

                search_result = search_chat_history(user_input)

                search_payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "你是一个聊天历史搜索助手，根据用户的查询和聊天历史记录，提供相关的回答。"},
                        {"role": "user", "content": f"用户查询: {user_input}\n\n聊天历史记录:\n{search_result.get('content', '')}"}
                    ],
                    "temperature": 0.7
                }

                conn = HTTPSConnection(host)
                conn.request('POST', path, json.dumps(search_payload), headers)
                response = conn.getresponse()
                response_data = response.read().decode('utf-8')
                conn.close()

                result = json.loads(response_data)
                if result.get('choices'):
                    search_response = result['choices'][0].get('message', {}).get('content', '').strip()
                    print(f"\nAssistant: {search_response}\n")
                continue

            chat_history.append({"role": "user", "content": user_input})

            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system_prompt}] + chat_history,
                "temperature": 0.7,
                "stream": True,
                "tools": tools
            }

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

                        second_payload = {
                            "model": model,
                            "messages": [{"role": "system", "content": system_prompt}] + chat_history + [
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

                chat_history.append({"role": "assistant", "content": assistant_response})
                conversation_count += 1

                end_time = time.time()
                total_time = end_time - start_time
                tokens_per_second = total_tokens / total_time if total_time > 0 else 0

                print(f"\n\n[Token Usage: {total_tokens}, Time: {total_time:.2f}s, Speed: {tokens_per_second:.2f} tokens/s]")
                print(f"[Chat History Length: {len(chat_history)} messages, Context Length: {calculate_context_length(chat_history)} characters]")
                print(f"[Conversation Count: {conversation_count}]\n")

            except Exception as e:
                print(f"\nError: {e}\n")
                if chat_history and chat_history[-1]['role'] == 'user':
                    chat_history.pop()

    except KeyboardInterrupt:
        print("\n\nExiting chat interface. Goodbye!")

if __name__ == "__main__":
    main()