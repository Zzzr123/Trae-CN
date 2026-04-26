import os
import json
import time
from http.client import HTTPSConnection
from urllib.parse import urlparse

# 读取.env文件
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

def main():
    # 加载环境变量
    env = load_env()
    base_url = env.get('BASE_URL', 'https://api.openai.com/v1')
    model = env.get('MODEL', 'gpt-3.5-turbo')
    token = env.get('TOKEN')
    
    if not token:
        print("Error: TOKEN not found in .env file")
        return
    
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    
    # 准备请求数据
    prompt = "Hello, how are you?"
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    # 发送请求并计时
    start_time = time.time()
    
    try:
        # 建立HTTPS连接
        conn = HTTPSConnection(host)
        
        # 准备请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        # 发送请求
        conn.request('POST', path, json.dumps(payload), headers)
        
        # 获取响应
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()
        
        # 解析响应
        result = json.loads(response_data)
        
        # 计算时间
        end_time = time.time()
        total_time = end_time - start_time
        
        # 提取token消耗
        usage = result.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        # 计算token/s速度
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0
        
        # 打印结果
        print("Request completed successfully!")
        print(f"Model: {model}")
        print(f"Base URL: {base_url}")
        print(f"Prompt: {prompt}")
        print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()}")
        print(f"\nToken Usage:")
        print(f"  Prompt tokens: {prompt_tokens}")
        print(f"  Completion tokens: {completion_tokens}")
        print(f"  Total tokens: {total_tokens}")
        print(f"\nPerformance:")
        print(f"  Total time: {total_time:.2f} seconds")
        print(f"  Tokens per second: {tokens_per_second:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
