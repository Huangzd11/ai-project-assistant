# Day16 — Tool Registry（工具注册表）

> 版本：**v0.3-alpha2** | Commit：`feat(tools)`  
> **Sprint 3 第二天：真正理解 Tool，新增工具不改 Agent 核心**

## 学习目标

- [x] 理解企业 AI 项目的通用模式：**LLM → Tool → LLM**
- [x] 理解 **Tool Registry** 的价值：新增工具只注册，不改 Executor
- [x] 将 Day15 硬编码 `TOOL_HANDLERS` 重构为可扩展注册表
- [x] 实现 `pdf_tool` / `rag_tool` / `calculator` 三个工具
- [x] Planner 能根据问题选择不同 Tool（如 PDF Tool）

---

## 完成内容

### 工具注册表

| 工具名 | 文件 | 职责 |
|--------|------|------|
| `rag_query` | `rag_tool.py` | 知识库 RAG 问答 |
| `pdf_read` | `pdf_tool.py` | 读取 uploads/ PDF 页数与内容 |
| `calculator` | `calculator.py` | 安全数学表达式计算 |

### 核心模块

| 模块 | 函数 | 职责 |
|------|------|------|
| `registry.py` | `register` / `run` / `list_names` | 工具注册与统一执行 |
| `tools/__init__.py` | bootstrap | 启动时注册全部工具 |
| `planner.py` | `plan()` | calculator → pdf_read → rag_query 路由 |
| `executor.py` | `run_agent()` | 只依赖 `registry.run`，不 import 具体工具 |

### 其他改动

- 删除 `app/agent/tools.py`，避免与 `app/agent/tools/` 包冲突
- 精简 `app/rag/__init__.py`，避免 import pdf_loader 时拉起 chromadb

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| `agent/tools/` 目录 + `registry.py` | Memory（Day17） |
| 迁移 `rag_query` → `rag_tool.py` | MCP（Day18~19） |
| 新增 `pdf_tool`、`calculator` | Search / Weather 真实 API（可留 stub 或 Day17+） |
| Executor / Planner 改为读 Registry | `llm.chat_with_tools()` 自动选工具（可选进阶） |
| 删除或废弃 Day15 `agent/tools.py` | 企业 Workflow（Day20） |

**Day16 核心成果：新增 Tool = 新建文件 + `registry.register()`，不动 `executor.py` 主逻辑。**

---

## 核心概念：什么是 Tool？

### 企业 AI 项目的通用模式

```
User Question
     │
     ▼
   LLM（决定调什么工具 / Planner 规划）
     │
     ▼
   Tool（执行真实能力：查库、读文件、计算……）
     │
     ▼
 Observation（工具返回的结构化结果）
     │
     ▼
   LLM（根据 Observation 生成 Answer）
```

很多项目的 Tool 举例：

| Tool | 作用 | Day16 |
|------|------|-------|
| Search Tool | 联网 / 站内搜索 | ⏭️ 预留接口 |
| PDF Tool | 读取 / 解析 PDF | ✅ 今天 |
| RAG Tool | 知识库检索问答 | ✅ 迁移 |
| Calculator Tool | 数学计算 | ✅ 今天 |
| Time Tool | 当前时间 | ⏭️ 预留 |
| Weather Tool | 天气查询 | ⏭️ 预留 |

**Tool 的本质：** 把 LLM **做不到或不该做** 的事（读文件、精确计算、查实时数据）封装成 **统一契约的函数**。

---

## Day15 → Day16 演进

### Day15 的问题

```python
# agent/tools.py — 硬编码
TOOL_HANDLERS = {"rag_query": rag_query}
```

- 新增工具要改 `tools.py`、改 `executor.py` 的 import
- Planner 写死 `"rag_query"`
- 无法统一管理 schema、描述、分类

### Day16 的目标

```python
# agent/tools/registry.py
registry.register(pdf_tool)
registry.register(rag_tool)
registry.register(calculator_tool)

# executor 只认 registry
handler = registry.get(tool_name)
result = handler.run(**args)
```

**新增 Weather Tool：** 新建 `weather_tool.py` + `registry.register()`，**不改 Executor**。

---

## 新增目录结构

