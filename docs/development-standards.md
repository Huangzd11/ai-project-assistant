# AI 项目开发规范

> 本规范适用于 **AI Project Assistant** 仓库，随项目演进持续更新。

---

## 1. 仓库结构

```
ai-project-assistant/
├── app/               # 服务代码（api / core / models / rag）
├── uploads/           # 原始 PDF（Day08）
├── data/parsed/       # 解析 JSON（Day09）
├── docs/              # 文档与工作日志
├── examples/          # Day01~03 学习脚本
├── tests/             # Day14 测试
├── requirements.txt / Dockerfile / .env.example
```

| 目录 | 用途 | 规则 |
|------|------|------|
| `app/api/` | HTTP 路由 | 不含 PDF 解析等业务细节 |
| `app/rag/` | RAG 流水线 | Day09 解析，Day10+ 切分/向量 |
| `uploads/` | 原始 PDF | 仅上传产物，不入库大文件 |
| `data/parsed/` | 解析 JSON | `.gitignore` 忽略 `*.json` |
| `docs/` | 全部文档 | 每日工作写入 `DayXX.md` |
| `examples/` | 学习示例 | 按 Day 命名，可独立运行 |

---

## 2. 代码分层

| 层 | 路径 | 职责 |
|----|------|------|
| 配置层 | `app/core/config.py` | 仅读取环境变量 |
| 契约层 | `app/models/schemas.py` | Pydantic 请求/响应 |
| 推理层 | `app/core/llm.py` | LLM 调用，不感知 HTTP |
| 解析层 | `app/rag/pdf_loader.py` | PDF → JSON（Day09） |
| 接口层 | `app/api/*.py` | FastAPI 路由 |

**原则**：上层依赖下层，推理层不反向依赖接口层。

---

## 3. Git 规范

### 3.1 分支

| 分支 | 用途 |
|------|------|
| `main` | 稳定可运行版本 |
| `feature/dayXX-*` | 每日学习功能分支（可选） |

### 3.2 提交信息

```
<type>: <简要描述>

示例：
feat: add /chat/stream SSE endpoint
docs: update Day06 work log
refactor: move retriever to src/
fix: handle Ollama connection timeout
```

| type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 缺陷修复 |
| `docs` | 文档变更 |
| `refactor` | 重构（不改变行为） |
| `chore` | 构建、依赖等杂项 |

### 3.3 禁止提交

- `.env`（含 API Key）
- `__pycache__/`、`.venv/`
- 大型模型文件、临时数据

`.gitignore` 已配置，提交前执行 `git status` 确认。

---

## 4. 环境变量与密钥

| 规则 | 说明 |
|------|------|
| 模板化 | 敏感配置写入 `.env.example`，标注获取方式 |
| 本地配置 | 实际密钥仅存在于本地 `.env`，绝不入库 |
| 容器注入 | Docker 通过 `-e` 或 compose 环境变量传入 |
| 默认值 | `config.py` 提供安全默认值（如 Ollama 本地地址） |

---

## 5. 文档规范

### 5.1 每日工作日志

- 路径：`docs/DayXX.md`
- 必含：学习目标、完成内容、关键命令、收获、下一步
- 完成后在 `roadmap.md` 打勾

### 5.2 方案与接口文档

| 文档 | 更新时机 |
|------|----------|
| `solution-design.md` | 架构变更、技术选型调整 |
| `api.md` | 新增或修改 HTTP 接口 |
| `roadmap.md` | 完成/新增学习阶段 |
| `README.md` | 功能、结构、快速开始变化时同步 |

### 5.3 README 最低要求

- 项目简介与技术栈
- 当前功能与学习进度
- 项目结构
- 快速开始步骤
- 文档索引

---

## 6. 依赖管理

- 所有依赖写入根目录 `requirements.txt`
- 新增依赖时注明用途（可在 commit message 或 Day 日志中说明）
- 避免锁定过多子项目各自维护 `requirements.txt`

---

## 7. 测试与验证

当前阶段以手动验证为主：

```powershell
# 命令行对话
python examples/chat_demo.py

# API 服务
python -m uvicorn app.main:app --reload

# Docker
docker build -t ai-chat:v1 . && docker run -p 8000:8000 ai-chat:v1
```

后续引入自动化测试时，测试文件放入 `tests/` 目录。

---

## 相关文档

- [roadmap.md](roadmap.md) — 学习进度
- [solution-design.md](solution-design.md) — 方案设计
- [Day06.md](Day06.md) — 规范建立记录
