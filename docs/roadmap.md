# Roadmap

## Sprint 1（v0.1.x）— 基础链路

- [x] Day01 LLM Basic
- [x] Day02 OpenAI API
- [x] Day03 Ollama
- [x] Day04 FastAPI
- [x] Day05 Docker
- [x] Day06 GitHub
- [x] Day07 Review

## Sprint 2（v0.2.x）— Enterprise RAG

- [x] Day08 Upload + Refactor — `feat(upload)` — v0.2.0-alpha
- [x] Day09 PDF Loader — `feat(pdf-loader)` — v0.2.0-alpha2
- [x] Day10 Chunker — `feat(chunker)` — v0.2.0-beta
- [x] Day11 Embedding — `feat(embedding)` — v0.2.0-beta2
- [x] Day12 ChromaDB — `feat(vector-db)` — v0.2.0-rc
- [x] Day13 RAG Pipeline — `feat(rag)` — v0.2.0
- [x] Day14 Enterprise Release — `release: v0.2 enterprise rag` — v0.2.0

---

## Sprint 3（v0.3.x）— Enterprise AI Agent

> 在 Sprint 2 RAG 知识库之上，构建可规划、可调工具、可记记忆的企业级 Agent。

**目标架构：**

```
用户 → AI Project Assistant
         ├── Chat
         ├── RAG 知识库
         └── Memory
               ↓
         Agent Planner
               ↓
         Tools（PDF / Search / MCP …）
               ↓
            LLM → Answer
```

**目标模块结构：**

```
AI Project Assistant
├── Chat
├── Knowledge Base
├── Agent
├── MCP
└── Tools
```

| Day | 功能 | Git Commit | 版本 |
|-----|------|------------|------|
| Day15 | Agent 基础 + Function Calling | `feat(agent-core)` | v0.3-alpha |
| Day16 | Tool 管理 | `feat(tools)` | v0.3-alpha2 |
| Day17 | Memory | `feat(memory)` | v0.3-beta |
| Day18 | MCP 基础（Client） | `feat(mcp-client)` | v0.3-beta2 |
| Day19 | 真实 MCP Server（Filesystem） | `feat(mcp-server)` | v0.3-rc |
| Day20 | 企业 Agent Workflow | `feat(agent-workflow)` | v0.3 |
| Day21 | Sprint Review + Release | `release(v0.3)` | Release |

**Backlog：**

- [x] Day15 Agent Core — `feat(agent-core)` — v0.3-alpha
- [x] Day16 Tool Registry — `feat(tools)` — v0.3-alpha2
- [x] Day17 Memory — `feat(memory)` — v0.3-beta
- [x] Day18 MCP Client — `feat(mcp-client)` — v0.3-beta2
- [x] Day19 Filesystem MCP — `feat(mcp-server)` — v0.3-rc
- [x] Day20 Agent Workflow — `feat(agent-workflow)` — v0.3
- [x] Day21 Review + Release — `release(v0.3)` — v0.3.0

---

## 更远期（Day22+）

| 方向 | 计划 |
|------|------|
| 流式 API | 新增 `/chat/stream`，SSE 逐字返回 |
| 前端 | 简单 Web 聊天界面 |
| 评测 | Prompt 效果对比与指标统计 |

---

## 工程化改进

| 项 | 说明 | 状态 |
|----|------|------|
| 统一虚拟环境 | 共享依赖管理，monorepo 结构 | 进行中 |
| `.env.example` | 提供配置模板，避免密钥泄露 | ✅ |
| 错误处理 | 统一超时、模型不可用等异常响应 | ✅ Day14 |
| 日志监控 | 请求耗时、Token 用量统计 | ✅ Day14（请求耗时） |
| docker-compose | API + Ollama 一键编排 | 待做 |
| CI/CD | 自动化测试与镜像构建 | 待做 |

---

## 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Ollama 文档](https://github.com/ollama/ollama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [阿里云百炼](https://bailian.console.aliyun.com/)
- [MCP 规范](https://modelcontextprotocol.io/)