```
app/agent/
├── planner.py          # Day16 升级：按意图选 pdf / rag / calculator
├── executor.py         # Day16 升级：从 registry 取工具，不 import 具体 tool
├── prompt.py
├── tools/              # Day16 新增
│   ├── __init__.py     # 导出 registry，启动时完成 register
│   ├── registry.py     # Tool 注册表核心
│   ├── rag_tool.py     # 从 Day15 tools.py 迁移
│   ├── pdf_tool.py     # 封装 parse_pdf
│   └── calculator.py   # 安全数学计算
└── tools.py            # ⚠️ 废弃或改为 re-export registry（避免破坏 import）
```

---

## Tool 统一契约（设计）

每个 Tool 实现同一接口，便于 Registry 管理：

```python
# 设计用数据结构（可用 dataclass 或简单 class）
ToolSpec = {
    "name": "pdf_read",           # 唯一标识，Planner / LLM 引用
    "description": "读取并解析 PDF 文件",
    "schema": { ... },            # OpenAI Function Calling JSON schema
    "run": callable,              # (**kwargs) -> dict
}
```

**`run()` 返回值约定（Observation）：**

```python
{
    "ok": True,                   # 是否成功
    "data": { ... },              # 工具业务数据
    "summary": "人类可读摘要",     # 给 LLM 读的短文本（可选但推荐）
    "sources": [],                # 仅 RAG 等需要溯源的工具填充
}
```

Executor 的 `_format_observation` 应优先读 `summary`，再 fallback 到 `data`。

---

## 模块设计

### 1. `registry.py` — 注册表核心

**职责：**
- `register(tool: ToolSpec)` — 注册工具
- `get(name: str) -> ToolSpec` — 按名获取，不存在抛清晰异常
- `list_tools() -> list[ToolSpec]` — 列出全部（给 Planner / Swagger / 调试）
- `get_schemas() -> list[dict]` — 返回所有 OpenAPI function schemas
- `run(name: str, **kwargs) -> dict` — 统一执行入口

**提示骨架：**

```python
_TOOLS: dict[str, ToolSpec] = {}

def register(tool: ToolSpec) -> None:
    if tool["name"] in _TOOLS:
        raise ValueError(f"Tool already registered: {tool['name']}")
    _TOOLS[tool["name"]] = tool

def get(name: str) -> ToolSpec:
    if name not in _TOOLS:
        raise KeyError(f"Unknown tool: {name}")
    return _TOOLS[name]

def run(name: str, **kwargs) -> dict:
    return get(name)["run"](**kwargs)

def list_names() -> list[str]:
    return list(_TOOLS.keys())
```

---

### 2. `rag_tool.py` — 知识库问答（迁移）

**从 Day15 迁移：**
- `name`: 建议改为 `rag_query`（保持 Planner 兼容）或 `rag_tool`（二选一，全文统一即可）
- `run(question: str)` → 调 `rag_answer(question)`
- 返回包装：

```python
{
    "ok": True,
    "data": result,  # rag_answer 原始 dict
    "summary": result["answer"],
    "sources": result.get("sources", []),
}
```

---

### 3. `pdf_tool.py` — PDF 读取（今天重点）

**职责：** 读取 `uploads/` 下 PDF，返回页数 / 文本摘要，**不经过 RAG**。

**底层复用：** `app.rag.pdf_loader.parse_pdf()` 或 `load_pdf_pages()`

**典型场景：**

| 用户问 | Planner 选 |
|--------|-----------|
| 「Linux.pdf 有多少页？」 | `pdf_read` |
| 「读取 test.pdf 第一页内容」 | `pdf_read` |
| 「总结 Linux.pdf」 | 可先 `pdf_read` 或走 `rag_query`（见 Planner） |

**schema 参数设计：**

```json
{
  "filename": "linux.pdf",
  "page": null
}
```

- `filename`：必填，PDF 文件名
- `page`：可选，指定页；null 表示返回元信息 + 前几页摘要

**返回示例：**

```python
{
    "ok": True,
    "data": {
        "source": "linux.pdf",
        "total_pages": 4,
        "pages": [{"page": 1, "content": "..."}],
    },
    "summary": "linux.pdf 共 4 页，第1页内容：……",
    "sources": [{"source": "linux.pdf", "page": 1}],
}
```

