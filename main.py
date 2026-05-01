import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from openai import AsyncOpenAI

# 初始化 FastAPI
app = FastAPI(title="AI Chatbot API")

# 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1")

# 初始化 OpenAI 客户端（支持 DeepSeek）
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

# 请求/响应模型
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    response: str
    history: List[Message]

# 简单的内存存储（生产环境应使用数据库）
chat_history = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回 Web 界面"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 智能聊天机器人</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <div class="chat-header">
            <h1>🤖 AI 聊天机器人</h1>
            <p>基于 DeepSeek 的智能对话系统</p>
        </div>

        <div class="chat-container" id="chat-container">
            <div class="message bot">
                <div class="message-content">
                    你好！我是 AI 聊天机器人。有什么我可以帮助你的吗？
                </div>
            </div>
        </div>

        <div class="input-area">
            <textarea id="user-input" placeholder="输入你的消息..."></textarea>
            <button id="send-btn" onclick="sendMessage()">发送</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');

        // 聊天历史
        let history = [];

        // 回车发送消息
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // 发送消息
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            // 显示用户消息
            addMessageToChat('user', message);
            userInput.value = '';

            // 显示加载状态
            const loadingId = addLoadingToChat();

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        history: history
                    })
                });

                const data = await response.json();

                // 移除加载状态
                document.getElementById(loadingId).remove();

                // 显示机器人回复
                addMessageToChat('bot', data.response);

                // 更新历史
                history = data.history;

            } catch (error) {
                document.getElementById(loadingId).remove();
                addMessageToChat('bot', '抱歉，发生错误：' + error.message);
            }
        }

        // 添加消息到聊天窗口
        function addMessageToChat(role, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + role;
            messageDiv.innerHTML = `
                <div class="avatar">${role === 'user' ? '👤' : '🤖'}</div>
                <div class="message-content">${formatContent(content)}</div>
            `;
            chatContainer.appendChild(messageDiv);
            scrollToBottom();
            return messageDiv;
        }

        // 添加加载状态
        function addLoadingToChat() {
            const id = 'loading-' + Date.now();
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message bot';
            loadingDiv.id = id;
            loadingDiv.innerHTML = `
                <div class="avatar">🤖</div>
                <div class="message-content loading">正在思考...</div>
            `;
            chatContainer.appendChild(loadingDiv);
            scrollToBottom();
            return id;
        }

        // 格式化内容（处理换行）
        function formatContent(content) {
            return content.replace(/\n/g, '<br>');
        }

        // 滚动到底部
        function scrollToBottom() {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

@app.get("/static/style.css")
async def get_css():
    """返回 CSS 文件"""
    css_content = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.container {
    width: 100%;
    max-width: 800px;
    height: 90vh;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    text-align: center;
}

.chat-header h1 {
    font-size: 1.5rem;
    margin-bottom: 5px;
}

.chat-header p {
    font-size: 0.9rem;
    opacity: 0.9;
}

.chat-container {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: #f5f5f5;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.message {
    display: flex;
    gap: 10px;
    max-width: 85%;
}

.message.user {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.message.bot {
    align-self: flex-start;
}

.message .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}

.message.user .avatar {
    background: #667eea;
    color: white;
}

.message.bot .avatar {
    background: #764ba2;
    color: white;
}

.message-content {
    padding: 12px 16px;
    border-radius: 18px;
    line-height: 1.6;
    word-wrap: break-word;
}

.message.user .message-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
}

.message.bot .message-content {
    background: white;
    color: #333;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.input-area {
    padding: 20px;
    background: white;
    border-top: 1px solid #eee;
    display: flex;
    gap: 10px;
}

#user-input {
    flex: 1;
    padding: 12px 16px;
    border: 2px solid #eee;
    border-radius: 25px;
    resize: none;
    font-family: inherit;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.3s;
}

#user-input:focus {
    border-color: #667eea;
}

#send-btn {
    padding: 12px 30px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: transform 0.2s, box-shadow 0.2s;
}

#send-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

#send-btn:active {
    transform: translateY(0);
}

/* 滚动条样式 */
.chat-container::-webkit-scrollbar {
    width: 8px;
}

.chat-container::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.chat-container::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 4px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
    background: #aaa;
}

/* 移动端适配 */
@media (max-width: 600px) {
    .container {
        height: 100vh;
        border-radius: 0;
    }

    .message {
        max-width: 90%;
    }
}
"""
    return HTMLResponse(content=css_content, media_type="text/css")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """处理聊天请求"""
    try:
        # 构建消息列表
        messages = [
            {"role": "system", "content": "你是一个友好的 AI 助手。请用中文回复，保持简洁明了。"}
        ]

        # 添加历史记录
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        # 添加当前消息
        messages.append({"role": "user", "content": request.message})

        # 调用 OpenAI API
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        ai_response = response.choices[0].message.content

        # 更新历史记录
        updated_history = request.history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": ai_response}
        ]

        return ChatResponse(response=ai_response, history=updated_history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
