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
    
    print("=== LLM Chat Interface ===")
    print("Type your message and press Enter. Press Ctrl+C to exit.")
    print("==========================\n")
    
    try:
        while True:
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
                
                print(f"\n\n[Token Usage: {total_tokens}, Time: {total_time:.2f}s, Speed: {tokens_per_second:.2f} tokens/s]\n")
                
            except Exception as e:
                print(f"\nError: {e}\n")
                # Remove the last user message from history to allow retry
                if chat_history and chat_history[-1]['role'] == 'user':
                    chat_history.pop()
    
    except KeyboardInterrupt:
        print("\n\nExiting chat interface. Goodbye!")

if __name__ == "__main__":
    main()
