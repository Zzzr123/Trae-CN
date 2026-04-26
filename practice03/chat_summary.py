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
    
    print("=== LLM Chat Interface with Summary ===")
    print("Type your message and press Enter. Press Ctrl+C to exit.")
    print("=======================================\n")
    
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
                
            # Get user input
            user_input = input("You: ")
            
            # Add user message to history
            chat_history.append({"role": "user", "content": user_input})
            
            # Prepare payload
            payload = {
                "model": model,
                "messages": chat_history,
                "temperature": 0.7,
                "stream": True
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
                                
                            if 'usage' in chunk:
                                total_tokens = chunk['usage'].get('total_tokens', 0)
                        except json.JSONDecodeError:
                            pass
                
                conn.close()
                
                # Add assistant response to history
                chat_history.append({"role": "assistant", "content": assistant_response})
                
                # Calculate performance
                end_time = time.time()
                total_time = end_time - start_time
                tokens_per_second = total_tokens / total_time if total_time > 0 else 0
                
                print(f"\n\n[Token Usage: {total_tokens}, Time: {total_time:.2f}s, Speed: {tokens_per_second:.2f} tokens/s]")
                print(f"[Chat History Length: {len(chat_history)} messages, Context Length: {calculate_context_length(chat_history)} characters]\n")
                
            except Exception as e:
                print(f"\nError: {e}\n")
                # Remove the last user message from history to allow retry
                if chat_history and chat_history[-1]['role'] == 'user':
                    chat_history.pop()
    
    except KeyboardInterrupt:
        print("\n\nExiting chat interface. Goodbye!")

if __name__ == "__main__":
    main()