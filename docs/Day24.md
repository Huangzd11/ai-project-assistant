# Day24 — 日志 + 配置管理设计

> 版本：**v0.4-beta** | 前置：**Day14 日志/异常**、**Day23 Nginx 部署**  
> **定位：工程化可观测 — 分级日志、统一配置、Request ID 贯穿请求链路**

## 学习目标

- [ ] 理解 **INFO / WARNING / ERROR** 三级日志的适用场景与写法
- [ ] 掌握 **配置分层**：`config/` 默认值 + `.env` 密钥与环境覆盖
- [ ] 实现 **Request ID**：每个 HTTP 请求唯一标识，便于排错串联
- [ ] 了解 **Trace ID** 在分布式链路追踪中的角色（本日不接入 OpenTelemetry）
- [ ] 能将 **错误日志** 单独落盘，与业务 INFO 分离

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| `logs/` 目录 + 文件落盘（`app.log` / `error.log`） | ELK / Loki / Datadog 接入 |
| `config/` 默认配置 + `.env` 覆盖 | K8s ConfigMap / Secret |
| Request ID 中间件 + 响应头 `X-Request-ID` | 全链路 OpenTelemetry SDK |
| Trace ID 概念说明 + 可选透传头 | Jaeger / Zipkin 部署 |
| 重构 `logger.py`、增强 `middleware.py` | 大改 `config.py` 全部变量为 Pydantic（可渐进） |
| Docker Compose 挂载 `logs/` 卷 | 日志轮转 Daemon（logrotate 仅文档说明） |

**Day24 核心成果：** 任意一次用户请求，可通过 **Request ID** 在 `logs/app.log` 中串联「进入 → 业务 → 耗时 → 退出」；严重错误在 `logs/error.log` 单独可查。

---

## 以前 vs 以后

### Day14 ~ Day23（当前）

```
配置：
  app/core/config.py  → load_dotenv() + os.getenv（单文件 100+ 行）
  .env                → 密钥 + 全部环境变量混在一起

日志：
  logging.basicConfig → 仅输出到 stdout（控制台）
  格式：2026-07-09 16:00:00 [INFO] ai-project-assistant: POST /agent ...
  无 request_id；Docker 重启后控制台日志丢失
```

问题：

- 配置项越来越多，`.env` 与代码常量边界模糊
- 生产环境需要 **落盘** 才能事后排查
- 多行日志无法关联同一次请求
- ERROR 混在 INFO 流里，告警不便筛选

### Day24（目标）

```
配置：
  config/settings.yaml   → 非敏感默认值（日志级别、目录路径）
  .env                   → 密钥 + 环境覆盖（APP_ENV=dev|prod）
  app/core/config.py     → 读取合并后的 Settings（渐进迁移）

日志：
  logs/app.log           → INFO 及以上（请求、RAG、Agent）
  logs/error.log         → 仅 ERROR（LLM 失败、未捕获异常）
  每条带 request_id=abc-123
  响应头：X-Request-ID: abc-123
```

---

## 目录结构（新增）

```
ai-project-assistant/
├── config/
│   ├── settings.yaml       # 默认配置（可提交 Git）
│   ├── logging.yaml        # 日志 handler / formatter 定义
│   └── README.md           # 配置说明（可选，实现日再写）
├── logs/
│   ├── .gitkeep            # 保留目录，日志文件不入库
│   ├── app.log             # 运行时生成
│   └── error.log           # 运行时生成
├── .env                    # 本地密钥（已在 .gitignore）
└── .env.example            # 模板 + Day24 新增项
```

---

## 配置分层设计

### 优先级（高 → 低）

```
环境变量 / .env  >  config/settings.yaml  >  代码内置默认值
```

### `config/settings.yaml` 草案

```yaml
app:
  name: ai-project-assistant
  env: dev          # dev | prod，可由 APP_ENV 覆盖

logging:
  level: INFO       # DEBUG | INFO | WARNING | ERROR
  dir: logs
  app_file: app.log
  error_file: error.log
  console: true     # 开发时仍打控制台
  format: text    # text | json（Day24 默认 text，便于阅读）

paths:
  upload_dir: uploads
  memory_dir: data/conversations
  chroma_dir: data/chroma
```

### `.env` 职责（延续 + 扩展）

