# API 接口说明

> **版本：v0.3.0**（Enterprise AI Agent Release）  
> 基础地址：`http://127.0.0.1:8000`  
> 交互文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 核心接口一览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查探活 |
| `/upload` | POST | 上传 PDF 至知识库 |
| `/chat` | POST | 纯 LLM 对话（不走知识库） |
| `/rag` | POST | 企业知识库 RAG 问答（含引用来源） |
| `/agent` | POST | Agent 规划 + 工具调用 + 总结（Day15） |
| `/mcp/status` | GET | MCP 连接状态与已注册工具（Day18） |
| `/mcp/tools` | GET | MCP 工具列表（Day18） |

## 错误响应（Day14）

| HTTP | 场景 | 响应示例 |
|------|------|----------|
| 400 | 上传非 PDF | `{"detail": "仅支持 PDF 文件"}` |
| 503 | LLM 不可达（Ollama 未启动） | `{"detail": "LLM 服务不可用，请检查 Ollama"}` |
| 504 | LLM 请求超时 | `{"detail": "LLM 请求超时"}` |
| 500 | 未知服务器错误 | `{"detail": "服务器内部错误"}` |

检索无结果时 `POST /rag` 仍返回 **200**，`sources` 为空数组：

```json
{
  "question": "不存在的问题",
  "answer": "知识库中未找到相关内容。",
  "sources": []
}
```

**引用来源展示约定（前端）：** `{source}  Page {page}`，例如 `test.pdf  Page 1`。

---

## GET `/`

服务欢迎接口。

```json
{ "message": "Hello AI" }
```

---

## GET `/health`

健康检查，用于探活（Docker/K8s）；含 API 版本号（Day21）。

