# AI Project Assistant

[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](docs/CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10+-green)](requirements.txt)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**v1.0** · 30 天 AI 技术项目经理实战收官作品。

企业级 **AI 项目助手**：知识库 RAG · Agent · MCP · Web UI · Docker 一键部署 · Token 成本可观测 · 完整方案文档。

仓库：[github.com/Huangzd11/ai-project-assistant](https://github.com/Huangzd11/ai-project-assistant)

---

## 目录

- [最终成果（30 天）](#最终成果30-天)
- [项目介绍](#项目介绍)
- [功能亮点](#功能亮点)
- [架构](#架构)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [功能展示](#功能展示)
- [API 文档](#api-文档)
- [Roadmap](#roadmap)
- [版本记录](#版本记录)
- [相关文档](#相关文档)

---

## 最终成果（30 天）

### 技术能力

| 能力 | 本项目落点 |
|------|------------|
| **LLM** | OpenAI 兼容 · Ollama / 通义双模 |
| **Prompt** | System / RAG / Agent 总结提示词 |
| **FastAPI** | REST + SSE + Swagger |
| **Docker** | Dockerfile + Compose 一键栈 |
| **RAG** | 检索增强 + `sources` 溯源 |
| **Embedding** | bge-small / 通义 Embedding |
| **Vector DB** | Chroma（embedded / server） |
| **Agent** | Workflow · Tool Registry · Memory |
| **MCP** | Filesystem 等外部工具桥接 |

### 项目能力

| 能力 | 本项目落点 |
|------|------------|
| **方案设计** | [solution-design.md](docs/solution-design.md) |
| **技术选型** | FastAPI / Chroma / Ollama / MCP 对比与边界 |
| **成本评估** | Token usage + `/metrics/cost-estimate` |
| **风险分析** | 幻觉 · Chunk · SSE · 密钥 · MCP 沙箱 |
| **项目交付** | Compose · Nginx · 日志 · README · LICENSE |

### 输出成果

| 产出 | 路径 |
|------|------|
| **GitHub 项目** | 本仓库 + MIT |
| **架构图** | [architecture.md](docs/architecture.md)（README 内嵌摘要） |
| **README** | 本文件（Quick Start · 结构 · Roadmap） |

> Day28~30（简历 / 模拟面试 / 投递）暂不展开；工程与文档已按 **v1.0** 收官。

---

## 项目介绍

把企业内部 PDF、项目文件与实时工具接到统一 Agent 入口：

| 你问 | 系统做什么 |
|------|------------|
| 「总结 test.pdf」 | Workflow → RAG → 带 `sources` 的回答 |
| 「README 写了什么」 | MCP Filesystem（可选） |
| 「北京天气」 | 天气 Tool |
| 「我是项目经理」→「我是谁」 | `session_id` Memory |

**方案文档：** [为什么这样做](docs/solution-design.md) · [系统长什么样](docs/architecture.md)

---

## 功能亮点

| 能力 | 说明 |
|------|------|
| **企业 RAG** | PDF → Chunk → Embedding → Chroma → 可溯源问答 |
| **Agent Workflow** | chat / rag / mcp / weather / news / sports / calculator |
| **Memory** | 短记忆 + Long facts |
| **MCP** | 标准协议接入外部工具 |
| **Web + SSE** | React 聊天，流式输出 + Cost 展示 |
| **一键部署** | Nginx + API + Chroma（可选 Ollama） |
| **可观测** | Request ID · 日志落盘 · Token/Cost |

---

## 架构

```
Client (Browser / curl)
    │
    ▼
Nginx (:80)
    │
    ▼
FastAPI
    │
    ▼
Agent (workflow + executor + memory)
    │
    ├─► Tool Registry ──► MCP / Weather / News / …
    │
    └─► RAG Pipeline → Chroma → LLM
            │
            ▼
        Answer + sources + usage(cost)
```

```
docker compose
  nginx ──► api ──► chroma
              ├──► 通义 API（默认）
              └──► ollama（--profile local-llm）
```

完整说明：[docs/architecture.md](docs/architecture.md)

---

## 快速开始

### 前置

- Docker Desktop（推荐），或 Python 3.10+ / Node 20+
- 通义 API Key（[百炼](https://bailian.console.aliyun.com/)）或本机 Ollama

### Docker Compose（推荐）

```powershell
git clone https://github.com/Huangzd11/ai-project-assistant.git
cd ai-project-assistant
copy .env.example .env
# 编辑 .env：OPENAI_API_KEY、MODEL_NAME=qwen-plus

docker compose up -d --build
Invoke-RestMethod http://localhost/health
# http://localhost       → Web UI
# http://localhost/docs  → Swagger
```

本地 Ollama：`docker compose --profile local-llm up -d --build`，再执行 `.\scripts\ollama-pull.ps1`。

### 本地开发

```powershell
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

cd frontend && npm install && npm run dev
# http://127.0.0.1:5173
```

### 验证

```powershell
Invoke-RestMethod http://localhost/health
# → version: 1.0.0

Invoke-RestMethod -Uri http://localhost/agent -Method Post `
  -ContentType "application/json" -Body '{"message":"用一句话介绍你自己"}'

Invoke-RestMethod "http://localhost/metrics/cost-estimate?users=1000&queries_per_user=20&avg_total_tokens=3000"
```

---

## 项目结构

```
ai-project-assistant/
├── app/                 # FastAPI：api / agent / rag / mcp / core
├── frontend/            # React + Vite
├── nginx/               # 反代 + 静态资源
├── config/              # settings / logging / pricing
├── docs/                # 架构、方案、API、Roadmap、Day 日志
├── mindmap/             # Day01~27 学习思维导图（Mermaid）
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── LICENSE
└── README.md
```

[docs/CODEMAP.md](docs/CODEMAP.md)

---

## 功能展示

```json
{
  "answer": "……",
  "workflow": { "intent": "chat", "need_tool": false },
  "sources": [],
  "usage": {
    "prompt_tokens": 1450,
    "completion_tokens": 632,
    "total_tokens": 2082,
    "cost_usd": 0.000336,
    "model": "qwen-plus"
  }
}
```

```powershell
python scripts/estimate_cost.py --users 1000 --qpu 20 --avg-tokens 3000
```

---

## API 文档

| 接口 | 说明 |
|------|------|
| `GET /health` | 探活 + **v1.0.0** |
| `POST /agent` · `/agent/stream` | Agent（含 usage） |
| `POST /rag` · `/chat` · `/upload` | RAG / 闲聊 / 上传 |
| `GET /metrics/cost-estimate` | 日成本估算 |
| `GET /mcp/status` | MCP 状态 |

书面说明：[docs/api.md](docs/api.md) · 交互：`/docs`

---

## Roadmap

| Sprint | 主题 | 状态 |
|--------|------|------|
| 1 · v0.1 | LLM · FastAPI · Docker | ✅ |
| 2 · v0.2 | 企业 RAG | ✅ |
| 3 · v0.3 | Agent · Memory · MCP · Web | ✅ |
| 4 · v0.4 | Compose · Nginx · 日志 · Token · 方案 · README | ✅ |
| **v1.0** | **工程与文档收官** | ✅ |
| Day28~30 | 简历 / 面试 / 投递（可选，暂不设计） | ⏸ |

详情：[docs/roadmap.md](docs/roadmap.md)

---

## 版本记录

当前版本：**v1.0.0**

| 版本 | 摘要 |
|------|------|
| **v1.0.0** | 30 天能力收官：技术栈齐全 · 方案/架构/README · 可一键演示 |
| v0.4.0 | Compose、Nginx、日志、Token、方案文档、GitHub 包装 |
| v0.3.0 | Enterprise Agent |
| v0.2.0 | Enterprise RAG |
| v0.1.x | 基础链路 |

[docs/CHANGELOG.md](docs/CHANGELOG.md)

---

## 技术栈

FastAPI · Uvicorn · OpenAI SDK · Ollama / 通义 · Chroma · PyMuPDF · LangChain Text Splitters · sentence-transformers · MCP · React · Vite · Docker Compose · Nginx

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [solution-design.md](docs/solution-design.md) | 方案（Why） |
| [architecture.md](docs/architecture.md) | 架构（How） |
| [api.md](docs/api.md) | HTTP 接口 |
| [roadmap.md](docs/roadmap.md) | 进度 |
| [CHANGELOG.md](docs/CHANGELOG.md) | 版本 |
| [RELEASE.md](docs/RELEASE.md) | v1.0.0 收官说明 |
| [CODEMAP.md](docs/CODEMAP.md) | 代码地图 |
| [mindmap/](mindmap/README.md) | Day01~27 学习思维导图 |

---

## License

MIT — 见 [LICENSE](LICENSE)
