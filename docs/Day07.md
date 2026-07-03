# Day07 — Review（Day01 ~ Day06 回顾）

## 学习目标

- [x] 回顾 Day01 ~ Day06 核心知识点
- [x] 检查代码、文档、示例是否一致
- [x] 查漏补缺，修复遗留问题
- [x] 确认 Day08 RAG 的前置条件

---

## 回顾清单

| Day | 主题 | 核心产出 | 状态 |
|-----|------|----------|------|
| Day01 | LLM Basic | Prompt 概念：system / few-shot / temperature | ✅ 已补 `examples/prompt_demo.py` |
| Day02 | OpenAI API | 多轮对话 + 流式输出 | ✅ `examples/chat_demo.py` |
| Day03 | Ollama | 本地模型 OpenAI 兼容调用 | ✅ 已补 `examples/ollama_demo.py` |
| Day04 | FastAPI | HTTP API + 分层架构 | ✅ `app.py` / `llm.py` / `config.py` / `models.py` |
| Day05 | Docker | 镜像构建与部署 | ✅ `Dockerfile`，已补 `.dockerignore` |
| Day06 | GitHub | 仓库托管 + README + 开发规范 | ✅ 文档体系完整 |

---

## 查漏补缺记录

### 发现的问题

| # | 问题 | 处理 |
|---|------|------|
| 1 | Day01 仅有概念文档，无实战示例 | 新增 `examples/prompt_demo.py` |
| 2 | Day03 代码仅在文档中，无独立脚本 | 新增 `examples/ollama_demo.py`，更新 Day03.md |
| 3 | Docker 构建复制了 docs/examples 等无关文件 | 新增 `.dockerignore` 减小镜像体积 |
| 4 | Day01.md 状态仍为「待补充」 | 更新为已完成，指向 prompt_demo |
| 5 | examples 目录仅有 chat_demo | README / 项目结构同步更新 |

### 暂未处理（留待 Day08+）

| 项 | 说明 |
|----|------|
| 流式 HTTP API | `/chat/stream` SSE 端点 |
| 多轮会话 | 服务端 `session_id` 历史管理 |
| 错误处理 | LLM 超时、模型不可用的统一异常响应 |
| 自动化测试 | `tests/` 目录与 CI |
| requirements 版本锁定 | 生产环境建议 pin 版本 |

---

## 知识体系串联

```
Day01 Prompt 设计
    ↓  messages 结构
Day02 OpenAI API 调用（云端）
    ↓  同一 SDK，切换 base_url
Day03 Ollama 本地推理
    ↓  封装为 chat()
Day04 FastAPI HTTP 服务
    ↓  Dockerfile
Day05 Docker 部署
    ↓  GitHub + 文档规范
Day06 工程化托管
    ↓
Day08 RAG（下一步）
```

**关键认知**：OpenAI Compatible API 是贯穿 Day02 ~ Day04 的核心抽象，切换 `base_url` 即可在云端与本地之间迁移。

---

## 自检命令

```powershell
# Day01 — Prompt 练习（需配置云端 .env）
python examples/prompt_demo.py

# Day02 — 命令行对话
python examples/chat_demo.py

# Day03 — Ollama 流式（需 ollama serve）
python examples/ollama_demo.py

# Day04 — HTTP API
uvicorn app:app --reload --host 127.0.0.1 --port 8000

# Day05 — Docker
docker build -t ai-chat:v1 .
docker run -p 8000:8000 -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 ai-chat:v1
```

---

## 收获

- 前 6 天已形成 **Prompt → API → 本地模型 → HTTP 服务 → 容器 → GitHub** 完整链路
- 文档（工作日志 + 方案设计 + 开发规范）与代码同步，便于后续 RAG 扩展
- 示例脚本按 Day 组织，降低回顾与复习成本

## 下一步

Day08 RAG — 文档切片、向量检索、知识库问答。
