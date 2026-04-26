import os
import json
import time
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

# 工具函数1: 列出目录下的文件及属性
def list_files(directory):
    """
    列出指定目录下的所有文件及其基本属性
    参数:
        directory: 目录路径
    返回:
        包含文件信息的列表
    """
    try:
        files_info = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files_info.append({
                    "name": filename,
                    "size": stat.st_size,
                    "modified_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime)),
                    "type": "file"
                })
            elif os.path.isdir(filepath):
                files_info.append({
                    "name": filename,
                    "type": "directory"
                })
        return {"success": True, "data": files_info}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 工具函数2: 修改文件名称
def rename_file(directory, old_name, new_name):
    """
    修改指定目录下的文件名称
    参数:
        directory: 目录路径
        old_name: 原文件名
        new_name: 新文件名
    返回:
        操作结果
    """
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            return {"success": True, "message": f"文件已重命名为: {new_name}"}
        else:
            return {"success": False, "error": "文件不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 工具函数3: 删除文件
def delete_file(directory, filename):
    """
    删除指定目录下的文件
    参数:
        directory: 目录路径
        filename: 要删除的文件名
    返回:
        操作结果
    """
    try:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return {"success": True, "message": "文件已删除"}
        else:
            return {"success": False, "error": "文件不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 工具函数4: 新建文件并写入内容
def create_file(directory, filename, content):
    """
    在指定目录下新建文件并写入内容
    参数:
        directory: 目录路径
        filename: 文件名
        content: 文件内容
    返回:
        操作结果
    """
    try:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"文件已创建: {filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 工具函数5: 读取文件内容
def read_file(directory, filename):
    """
    读取指定目录下的文件内容
    参数:
        directory: 目录路径
        filename: 文件名
    返回:
        文件内容
    """
    try:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content}
        else:
            return {"success": False, "error": "文件不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 工具函数6: curl网络访问
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
        path = parsed_url.path or '/' + parsed_url.query
        
        if scheme == 'https':
            conn = HTTPSConnection(host)
        else:
            from http.client import HTTPConnection
            conn = HTTPConnection(host)
        
        conn.request('GET', path)
        response = conn.getresponse()
        content = response.read().decode('utf-8')
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
    
    if tool_name == "list_files":
        return list_files(arguments.get('directory'))
    elif tool_name == "rename_file":
        return rename_file(
            arguments.get('directory'),
            arguments.get('old_name'),
            arguments.get('new_name')
        )
    elif tool_name == "delete_file":
        return delete_file(
            arguments.get('directory'),
            arguments.get('filename')
        )
    elif tool_name == "create_file":
        return create_file(
            arguments.get('directory'),
            arguments.get('filename'),
            arguments.get('content')
        )
    elif tool_name == "read_file":
        return read_file(
            arguments.get('directory'),
            arguments.get('filename')
        )
    elif tool_name == "curl_get":
        return curl_get(
            arguments.get('url')
        )
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
    
    # 系统提示词，包含工具调用说明
    system_prompt = """
    你是一个AI助手，具有以下工具调用能力：
    
    1. list_files: 列出目录下的文件及属性
       参数:
           directory: 目录路径
    
    2. rename_file: 修改文件名称
       参数:
           directory: 目录路径
           old_name: 原文件名
           new_name: 新文件名
    
    3. delete_file: 删除文件
       参数:
           directory: 目录路径
           filename: 要删除的文件名
    
    4. create_file: 新建文件并写入内容
       参数:
           directory: 目录路径
           filename: 文件名
           content: 文件内容
    
    5. read_file: 读取文件内容
       参数:
           directory: 目录路径
           filename: 文件名
    
    6. curl_get: 通过HTTP GET请求访问指定URL并返回网页内容
       参数:
           url: 要访问的网址
    
    当用户的请求需要使用这些工具时，你应该生成tool_calls字段，包含工具调用的详细信息。
    """
    
    while True:
        user_input = input("请输入你的请求: ")
        
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
                        "name": "list_files",
                        "description": "列出目录下的文件及属性",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "directory": {
                                    "type": "string",
                                    "description": "目录路径"
                                }
                            },
                            "required": ["directory"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "rename_file",
                        "description": "修改文件名称",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "directory": {
                                    "type": "string",
                                    "description": "目录路径"
                                },
                                "old_name": {
                                    "type": "string",
                                    "description": "原文件名"
                                },
                                "new_name": {
                                    "type": "string",
                                    "description": "新文件名"
                                }
                            },
                            "required": ["directory", "old_name", "new_name"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_file",
                        "description": "删除文件",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "directory": {
                                    "type": "string",
                                    "description": "目录路径"
                                },
                                "filename": {
                                    "type": "string",
                                    "description": "要删除的文件名"
                                }
                            },
                            "required": ["directory", "filename"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_file",
                        "description": "新建文件并写入内容",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "directory": {
                                    "type": "string",
                                    "description": "目录路径"
                                },
                                "filename": {
                                    "type": "string",
                                    "description": "文件名"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "文件内容"
                                }
                            },
                            "required": ["directory", "filename", "content"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "description": "读取文件内容",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "directory": {
                                    "type": "string",
                                    "description": "目录路径"
                                },
                                "filename": {
                                    "type": "string",
                                    "description": "文件名"
                                }
                            },
                            "required": ["directory", "filename"]
                        }
                    }
                },
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
            conn = HTTPSConnection(host)
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
                        
                        conn = HTTPSConnection(host)
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
