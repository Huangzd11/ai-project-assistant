# Day21 — Sprint Review + Release（v0.3.0）

> 版本：**v0.3.0** | Commit：`release(v0.3)`  
> **今日：不写新功能，把 Sprint 3 打磨成可交付的企业 AI Agent**

## 学习目标

- [x] 理解 Sprint Review 的目标：**可观测、可排错、可交付**
- [x] 完成 README / api.md / 架构说明 / CHANGELOG 收尾
- [x] 验证日志、异常、Docker、Swagger 与 v0.3.0 一致
- [x] 优化 Agent / RAG 相关 Prompt
- [ ] 全链路验收后打 Tag **`v0.3.0`**

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| 文档、Prompt、日志、异常、Docker 验证 | 新 HTTP 接口、新 Tool |
| README v0.3.0 交付说明 | 流式 SSE、前端 UI |
| `/health` 返回版本号 | 多 MCP Server 编排 |
| CHANGELOG、架构图文字版 | Day22+ 新 Sprint |

**Day21 = 把 Day15~20 的 Agent 能力「包装成可交付的 v0.3.0」。**

---

## Sprint 3 结束后的能力

到 Day21，项目已不再是普通 RAG，而是具备 **企业 AI Agent 雏形**：

- ✅ **多轮对话（Memory）** — `session_id` + Short/Long Memory
- ✅ **企业知识库（RAG）** — 检索 + 引用来源
- ✅ **工具调用（Tool Calling）** — Registry：rag / pdf / calculator
- ✅ **MCP 集成** — Filesystem MCP 读项目文件
- ✅ **Workflow 编排** — 自动选择 RAG / MCP / Chat

---

## 在 Sprint 3 中的位置

```
Day15~17  Agent Core + Tools + Memory     ✅
Day18~19  MCP Client + Filesystem         ✅
Day20     Enterprise Workflow             ✅
Day21     Review + Release v0.3.0         ← 今天
```

---

## 优化清单

| # | 方向 | Day21 目标 | 状态 |
|---|------|------------|------|
| 1 | README | 增加 **v0.3.0 Agent** 快速体验 + 架构说明 | ✅ |
| 2 | 架构图 | `solution-design.md` 补充 Sprint 3 链路 | ✅ |
| 3 | 日志 | 确认 HTTP / Agent workflow / RAG 耗时日志 | ✅ |
| 4 | 异常 | 确认 LLM 503/504、全局 500 仍正常 | ✅ |
| 5 | Docker | 镜像 tag `v0.3.0`，补充 MCP 说明 | ✅ |
| 6 | API | `api.md` + Swagger 对齐 `workflow` 字段 | ✅ |
| 7 | Prompt | 优化 `AGENT_ANSWER_PROMPT`（RAG / 文件 / MCP） | ✅ |
| 8 | 版本 | `main.py`、 `/health` → `0.3.0` | ✅ |
| 9 | CHANGELOG | `docs/CHANGELOG.md` Sprint 3 发布说明 | ✅ |
| 10 | Git | Tag `v0.3.0` | ⬜ |

---

## 架构（Sprint 3 · v0.3.0）

```
                    POST /agent
                         │
                         ▼
              ┌─────────────────────┐
              │  workflow.py        │  意图：chat/rag/filesystem/...
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    calculator      mcp_read_file     rag_query
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  executor + memory    │
              └──────────┬──────────┘
                         ▼
              Answer + workflow + sources
```

**与 v0.2.0 对比：**

| 版本 | 核心能力 | 入口 |
|------|----------|------|
| v0.2.0 | 企业 RAG | `POST /rag` |
| v0.3.0 | 企业 Agent（RAG + Tool + MCP + Memory） | `POST /agent` |

---

## v0.3.0 验收清单

### 1. Agent Workflow

```powershell
# RAG 总结 PDF（需知识库已入库）
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post `
  -ContentType "application/json" -Body '{"message":"帮我总结 Linux.pdf"}'
# 期望：workflow.intent=rag, sources 非空

# Filesystem 读 README（需 MCP_ENABLED=true + Node.js）
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post `
  -ContentType "application/json" -Body '{"message":"README 里面写了什么"}'
# 期望：workflow.intent=filesystem

# 多轮记忆
Invoke-RestMethod ... -Body '{"message":"我是项目经理","session_id":"s1"}'
Invoke-RestMethod ... -Body '{"message":"我是谁","session_id":"s1"}'
```

### 2. 基础 API

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
# 期望：status=OK, version=0.3.0

Invoke-RestMethod http://127.0.0.1:8000/mcp/status
```

### 3. Docker

```powershell
docker build -t ai-assistant:v0.3.0 .
docker run -p 8000:8000 `
  -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 `
  -e MCP_ENABLED=false `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/uploads:/app/uploads `
  ai-assistant:v0.3.0
curl http://127.0.0.1:8000/health
```

> 容器内默认 **不启用 MCP**（需 Node.js）；本地开发可 `MCP_ENABLED=true`。

---

## Prompt 优化说明

| Prompt | 用途 | Day21 调整 |
|--------|------|------------|
| `SYSTEM_PROMPT` | 纯闲聊 | 保持 |
| `RAG_SYSTEM_PROMPT` | `/rag` 流水线 | 保持 |
| `AGENT_ANSWER_PROMPT` | 工具结果 → 总结 | 区分 RAG sources / 文件内容 / 工具失败 |

---

## Git Release

```powershell
git add .
git commit -m "release(v0.3): Sprint 3 Enterprise AI Agent v0.3.0"
git tag v0.3.0
git push origin main --tags
```

---

## 收获（完成后填写）

- Sprint 3 从「能跑」到「能交付、能演示、能写进简历」
- v0.2.0 = 知识库；v0.3.0 = Agent 助手
- Day22+ 可选：流式、前端、评测、自建 MCP Server

---

## 下一步（Day22+）

- Web 聊天界面设计见 [Day21_1.md](Day21_1.md)（已实现 `frontend/`）
- 更远期见 [roadmap.md](roadmap.md)：流式 API、Prompt 评测等