```json
{ "status": "OK", "version": "0.3.0" }
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 服务状态，正常为 OK |
| `version` | string | 当前 API 版本 |

**PowerShell 测试：**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

---

## GET `/models`

返回当前模型配置。

```json
{
  "provider": "ollama",
  "model": "qwen3:4b",
  "base_url": "http://127.0.0.1:11434/v1"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `provider` | string | 模型提供方 |
| `model` | string | 当前模型名 |
| `base_url` | string | API 基础地址 |

---

## POST `/chat`

AI 聊天接口。

**请求：**

```json
{ "message": "什么是 RAG？" }
```

**响应：**

```json
{ "answer": "RAG（Retrieval-Augmented Generation）是检索增强生成..." }
```

**PowerShell 测试：**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"什么是 RAG？"}'
```

---

## POST `/upload`

上传 PDF 文件至 `uploads/` 目录。

**请求：** `multipart/form-data`，字段名 `file`

**响应：**

```json
{
  "filename": "linux.pdf",
  "size": "8MB"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `filename` | string | 保存的文件名 |
| `size` | string | 人类可读大小（如 `8MB`、`512KB`） |

**浏览器测试：** 访问 http://127.0.0.1:8000/docs ，在 `POST /upload` 中选择 PDF 文件上传。

**PowerShell 测试：**

```powershell
curl.exe -X POST http://127.0.0.1:8000/upload -F "file=@C:\path\to\linux.pdf"
```

---

## PDF 解析（Day09 · 模块调用）

上传后的 PDF 可通过 `app/rag/pdf_loader.py` 解析为 JSON（当前非 HTTP 接口，Day13 纳入流水线）。

```powershell
python -c "from app.rag.pdf_loader import parse_pdf; print(parse_pdf('uploads/linux.pdf'))"
```

**输出文件：** `data/parsed/linux.json`

```json
{
  "source": "linux.pdf",
  "total_pages": 4,
  "pages": [
    { "page": 1, "content": "..." },
    { "page": 2, "content": "..." }
  ]
}
```

---

## Chunk 切分（Day10 · 模块调用）

解析后的 JSON 可通过 `app/rag/chunker.py` 切分为 Chunk（当前非 HTTP 接口，Day13 纳入流水线）。

```powershell
python -c "from app.rag.chunker import chunk_pdf; print(chunk_pdf('data/parsed/linux.json'))"
```

**输出文件：** `data/chunks/linux.json`

```json
{
  "source": "linux.pdf",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "total_chunks": 12,
  "chunks": [
    { "chunk_id": 1, "page": 1, "content": "..." },
    { "chunk_id": 2, "page": 1, "content": "..." }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `chunk_id` | int | 全局递增块编号 |
| `page` | int | 来源页码（便于溯源） |
| `content` | string | 块文本内容 |

---

## Embedding 向量化（Day11 · 模块调用）

Chunk JSON 可通过 `app/rag/embedder.py` 转为向量（当前非 HTTP 接口，Day13 纳入流水线）。

```powershell
python -c "from app.rag.embedder import embed_chunks; print(embed_chunks('data/chunks/linux.json'))"
```

**输出文件：** `data/vectors/linux.json`

```json
{
  "source": "linux.pdf",
  "provider": "local",
  "model": "BAAI/bge-small-zh-v1.5",
  "dimension": 512,
  "total_vectors": 12,
  "vectors": [
    { "chunk": 1, "page": 1, "embedding": [0.22, -0.11, ...] },
    { "chunk": 2, "page": 1, "embedding": [...] }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `chunk` | int | 对应 chunks JSON 的 `chunk_id` |
| `page` | int | 来源页码 |
| `embedding` | float[] | 向量（本地 bge-small 为 512 维） |

**Provider 切换：**

| `EMBEDDING_PROVIDER` | 模型示例 | 依赖 |
|----------------------|----------|------|
| `local`（默认） | `BAAI/bge-small-zh-v1.5` | `sentence-transformers` |
| `dashscope` | `text-embedding-v3` | 百炼 API Key |

---

## 向量检索（Day12 · 模块调用）

Chunk + Vector 入库 Chroma 后，可通过 `search()` 做纯检索（**不接 LLM**）。

```powershell
# 入库
python -c "from app.rag.vector_store import index_chunks; print(index_chunks('data/chunks/test.json'))"

# 检索
python -c "from app.rag.vector_store import search; import json; print(json.dumps(search('telnet'), ensure_ascii=False, indent=2))"
```

**检索返回：**

```json
{
  "query": "telnet",
  "top_k": 5,
  "results": [
    {
      "rank": 1,
      "score": 0.6835,
      "chunk": 2,
      "page": 2,
      "source": "test.pdf",
      "content": "工具选择telnet终端：..."
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `rank` | int | 排名 |
| `score` | float | 相似度（越高越相关） |
| `chunk` / `page` / `source` | — | 溯源信息 |
| `content` | string | 命中原文 |

---

## POST `/rag`

知识库 RAG 问答（Day13）：检索 Top-K → 拼接 Prompt → LLM 生成带引用的回答。

**请求：**

```json
{ "question": "如何开启 telnet？" }
```

**响应：**

```json
{
  "question": "如何开启 telnet？",
  "answer": "根据《test.pdf》第1页：ASR1803开启telnetd……",
  "sources": [
    {
      "source": "test.pdf",
      "page": 1,
      "chunk": 1,
      "score": 0.72
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `question` | string | 用户问题 |
| `answer` | string | LLM 生成的回答（含引用句式） |
| `sources` | array | 引用来源列表 |
| `sources[].source` | string | 文档名 |
| `sources[].page` | int | 页码 |
| `sources[].chunk` | int | chunk 编号 |
| `sources[].score` | float | 检索相似度 |

**PowerShell 测试：**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/rag `
  -Method Post -ContentType "application/json" `
  -Body '{"question":"如何开启 telnet？"}'
```

**模块调用（无 HTTP）：**

```powershell
python -c "from app.rag.rag_pipeline import rag_answer; import json; print(json.dumps(rag_answer('telnet'), ensure_ascii=False, indent=2))"
```

> 前置条件：知识库已通过 `index_chunks()` 入库；LLM 服务（Ollama 或通义）可用。

---

## POST `/agent`

Agent 问答（Day15~20）：Workflow 意图路由 + Tool + **session_id 多轮记忆**。

**与 `/rag` 区别：**

| 接口 | 路径 | 特点 |
|------|------|------|
| `/rag` | 固定 RAG 流水线 | 无规划层，直接检索+回答 |
| `/agent` | Workflow + Tool + Memory | 返回 `workflow` + `plan`；自动选择 RAG / MCP / Chat |

**请求：**

```json
{
  "message": "我是谁？",
  "session_id": "work-001"
}
```

`session_id` 可选；不传则单轮无记忆（兼容 Day16）。

**响应：**

```json
{
  "message": "帮我总结 Linux.pdf",
  "answer": "Linux.pdf 主要介绍了……",
  "session_id": "work-001",
  "workflow": {
    "intent": "rag",
    "need_tool": true,
    "route": "Question → RAG Search → Summary → Answer",
    "reason": "知识库检索与总结"
  },
  "plan": [
    {
      "tool": "rag_query",
      "args": { "question": "Linux.pdf 的主要内容是什么？" },
      "reason": "需要从知识库获取文档内容"
    }
  ],
  "tool_calls": [{ "tool": "rag_query" }],
  "sources": []
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `workflow.intent` | string | `chat` / `rag` / `filesystem` / `calculator` / `pdf_read` / `mcp_explicit` |
| `workflow.need_tool` | bool | 是否调用了工具 |
| `workflow.route` | string | 路由链路说明 |
| `workflow.reason` | string | 决策原因 |

**响应（闲聊）：**

```json
{
  "message": "我是谁？",
  "answer": "您是项目经理。",
  "session_id": "work-001",
  "workflow": {
    "intent": "chat",
    "need_tool": false,
    "route": "Question → Memory → LLM → Answer",
    "reason": "无需工具，直接对话"
  },
  "plan": [],
  "tool_calls": [],
  "sources": []
}
```

**多轮记忆测试：**

```powershell
# 第 1 轮
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post -ContentType "application/json `
  -Body '{"message":"我是项目经理","session_id":"work-001"}'

# 第 2 轮（同一 session_id）
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post -ContentType "application/json" `
  -Body '{"message":"我是谁？","session_id":"work-001"}'
```

**带工具调用的请求示例：**

```json
{ "message": "总结一下 test.pdf", "session_id": "work-001" }
```

**带工具调用的响应示例：**

```json
{
  "message": "总结一下 test.pdf",
  "answer": "test.pdf 主要介绍了……",
  "session_id": "work-001",
  "plan": [
    {
      "tool": "rag_query",
      "args": { "question": "test.pdf 的主要内容是什么？" },
      "reason": "需要从知识库获取文档内容"
    }
  ],
  "tool_calls": [{ "tool": "rag_query" }],
  "sources": [
    { "source": "test.pdf", "page": 1, "chunk": 1, "score": 0.72 }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 用户目标 |
| `answer` | string | Agent 最终回答 |
| `session_id` | string | 会话 ID（Day17）；多轮记忆 |
| `plan` | array | 规划步骤（可观测、可调试） |
| `tool_calls` | array | 实际调用的工具 |
| `sources` | array | RAG 引用来源；纯闲聊时为空 |

**PowerShell 测试：**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"总结一下 test.pdf"}'
```

**模块调用（无 HTTP）：**

```powershell
python -c "from app.agent import run_agent; import json; print(json.dumps(run_agent('总结 test.pdf'), ensure_ascii=False, indent=2))"
```

**MCP 显式调用（Day18）：**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"mcp read_file README.md"}'
```

**Filesystem 自然语言（Day19）：**

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"帮我看看 README 写了什么"}'
```

---

## GET `/mcp/status`

MCP 连接状态与已注册工具（Day18）。

**响应：**

```json
{
  "enabled": true,
  "tool_count": 13,
  "tools": [
    { "name": "mcp_echo", "description": "Echoes back the input" }
  ]
}
```

---

## GET `/mcp/tools`

返回 MCP 工具列表（与 `/mcp/status` 的 `tools` 字段相同）。

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
| `PARSED_DIR` | `data/parsed` | PDF 解析 JSON 输出目录 |
| `CHUNKS_DIR` | `data/chunks` | Chunk JSON 输出目录 |
| `CHUNK_SIZE` | `500` | 文本块大小（字符） |
| `CHUNK_OVERLAP` | `50` | 块间重叠字符数 |
| `VECTORS_DIR` | `data/vectors` | 向量 JSON 输出目录 |
| `EMBEDDING_PROVIDER` | `local` | `local` 或 `dashscope` |
| `EMBEDDING_MODEL` | `BAAI/bge-small-zh-v1.5` | Embedding 模型名 |
| `EMBEDDING_DIMENSION` | `512` | 云端向量维度 |
| `CHROMA_DIR` | `data/chroma` | Chroma 持久化目录 |
| `CHROMA_COLLECTION` | `knowledge` | Collection 名称 |
| `SEARCH_TOP_K` | `5` | 检索返回条数 |
| `RAG_SYSTEM_PROMPT` | （见 config.py） | RAG 专用 system 提示词 |
| `AGENT_ANSWER_PROMPT` | （见 config.py） | Agent 总结阶段 system 提示词 |
| `MEMORY_DIR` | `data/conversations` | 会话记忆 JSON 目录 |
| `MEMORY_MAX_TURNS` | `10` | Short Memory 保留轮数 |
| `MCP_ENABLED` | `false` | 是否启动 MCP Client |
| `MCP_SERVER_COMMAND` | `npx` | MCP Server 启动命令 |
| `MCP_FILESYSTEM_ROOT` | 项目根目录 | Filesystem MCP 沙箱根目录（绝对路径） |
| `MCP_SERVER_ARGS` | 自动拼接 filesystem + root | MCP Server 参数（逗号分隔） |
