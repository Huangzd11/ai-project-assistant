# API 接口说明

> **版本：v1.0.0**（30 天实战收官）  
> Compose 入口：`http://localhost`（经 Nginx）  
> 本地开发：`http://127.0.0.1:8000`  
> 交互文档：`/docs`（Swagger）

## 核心接口一览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查探活 + 版本号 |
| `/upload` | POST | 上传 PDF 至知识库 |
| `/chat` | POST | 纯 LLM 对话（含 `usage`） |
| `/rag` | POST | 企业知识库 RAG 问答（含 sources + `usage`） |
| `/agent` | POST | Agent 规划 + 工具 + 总结（含 `usage`） |
| `/agent/stream` | POST | Agent SSE 流式（token / usage / done） |
| `/metrics/cost-estimate` | GET | 规模化日成本粗算（AI PM） |
| `/mcp/status` | GET | MCP 连接状态与已注册工具 |
| `/mcp/tools` | GET | MCP 工具列表 |
| `/models` | GET | 当前模型配置 |

## 通用：Token / 成本（Day25）

多数 LLM 接口响应可含：

```json
"usage": {
  "prompt_tokens": 1450,
  "completion_tokens": 632,
  "total_tokens": 2082,
  "cost_usd": 0.000336,
  "model": "qwen-plus",
  "currency": "USD"
}
```

单价见 `config/pricing.yaml`（估算用，非账单权威）。无 usage 时字段可为 `null`。

错误响应可含 `request_id`；成功响应头含 `X-Request-ID`（Day24）。

## 错误响应（Day14）

| HTTP | 场景 | 响应示例 |
|------|------|----------|
| 400 | 上传非 PDF | `{"detail": "仅支持 PDF 文件"}` |
| 503 | LLM 不可达 | `{"detail": "LLM 服务不可用，请检查 Ollama"}` |
| 504 | LLM 请求超时 | `{"detail": "LLM 请求超时"}` |
| 500 | 未知服务器错误 | `{"detail": "服务器内部错误", "request_id": "..."}` |

检索无结果时 `POST /rag` 仍返回 **200**，`sources` 为空数组。

**引用来源展示约定：** `{source}  Page {page}`。

---

## GET `/health`

```json
{ "status": "OK", "version": "1.0.0" }
```

```powershell
Invoke-RestMethod -Uri http://localhost/health
```

---

## GET `/models`

返回当前 `provider` / `model` / `base_url`。

---

## GET `/metrics/cost-estimate`（Day25）

| 参数 | 默认 | 说明 |
|------|------|------|
| `users` | 1000 | 日活用户 |
| `queries_per_user` | 20 | 每用户每日问答次数 |
| `avg_total_tokens` | 3000 | 平均每次总 Token |
| `input_ratio` | 0.67 | Input 占比 |
| `model` | 当前 MODEL_NAME | 计价模型 |

```powershell
Invoke-RestMethod "http://localhost/metrics/cost-estimate?users=1000&queries_per_user=20&avg_total_tokens=3000"
```

---

## POST `/chat`

纯 LLM 单轮对话。响应：`answer` + 可选 `usage`。

---

## POST `/rag`

知识库 RAG。响应：`question`、`answer`、`sources[]`、可选 `usage`。

---

## POST `/agent`

企业 Agent。响应：`answer`、`workflow`、`plan`、`tool_calls`、`sources`、可选 `usage`、`session_id`。

```powershell
Invoke-RestMethod -Uri http://localhost/agent -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"帮我总结 test.pdf","session_id":"work-001"}'
```

---

## POST `/agent/stream`

SSE 事件顺序：`workflow` → `plan` → `tool_calls?` → `token*` → `usage?` → `done`。

```powershell
curl.exe -N -X POST http://localhost/agent/stream `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"你好\"}"
```

---

## POST `/upload`

`multipart/form-data`，字段名 `file`，仅 PDF。

---

## GET `/mcp/status` · `/mcp/tools`

需 `MCP_ENABLED=true`。

---

## 相关文档

- Swagger：`/docs`
- [architecture.md](architecture.md) · [solution-design.md](solution-design.md) · [CHANGELOG.md](CHANGELOG.md)