| 类别 | 示例 | 存放位置 |
|------|------|----------|
| 密钥 | `OPENAI_API_KEY` | **仅 `.env`** |
| 环境标识 | `APP_ENV=prod` | `.env` |
| 日志级别 | `LOG_LEVEL=DEBUG` | `.env` 覆盖 yaml |
| 连接串 | `CHROMA_HOST`、`REDIS_URL` | `.env`（Compose 注入） |
| 业务调参 | `MEMORY_MAX_TURNS` | yaml 默认，`.env` 可覆盖 |

### `app/core/config.py` 迁移策略（渐进）

**Day24 不一次性重写全部 `os.getenv`。**

| 阶段 | 内容 |
|------|------|
| Step 1 | 新增 `load_settings()` 读取 yaml + env，导出 `LOG_*`、`APP_ENV` |
| Step 2 | 现有 `OPENAI_API_KEY` 等仍用 `os.getenv`（兼容） |
| Step 3 | （可选后续）逐步迁入 Pydantic `BaseSettings` |

```python
# 设计示意（实现日）
from app.core.settings import settings

LOG_LEVEL = settings.logging.level
LOG_DIR = settings.logging.dir
```

---

## 日志架构

### 三级日志场景

| 级别 | 何时使用 | 本项目示例 |
|------|----------|------------|
| **INFO** | 正常业务流程、可审计 | 请求完成、上传成功、Agent 工具调用、RAG 命中 |
| **WARNING** | 可恢复、需关注 | LLM 空响应、RAG 无结果、Memory 加载失败 |
| **ERROR** | 失败、需排查 | LLM 超时/连接失败、MCP 启动失败、未捕获 500 |

### 输出目标

```
                    ┌─────────────┐
  logger.info()  ──►│  Console    │  （LOG_CONSOLE=true）
                    ├─────────────┤
                    │ logs/app.log│  INFO+
                    └─────────────┘

  logger.error() ──►┌─────────────┐
                    │ logs/app.log│
                    ├─────────────┤
                    │ error.log   │  ERROR only
                    └─────────────┘
```

### 日志格式（text，Day24 默认）

```
2026-07-09 16:30:01 [INFO] ai-project-assistant request_id=7f3a2b1c method=POST path=/agent duration=3.2s status=200
2026-07-09 16:30:05 [ERROR] ai-project-assistant request_id=7f3a2b1c event=llm_timeout model=qwen-plus
```

**字段约定：**

| 字段 | 说明 |
|------|------|
| `request_id` | 本服务生成，贯穿单次 HTTP 请求 |
| `trace_id` | 可选；若请求头带 `X-Trace-ID` 则透传记录，否则留空或等于 request_id |
| `event` | 业务事件名（`llm_timeout`、`agent_tool`） |
| key=value | 延续 Day14 风格，便于 grep |

### `config/logging.yaml` 草案

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: "%(asctime)s [%(levelname)s] %(name)s %(request_id)s %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"

handlers:
  console:
    class: logging.StreamHandler
    formatter: standard
    level: INFO
  app_file:
    class: logging.handlers.RotatingFileHandler
    filename: logs/app.log
    maxBytes: 10485760   # 10MB
    backupCount: 5
    formatter: standard
    level: INFO
  error_file:
    class: logging.handlers.RotatingFileHandler
    filename: logs/error.log
    maxBytes: 10485760
    backupCount: 5
    formatter: standard
    level: ERROR

root:
  level: INFO
  handlers: [console, app_file, error_file]
```

> 实现时可用 `logging.config.dictConfig` 加载；`request_id` 通过 `contextvars` + 自定义 `Filter` 注入。

---

## Request ID 设计

### 流程

```
客户端请求
    │
    ▼
RequestIdMiddleware
    ├─ 读 X-Request-ID（若有则复用，否则 uuid4）
    ├─ 写入 contextvars + request.state
    ├─ 业务日志自动带 request_id
    └─ 响应头 X-Request-ID: <id>
```

### 中间件（设计示意）

```python
# app/core/request_context.py
import contextvars
import uuid

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

def get_request_id() -> str:
    return request_id_var.get()

