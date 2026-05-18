import os
import json
import time
import sys
import subprocess
import re
from http.client import HTTPSConnection, HTTPConnection
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

def list_available_skills():
    skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.agents', 'skills')
    skills = []

    if not os.path.exists(skills_dir):
        return skills

    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if os.path.isdir(skill_path):
            skill_file = os.path.join(skill_path, 'SKILL.md')
            if os.path.exists(skill_file):
                try:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.startswith('---'):
                        front_matter_end = content.find('---', 3)
                        if front_matter_end != -1:
                            front_matter = content[3:front_matter_end].strip()
                            skill_info = {}
                            for line in front_matter.split('\n'):
                                line = line.strip()
                                if line and ':' in line:
                                    key, value = line.split(':', 1)
                                    key = key.strip()
                                    value = value.strip()
                                    if key == 'name':
                                        skill_info['name'] = value
                                    elif key == 'description':
                                        skill_info['description'] = value
                            if 'name' in skill_info:
                                skills.append(skill_info)
                except Exception as e:
                    print(f"读取技能文件 {skill_file} 时出错: {e}")

    return skills

def load_skill_content(skill_name):
    skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.agents', 'skills', skill_name)
    skill_file = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_file):
        return {"success": False, "error": f"技能 {skill_name} 不存在"}

    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            front_matter_end = content.find('---', 3)
            if front_matter_end != -1:
                body_content = content[front_matter_end + 3:].strip()
                return {"success": True, "content": body_content}
            else:
                return {"success": False, "error": "技能文件格式错误，缺少YAML front matter结束标记"}
        else:
            return {"success": False, "error": "技能文件格式错误，缺少YAML front matter开始标记"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def search_files_with_keyword(directory, keyword):
    """
    搜索指定目录下包含指定关键词的文件
    """
    results = []
    
    if not os.path.exists(directory):
        return {"success": False, "error": f"目录 {directory} 不存在"}
    
    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.py'):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if keyword in content:
                                results.append({
                                    "file": filepath,
                                    "line_count": len(content.split('\n'))
                                })
                    except Exception as e:
                        print(f"读取文件 {filepath} 时出错: {e}")
        
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_file_content(filepath):
    """
    读取文件内容
    """
    if not os.path.exists(filepath):
        return {"success": False, "error": f"文件 {filepath} 不存在"}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

def curl_get(url):
    """
    使用curl访问网页并返回内容
    """
    try:
        cmd = [
            'curl', '-s', url,
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            return {"success": False, "error": f"Curl命令执行失败: {result.stderr}"}
        
        return {"success": True, "content": result.stdout}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(filepath, content):
    """
    将内容写入文件
    """
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"success": True, "message": f"文件已成功写入: {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

class ChainedCallContext:
    """
    链式调用上下文管理器，用于在多个工具调用之间传递数据和状态
    """
    
    def __init__(self, max_iterations=10):
        self.steps = []
        self.variables = {}
        self.max_iterations = max_iterations
        self.current_iteration = 0
    
    def add_step(self, tool_name, arguments, result):
        """
        添加工具调用步骤
        """
        self.steps.append({
            "iteration": self.current_iteration,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        })
        self.current_iteration += 1
    
    def set_variable(self, name, value):
        """
        设置上下文变量
        """
        self.variables[name] = value
    
    def get_variable(self, name, default=None):
        """
        获取上下文变量
        """
        return self.variables.get(name, default)
    
    def is_max_iterations_reached(self):
        """
        检查是否达到最大迭代次数
        """
        return self.current_iteration >= self.max_iterations
    
    def get_steps_summary(self):
        """
        获取已执行步骤的摘要
        """
        summary = []
        for step in self.steps:
            summary.append(f"步骤 {step['iteration'] + 1}: {step['tool_name']}({step['arguments']}) -> {'成功' if step['result'].get('success') else '失败'}")
        return "\n".join(summary)

def extract_json_from_response(content):
    """
    从LLM响应中提取JSON部分
    """
    if not content:
        return None
    
    # 移除markdown代码块标记
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("'''json"):
        content = content[8:]
    if content.endswith("```"):
        content = content[:-3]
    if content.endswith("'''"):
        content = content[:-3]
    content = content.strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None

def build_analysis_prompt(user_request, context):
    """
    构建分析提示词，用于引导LLM进行链式工具调用决策
    """
    steps_summary = context.get_steps_summary()
    variables_info = "\n".join([f"- {key}: {value}" for key, value in context.variables.items()])
    
    prompt = f"""
    你是一个智能助手，能够进行链式工具调用。请根据用户请求和已执行的步骤，决定下一步操作。

    用户请求: {user_request}

    已执行的步骤:
    {steps_summary if steps_summary else "无"}

    当前上下文变量:
    {variables_info if variables_info else "无"}

    可用工具列表:
    1. search_files_with_keyword - 搜索目录下包含关键词的文件
       参数: directory (目录路径), keyword (关键词)
    2. read_file_content - 读取文件内容
       参数: filepath (文件路径)
    3. load_skill_content - 加载技能内容
       参数: skill_name (技能名称)
    4. search_chat_history - 搜索聊天历史
       参数: query (搜索查询)
    5. anythingllm_query - 查询AnythingLLM文档仓库
       参数: query (查询内容)
    6. curl_get - 访问网页并返回内容
       参数: url (网页URL)
    7. write_file - 将内容写入文件
       参数: filepath (文件路径), content (内容)

    决策规则:
    1. 分析用户请求，确定是否需要调用工具
    2. 如果需要调用工具，选择合适的工具和参数
    3. 如果任务已完成，直接给出最终回答
    4. 可以将前一个工具的输出作为后一个工具的输入
    5. 使用上下文变量存储和传递中间结果

    请按照以下JSON格式返回决策:
    
    任务完成时:
    {{
        "done": true,
        "answer": "最终回答内容"
    }}
    
    继续调用工具时:
    {{
        "done": false,
        "tool_call": {{
            "name": "工具名称",
            "arguments": {{
                "参数名": "参数值"
            }}
        }}
    }}
    """
    
    return prompt

def execute_tool(tool_call):
    """
    执行工具调用
    """
    tool_name = tool_call.get('name')
    arguments = tool_call.get('arguments', {})

    if tool_name == "search_chat_history":
        return search_chat_history(arguments.get('query', ''))
    elif tool_name == "anythingllm_query":
        return anythingllm_query(arguments.get('query', ''))
    elif tool_name == "load_skill_content":
        return load_skill_content(arguments.get('skill_name', ''))
    elif tool_name == "search_files_with_keyword":
        return search_files_with_keyword(arguments.get('directory', ''), arguments.get('keyword', ''))
    elif tool_name == "read_file_content":
        return read_file_content(arguments.get('filepath', ''))
    elif tool_name == "curl_get":
        return curl_get(arguments.get('url', ''))
    elif tool_name == "write_file":
        return write_file(arguments.get('filepath', ''), arguments.get('content', ''))
    else:
        return {"success": False, "error": f"未知工具: {tool_name}"}

def execute_chained_tool_call(user_request, host, path, headers, model, max_iterations=10):
    """
    执行链式工具调用的完整流程
    """
    context = ChainedCallContext(max_iterations=max_iterations)
    
    print(f"开始链式工具调用，最大迭代次数: {max_iterations}")
    
    for iteration in range(max_iterations):
        print(f"\n--- 迭代 {iteration + 1}/{max_iterations} ---")
        
        # 构建分析提示词
        analysis_prompt = build_analysis_prompt(user_request, context)
        
        # 调用LLM决定下一步操作
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个智能助手，擅长进行链式工具调用。请根据用户请求和已执行的步骤，决定下一步操作。"},
                {"role": "user", "content": analysis_prompt}
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
            if not result.get('choices'):
                print("LLM响应为空")
                continue
            
            llm_response = result['choices'][0].get('message', {}).get('content', '')
            
            print(f"LLM响应: {llm_response[:200]}...")
            
            # 解析LLM响应
            decision = extract_json_from_response(llm_response)
            
            if decision is None:
                # 尝试解析tool_calls格式
                tool_calls = result['choices'][0].get('message', {}).get('tool_calls', [])
                if tool_calls:
                    tool_call = tool_calls[0]
                    func_name = tool_call.get('function', {}).get('name')
                    func_args = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
                    decision = {
                        "done": False,
                        "tool_call": {
                            "name": func_name,
                            "arguments": func_args
                        }
                    }
                else:
                    print("无法解析LLM响应")
                    continue
            
            # 检查任务是否完成
            if decision.get('done'):
                answer = decision.get('answer', '')
                print(f"\n任务完成！最终回答: {answer[:200]}...")
                return answer
            
            # 执行工具调用
            tool_call = decision.get('tool_call', {})
            tool_name = tool_call.get('name')
            arguments = tool_call.get('arguments', {})
            
            print(f"执行工具: {tool_name}")
            print(f"参数: {arguments}")
            
            tool_result = execute_tool(tool_call)
            print(f"工具执行结果: {'成功' if tool_result.get('success') else '失败'}")
            
            # 记录到上下文
            context.add_step(tool_name, arguments, tool_result)
            
            # 将结果添加到上下文变量
            if tool_result.get('success'):
                if 'results' in tool_result:
                    context.set_variable('last_search_results', tool_result['results'])
                elif 'content' in tool_result:
                    context.set_variable('last_content', tool_result['content'])
                elif 'data' in tool_result:
                    context.set_variable('last_data', tool_result['data'])
            
        except Exception as e:
            print(f"迭代 {iteration + 1} 出错: {e}")
            continue
    
    print(f"达到最大迭代次数 {max_iterations}，任务未完成")
    return f"已执行 {max_iterations} 次工具调用，但任务未完成。已执行的步骤:\n{context.get_steps_summary()}"

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

    skills = list_available_skills()
    skills_json = json.dumps({"skills": skills}, ensure_ascii=False, indent=2)

    print("=== LLM Chat Interface with Chained Tool Calls ===")
    print("Type your message and press Enter. Press Ctrl+C to exit.")
    print("支持链式工具调用，前一个工具的输出可以作为后一个工具的输入")
    print("Available skills:")
    for skill in skills:
        print(f"- {skill['name']}: {skill['description']}")
    print("====================================================\n")

    system_prompt = f"""
    你是一个AI助手，具有以下工具调用能力：

    1. search_chat_history: 搜索聊天历史记录
       参数: query - 搜索查询

    2. anythingllm_query: 查询AnythingLLM文档仓库
       参数: query - 查询内容
       当用户提到"文档仓库"、"文件仓库"、"仓库"时使用此工具

    3. load_skill_content: 加载技能内容
       参数: skill_name - 技能名称

    4. search_files_with_keyword: 搜索目录下包含关键词的文件
       参数: directory - 目录路径, keyword - 关键词

    5. read_file_content: 读取文件内容
       参数: filepath - 文件路径

    6. curl_get: 访问网页并返回内容
       参数: url - 网页URL

    7. write_file: 将内容写入文件
       参数: filepath - 文件路径, content - 内容

    可用技能列表：
    {skills_json}

    链式调用规则：
    - 你可以进行多步骤的工具调用，前一个工具的输出可以作为后一个工具的输入
    - 例如：先搜索文件 -> 读取文件内容 -> 总结内容 -> 保存到文件
    - 当你需要进行多个步骤才能完成任务时，请使用tool_calls格式
    - 如果任务可以一步完成，直接给出回答即可

    示例：
    用户请求："查找practice05目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
    步骤1：调用search_files_with_keyword搜索文件
    步骤2：调用read_file_content读取每个文件
    步骤3：总结内容并返回

    当用户的请求需要使用工具时，你应该生成tool_calls字段，包含工具调用的详细信息。
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
                        "query": {"type": "string", "description": "搜索查询"}
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
                        "query": {"type": "string", "description": "查询内容"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "load_skill_content",
                "description": "加载技能内容，获取技能的具体执行规则",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {"type": "string", "description": "技能名称"}
                    },
                    "required": ["skill_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files_with_keyword",
                "description": "搜索指定目录下包含指定关键词的文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "目录路径"},
                        "keyword": {"type": "string", "description": "关键词"}
                    },
                    "required": ["directory", "keyword"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file_content",
                "description": "读取文件内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "文件路径"}
                    },
                    "required": ["filepath"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "curl_get",
                "description": "访问网页并返回内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "网页URL"}
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "将内容写入文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "文件路径"},
                        "content": {"type": "string", "description": "内容"}
                    },
                    "required": ["filepath", "content"]
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

            # 检查是否需要使用链式调用
            if any(keyword in user_input for keyword in ['查找', '搜索', '总结', '读取', '访问', '保存', '下载']):
                print("\n检测到复杂请求，启动链式工具调用...")
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
                result = execute_chained_tool_call(user_input, host, path, headers, model)
                print(f"\nAssistant: {result}\n")
                chat_history.append({"role": "user", "content": user_input})
                chat_history.append({"role": "assistant", "content": result})
                conversation_count += 1
                continue

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

                        new_system_prompt = system_prompt
                        if tool_name == "load_skill_content" and tool_result.get('success'):
                            skill_content = tool_result.get('content', '')
                            new_system_prompt = f"{system_prompt}\n\n当前使用的技能内容：\n{skill_content}"

                        second_payload = {
                            "model": model,
                            "messages": [{"role": "system", "content": new_system_prompt}] + chat_history + [
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