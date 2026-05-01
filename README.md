# AI Chatbot - 智能聊天机器人

一个基于 Python + FastAPI + OpenAI GPT 构建的智能聊天机器人 Web 应用。

## 功能特性

- 🚀 **FastAPI 后端** - 高性能异步 API 服务
- 🌐 **Web 界面** - 简洁的聊天界面
- 🤖 **OpenAI GPT 集成** - 支持 GPT-4/GPT-3.5
- 💬 **流式响应** - 实时显示 AI 回复
- 📝 **对话历史** - 自动保存聊天记录
- 🎨 **响应式设计** - 支持移动端访问

## 技术栈

- **后端**: Python 3.10+, FastAPI, Uvicorn
- **前端**: HTML5, CSS3, JavaScript (原生)
- **AI**: OpenAI API
- **部署**: Docker 可选

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-chatbot.git
cd ai-chatbot
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 OpenAI API Key：

```
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
```

### 4. 运行应用

```bash
python main.py
```

访问 http://localhost:8000 即可开始聊天！

## 项目结构

```
ai-chatbot/
├── main.py              # FastAPI 应用主入口
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量示例
├── static/
│   └── style.css        # 样式文件
└── templates/
    └── index.html       # Web 界面
```

## API 接口

### POST /api/chat
发送消息并获取回复

**请求体:**
```json
{
  "message": "你好",
  "history": []
}
```

**响应:**
```json
{
  "response": "你好！有什么可以帮助你的？",
  "history": [...]
}
```

## Docker 部署

```bash
docker build -t ai-chatbot .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-xxx ai-chatbot
```

## 许可证

MIT License
