# Changelog

## v0.3.0 — Enterprise AI Agent（Sprint 3 · Day15~21）

**发布日期：** 2026-07

### 核心能力

- **Agent Workflow**：`POST /agent` 自动路由 chat / RAG / Filesystem MCP / calculator / pdf_read
- **会话 Memory**：`session_id` 多轮对话，Short Memory + Long facts
- **Tool Registry**：`rag_query`、`pdf_read`、`calculator` 可扩展注册
- **MCP Client**：连接 Filesystem MCP，自然语言读 README、列目录
- **可观测性**：响应含 `workflow`（intent / need_tool / route / reason）

### API

| 接口 | 说明 |
|------|------|
| `POST /agent` | 企业 Agent 主入口（Workflow + Memory + Tools） |
| `GET /mcp/status` | MCP 连接状态与工具列表 |
| `GET /health` | 健康检查 + 版本号 |

### 配置新增

- `MCP_ENABLED`、`MCP_FILESYSTEM_ROOT`、`MCP_SERVER_ARGS`
- `MEMORY_DIR`、`MEMORY_MAX_TURNS`

### 文档

- Day15~21 工作日志、api.md、CODEMAP、solution-design Sprint 3 架构

---

## v0.2.0 — Enterprise RAG（Sprint 2 · Day08~14）

- PDF 上传 → 解析 → Chunk → Embedding → Chroma
- `POST /rag` 知识库问答 + sources
- 请求日志、统一异常、Swagger、Docker

---

## v0.1.x — 基础链路（Sprint 1 · Day01~07）

- LLM / Ollama / FastAPI / Docker / GitHub
