# API 接口说明

基础地址：`http://127.0.0.1:8000`

## GET `/`

服务欢迎接口。

```json
{ "message": "Hello AI" }
```

---

## GET `/health`

健康检查，用于探活。

```json
{ "status": "OK" }
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
