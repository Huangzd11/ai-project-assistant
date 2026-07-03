# 代码地图（Code Map）

> 按目录列出每个文件的 **Day 来源**、**主要功能** 与 **核心逻辑**，便于回顾学习路径。

---

## 完整目录

```
ai-project-assistant/
│
├── app/                              # Day04 创建 · Day08 重构
│   ├── main.py                       # Day04/08 — FastAPI 入口，挂载路由
│   │
│   ├── api/                          # Day04 拆分 · Day08 扩展
│   │   ├── health.py                 # Day04 — GET / 、/health
│   │   ├── chat.py                   # Day04 — GET /models 、POST /chat
│   │   └── upload.py                 # Day08 — POST /upload（PDF 上传）
│   │
│   ├── core/                         # Day04 核心层 · Day08 扩展
│   │   ├── config.py                 # Day02/04/08 — 环境变量配置
│   │   ├── llm.py                    # Day02/04 — LLM chat() 封装
│   │   ├── logger.py                 # Day08 — 日志
│   │   └── files.py                  # Day08 — 文件大小格式化、目录创建
│   │
│   ├── models/                       # Day04 数据契约 · Day08 扩展
│   │   ├── schemas.py                # Pydantic 请求/响应模型
│   │   └── __init__.py               # 统一导出
│   │
│   └── rag/                          # Day09+ 预留
│       └── __init__.py               # RAG 流水线（解析/切分/向量/检索）
│
├── examples/                         # Day01~03 学习示例（独立脚本）
│   ├── prompt_demo.py                # Day01 — Prompt 练习
│   ├── chat_demo.py                  # Day02 — 命令行多轮对话
│   └── ollama_demo.py                # Day03 — Ollama 流式调用
│
├── uploads/                          # Day08 — PDF 上传存储目录
├── data/                             # Day12+ — 向量库等数据（预留）
├── tests/                            # Day14 — 自动化测试（预留）
│
├── docs/                             # Day06~08 — 项目文档
│   ├── Day01.md ~ Day08.md           # 每日工作日志
│   ├── api.md                        # HTTP 接口说明
│   ├── roadmap.md                    # 学习路线
│   ├── solution-design.md            # AI 方案设计
│   ├── development-standards.md      # 开发规范
│   ├── architecture.png              # 架构结构图
│   └── CODEMAP.md                    # 本文件
│
├── requirements.txt                  # Day02 起逐步追加依赖
├── Dockerfile                        # Day05 — 容器化
├── .dockerignore                     # Day07 — 减小镜像体积
├── .env.example                      # Day02 — 环境变量模板
├── .gitignore
└── README.md                         # Day06 完善
```

---

## 按 Day 索引

| Day | 文件 | 功能 | 逻辑概要 |
|-----|------|------|----------|
| **Day01** | `examples/prompt_demo.py` | Prompt 实验 | system / few-shot / temperature 三组对比 |
| **Day02** | `examples/chat_demo.py` | 命令行对话 | messages 列表 + stream 流式输出 |
| **Day02** | `app/core/config.py` | 环境配置 | dotenv 加载 API Key、Base URL |
| **Day02** | `app/core/llm.py` | LLM 调用 | OpenAI SDK → chat.completions |
| **Day03** | `examples/ollama_demo.py` | 本地模型 | base_url 指向 Ollama /v1 |
| **Day04** | `app/main.py` | 应用入口 | 创建 FastAPI，注册路由 |
| **Day04** | `app/api/chat.py` | 聊天 API | 请求校验 → llm.chat() → 响应 |
| **Day04** | `app/api/health.py` | 探活 | 返回 status OK |
| **Day04** | `app/models/schemas.py` | 数据模型 | ChatRequest/Response 等 |
| **Day05** | `Dockerfile` | 容器部署 | pip install + uvicorn |
| **Day07** | `.dockerignore` | 构建优化 | 排除 docs/examples 等 |
| **Day08** | `app/api/upload.py` | PDF 上传 | 校验 → 写盘 → 返回 filename/size |
| **Day08** | `app/core/files.py` | 文件工具 | 大小格式化、目录创建 |
| **Day08** | `app/core/logger.py` | 日志 | 统一格式记录上传事件 |
| **Day09+** | `app/rag/` | RAG 流水线 | 待实现 |

---

## 请求链路

```
# 聊天（Day04）
Browser → POST /chat → app/api/chat.py → app/core/llm.py → Ollama/Qwen

# 上传（Day08）
Browser → POST /upload → app/api/upload.py → uploads/
```

---

## 启动命令

```powershell
# 安装依赖
python -m pip install -r requirements.txt

# 启动 API 服务（Day04+）
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 学习示例
python examples/prompt_demo.py    # Day01
python examples/chat_demo.py      # Day02
python examples/ollama_demo.py    # Day03
```