**路径拼接：** `UPLOAD_DIR / filename`，文件不存在时 `ok: False`。

---

### 4. `calculator.py` — 计算器

**职责：** 精确数学计算，避免 LLM 算错。

**实现建议（安全）：**
- 只用 `ast` 解析字面量表达式，**禁止** `eval(用户输入)` 裸执行
- 或限制字符集：`0-9+-*/().` 和空格

**schema：**

```json
{ "expression": "123 * 456" }
```

**返回：**

```python
{"ok": True, "data": {"expression": "...", "result": 56088}, "summary": "123 * 456 = 56088"}
```

**Planner 触发词：** `计算`、`等于`、`+`、`-`、`*`、`/`、数字表达式

---

### 5. `tools/__init__.py` — 启动注册

**职责：** 模块导入时完成所有 `register()`，保证 Executor 用时已就绪。

```python
from app.agent.tools.registry import register
from app.agent.tools import rag_tool, pdf_tool, calculator

def _bootstrap():
    register(rag_tool.SPEC)
    register(pdf_tool.SPEC)
    register(calculator.SPEC)

_bootstrap()
```

---

## Planner 升级（Day16）

Day15 只认 `rag_query`。Day16 按 **意图** 选工具：

| 意图 | 关键词 / 规则 | Tool | args 示例 |
|------|---------------|------|-----------|
| 计算 | `计算`、含 `+ - * /`、纯算式 | `calculator` | `{"expression": "1+2"}` |
| 读 PDF | `.pdf` + `页`/`读取`/`解析`/`多少页` | `pdf_read` | `{"filename": "linux.pdf"}` |
| 知识库 | `总结`/`知识库`/`telnet` 等 | `rag_query` | `{"question": "..."}` |
| 默认闲聊 | 无匹配 | 无工具 | `[]` |

**多步计划（可选）：**

用户：「总结 Linux.pdf」

```
Step 1: pdf_read(filename="linux.pdf")   # 确认文件存在
Step 2: rag_query(question="Linux.pdf 主要内容")
```

Day16 **最小验收**：单步 `pdf_read` 能回答「Linux.pdf 有多少页」即可；多步可进阶。

**注意：** Planner 通过 `registry.list_names()` 校验工具名，不硬编码 import。

---

## Executor 升级（Day16）

**改动点（尽量小）：**

```python
# 之前
from app.agent.tools import TOOL_HANDLERS
handler = TOOL_HANDLERS[tool_name]
result = handler(**step["args"])

# 之后
from app.agent.tools.registry import run as run_tool
result = run_tool(tool_name, **step["args"])
```

**`_format_observation` 升级：**

```python
def _format_tool_result(result: dict) -> str:
    if result.get("summary"):
        return result["summary"]
    return str(result.get("data", result))
```

**sources 聚合：** 遍历所有 tool results，合并 `sources` 字段（RAG + PDF 都可能贡献）。

---

## 端到端示例（Day16 验收场景）

### 场景 A：PDF Tool

```
用户：Linux.pdf 有多少页？
  → Planner: [{ tool: "pdf_read", args: { filename: "linux.pdf" } }]
  → pdf_tool.run() → { total_pages: 4, summary: "linux.pdf 共 4 页" }
  → LLM 总结 → "Linux.pdf 共有 4 页。"
```

### 场景 B：Calculator

```
用户：计算 123 * 456
  → Planner: [{ tool: "calculator", args: { expression: "123*456" } }]
  → calculator.run() → { result: 56088 }
  → Answer: "123 × 456 = 56088"
```

### 场景 C：RAG Tool（回归）

```
用户：如何开启 telnet？
  → Planner: [{ tool: "rag_query", args: { question: "..." } }]
  → 与 Day15 行为一致，sources 非空
```

---

## 与现有模块依赖

```
pdf_tool.py   → app.rag.pdf_loader.parse_pdf / load_pdf_pages
              → app.core.config.UPLOAD_DIR

rag_tool.py   → app.rag.rag_pipeline.rag_answer

calculator.py → 标准库 ast / re（无外部依赖）

registry.py   → 无业务依赖

executor.py   → registry.run（不再依赖具体 tool 模块）

planner.py    → registry.list_names() 校验
```

