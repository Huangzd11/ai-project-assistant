# Changelog

## v1.0.0 — 30 天实战收官

**发布日期：** 2026-07

将 Sprint 1~4 工程与文档能力正式定版为 **v1.0**：可一键演示的企业 AI 助手 + 完整 Solution 交付物。

### 技术能力（已交付）

LLM · Prompt · FastAPI · Docker · RAG · Embedding · Vector DB · Agent · MCP

### 项目能力（已交付）

方案设计 · 技术选型 · 成本评估 · 风险分析 · 项目交付

### 输出成果

- GitHub 项目（本仓库 + MIT）
- 架构图：`docs/architecture.md`
- README：产品化 Quick Start / Roadmap / 成果清单

### 相对 v0.4.0

- `APP_VERSION` / 文档 / 徽章统一为 **1.0.0**
- README 增加「最终成果（30 天）」总览
- Roadmap：工程收官；Day28~30（简历/面试/投递）标记为可选、暂不设计

---

## v0.4.0 — 工程化与作品集（Sprint 4 · Day22~27）

**发布日期：** 2026-07

### 核心能力

- **Docker Compose**：api + chroma 一键启动；`--profile local-llm` 可选 Ollama
- **Nginx**：统一入口 `:80`，静态 Web + API 反代 + SSE
- **日志 / 配置**：`config/` 分层、`logs/app.log` & `error.log`、Request ID
- **Token / 成本**：响应 `usage`；`GET /metrics/cost-estimate`
- **方案文档**：`architecture.md` + `solution-design.md`
- **GitHub 包装**：产品化 README、MIT License、徽章

### API 新增 / 增强

| 接口 | 说明 |
|------|------|
| `POST /agent` | 响应增加 `usage` |
| `POST /agent/stream` | SSE：`usage` 事件 + `done.usage` |
| `POST /chat` / `POST /rag` | 响应增加 `usage` |
| `GET /metrics/cost-estimate` | 规模化日成本粗算 |
| 响应头 `X-Request-ID` | 请求追踪 |

### 配置新增

- `APP_ENV`、`LOG_LEVEL`、`LOG_DIR`、`LOG_CONSOLE`
- `PRICING_FILE`、`COST_CURRENCY`
- `config/settings.yaml`、`logging.yaml`、`pricing.yaml`

### 文档

- Day22~27、architecture、solution-design、api.md、CHANGELOG

---

## v0.3.0 — Enterprise AI Agent（Sprint 3 · Day15~21）

**发布日期：** 2026-07

### 核心能力

- **Agent Workflow**：`POST /agent` 自动路由 chat / RAG / Filesystem MCP / calculator / pdf_read
- **会话 Memory**：`session_id` 多轮对话，Short Memory + Long facts
- **Tool Registry**：可扩展注册
- **MCP Client**：Filesystem MCP
- **Web + SSE**：React UI、`POST /agent/stream`；天气 / 新闻 / 体育 Tool

### API

| 接口 | 说明 |
|------|------|
| `POST /agent` | 企业 Agent 主入口 |
| `POST /agent/stream` | SSE 流式 |
| `GET /mcp/status` | MCP 状态 |
| `GET /health` | 健康检查 + 版本号 |

---

## v0.2.0 — Enterprise RAG（Sprint 2 · Day08~14）

- PDF 上传 → 解析 → Chunk → Embedding → Chroma
- `POST /rag` 知识库问答 + sources
- 请求日志、统一异常、Swagger、Docker

---

## v0.1.x — 基础链路（Sprint 1 · Day01~07）

- LLM / Ollama / FastAPI / Docker / GitHub
