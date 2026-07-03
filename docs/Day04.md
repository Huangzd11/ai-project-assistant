# Day04 — FastAPI HTTP 服务

## 目标

- 将 LLM 能力封装为 HTTP API
- 使用 Pydantic 定义请求/响应模型
- 分层组织代码：`config` / `models` / `llm` / `app`

## 模块职责

| 文件 | 职责 |
|------|------|
| `config.py` | 读取环境变量（API、模型、超时等） |
| `models.py` | 定义 `ChatRequest`、`ChatResponse` 等 Pydantic 模型 |
| `llm.py` | 封装 OpenAI 客户端与 `chat()` 函数 |
| `app.py` | 注册 HTTP 路由 |

## 启动方式

**前置条件：** Ollama 已启动（或已配置云端 API）。

```powershell
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

访问地址：

- 服务根路径：http://127.0.0.1:8000/
- 交互式文档：http://127.0.0.1:8000/docs

## 接口文档

详见 [api.md](api.md)。

## 下一步

容器化部署见 [Day05.md](Day05.md)。