# app/core/middleware.py — 增强 RequestLoggingMiddleware
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(rid)
        request.state.request_id = rid
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_var.reset(token)
```

### 与现有中间件顺序（`main.py`）

```python
# 先 RequestId，再 RequestLogging（日志才能带上 id）
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIdMiddleware)  # 后添加 = 先执行（Starlette 洋葱模型）
```

> Starlette：`add_middleware` **后加的在外层先执行**。RequestId 须在最外层。

---

## Trace ID（了解即可）

### 与 Request ID 的区别

| 概念 | 范围 | 本项目 Day24 |
|------|------|--------------|
| **Request ID** | 单次 HTTP 请求 | **实现** |
| **Trace ID** | 跨服务整条调用链（Nginx → API → Chroma → 通义 API） | **仅记录/透传** |

### 设计说明（不实现完整链路）

```
用户 → Nginx → FastAPI → 通义 API
         │         │            │
    (无 trace)  trace_id    span_id
                贯穿全链
```

- 若客户端或 Nginx 传入 `X-Trace-ID` / `traceparent`（W3C），中间件 **读取并写入日志**，不强制生成
- 未来 Day25+ 接 OpenTelemetry 时，`trace_id` 由 SDK 自动注入
- **面试话术：** Request ID 管「这一跳」；Trace ID 管「整条业务链路」

---

## 错误日志设计

### 记录点（增强现有代码，不大改逻辑）

| 位置 | 现状 | Day24 |
|------|------|-------|
| `main.py` AppError handler | `logger.error` | + `request_id` + `status_code` |
| `main.py` 未捕获异常 | `logger.exception` | 写入 `error.log`（自动，level=ERROR） |
| `llm.py` | `logger.error` 超时/连接失败 | + `request_id` + `event=llm_*` |
| `agent.py` stream 异常 | `logger.exception` | 同上 |
| `mcp/__init__.py` bootstrap 失败 | `logger.error` | 同上 |

### 错误日志示例

```
2026-07-09 16:35:00 [ERROR] ai-project-assistant request_id=a1b2c3d4 event=unhandled_error path=/agent/stream error=Connection reset
Traceback (most recent call last):
  ...
