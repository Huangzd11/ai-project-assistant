# AI Project Assistant

30 天 AI 技术项目经理实战学习项目。从 LLM 基础概念出发，逐步掌握云端 API 调用、本地模型部署、Web API 封装与容器化部署等核心技能。

仓库地址：[https://github.com/Huangzd11/ai-project-assistant](https://github.com/Huangzd11/ai-project-assistant)

---

## 项目简介

本项目是一个 **渐进式学习仓库**，采用 monorepo 结构，将每日实战代码与文档统一管理。目前已完成 Day01 ~ Day07，涵盖：

- LLM 基础与 Prompt 设计
- OpenAI 兼容 API 调用（通义千问 / Ollama）
- 命令行多轮对话与流式输出
- FastAPI HTTP 服务封装
- Docker 容器化部署
- GitHub 托管与项目开发规范
- Day01 ~ Day06 回顾与查漏补缺

适合希望系统学习 AI 应用开发的开发者，尤其是想从技术项目经理视角理解 LLM 工程化落地的同学。

---

## 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.10+ | 全部实战代码 |
| LLM 客户端 | OpenAI Python SDK | 统一调用云端 / 本地兼容接口 |
| 云端模型 | 通义千问（DashScope） | Day02 默认方案 |
| 本地模型 | Ollama + qwen3:4b | Day03、Day04 默认方案 |
| 配置管理 | python-dotenv | 环境变量加载 |
| Web 框架 | FastAPI | HTTP API 服务 |
| ASGI 服务器 | Uvicorn | 运行 FastAPI |
| 数据校验 | Pydantic | 请求 / 响应模型 |
| 容器化 | Docker | 镜像构建与部署 |

---

## 当前功能

### Prompt 练习（Day01）

- System Prompt、Few-shot、Temperature 对比实验

运行：`python examples/prompt_demo.py`

### 命令行对话（Day02）

- 从 `.env` 读取 API Key、Base URL、模型名
- 维护 `messages` 列表实现多轮对话
- 流式逐字输出（`stream=True`）

运行：`python examples/chat_demo.py`

### 本地 Ollama 调用（Day03）

- 通过 `http://127.0.0.1:11434/v1` 连接本地 Ollama
- OpenAI SDK 零改动接入本地模型

运行：`python examples/ollama_demo.py`

### 企业知识库 — PDF 上传（Day08 · v0.2.0-alpha）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/upload` | POST | 上传 PDF，保存至 `uploads/` |

```json
{ "filename": "linux.pdf", "size": "8MB" }
```

在 http://127.0.0.1:8000/docs 中测试上传。

详见 [docs/Day08.md](docs/Day08.md)。

### HTTP API 服务（Day04）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务欢迎 |
| `/health` | GET | 健康检查 |
| `/models` | GET | 当前模型配置 |
| `/chat` | POST | AI 聊天 |
| `/upload` | POST | PDF 上传（Day08） |

运行：`uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`  
交互文档：http://127.0.0.1:8000/docs

### Docker 部署（Day05）

- 基于 `Dockerfile` 一键构建镜像
- 支持容器访问宿主机 Ollama

详见 [docs/Day05.md](docs/Day05.md)。

### GitHub 与项目规范（Day06）

- 代码托管于 [GitHub](https://github.com/Huangzd11/ai-project-assistant)
- 完善 README、方案设计、架构图等文档体系
- 建立 [开发规范](docs/development-standards.md)

详见 [docs/Day06.md](docs/Day06.md)。

### 阶段回顾（Day07）

- 回顾 Day01 ~ Day06 知识体系
- 补齐示例脚本与 `.dockerignore`
- 确认 Day08 RAG 前置条件

详见 [docs/Day07.md](docs/Day07.md)。

---

## 学习进度

完整路线见 [docs/roadmap.md](docs/roadmap.md)。

- [x] Day01 LLM Basic
- [x] Day02 OpenAI API
- [x] Day03 Ollama
- [x] Day04 FastAPI
- [x] Day05 Docker
- [x] Day06 GitHub
- [x] Day07 Review
- [x] Day08 Upload + Refactor
- [ ] Day09 PDF Loader

---

## 项目结构

```
ai-project-assistant/
│
├── app/
│   ├── api/
│   │   ├── chat.py         # 聊天与模型信息接口
│   │   ├── upload.py       # PDF 上传接口
│   │   └── health.py       # 健康检查
│   ├── core/
│   │   ├── config.py       # 环境配置
│   │   ├── llm.py          # LLM 调用封装
│   │   └── logger.py       # 日志
│   ├── rag/                # RAG 模块（Day08+）
│   ├── models/             # Pydantic 模型
│   └── main.py             # FastAPI 入口
│
├── uploads/                # 上传文件目录
├── data/                   # 数据存储目录
├── tests/                  # 测试
├── docs/
├── examples/               # 学习示例脚本
├── requirements.txt
├── Dockerfile
└── README.md
```

| 模块 | 职责 |
|------|------|
| `app/api/` | HTTP 路由层 |
| `app/core/` | 配置、LLM、日志等核心能力 |
| `app/models/` | 请求/响应数据契约 |
| `app/rag/` | 检索增强生成（Sprint 2 扩展） |

---

## 快速开始

### 1. 安装依赖

```powershell
pip install -r requirements.txt
copy .env.example .env    # 按需填写 API Key
```

### 2. 命令行对话（云端 API）

在 [阿里云百炼](https://bailian.console.aliyun.com/) 获取 API Key，写入 `.env`：

```
OPENAI_API_KEY=你的密钥
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-plus
```

```powershell
python examples/chat_demo.py
```

### 3. HTTP API 服务（本地 Ollama）

```powershell
ollama pull qwen3:4b
ollama serve
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**上传 PDF：** 打开 http://127.0.0.1:8000/docs ，使用 `POST /upload` 选择文件。

### 4. Docker 部署

```powershell
docker build -t ai-chat:v1 .
docker run -p 8000:8000 ai-chat:v1
```

容器访问宿主机 Ollama：

```powershell
docker run -p 8000:8000 -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 ai-chat:v1
```

---

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `OPENAI_API_KEY` | `ollama` | API 密钥 |
| `OPENAI_BASE_URL` | `http://127.0.0.1:11434/v1` | 兼容 API 地址 |
| `MODEL_NAME` | `qwen3:4b` | 模型名称 |
| `PROVIDER` | `ollama` | 提供方标识 |
| `SYSTEM_PROMPT` | `你是一名AI技术项目经理.` | 系统提示词 |
| `REQUEST_TIMEOUT` | `600` | 请求超时（秒） |
| `UPLOAD_DIR` | `uploads` | PDF 上传保存目录 |

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/development-standards.md](docs/development-standards.md) | AI 项目开发规范 |
| [docs/solution-design.md](docs/solution-design.md) | AI 方案设计（技术选型与演进路线） |
| [docs/api.md](docs/api.md) | HTTP 接口详细说明 |
| [docs/roadmap.md](docs/roadmap.md) | 学习路线与后续规划 |
| [docs/Day01.md](docs/Day01.md) ~ [Day08.md](docs/Day08.md) | 每日工作日志 |

---

## 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Ollama 文档](https://github.com/ollama/ollama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [阿里云百炼](https://bailian.console.aliyun.com/)
