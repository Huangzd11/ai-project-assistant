# AI Project Assistant

30 天 AI 技术项目经理学习项目。

仓库地址：[https://github.com/Huangzd11/ai-project-assistant](https://github.com/Huangzd11/ai-project-assistant)

## 项目结构

```
ai-project-assistant/
│
├── app.py                  # FastAPI 入口
├── llm.py                  # LLM 调用封装
├── config.py               # 环境变量配置
├── models.py               # 请求/响应模型
├── requirements.txt
├── Dockerfile
├── .gitignore
├── README.md
│
├── docs/
│   ├── architecture.png    # 架构图（待补充）
│   ├── api.md              # 接口文档
│   ├── roadmap.md          # 后续规划
│   ├── Day01.md            # 工作日志
│   ├── Day02.md
│   ├── Day03.md
│   ├── Day04.md
│   └── Day05.md
│
├── examples/
│   └── chat_demo.py        # 命令行连续对话示例
│
└── src/                    # 后续模块扩展
```

## 快速开始

```powershell
# 安装依赖
pip install -r requirements.txt
copy .env.example .env    # 按需填写 API Key

# 命令行对话（Day02）
python examples/chat_demo.py

# HTTP API 服务（Day04）
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## 文档

| 文档 | 说明 |
|------|------|
| [docs/api.md](docs/api.md) | HTTP 接口说明 |
| [docs/roadmap.md](docs/roadmap.md) | 学习路线与工程化规划 |
| [docs/Day01.md](docs/Day01.md) ~ [Day05.md](docs/Day05.md) | 每日工作日志 |

## Docker（Day05）

```powershell
docker build -t ai-chat:v1 .
docker run -p 8000:8000 ai-chat:v1
```

详见 [docs/Day05.md](docs/Day05.md)。

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| LLM 客户端 | OpenAI Python SDK |
| 云端模型 | 通义千问（DashScope） |
| 本地模型 | Ollama + qwen3:4b |
| Web 框架 | FastAPI + Uvicorn |
| 容器化 | Docker |
