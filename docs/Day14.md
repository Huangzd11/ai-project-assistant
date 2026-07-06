# Day14 — 企业化优化与 Release（v0.2.0）

> 版本：**v0.2.0** | Commit：`release: v0.2 enterprise rag`  
> **今日：不写新功能，做企业项目收尾**

## 学习目标

- [x] 理解企业级 API 服务的「可观测、可排错、可交付」三要素
- [x] 完善引用来源、日志、异常处理等工程化能力
- [x] 完成 Swagger / README / 接口文档 / Docker 验证
- [x] 正式发布 Sprint 2：**Enterprise RAG v0.2.0**

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| 日志、异常、文档、Docker 测试 | 新 RAG 算法、新 HTTP 接口 |
| Swagger 描述完善 | 流式 `/chat/stream` |
| 引用来源展示优化 | Agent / 多轮对话 |
| Git Tag `v0.2.0` 发布 | Day15+ 新功能 |

**Day14 = 把 Day08~13 的功能「包装成可交付的企业项目」。**

---

## 在 Sprint 2 中的位置

```
Day08~13  功能开发（上传 → 解析 → 切分 → 向量 → 检索 → RAG）  ✅
Day14     企业化优化 + Release v0.2.0                          ← 今天
Day15+    流式 / Agent / 前端 …
```

---

## 优化清单总览

| # | 方向 | 现状 | Day14 目标 |
|---|------|------|------------|
| 1 | 引用来源 | `POST /rag` 已有 `sources[]` | 响应规范 + Swagger 示例 + 空来源处理 |
| 2 | 日志 | 仅 upload 有 logger | 全链路请求日志 + RAG 耗时 |
| 3 | 异常处理 | 少量 HTTPException | 统一 LLM / 检索 / 上传异常 |
| 4 | README | 学习向文档 | 增加 **v0.2.0 企业 RAG** 交付说明 |
| 5 | 接口文档 | `api.md` 较完整 | 与 Swagger 对齐、补 Release 说明 |
| 6 | Swagger | 自动生成，描述简陋 | 完善 `/health` `/upload` `/chat` `/rag` |
| 7 | Docker | Dockerfile 存在，未系统测试 | 构建 + 运行 + 探活验证 |
| 8 | Git Release | 各 Day 分散 commit | 打 Tag `v0.2.0` 并推送 |

---

## 1. 引用来源（Citation）

### 现状（Day13 已有）

`POST /rag` 返回：

```json
{
  "answer": "根据《test.pdf》第1页：……",
  "sources": [
    { "source": "test.pdf", "page": 1, "chunk": 1, "score": 0.69 }
  ]
}
```

### Day14 优化点

| 项 | 说明 |
|----|------|
| 响应契约固定 | `sources` 始终为数组（无命中时 `[]`） |
| Swagger 示例 | 在 `RagResponse` / 路由上补充 `openapi_examples` |
| 可读展示格式 | 文档中约定前端展示：`{source}  Page {page}` |
| 日志记录 | 记录本次 RAG 引用了哪些 source/page |

**不改算法**，只规范 **API 契约 + 文档 + 日志**。

---

## 2. 日志（Logging）

### 现状

- `app/core/logger.py` 仅 upload 使用
- RAG / chat 无请求级日志

### Day14 目标

**A. 请求中间件（建议 `app/core/middleware.py` 或 `main.py`）**

```
INFO  POST /rag  question=如何开启telnet  duration=12.3s  status=200
INFO  POST /chat  duration=2.1s  status=200
INFO  GET  /health  duration=1ms  status=200
```

**B. RAG 链路分段耗时（`rag_pipeline.py`）**

```
INFO  rag search  duration=3.2s  hits=3
INFO  rag llm     duration=45.1s  model=qwen3:4b
INFO  rag total   duration=48.5s  sources=3
```

**C. 规范**

| 级别 | 场景 |
|------|------|
| INFO | 正常请求、上传成功、RAG 完成 |
| WARNING | 检索无结果、LLM 返回空 |
| ERROR | LLM 连接失败、Chroma 异常 |

---

## 3. 异常处理（Exception Handling）

### 现状问题

- `llm.chat()` 失败 → 可能 500 裸栈
- Chroma 未入库 → 检索空，但无明确提示
- 上传非 PDF → 已有 400 ✅

### Day14 目标

**建议新增 `app/core/exceptions.py` + `main.py` 全局处理器：**

| 场景 | HTTP | 响应示例 |
|------|------|----------|
| LLM 不可达（Ollama 未启动） | 503 | `{"detail": "LLM 服务不可用，请检查 Ollama"}` |
| LLM 超时 | 504 | `{"detail": "LLM 请求超时"}` |
| 检索无结果 | 200 | `answer: "知识库中未找到相关内容"`, `sources: []` |
| 上传非 PDF | 400 | 已有 ✅ |
| 未知异常 | 500 | `{"detail": "服务器内部错误"}` + ERROR 日志 |

**原则：** 用户看到友好 `detail`；开发看日志栈。

---

## 4. Swagger（OpenAPI）完善

访问：http://127.0.0.1:8000/docs

### 需完善的接口

| 接口 | tags | summary 示例 |
|------|------|--------------|
| `GET /health` | health | 健康检查探活 |
| `POST /upload` | upload | 上传 PDF 至知识库 |
| `POST /chat` | chat | 纯 LLM 对话（不走知识库） |
| `POST /rag` | rag | 企业知识库 RAG 问答（含来源） |

### 实现方式（FastAPI 原生）

```python
@router.get("/health", summary="健康检查", response_description="服务正常时返回 OK")
@router.post("/upload", summary="上传 PDF", description="...")
@router.post("/chat", summary="AI 聊天", ...)
@router.post("/rag", summary="知识库问答", ...)
```

