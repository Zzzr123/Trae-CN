import os
import sys
import json
import time
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse, quote

# 强制设置 Python 默认编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# curl网络访问函数
def curl_get(url):
    """
    通过HTTP GET请求访问指定URL并返回网页内容
    参数:
        url: 要访问的网址
    返回:
        网页内容
    """
    try:
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        host = parsed_url.netloc
        # 对路径进行URL编码，保留斜杠，处理中文
        path = quote(parsed_url.path, safe='/')

        if scheme == 'https':
            conn = HTTPSConnection(host)
        else:
            conn = HTTPConnection(host)

        conn.request('GET', path)
        response = conn.getresponse()
        # 读取时强制使用UTF-8解码，忽略无法解析的字符
        content = response.read().decode('utf-8', errors='ignore')
        conn.close()

        return {"success": True, "content": content, "status": response.status, "reason": response.reason}
    except Exception as e:
        return {"success": False, "error": str(e)}

def execute_tool(tool_call):
    """
    执行工具调用
    """
    tool_name = tool_call.get('name')
    arguments = tool_call.get('arguments', {})

    if tool_name == "curl_get":
        return curl_get(arguments.get('url'))
    else:
        return {"success": False, "error": f"未知工具: {tool_name}"}

def main():
    # 直接写死 LM Studio 本地配置，无需 .env 文件
    base_url = "http://127.0.0.1:1234/v1"
    model = "qwen3.5-4b"
    token = "lm-studio"

    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'

    # 系统提示词，包含工具调用说明
    system_prompt = """
    你是一个AI助手，具有curl网络访问能力：

    curl_get: 通过HTTP GET请求访问指定URL并返回网页内容
       参数:
           url: 要访问的网址

    当用户的请求需要使用这个工具时，你应该生成tool_calls字段，包含工具调用的详细信息。
    """

    print("=== AI 对话工具已启动 ===")
    print("输入 'quit' 或 '退出' 结束对话\n")

    while True:
        user_input = input("请输入你的请求: ")

        # 退出逻辑
        if user_input.lower() in ["quit", "exit", "q", "退出"]:
            print("对话结束！")
            break

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "curl_get",
                        "description": "通过HTTP GET请求访问指定URL并返回网页内容",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "要访问的网址"
                                }
                            },
                            "required": ["url"]
                        }
                    }
                }
            ]
        }

        start_time = time.time()

        try:
            # 连接 LM Studio，根据 scheme 选择 HTTP/HTTPS
            if parsed_url.scheme == 'https':
                conn = HTTPSConnection(host)
            else:
                conn = HTTPConnection(host)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }

            conn.request('POST', path, json.dumps(payload), headers)
            response = conn.getresponse()
            response_data = response.read().decode('utf-8')
            conn.close()

            result = json.loads(response_data)

            end_time = time.time()
            total_time = end_time - start_time

            usage = result.get('usage', {})
            total_tokens = usage.get('total_tokens', 0)
            tokens_per_second = total_tokens / total_time if total_time > 0 else 0

            # 处理工具调用
            if result.get('choices'):
                choice = result['choices'][0]
                if choice.get('finish_reason') == 'tool_calls':
                    tool_calls = choice.get('message', {}).get('tool_calls', [])

                    for tool_call in tool_calls:
                        print(f"执行工具: {tool_call.get('function', {}).get('name')}")
                        tool_result = execute_tool({
                            'name': tool_call.get('function', {}).get('name'),
                            'arguments': json.loads(tool_call.get('function', {}).get('arguments', '{}'))
                        })

                        print(f"工具执行结果: {tool_result}")

                        # 将工具执行结果发送给LLM
                        second_payload = {
                            "model": model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_input},
                                choice['message'],
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.get('id'),
                                    "content": json.dumps(tool_result)
                                }
                            ],
                            "temperature": 0.7
                        }

                        # 第二次请求同样适配 HTTP/HTTPS
                        if parsed_url.scheme == 'https':
                            conn = HTTPSConnection(host)
                        else:
                            conn = HTTPConnection(host)

                        conn.request('POST', path, json.dumps(second_payload), headers)
                        second_response = conn.getresponse()
                        second_response_data = second_response.read().decode('utf-8')
                        conn.close()

                        second_result = json.loads(second_response_data)
                        if second_result.get('choices'):
                            second_choice = second_result['choices'][0]
                            print(f"\nAI响应: {second_choice.get('message', {}).get('content', '').strip()}")
                else:
                    print(f"\nAI响应: {choice.get('message', {}).get('content', '').strip()}")

            print(f"\nToken Usage: {total_tokens}, Time: {total_time:.2f}s, Speed: {tokens_per_second:.2f} tokens/s")
            print("-" * 50)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()