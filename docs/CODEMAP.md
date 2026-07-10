# 代码地图（Code Map）

> 按目录列出每个文件的 **Day 来源**、**主要功能** 与 **核心逻辑**，便于回顾学习路径。  
> 当前版本：**v1.0.0**（30 天实战收官）

---

## 完整目录

```
ai-project-assistant/
│
├── app/                              # Day04 创建 · Day08 重构
│   ├── main.py                       # Day04/14/18/24/25 — 入口、中间件、metrics
│   │
│   ├── api/
│   │   ├── health.py                 # Day04 — GET / 、/health
│   │   ├── chat.py                   # Day04/25 — POST /chat + usage
│   │   ├── upload.py                 # Day08 — POST /upload
│   │   ├── rag.py                    # Day13/25 — POST /rag + usage
│   │   ├── agent.py                  # Day15/21_2/25 — /agent、/agent/stream
│   │   ├── mcp.py                    # Day18 — /mcp/status、/mcp/tools
│   │   └── metrics.py                # Day25 — /metrics/cost-estimate
│   │
│   ├── agent/                        # Day15~21 Agent
│   │   ├── workflow.py               # Day20 — 意图路由
│   │   ├── executor.py               # Day15/17/21_2/25 — 执行 + SSE + usage
│   │   ├── memory.py                 # Day17 — Short / Long Memory
│   │   ├── planner.py                # Day16/18 — 薄封装 → workflow
│   │   └── tools/                    # Day16/21_2 — Registry + 天气/新闻/体育等
│   │
│   ├── mcp/                          # Day18/19 — MCP Client + Bridge
│   ├── rag/                          # Day09~13 — PDF → Chroma → RAG
│   ├── core/
│   │   ├── config.py                 # Day02+ — 环境变量 + APP_VERSION
│   │   ├── settings.py               # Day24 — yaml + env 分层
│   │   ├── llm.py                    # Day02/17/21_2/25 — chat + stream + usage
│   │   ├── logger.py                 # Day08/24 — 落盘 + dictConfig
│   │   ├── middleware.py             # Day14/24 — RequestId + 请求日志
│   │   ├── request_context.py        # Day24 — request_id / trace_id
│   │   ├── pricing.py                # Day25 — 单价与日成本估算
│   │   ├── token_meter.py            # Day25 — UsageInfo
│   │   ├── exceptions.py             # Day14
│   │   └── files.py                  # Day08
│   └── models/                       # Pydantic 契约（含 UsageInfo）
│
├── frontend/                         # Day21_1/21_2/25 — React + Vite + usage UI
├── nginx/                            # Day23 — 反代 + 静态资源镜像
├── config/                           # Day24/25 — settings / logging / pricing
├── scripts/                          # entrypoint、ollama-pull、estimate_cost
├── docs/                             # 架构、方案、API、Roadmap、Day01~27
├── docker-compose.yml                # Day22/23/24
├── docker-compose.dev-api.yml        # Day23 — 开发暴露 8000
├── Dockerfile
├── LICENSE                           # Day27 — MIT
└── README.md                         # Day27 — 产品化首页
```

---

## 按 Day 索引（摘要）

| Day | 文件 / 主题 | 逻辑概要 |
|-----|-------------|----------|
| Day01~07 | examples + FastAPI + Docker + GitHub | 基础链路 |
| Day08~14 | upload → RAG → 企业化 | PDF 知识库 v0.2 |
| Day15~21 | Agent / Memory / MCP / Web / SSE | Enterprise Agent v0.3 |
| **Day22** | `docker-compose.yml` | api + chroma + ollama profile |
| **Day23** | `nginx/` | 统一入口 :80，静态 + 反代 |
| **Day24** | `settings` / `logger` / `request_context` | 配置分层、日志、Request ID |
| **Day25** | `pricing` / `token_meter` / `metrics` | Token + Cost + 日成本估算 |
| **Day26** | `architecture.md` / `solution-design.md` | Solution 文档 |
| **Day27** | `README.md` / `LICENSE` / `CHANGELOG` | GitHub 作品集包装 |

更细的 Day01~21 行级索引见本文件历史版本；Sprint 4 以目录树与 [roadmap.md](roadmap.md) 为准。

---

## 主请求链路（v1.0）

```
Client → Nginx → FastAPI → Agent → RAG → Chroma → LLM
                              └─ Tools / MCP
                                 → Answer + sources + usage
```

```
# Compose
docker compose up -d --build
# http://localhost  → Web + API

# 本地
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

---

## 相关文档

- [README.md](../README.md) · [architecture.md](architecture.md) · [solution-design.md](solution-design.md)
- [api.md](api.md) · [CHANGELOG.md](CHANGELOG.md) · [roadmap.md](roadmap.md)
