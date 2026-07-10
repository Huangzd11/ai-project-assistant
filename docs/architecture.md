# Architecture — AI Project Assistant

> 版本：**v1.0.0** | 配套方案决策见 [solution-design.md](solution-design.md)  
> **本文回答：系统长什么样？请求怎么走？模块边界在哪？**

---

## 1. 文档目的与范围

| 项 | 说明 |
|----|------|
| 目的 | 给工程师 / 架构面试提供统一的结构视图与数据流 |
| 范围 | 当前已实现能力（至 Day25）：Web、Nginx、Agent、RAG、MCP、Compose、日志、Token |
| 非范围 | 商业 BRD、K8s 生产拓扑、多租户计费系统 |

代码级文件索引见 [CODEMAP.md](CODEMAP.md)；「为什么这样选」见 [solution-design.md](solution-design.md)。

---

## 2. 系统上下文

```
┌──────────────┐     HTTP :80      ┌─────────────────────────────────────┐
│  Browser /   │ ────────────────► │  AI Project Assistant (Compose)     │
│  curl / API  │                   │  nginx · api · chroma · [ollama]    │
└──────────────┘                   └──────────────┬──────────────────────┘
                                                  │
                         ┌────────────────────────┼────────────────────────┐
                         ▼                        ▼                        ▼
                   通义千问 API              Ollama(本地)              MCP Server
                   (OpenAI 兼容)            (可选 profile)           (Filesystem 等)
```

**调用方：** Web UI（React）、Swagger、`curl` / PowerShell。  
**被调用方：** LLM（Ollama 或通义）、Chroma、可选 MCP Server、天气/新闻等外部 HTTP。

---

## 3. 逻辑架构（分层）

```
┌─────────────────────────────────────────────────────────────┐
│  Client          React Web / curl / Swagger                 │
├─────────────────────────────────────────────────────────────┤
│  Edge            Nginx（静态资源 + Reverse Proxy）            │
├─────────────────────────────────────────────────────────────┤
│  API Gateway     FastAPI（路由、校验、CORS、异常、中间件）      │
├─────────────────────────────────────────────────────────────┤
│  Agent           Workflow · Executor · Memory · Tool Registry│
├─────────────────────────────────────────────────────────────┤
│  RAG             Pipeline · Embedder · Vector Store          │
├─────────────────────────────────────────────────────────────┤
│  Data            Chroma · uploads/ · data/* · logs/          │
├─────────────────────────────────────────────────────────────┤
│  LLM             OpenAI SDK → Ollama / DashScope             │
├─────────────────────────────────────────────────────────────┤
│  Cross-cutting   Config · Logging · Request ID · Token/Cost  │
└─────────────────────────────────────────────────────────────┘
```

| 层级 | 关键路径 | 职责 |
|------|----------|------|
| Edge | `nginx/` | 唯一对外入口；托管 `frontend/dist`；反代 API；SSE 关缓冲 |
| API | `app/main.py`, `app/api/` | HTTP 契约、健康检查、上传、Agent、RAG、Metrics |
| Agent | `app/agent/` | 意图路由、工具执行、会话记忆、流式输出 |
| RAG | `app/rag/` | PDF 解析 → Chunk → Embedding → 检索 → 带 sources 回答 |
| MCP | `app/mcp/` | 连接外部 MCP Server，桥接进 Tool Registry |
| Core | `app/core/` | LLM、配置、日志、定价、Token 计量 |
| Data | `uploads/`, `data/`, `logs/` | 原始文件、向量库、会话、运行日志 |

---

## 4. 主请求链路（核心）

```
Client (Browser / curl)
    │
    ▼
Nginx (:80)                          ← 静态页 + 反代
    │
    ▼
FastAPI (api:8000)
    │
    ▼
Agent (workflow + executor + memory)
    │
    ├─► Tool Registry ──► MCP / Weather / News / Sports / Calculator / …
    │
    └─► RAG Pipeline
            │
            ▼
        Vector DB (Chroma)
            │
            ▼
        Top-K chunks → Prompt → LLM (Ollama / 通义)
            │
            ▼
        Answer + sources + usage(cost)
```

**一句话：** 用户只打 Nginx；业务进 FastAPI；Agent 决定走工具还是知识库；知识落在 Chroma；最终由 LLM 生成可引用、可计量的回答。

### 4.1 典型 API

