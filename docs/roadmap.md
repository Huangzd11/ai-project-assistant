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
- [x] Day21_1 Web 前端 — `feat(frontend)` — v0.3.0+
- [x] Day21_2 实时 Tool + SSE — `feat(live-tools,stream)` — v0.3.2

---

## Sprint 4（v1.0）— Engineering + Interview

> **主题：** 从「能跑的 Agent」到「能部署、能演示、能写进简历、能讲方案、能面试」的完整交付物。  
> **Release：** AI Project Assistant **v1.0**

### Goal

完成 **v1.0 Release**，达到：

| 维度 | 标准 |
|------|------|
| 可以部署 | Docker Compose 一键启动，Nginx 反代，配置可管理 |
| 可以演示 | 浏览器完整链路可复现，有固定 Demo 脚本 |
| 可以写进简历 | README / 作品集包装到位，亮点可量化 |
| 可以讲技术方案 | 有架构设计文档，能画链路、讲权衡 |
| 可以应对 AI 创业公司面试 | 模拟面试 + 项目故事线熟练 |

### v1.0 最终项目能力

```
AI Project Assistant
├── Chat
├── RAG
├── Agent
├── MCP
├── Docker
├── Logging
├── Monitoring
├── Deployment
├── README
├── Architecture
└── Demo
```

### 演示主链路（Demo Flow）

```
上传 PDF → 提问 → RAG 检索 → Agent 调用工具 → 返回答案 + 引用来源
```

浏览器端已具备聊天、上传、workflow / sources 展示与 SSE 流式输出（Day21_1 / Day21_2）；Sprint 4 重点是**工程化补齐**与**求职交付**。

### Backlog

| Day | 主题 | 输出 | 版本 |
|-----|------|------|------|
| Day22 | Docker Compose | 一键启动（API + Chroma + Ollama） | v0.4-alpha ✅ |
| Day23 | Nginx + Reverse Proxy | 部署能力（反代、静态资源、生产入口） | v0.4-alpha2 |
| Day24 | 日志 + 配置管理 | 工程化（结构化日志、环境分层） | v0.4-beta |
| Day25 | Token / 成本统计 | AI PM 能力（用量可观测、成本估算） | v0.4-beta2 |
| Day26 | 架构设计文档 | Solution 能力（方案文档、架构图） | v0.4-rc |
| Day27 | README + GitHub 包装 | 作品集（徽章、截图、Quick Start） | v0.4 |
| Day28 | 简历优化 | 投递材料（项目描述、技术关键词） | — |
| Day29 | AI 创业公司模拟面试 | 面试准备（项目深挖 Q&A） | — |
| Day30 | 项目发布 + 投递 | 冲刺（tag v1.0、投递） | **v1.0** |

- [x] Day22 Docker Compose — `feat(docker-compose)` — v0.4-alpha — [Day22.md](Day22.md)
- [ ] Day23 Nginx 反代 — `feat(nginx)` — v0.4-alpha2
- [ ] Day24 日志与配置 — `feat(logging,config)` — v0.4-beta
- [ ] Day25 Token / 成本 — `feat(token-metrics)` — v0.4-beta2
- [ ] Day26 架构文档 — `docs(architecture)` — v0.4-rc
- [ ] Day27 README / GitHub — `docs(readme,portfolio)` — v0.4
- [ ] Day28 简历 — 投递材料
- [ ] Day29 模拟面试 — 面试准备
- [ ] Day30 发布 + 投递 — `release(v1.0)` — **v1.0**

### Sprint 4 与 Sprint 3 的分工

| Sprint 3（已完成） | Sprint 4（进行中） |
|-------------------|-------------------|
| Agent / Workflow / Tool / MCP / RAG 核心能力 | Compose / Nginx / 部署 |
| Web UI + SSE 流式 | 日志、监控、Token 成本 |
| 实时 Tool（天气 / 新闻 / 体育） | 架构文档、README 包装 |
| v0.3.x 功能交付 | 简历、面试、v1.0 发布 |

---

## 工程化改进

| 项 | 说明 | 状态 |
|----|------|------|
| 统一虚拟环境 | 共享依赖管理，monorepo 结构 | ✅ |
| `.env.example` | 提供配置模板，避免密钥泄露 | ✅ |
| 错误处理 | 统一超时、模型不可用等异常响应 | ✅ Day14 |
| 请求耗时日志 | 中间件记录 | ✅ Day14 |
| Web 前端 | React + Vite 聊天界面 | ✅ Day21_1 |
| SSE 流式 API | `POST /agent/stream` 逐字返回 | ✅ Day21_2 |
| docker-compose | API + Chroma + Ollama 一键编排 | ✅ Day22 |
| Nginx 反代 | 生产部署入口 | 📋 Day23 |
| 结构化日志 + 配置分层 | 工程化运维 | 📋 Day24 |
| Token / 成本统计 | AI PM 可观测 | 📋 Day25 |
| CI/CD | 自动化测试与镜像构建 | 待做 |

---

## 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Ollama 文档](https://github.com/ollama/ollama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [阿里云百炼](https://bailian.console.aliyun.com/)
- [MCP 规范](https://modelcontextprotocol.io/)
