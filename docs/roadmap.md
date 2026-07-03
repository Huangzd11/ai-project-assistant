# 后续规划

## 学习路线（Day06+）

| 方向 | 计划 |
|------|------|
| Day01 | 补充 LLM 基础概念与 Prompt 练习 |
| 流式 API | 新增 `/chat/stream`，SSE 逐字返回 |
| 多轮对话 | 引入 `session_id`，服务端维护对话历史 |
| RAG | 文档切片、向量检索、知识库问答 |
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
