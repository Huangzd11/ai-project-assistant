# AI Project Assistant

30 天 AI 技术项目经理实战学习项目。从 LLM 基础概念出发，逐步掌握云端 API 调用、本地模型部署、Web API 封装与容器化部署等核心技能。

仓库地址：[https://github.com/Huangzd11/ai-project-assistant](https://github.com/Huangzd11/ai-project-assistant)

---

## 项目简介

本项目是一个 **渐进式学习仓库**，采用 monorepo 结构，将每日实战代码与文档统一管理。目前已完成 **Sprint 3（v0.3.0 Enterprise AI Agent）**，Day01 ~ Day21 全部收官。

- LLM 基础与 Prompt 设计（Day01）
- OpenAI 兼容 API 多轮对话（Day02）
- 本地 Ollama 调用（Day03）
- FastAPI HTTP 服务（Day04）
- Docker 容器化（Day05）
- GitHub 托管与开发规范（Day06）
- 阶段回顾与查漏补缺（Day07）
- 项目重构 + PDF 上传（Day08）
- PDF 按页解析为 JSON（Day09）
- LangChain 文本 Chunk 切分（Day10）
- 文本 Embedding 向量化（Day11）
- Chroma 向量入库与 Top-K 检索（Day12）
- RAG 知识库问答（Day13，检索 + LLM + 来源溯源）
- 企业化优化与 Release（Day14，日志 / 异常 / Swagger / Docker）
- Agent Core + RAG 工具调用（Day15，Planner / Executor / POST /agent）
- Tool Registry 多工具（Day16，PDF / Calculator / RAG）
- 会话 Memory（Day17，`session_id` 多轮对话 + Long facts）
- MCP Client 外部工具（Day18，连接 MCP Server 并桥接进 Tool Registry）
- Filesystem MCP 读项目文件（Day19，自然语言「看看 README」）
- Enterprise Workflow（Day20，RAG / MCP / Chat 统一路由 + `workflow` 可观测）
- Sprint Review + Release（Day21，v0.3.0 交付）

适合希望系统学习 AI 应用开发的开发者，尤其是想从技术项目经理视角理解 LLM 工程化落地的同学。

---

## v0.3.0 Release — 企业 AI Agent 快速体验

**Sprint 3 核心能力：** 多轮 Memory · 企业 RAG · Tool Calling · MCP · Workflow 编排

```powershell
# 1. 启动（Ollama 或通义千问，见 .env）
ollama serve
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. 健康检查（含版本号）
Invoke-RestMethod http://127.0.0.1:8000/health

# 3. Agent — 总结 PDF（需知识库已入库）
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post `
  -ContentType "application/json" -Body '{"message":"帮我总结 test.pdf"}'

# 4. Agent — 读 README（.env: MCP_ENABLED=true，需 Node.js）
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post `
  -ContentType "application/json" -Body '{"message":"README 里面写了什么"}'

# 5. 多轮记忆
Invoke-RestMethod ... -Body '{"message":"我是项目经理","session_id":"work-001"}'
Invoke-RestMethod ... -Body '{"message":"我是谁","session_id":"work-001"}'
```

**架构（v0.3.0）：**

```
用户 → POST /agent → Workflow → Tool（RAG / MCP / Calculator）→ Memory + LLM → Answer
```

| 能力 | 说明 |
|------|------|
| Workflow | 自动选择 chat / rag / filesystem / calculator |
| Memory | `session_id` 多轮对话 |
| RAG | 知识库总结 PDF，带 sources |
| MCP | Filesystem 读项目文件 |
| 可观测 | 响应 `workflow.intent` + `route` |

**Docker Compose（v0.4.0-beta · 推荐）：**

```powershell
# 1. 配置 .env（通义千问 Key 等，见 .env.example）
cp .env.example .env

# 2a. 一键启动（Nginx :80 + API + Chroma）
docker compose up -d --build
docker compose ps
Invoke-RestMethod http://localhost/health
# 浏览器 http://localhost  → Web UI
# 浏览器 http://localhost/docs → Swagger

# 2b. 本地 Ollama（可选 profile）
docker compose --profile local-llm up -d --build
.\scripts\ollama-pull.ps1

# 3. 可选 Redis
docker compose --profile redis up -d

# 4. Vite 开发模式（需容器 API 暴露 8000）
docker compose -f docker-compose.yml -f docker-compose.dev-api.yml up -d api chroma
cd frontend && npm run dev
```

详见 [docs/Day22.md](docs/Day22.md)、[docs/Day23.md](docs/Day23.md)、[docs/Day24.md](docs/Day24.md)。

**单容器 Docker（v0.3.0）：**

```powershell
docker build -t ai-assistant:v0.3.0 .
docker run -p 8000:8000 `
  -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 `
  -e MCP_ENABLED=false `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/uploads:/app/uploads `
  ai-assistant:v0.3.0
```

详见 [docs/Day21.md](docs/Day21.md)、[docs/Day21_1.md](docs/Day21_1.md)、[docs/CHANGELOG.md](docs/CHANGELOG.md)。

### Web 聊天界面（frontend · React）

简易 Web UI：聊天、PDF 上传、引用来源、工具 / Workflow 状态展示。

```powershell
# 终端 1：后端
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 终端 2：前端
cd frontend
npm install
npm run dev
```

浏览器打开 [http://127.0.0.1:5173](http://127.0.0.1:5173)。开发模式通过 Vite 代理访问 API；后端已启用 CORS。

---

## v0.2.0 Release — 企业 RAG 快速体验

**四步跑通知识库问答：**

```powershell
# 1. 启动服务（需 Ollama）
ollama serve
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. 上传 PDF（Swagger 或 curl）
curl.exe -X POST http://127.0.0.1:8000/upload -F "file=@uploads/test.pdf"

# 3. 入库（解析 → 切分 → 向量 → Chroma，按模块执行）
python -c "from app.rag.pdf_loader import parse_pdf; parse_pdf('uploads/test.pdf')"
python -c "from app.rag.chunker import chunk_pdf; chunk_pdf('data/parsed/test.json')"
python -c "from app.rag.embedder import embed_chunks; embed_chunks('data/chunks/test.json')"
python -c "from app.rag.vector_store import index_chunks; print(index_chunks('data/chunks/test.json'))"

# 4. RAG 问答
Invoke-RestMethod -Uri http://127.0.0.1:8000/rag -Method Post -ContentType "application/json" -Body '{"question":"如何开启 telnet？"}'
```

**核心 API：**

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/upload` | POST | 上传 PDF |
| `/chat` | POST | 纯 LLM 对话 |
| `/rag` | POST | 知识库问答 + sources |
| `/agent` | POST | Agent 规划 + 工具调用 + 总结（Day15） |

**性能说明：** 首次 `/rag` 较慢（Embedding 模型冷启动 + LLM 生成）。可换 `qwen3:1.5b` 加速 LLM 部分；生产环境建议关闭 `--reload`。

**Docker 部署（v0.2.0）：**

```powershell
docker build -t ai-assistant:v0.2.0 .
docker run -p 8000:8000 `
  -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 `
  -e MODEL_NAME=qwen3:1.5b `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/uploads:/app/uploads `
  ai-assistant:v0.2.0
```

Git Tag：`v0.2.0`

---



## 技术栈


| 类别       | 技术                                | 说明                |
| -------- | --------------------------------- | ----------------- |
| 语言       | Python 3.10+                      | 全部实战代码            |
| LLM 客户端  | OpenAI Python SDK                 | 统一调用云端 / 本地兼容接口   |
| 云端模型     | 通义千问（DashScope）                   | Day02 默认方案        |
| 本地模型     | Ollama + qwen3:4b                 | Day03、Day04 默认方案  |
| 配置管理     | python-dotenv                     | 环境变量加载            |
| Web 框架   | FastAPI                           | HTTP API 服务       |
| ASGI 服务器 | Uvicorn                           | 运行 FastAPI        |
| 数据校验     | Pydantic                          | 请求 / 响应模型         |
| 容器化      | Docker                            | 镜像构建与部署           |
| PDF 解析   | PyMuPDF                           | Day09 按页提取文本      |
| 文本切分     | LangChain Text Splitters          | Day10 Chunk 切分    |
| 向量化      | sentence-transformers / DashScope | Day11 Embedding   |
| 向量库      | ChromaDB                          | Day12 持久化 + 相似度检索 |


---



## 当前功能



### Prompt 练习（Day01）

- System Prompt、Few-shot、Temperature 对比实验

运行：`python examples/prompt_demo.py`

### 命令行对话（Day02）

- 从 `.env` 读取 API Key、Base URL、模型名
- 维护 `messages` 列表实现多轮对话
- 流式逐字输出（`stream=True`）

运行：`python examples/chat_demo.py`

### 本地 Ollama 调用（Day03）

- 通过 `http://127.0.0.1:11434/v1` 连接本地 Ollama
- OpenAI SDK 零改动接入本地模型

运行：`python examples/ollama_demo.py`

### 企业知识库 — PDF 上传（Day08 · v0.2.0-alpha）


| 接口        | 方法   | 说明                    |
| --------- | ---- | --------------------- |
| `/upload` | POST | 上传 PDF，保存至 `uploads/` |


```json
{ "filename": "linux.pdf", "size": "8MB" }
```

在 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 中测试上传。

详见 [docs/Day08.md](docs/Day08.md)。

### PDF 解析（Day09 · v0.2.0-alpha2）

- PyMuPDF 按页提取 PDF 纯文本
- 输出 `data/parsed/{name}.json`（`source`、`total_pages`、`pages`）

```powershell
python -c "from app.rag.pdf_loader import parse_pdf; print(parse_pdf('uploads/test.pdf'))"
```

详见 [docs/Day09.md](docs/Day09.md)。

### Chunk 切分（Day10 · v0.2.0-beta）

- LangChain `RecursiveCharacterTextSplitter` 按页切分
- 可配置 `chunk_size` / `chunk_overlap`
- 输出 `data/chunks/{name}.json`（`chunk_id`、`page`、`content`）

```powershell
python -c "from app.rag.chunker import chunk_pdf; print(chunk_pdf('data/parsed/test.json'))"
```

详见 [docs/Day10.md](docs/Day10.md)。

### Embedding 向量化（Day11 · v0.2.0-beta2）

- 本地 `BAAI/bge-small-zh-v1.5` 或云端通义 `text-embedding-v3`
- 通过 `EMBEDDING_PROVIDER` 切换 `local` / `dashscope`
- 输出 `data/vectors/{name}.json`（`chunk`、`page`、`embedding`）

```powershell
python -c "from app.rag.embedder import embed_chunks; print(embed_chunks('data/chunks/test.json'))"
```

详见 [docs/Day11.md](docs/Day11.md)。

### 向量检索（Day12 · v0.2.0-rc）

- Chroma 持久化存储，cosine 相似度检索
- **纯检索**：Question → Embedding → Top5（不接 LLM）
- 入库合并 `chunks` + `vectors`，检索返回原文 + 分数

```powershell
python -c "from app.rag.vector_store import index_chunks; print(index_chunks('data/chunks/test.json'))"
python -c "from app.rag.vector_store import search; print(search('telnet')['results'][0])"
```

详见 [docs/Day12.md](docs/Day12.md)。

### RAG 知识库问答（Day13 · v0.2.0）

- 完整链路：Question → Search → Prompt → LLM → Answer
- `POST /rag` 返回答案与 `sources`（文档名 + 页码）
- `POST /chat` 保持纯 LLM 对话不变

```powershell
# 模块调用
python -c "from app.rag.rag_pipeline import rag_answer; import json; print(json.dumps(rag_answer('如何开启 telnet'), ensure_ascii=False, indent=2))"
```

```json
{ "question": "...", "answer": "根据《test.pdf》第1页：……", "sources": [{ "source": "test.pdf", "page": 1, "score": 0.72 }] }
```

详见 [docs/Day13.md](docs/Day13.md)。

### 企业化优化（Day14 · v0.2.0）

- 请求日志中间件（路径 / 耗时 / 状态码）
- LLM 异常友好响应（503 / 504）
- RAG 分段耗时日志 + 引用来源记录
- Swagger 完善：`/health` `/upload` `/chat` `/rag`
- Docker 构建验证

详见 [docs/Day14.md](docs/Day14.md)。

### Agent Core（Day15 · v0.3-alpha）

- Planner 规则分解：含 pdf/总结 → 调用 `rag_query`
- Executor：`plan` → Tool → Observation → LLM 总结
- `POST /agent` 返回 `answer` + `plan` + `sources`

```powershell
python -c "from app.agent import run_agent; import json; print(json.dumps(run_agent('总结 test.pdf'), ensure_ascii=False, indent=2))"
```

详见 [docs/Day15.md](docs/Day15.md)。

### Tool Registry（Day16 · v0.3-alpha2）

- `agent/tools/registry.py`：工具注册表，`register()` / `run()`
- 三工具：`pdf_read` / `rag_query` / `calculator`
- 新增工具只需注册，不改 Executor

```powershell
python -c "import app.agent.tools; from app.agent.tools.registry import list_names; print(list_names())"
```

详见 [docs/Day16.md](docs/Day16.md)。

### 会话 Memory（Day17 · v0.3-beta）

- Short Memory：`data/conversations/{session_id}.json`
- Long Memory：规则提取「我是xxx」→ facts 注入 system
- `POST /agent` 增加可选 `session_id`

```powershell
# 多轮：同一 session_id 连续请求
Invoke-RestMethod ... -Body '{"message":"我是项目经理","session_id":"work-001"}'
Invoke-RestMethod ... -Body '{"message":"我是谁？","session_id":"work-001"}'
```

详见 [docs/Day17.md](docs/Day17.md)。

### MCP Client（Day18 · v0.3-beta2）

- `app/mcp/client.py`：stdio 连接 MCP Server，`list_tools` / `call_tool`
- `app/mcp/bridge.py`：动态注册 `mcp_*` 到 Tool Registry
- Planner 支持显式调用：`mcp read_file README.md`
- `GET /mcp/status`、`GET /mcp/tools` 调试接口

```powershell
# .env 中 MCP_ENABLED=true，需 Node.js（npx）
python -m uvicorn app.main:app --reload
Invoke-RestMethod -Uri http://127.0.0.1:8000/mcp/status
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post -ContentType "application/json" -Body '{"message":"mcp echo hello"}'
```

详见 [docs/Day18.md](docs/Day18.md)。

### Filesystem MCP（Day19 · v0.3-rc）

- 默认 Server：`@modelcontextprotocol/server-filesystem`
- `MCP_FILESYSTEM_ROOT` 沙箱根目录
- Planner：「看看 README」→ `mcp_read_file`；「列出 docs 目录」→ `mcp_list_directory`

```powershell
# .env: MCP_ENABLED=true
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post -ContentType "application/json" -Body '{"message":"帮我看看 README 写了什么"}'
```

详见 [docs/Day19.md](docs/Day19.md)。

### Enterprise Workflow（Day20 · v0.3）

- `app/agent/workflow.py`：`classify` + `build_workflow` 统一意图路由
- `POST /agent` 响应增加 `workflow`（intent / need_tool / route / reason）
- 「总结 Linux.pdf」→ RAG；「README 写了什么」→ Filesystem MCP

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post -ContentType "application/json" -Body '{"message":"帮我总结 Linux.pdf"}'
```

详见 [docs/Day20.md](docs/Day20.md)。

### HTTP API 服务（Day04）


| 接口        | 方法   | 说明            |
| --------- | ---- | ------------- |
| `/`       | GET  | 服务欢迎          |
| `/health` | GET  | 健康检查          |
| `/models` | GET  | 当前模型配置        |
| `/chat`   | POST | AI 聊天         |
| `/upload` | POST | PDF 上传（Day08） |
| `/rag` | POST | 知识库 RAG 问答（Day13） |
| `/agent` | POST | Agent 问答（Day15） |
| `/mcp/status` | GET | MCP 状态（Day18） |


运行：`python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`  
交互文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Docker 部署（Day05）

- 基于 `Dockerfile` 一键构建镜像
- 支持容器访问宿主机 Ollama

详见 [docs/Day05.md](docs/Day05.md)。

### GitHub 与项目规范（Day06）

- 代码托管于 [GitHub](https://github.com/Huangzd11/ai-project-assistant)
- 完善 README、方案设计、架构图等文档体系
- 建立 [开发规范](docs/development-standards.md)

详见 [docs/Day06.md](docs/Day06.md)。

### 阶段回顾（Day07）

- 回顾 Day01 ~ Day06 知识体系
- 补齐示例脚本与 `.dockerignore`
- 确认 Day08 RAG 前置条件

详见 [docs/Day07.md](docs/Day07.md)。

---



## 学习进度

完整路线见 [docs/roadmap.md](docs/roadmap.md)。

- [x] Day01 LLM Basic
- [x] Day02 OpenAI API
- [x] Day03 Ollama
- [x] Day04 FastAPI
- [x] Day05 Docker
- [x] Day06 GitHub
- [x] Day07 Review
- [x] Day08 Upload + Refactor
- [x] Day09 PDF Loader
- [x] Day10 Chunker
- [x] Day11 Embedding
- [x] Day12 ChromaDB
- [x] Day13 RAG Pipeline
- [x] Day14 Enterprise Release
- [x] Day15 Agent Core
- [x] Day16 Tool Registry
- [x] Day17 Memory
- [x] Day18 MCP Client
- [x] Day19 Filesystem MCP
- [x] Day20 Enterprise Workflow
- [x] Day21 Sprint Review — v0.3.0

---



## 项目结构

完整代码地图见 **[docs/CODEMAP.md](docs/CODEMAP.md)**（含每个文件的 Day 来源与逻辑说明）。

```
ai-project-assistant/
│
├── app/                              # Day04 创建 · Day08 重构
│   ├── main.py                       # FastAPI 入口
│   ├── api/
│   │   ├── health.py                 # Day04 — / 、/health
│   │   ├── chat.py                   # Day04 — /chat 、/models
│   │   ├── upload.py                 # Day08 — /upload
│   │   ├── rag.py                    # Day13 — /rag
│   │   ├── agent.py                  # Day15 — /agent
│   │   └── mcp.py                    # Day18 — /mcp/status
│   ├── agent/                        # Day15/16 — Planner / Executor / Tools
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── memory.py                 # Day17 — 会话记忆
│   │   ├── prompt.py
│   │   └── tools/                    # Day16 — registry + pdf/rag/calculator
│   │       ├── registry.py
│   │       ├── rag_tool.py
│   │       ├── pdf_tool.py
│   │       └── calculator.py
│   ├── mcp/                          # Day18 — MCP Client
│   │   ├── client.py
│   │   ├── bridge.py
│   │   └── runtime.py
│   ├── core/
│   │   ├── config.py                 # Day02/04/08 — 环境配置
│   │   ├── llm.py                    # Day02/04 — LLM 调用
│   │   ├── logger.py                 # Day08/14 — 日志
│   │   ├── middleware.py             # Day14 — 请求日志中间件
│   │   ├── exceptions.py             # Day14 — 统一异常
│   │   └── files.py                  # Day08 — 文件工具
│   ├── models/
│   │   └── schemas.py                # Day04/08 — Pydantic 模型
│   └── rag/                          # Day09+ RAG
│       ├── pdf_loader.py             # Day09 — PDF 解析
│       ├── chunker.py                # Day10 — Chunk 切分
│       ├── embedder.py               # Day11 — Embedding 向量化
│       ├── vector_store.py           # Day12 — Chroma 入库 + 检索
│       └── rag_pipeline.py           # Day13 — RAG 问答
│
├── examples/                         # Day01~03 学习示例
│   ├── prompt_demo.py                # Day01
│   ├── chat_demo.py                  # Day02
│   └── ollama_demo.py                # Day03
│
├── uploads/                          # Day08 — 原始 PDF
├── data/
│   ├── parsed/                       # Day09 — 解析 JSON
│   ├── chunks/                       # Day10 — Chunk JSON
│   ├── vectors/                      # Day11 — Vector JSON
│   └── chroma/                       # Day12 — Chroma 持久化
├── tests/                            # Day14 测试（预留）
│
├── docs/                             # 文档与工作日志
│   ├── CODEMAP.md                    # 代码地图（按 Day 索引）
│   ├── Day01.md ~ Day21.md
│   ├── api.md / roadmap.md
│   ├── solution-design.md
│   ├── development-standards.md
│   └── architecture.png
│
├── requirements.txt                  # 依赖（按 Day 注释）
├── Dockerfile                        # Day05 容器化
├── .dockerignore                     # Day07
├── .env.example
└── README.md
```


| 层级    | 目录            | 职责                    |
| ----- | ------------- | --------------------- |
| 接口层   | `app/api/`    | HTTP 路由，不含业务细节        |
| 核心层   | `app/core/`   | 配置、LLM、日志、文件工具        |
| 契约层   | `app/models/` | 请求/响应 Pydantic 模型     |
| RAG 层 | `app/rag/`    | 文档解析→切分→向量→检索（Day09+） |
| 示例层   | `examples/`   | 独立学习脚本，按 Day 组织       |


---



## 快速开始



### 1. 安装依赖

```powershell
pip install -r requirements.txt
copy .env.example .env    # 按需填写 API Key
```



### 2. 命令行对话（云端 API）

在 [阿里云百炼](https://bailian.console.aliyun.com/) 获取 API Key，写入 `.env`：

```
OPENAI_API_KEY=你的密钥
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-plus
```

```powershell
python examples/chat_demo.py
```



### 3. HTTP API 服务（本地 Ollama）

```powershell
ollama pull qwen3:4b
ollama serve
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**上传 PDF：** 打开 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) ，使用 `POST /upload` 选择文件。

### 4. PDF 解析（Day09）

```powershell
python -c "from app.rag.pdf_loader import parse_pdf; print(parse_pdf('uploads/test.pdf'))"
```



### 5. Chunk 切分（Day10）

```powershell
python -c "from app.rag.chunker import chunk_pdf; print(chunk_pdf('data/parsed/test.json'))"
```



### 6. Embedding 向量化（Day11）

```powershell
python -c "from app.rag.embedder import embed_chunks; print(embed_chunks('data/chunks/test.json'))"
```



### 7. 向量入库与检索（Day12）

```powershell
python -c "from app.rag.vector_store import index_chunks; print(index_chunks('data/chunks/test.json'))"
python -c "from app.rag.vector_store import search; print(search('telnet')['results'][0])"
```



### 8. RAG 知识库问答（Day13）

```powershell
python -c "from app.rag.rag_pipeline import rag_answer; import json; print(json.dumps(rag_answer('telnet'), ensure_ascii=False, indent=2))"
```

### 9. Docker 部署（v0.2.0）

```powershell
docker build -t ai-assistant:v0.2.0 .
docker run -p 8000:8000 `
  -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 `
  -e MODEL_NAME=qwen3:1.5b `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/uploads:/app/uploads `
  ai-assistant:v0.2.0

curl http://127.0.0.1:8000/health
```

> 镜像内不含 Ollama；Embedding 模型首次请求会从 HuggingFace 下载。

---



## 环境变量


| 变量名                   | 默认值                         | 说明                    |
| --------------------- | --------------------------- | --------------------- |
| `OPENAI_API_KEY`      | `ollama`                    | API 密钥                |
| `OPENAI_BASE_URL`     | `http://127.0.0.1:11434/v1` | 兼容 API 地址             |
| `MODEL_NAME`          | `qwen3:4b`                  | 模型名称                  |
| `PROVIDER`            | `ollama`                    | 提供方标识                 |
| `SYSTEM_PROMPT`       | `你是一名AI技术项目经理.`             | 系统提示词                 |
| `REQUEST_TIMEOUT`     | `600`                       | 请求超时（秒）               |
| `UPLOAD_DIR`          | `uploads`                   | PDF 上传保存目录            |
| `PARSED_DIR`          | `data/parsed`               | PDF 解析 JSON 输出目录      |
| `CHUNKS_DIR`          | `data/chunks`               | Chunk JSON 输出目录       |
| `CHUNK_SIZE`          | `500`                       | 文本块大小（字符）             |
| `CHUNK_OVERLAP`       | `50`                        | 块间重叠字符数               |
| `VECTORS_DIR`         | `data/vectors`              | 向量 JSON 输出目录          |
| `EMBEDDING_PROVIDER`  | `local`                     | `local` 或 `dashscope` |
| `EMBEDDING_MODEL`     | `BAAI/bge-small-zh-v1.5`    | Embedding 模型名         |
| `EMBEDDING_DIMENSION` | `512`                       | 云端向量维度                |
| `CHROMA_DIR`          | `data/chroma`               | Chroma 持久化目录          |
| `CHROMA_COLLECTION`   | `knowledge`                 | Collection 名称         |
| `SEARCH_TOP_K`        | `5`                         | 检索返回条数                |
| `MCP_ENABLED`         | `false`                     | 是否启用 MCP Client        |
| `MCP_FILESYSTEM_ROOT` | 项目根目录                     | Filesystem 沙箱路径         |
| `MCP_SERVER_COMMAND`  | `npx`                       | MCP Server 启动命令         |
| `RAG_SYSTEM_PROMPT`   | （见 config.py）               | RAG 专用 system 提示词     |


---



## 文档


| 文档                                                             | 说明                 |
| -------------------------------------------------------------- | ------------------ |
| [docs/CODEMAP.md](docs/CODEMAP.md)                             | 代码地图（按 Day 索引每个文件） |
| [docs/development-standards.md](docs/development-standards.md) | AI 项目开发规范          |
| [docs/solution-design.md](docs/solution-design.md)             | AI 方案设计（技术选型与演进路线） |
| [docs/api.md](docs/api.md)                                     | HTTP 接口详细说明        |
| [docs/roadmap.md](docs/roadmap.md)                             | 学习路线与后续规划          |
| [docs/CHANGELOG.md](docs/CHANGELOG.md)                             | 版本发布说明             |
| [docs/Day01.md](docs/Day01.md) ~ [Day21.md](docs/Day21.md)     | 每日工作日志             |


---



## 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Ollama 文档](https://github.com/ollama/ollama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [阿里云百炼](https://bailian.console.aliyun.com/)

