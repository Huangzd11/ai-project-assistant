# Roadmap

## Sprint 1（v0.1.x）— 基础链路

- [x] Day01 LLM Basic
- [x] Day02 OpenAI API
- [x] Day03 Ollama
- [x] Day04 FastAPI
- [x] Day05 Docker
- [x] Day06 GitHub
- [x] Day07 Review

## Sprint 2（v0.2.x）— Enterprise RAG

- [x] Day08 Upload + Refactor — `feat(upload)` — v0.2.0-alpha
- [x] Day09 PDF Loader — `feat(pdf-loader)` — v0.2.0-alpha2
- [x] Day10 Chunker — `feat(chunker)` — v0.2.0-beta
- [x] Day11 Embedding — `feat(embedding)` — v0.2.0-beta2
- [ ] Day12 ChromaDB — `feat(vector-db)` — v0.2.0-rc
- [ ] Day13 RAG Pipeline — `feat(rag)` — v0.2.0
- [ ] Day14 Test & Release — `release(v0.2.0)`

---

## 后续方向（Day15+）

| 方向 | 计划 |
|------|------|
| 流式 API | 新增 `/chat/stream`，SSE 逐字返回 |
| 多轮对话 | 引入 `session_id`，服务端维护对话历史 |
| Agent | 工具调用、任务编排 |
| 前端 | 简单 Web 聊天界面 |
| 评测 | Prompt 效果对比与指标统计 |

## 工程化改进

| 项 | 说明 |
|----|------|
| 统一虚拟环境 | 共享依赖管理，monorepo 结构 |
| `.env.example` | 提供配置模板，避免密钥泄露 |
| 错误处理 | 统一超时、模型不可用等异常响应 |
| 日志监控 | 请求耗时、Token 用量统计 |
| docker-compose | API + Ollama 一键编排 |
| CI/CD | 自动化测试与镜像构建 |

## 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Ollama 文档](https://github.com/ollama/ollama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [阿里云百炼](https://bailian.console.aliyun.com/)