---

## 实现清单（待编码）

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 1 | `ToolSpec` 契约 + `registry.py` | `tools/registry.py` | ✅ |
| 2 | 迁移 RAG → `rag_tool.py` | `tools/rag_tool.py` | ✅ |
| 3 | 实现 `pdf_tool.py` | `tools/pdf_tool.py` | ✅ |
| 4 | 实现 `calculator.py` | `tools/calculator.py` | ✅ |
| 5 | `tools/__init__.py` 启动注册 | `tools/__init__.py` | ✅ |
| 6 | Executor 改读 registry | `executor.py` | ✅ |
| 7 | Planner 多工具路由 | `planner.py` | ✅ |
| 8 | 删除旧 `agent/tools.py` | — | ✅ |
| 9 | 联调三工具 + POST /agent 回归 | — | ✅ |

---

## 测试命令（设计）

```powershell
# Registry
python -c "from app.agent.tools.registry import list_names; print(list_names())"

# PDF Tool
python -c "from app.agent.tools.registry import run; import json; print(json.dumps(run('pdf_read', filename='test.pdf'), ensure_ascii=False, indent=2))"

# Calculator
python -c "from app.agent.tools.registry import run; print(run('calculator', expression='123*456'))"

# Agent 全流程
python -c "from app.agent import run_agent; import json; print(json.dumps(run_agent('test.pdf 有多少页'), ensure_ascii=False, indent=2))"
```

---

## 验收标准（Day16 完成定义）

- [x] `agent/tools/` 含 `registry.py`、`rag_tool.py`、`pdf_tool.py`、`calculator.py`
- [x] 新增工具只需 `register()`，**不修改** `executor.py` 主循环
- [x] `run_agent("test.pdf 有多少页")` 走 PDF Tool 并返回正确页数
- [x] `run_agent("计算 1+2")` 走 Calculator
- [x] `run_agent("telnet")` 仍走 RAG，sources 正常
- [x] `POST /agent` 回归通过
- [ ] Git Commit：`feat(tools)`，Tag：`v0.3-alpha2`

---

## 测试命令

```powershell
python -c "import app.agent.tools; from app.agent.tools.registry import list_names, run; print(list_names())"
python -c "import app.agent.tools; from app.agent.tools.registry import run; print(run('calculator', expression='123*456'))"
python -c "from app.agent.planner import plan; print(plan('test.pdf 有多少页'))"
python -c "from app.agent import run_agent; import json; print(json.dumps(run_agent('计算 1+2'), ensure_ascii=False, indent=2))"
```

---

## 每日收尾

- [x] 更新 Day16.md、CODEMAP、roadmap
- [ ] Git Commit：`feat(tools)`
- [ ] Tag：`v0.3-alpha2`

---

## 架构图

```
User Question
     │
     ▼
┌─────────────┐
│  planner.py │  意图 → tool name + args
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ executor.py │  registry.run(name, **args)  ← 不感知具体工具
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      tools/registry.py          │
│  register / get / run / schemas │
└──────┬──────────┬──────────┬────┘
       │          │          │
       ▼          ▼          ▼
  pdf_tool   rag_tool   calculator
       │          │          │
       ▼          ▼          ▼
  pdf_loader  rag_answer   ast/re
```

---

## 常见坑

1. **循环 import** — `registry.py` 不要 import 各 tool；由 `tools/__init__.py` 统一 register
2. **工具名不一致** — Planner 写 `pdf_tool`，registry 注册 `pdf_read`，会对不上
3. **`eval()` 安全风险** — Calculator 必须用安全解析
4. **PDF 路径** — 只用 `uploads/` 下文件名，防路径穿越（`Path(filename).name`）
5. **忘记 bootstrap** — 未调用 register 会导致 `Unknown tool`

---

## 收获（完成后填写）

- Tool Registry 是 Agent 可扩展性的关键
- LLM 负责「想」，Tool 负责「做」，Observation 负责「证」
- 新增 Search / Weather 只需复制 `xxx_tool.py` + register 模式

---

## 下一步

Day17 — Memory（`feat(memory)` · v0.3-beta）← 见 [roadmap.md](roadmap.md)
