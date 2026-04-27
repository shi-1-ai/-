from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import os
import requests

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set AI provider configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "qwen")  # Options: openai, qwen

# OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
)

# Qwen API configuration
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "sk-47fd7e6f7fa84728bd7477a72a1ba503")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo")
QWEN_API_URL = os.getenv("QWEN_API_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")

@app.get("/", response_class=HTMLResponse)
async def root():
    import os
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat(message: str = Form(...)):
    try:
        # Set timeout for API call
        import time
        start_time = time.time()
        
        # Check if we should use mock response
        if AI_PROVIDER == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
            if api_key == "your-api-key-here":
                # Return mock response for testing purposes
                mock_responses = [
                    "您好！我是客服机器人，很高兴为您服务。",
                    "请问有什么可以帮助您的吗？",
                    "感谢您的咨询，我会尽力回答您的问题。",
                    "这个问题很有趣，让我为您解答。",
                    "抱歉，我暂时无法回答这个问题，请尝试其他问题。"
                ]
                import random
                mock_response = random.choice(mock_responses)
                print("Using mock response for testing")
                return {"response": mock_response}
        elif AI_PROVIDER == "qwen":
            # Use the QWEN_API_KEY variable which has the user's API key
            if QWEN_API_KEY == "your-qwen-api-key-here":
                # Return mock response for testing purposes
                mock_responses = [
                    "您好！我是客服机器人，很高兴为您服务。",
                    "请问有什么可以帮助您的吗？",
                    "感谢您的咨询，我会尽力回答您的问题。",
                    "这个问题很有趣，让我为您解答。",
                    "抱歉，我暂时无法回答这个问题，请尝试其他问题。"
                ]
                import random
                mock_response = random.choice(mock_responses)
                print("Using mock response for testing")
                return {"response": mock_response}
        
        # Call the appropriate AI provider API
        if AI_PROVIDER == "openai":
            # Call OpenAI API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful customer service assistant."},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.7,
                timeout=30  # 30 seconds timeout
            )
            
            elapsed_time = time.time() - start_time
            print(f"OpenAI API call took {elapsed_time:.2f} seconds")
            
            return {"response": response.choices[0].message.content.strip()}
        elif AI_PROVIDER == "qwen" and QWEN_API_KEY != "your-qwen-api-key-here":
            # Call Qwen API (Aliyun Qianwen) using DashScope API
            headers = {
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": QWEN_MODEL,
                "input": {
                    "prompt": f"You are a helpful customer service assistant.\nUser: {message}\nAssistant:"
                },
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                QWEN_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            print(f"Qwen API call took {elapsed_time:.2f} seconds")
            
            # Extract response content
            response_data = response.json()
            if "output" in response_data and "text" in response_data["output"]:
                return {"response": response_data["output"]["text"].strip()}
            else:
                return {"response": f"Error: {response_data.get('error', {}).get('message', 'Unknown error')}"}
        else:
            return {"response": "AI provider not configured or unavailable."}
    except Exception as e:
        print(f"Error: {str(e)}")
        # Return mock response on error for testing
        mock_error_response = "抱歉，暂时无法连接到服务器，请稍后再试。"
        return {"response": mock_error_response}