```

### API 响应（不暴露内部栈）

```json
{
  "detail": "服务器内部错误",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

> 4xx/5xx 响应体可选带 `request_id`，方便用户反馈时提供 ID。

---

## Docker / Compose 集成

### 卷挂载

```yaml
# docker-compose.yml（实现日）
services:
  api:
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config:ro   # 只读挂载默认配置
    environment:
      APP_ENV: prod
      LOG_LEVEL: INFO
      LOG_CONSOLE: "true"        # 容器仍打 stdout，供 docker logs
```

### Nginx 侧（可选）

- Nginx access log 可记录 `$http_x_request_id`（需客户端或 API 回写；Day24 不强制）
- API 响应头 `X-Request-ID` 已足够前端展示「反馈 ID」

---

## 实现日文件清单（预览）

| 文件 | 职责 |
|------|------|
| `config/settings.yaml` | 默认配置 |
| `config/logging.yaml` | logging dictConfig |
| `logs/.gitkeep` | 保留目录 |
| `app/core/settings.py` | 加载 yaml + env |
| `app/core/request_context.py` | contextvars + Filter |
| `app/core/logger.py` | 重构：dictConfig、移除 basicConfig |
| `app/core/middleware.py` | RequestId + 日志带 request_id |
| `app/main.py` | 中间件顺序、错误响应带 request_id |
| `.env.example` | 新增 `APP_ENV`、`LOG_LEVEL`、`LOG_DIR` |
| `.gitignore` | `logs/*.log` |
| `docker-compose.yml` | 挂载 logs、config |
| `docs/Day24.md` | 设计 + 使用指南 |

---

## 环境变量（`.env.example` 新增项）

```env
# Day24 — 环境与日志
APP_ENV=dev
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_CONSOLE=true
```

---

## 验收标准

- [ ] 启动后自动创建 `logs/app.log`、`logs/error.log`
- [ ] `GET /health` 响应头含 `X-Request-ID`
- [ ] `logs/app.log` 中同一请求的 access 日志与业务日志 `request_id` 一致
- [ ] 触发 LLM 错误或 500 时，`logs/error.log` 有对应记录
- [ ] `LOG_LEVEL=WARNING` 时 INFO 不再写入 app.log（可配置验证）
- [ ] `config/settings.yaml` 修改默认 `logging.level` 可被 `.env` 覆盖
- [ ] Docker Compose 重启后 `logs/` 卷内日志保留
- [ ] `logs/*.log` 未提交 Git

---

## 测试命令（实现后）

```powershell
# 启动
docker compose up -d --build

# 探活 + 看 Request ID
$r = Invoke-WebRequest http://localhost/health -UseBasicParsing
$r.Headers["X-Request-ID"]

# 触发业务日志
Invoke-RestMethod -Uri http://localhost/agent -Method Post `
  -ContentType "application/json" -Body '{"message":"你好"}'

# 查看日志
Get-Content logs/app.log -Tail 20
Get-Content logs/error.log -Tail 10

# 本地开发（非 Docker）
$env:LOG_LEVEL="DEBUG"
python -m uvicorn app.main:app --reload
```

---

## 风险与对策

| 风险 | 对策 |
|------|------|
| `basicConfig` 与 dictConfig 冲突 | 启动时只调用一次 `setup_logging()` |
| SSE 长连接日志过多 | Agent stream 仅记录开始/结束 + duration |
| 日志文件撑满磁盘 | RotatingFileHandler 10MB × 5 |
| contextvars 在 async 任务中丢失 | 中间件 set/reset；子任务显式传 id（Agent 内一般同请求） |
| 敏感信息写入日志 | 禁止记录 API Key、完整用户消息可截断 |

---

## 与 Sprint 4 后续的关系

| Day | 衔接 |
|-----|------|
| Day25 Token / 成本 | 日志增加 `tokens_in`、`tokens_out`、`cost_usd` 字段 |
| Day26 架构文档 | 可观测性章节引用 Request ID + 日志目录 |
| Day27 README | Quick Start 增加「查看 logs/error.log 排错」 |

---

## 小结

Day24 在 Day14 请求日志基础上，补齐 **配置分层**（`config/` + `.env`）与 **生产级落盘**（`logs/app.log` / `error.log`），并用 **Request ID** 把一次 HTTP 请求的全链路日志串起来。Trace ID 作为分布式追踪的预习，本日仅透传记录，为后续 Token 统计与可观测性升级铺路。

---

## 使用指南（实现后）

### 一键启动

```powershell
docker compose up -d --build
docker compose ps

# 探活 + Request ID
$r = Invoke-WebRequest http://localhost/health -UseBasicParsing
$r.Headers["X-Request-ID"]
Invoke-RestMethod http://localhost/health
```

### 日志文件

| 文件 | 内容 |
|------|------|
| `logs/app.log` | INFO 及以上（请求、Agent、RAG） |
| `logs/error.log` | 仅 ERROR（LLM 失败、未捕获异常） |

```powershell
Get-Content logs/app.log -Tail 20
Get-Content logs/error.log -Tail 10
```

### 配置优先级

```
.env / 环境变量  >  config/settings.yaml  >  代码默认值
```

| 变量 | 说明 | 默认 |
|------|------|------|
| `APP_ENV` | 运行环境 | `dev` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_DIR` | 日志目录 | `logs` |
| `LOG_CONSOLE` | 是否输出控制台 | `true` |

### 本地开发（非 Docker）

```powershell
$env:LOG_LEVEL="DEBUG"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# 日志写入 logs/app.log，同时打控制台
```

### 实现文件清单

| 文件 | 职责 |
|------|------|
| `config/settings.yaml` | 默认配置 |
| `config/logging.yaml` | logging dictConfig 模板 |
| `app/core/settings.py` | yaml + env 合并 |
| `app/core/request_context.py` | Request ID / Trace ID contextvars |
| `app/core/logger.py` | 落盘 + 轮转 |
| `app/core/middleware.py` | RequestId + 请求日志 |
| `app/main.py` | 中间件顺序、错误响应带 request_id |

### 验收清单

- [x] 启动后自动创建 `logs/app.log`、`logs/error.log`
- [x] `GET /health` 响应头含 `X-Request-ID`
- [x] 同一请求日志 `request_id` 一致
- [x] ERROR 写入 `logs/error.log`
- [x] `.env` 可覆盖 `LOG_LEVEL`
- [x] Compose 挂载 `logs/` 卷持久化
- [x] `logs/*.log` 未提交 Git