Pydantic 模型字段补充 `Field(description=...)` 和 `json_schema_extra` 示例。

### 验收

在 `/docs` 中四个接口均有中文说明、请求/响应示例可展开测试。

---

## 5. README 优化

### 新增/调整章节

| 章节 | 内容 |
|------|------|
| **v0.2.0 Release** | Sprint 2 完成功能一览 |
| **企业 RAG 快速体验** | 上传 → 入库 → `/rag` 三步 |
| **API 一览表** | `/health` `/upload` `/chat` `/rag` |
| **性能说明** | 首次慢（Embedding 冷启动）、建议 `qwen3:1.5b` |
| **Docker 部署** | 构建命令 + 访问宿主机 Ollama |
| **版本与 Tag** | `v0.2.0` |

学习进度保留，但 tone 从「学习日志」升级为「可运行产品说明」。

---

## 6. 接口文档（api.md）

与 Swagger **双轨一致**：

- 每个接口：请求 / 响应 / 错误码 / PowerShell 示例
- 新增 **错误响应** 章节（400 / 503 / 504）
- 标注 **v0.2.0** Release 日期与版本

---

## 7. Docker 测试

### 现状

```dockerfile
FROM python:3.13-slim
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Day14 测试清单

```powershell
# 1. 构建
docker build -t ai-assistant:v0.2.0 .

# 2. 运行（连接宿主机 Ollama）
docker run -p 8000:8000 `
  -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 `
  -e MODEL_NAME=qwen3:1.5b `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/uploads:/app/uploads `
  ai-assistant:v0.2.0

# 3. 探活
curl http://127.0.0.1:8000/health

# 4. Swagger
# 浏览器打开 http://127.0.0.1:8000/docs
```

| 检查项 | 期望 |
|--------|------|
| `GET /health` | `{"status":"OK"}` |
| `POST /upload` | 上传 PDF 成功 |
| `POST /chat` | 返回答案（Ollama 可用） |
| `POST /rag` | 返回答案 + sources |
| 数据持久化 | `data/chroma` 挂载卷生效 |

**注意：** 镜像内不含 Ollama / Embedding 模型，需挂载或连宿主机；`sentence-transformers` 首次会下载模型，镜像体积较大——Day14 记录已知限制即可。

---

## 8. Git Release

### 提交

```powershell
git add .
git commit -m "release: v0.2 enterprise rag"
```

### 打 Tag

```powershell
git tag v0.2.0
```

### 推送（确认无误后）

```powershell
git push origin main
git push origin v0.2.0
```

### Release 说明（GitHub Releases 可选）

```markdown
## v0.2.0 — Enterprise RAG

- PDF 上传 / 解析 / 切分 / 向量化 / Chroma 入库
- POST /rag 知识库问答（含引用来源）
- 企业化：日志、异常处理、Swagger、Docker
```

---

## 建议改动文件

| 文件 | 改动 |
|------|------|
| `app/main.py` | 中间件、全局异常、OpenAPI metadata |
| `app/core/exceptions.py` | 自定义异常（新建） |
| `app/core/logger.py` | 可选：request_id、耗时工具 |
| `app/api/*.py` | summary / description / 示例 |
| `app/models/schemas.py` | Field description + examples |
| `app/rag/rag_pipeline.py` | 分段耗时日志 |
| `README.md` | v0.2.0 企业交付说明 |
| `docs/api.md` | 错误码、Release 注记 |
| `docs/Day14.md` | 本文件（完成后打勾） |
| `Dockerfile` | 可选：多阶段构建减小体积（非必须） |

---

## 实现清单（待编码）

| # | 任务 | 状态 |
|---|------|------|
| 1 | 全局异常处理 + 友好错误响应 | ✅ |
| 2 | 请求日志中间件 | ✅ |
| 3 | RAG 分段耗时日志 | ✅ |
| 4 | Swagger 完善（health/upload/chat/rag） | ✅ |
| 5 | sources 契约与文档对齐 | ✅ |
| 6 | README v0.2.0 企业版 | ✅ |
| 7 | api.md 补充错误码 | ✅ |
| 8 | Docker 构建 + 四接口实测 | ✅ |
| 9 | `git commit` + `tag v0.2.0` + push | ⬜ |

---

## 验收标准（Day14 完成定义）

- [x] `/docs` 四个核心接口有清晰中文说明，可在线调试
- [x] `/rag` 返回 `answer` + `sources`，无结果时 `sources: []`
- [x] LLM 不可用时返回 503，非 500 裸错
- [x] 日志可见请求路径、状态码、耗时
- [x] Docker 容器 `GET /health` 通过
- [x] README 含 v0.2.0 企业 RAG 快速开始
- [ ] Git Tag `v0.2.0` 已打并推送

---

## 架构：企业化分层

```
Client（Swagger / curl）
        │
        ▼
┌───────────────────┐
│  FastAPI 网关层    │  ← 中间件日志、全局异常、OpenAPI
├───────────────────┤
│  api/ 路由层       │  ← /health /upload /chat /rag
├───────────────────┤
│  rag/ 业务层       │  ← Day08~13 已有
├───────────────────┤
│  core/ 基础设施    │  ← config / llm / logger / exceptions
└───────────────────┘
```

---

## 收获（完成后填写）

- 功能完成 ≠ 可交付；日志、异常、文档是 enterprise 最后一公里
- Swagger 是 API 的「活文档」，降低联调成本
- Release Tag 标记稳定版本，便于回滚与演示

---

## 下一步

Day15+ — 流式 API、多轮对话、Agent、前端 UI（见 roadmap）
