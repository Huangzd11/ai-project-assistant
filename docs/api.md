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