| 入口 | 行为 |
|------|------|
| `POST /agent` | 同步 Agent：Workflow → Tool/RAG → 总结 |
| `POST /agent/stream` | 同上，SSE 逐 token + `usage` 事件 |
| `POST /rag` | 纯知识库问答（不经完整 Agent 编排） |
| `POST /chat` | 纯 LLM，无检索 |
| `POST /upload` | PDF 入库链路入口 |
| `GET /metrics/cost-estimate` | 规模化日成本粗算（AI PM） |
| `GET /health` | 探活 + 版本号 |

---

## 5. 关键子链路

### 5.1 文档入库（RAG 写入路径）

```
POST /upload
    → uploads/xxx.pdf
    → pdf_loader   → data/parsed/
    → chunker      → data/chunks/     (CHUNK_SIZE≈500, OVERLAP≈50)
    → embedder     → data/vectors/
    → vector_store → Chroma (embedded 或 server 模式)
```

### 5.2 工具调用（Agent 分支）

```
POST /agent
    → workflow.build_workflow(intent)
    → executor 按 plan 调用 Tool Registry
         ├─ rag_query
         ├─ mcp_read_file / filesystem
         ├─ weather / news / sports
         └─ calculator / pdf_read …
    → 观察结果写入 Prompt
    → LLM 总结 → Answer + workflow 元数据
```

### 5.3 流式输出

```
POST /agent/stream
    → 同 Agent 准备阶段
    → chat_messages_stream (stream_options.include_usage)
    → SSE: workflow → plan → tool_calls → token* → usage → done
```

Nginx 对 API location 配置 `proxy_buffering off`，避免 SSE 被攒包。

### 5.4 配置与密钥

```
.env / 环境变量  >  config/settings.yaml  >  代码默认值
单价表：config/pricing.yaml
日志：config/logging.yaml → logs/app.log + logs/error.log
```

---

## 6. 部署架构

```
┌─ docker compose (app-net) ──────────────────────────┐
│                                                      │
│   Browser ──:80──► nginx                             │
│                      ├─ /        → 静态 React        │
│                      └─ /agent…  → api:8000          │
│                                      │               │
│                                      ├─► chroma:8000 │
│                                      ├─► 通义 API    │
│                                      └─► ollama      │
│                                          (profile:   │
│                                           local-llm) │
└──────────────────────────────────────────────────────┘
```

| 服务 | 宿主机端口 | 说明 |
|------|------------|------|
| `nginx` | **80** | 生产演示唯一入口 |
| `api` | 默认不映射（仅内网） | 开发可用 `docker-compose.dev-api.yml` 暴露 8000 |
| `chroma` | 无 | 向量库 |
| `ollama` | 11434（profile） | 本地 LLM |

详见 [Day22.md](Day22.md)、[Day23.md](Day23.md)。

---

## 7. 横切能力

| 能力 | 实现 | 文档 |
|------|------|------|
| Request ID | 中间件 + 响应头 `X-Request-ID` + 日志字段 | [Day24.md](Day24.md) |
| 分级日志 | `logs/app.log` / `error.log`，可轮转 | Day24 |
| Token / Cost | `usage` 字段 + `pricing.yaml` + metrics API | [Day25.md](Day25.md) |
| 健康检查 | `GET /health` → Compose / Nginx 探活 | Day14/21 |
| 配置分层 | `config/` + `.env` | Day24 |

---

## 8. 目录与模块映射（摘要）

```
app/
  api/          # HTTP 路由
  agent/        # Workflow / Executor / Memory / Tools
  rag/          # PDF → Chunk → Embed → Chroma → RAG
  mcp/          # MCP Client + Bridge
  core/         # llm / config / logger / pricing / token_meter
  models/       # Pydantic 契约
frontend/       # React + Vite
nginx/          # 反代 + 静态资源镜像
config/         # settings / logging / pricing
docs/           # 本文件 + solution-design + DayXX
```

完整 Day 索引：[CODEMAP.md](CODEMAP.md)。

---

## 9. 非目标 / 边界

当前架构**有意不做**：

- 多租户隔离与正式账单系统  
- Kubernetes Ingress / Service Mesh  
- 自研分布式追踪（仅透传 Trace ID，见 Day24）  
- 对 PDF 做模型 Fine-tune  

演进方向见 [solution-design.md](solution-design.md) 第 6 节。

---

*文档版本：v1.0.0 | 30 天收官*
