# Day15 — Agent Core（Planner + Function Calling）

> 版本：**v0.3-alpha** | Commit：`feat(agent-core)`  
> **Sprint 3 第一天：从 ChatBot 进化到 Agent**

## 学习目标

- [x] 理解 **Agent ≠ ChatBot** 的本质区别
- [x] 掌握 Agent 核心循环：Planner → LLM → Tool → Observation → LLM → Answer
- [x] 理解为什么需要 **Planner**（任务分解），而不是「用户一问，直接 LLM」
- [x] 实现最小 Agent，能 **调用 RAG 工具** 回答知识库问题
- [x] 为 Day16 Tool 管理、Day17 Memory 预留扩展点

---

## 完成内容

### 核心模块

| 模块 | 函数 | 职责 |
|------|------|------|
| `planner.py` | `plan()` | 规则判断 → 生成 `rag_query` 步骤 |
| `tools.py` | `rag_query()` | 封装 `rag_answer()`，提供 schema |
| `executor.py` | `run_agent()` | 执行计划 → Observation → LLM 总结 |
| `prompt.py` | `FINAL_ANSWER_PROMPT` | Agent 总结阶段 system prompt |

### HTTP 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /agent` | Agent 问答 | 返回答案 + plan + tool_calls + sources |

### 实现策略

Day15 采用 **Phase 1（规则 Planner + 手动调工具）**：
- Planner 用关键词规则，不依赖 LLM 输出 JSON 计划
- Executor 按 plan 调用 `TOOL_HANDLERS`，再用 `llm.chat()` 总结 Observation
- `llm.chat_with_tools()` 留作 Day16 进阶（Function Calling 自动选工具）

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| `app/agent/` 四文件骨架 + RAG 工具调用 | Memory / 多轮会话（Day17） |
| Planner 任务分解（规则或 LLM） | MCP 接入（Day18~19） |
| Function Calling 最小闭环 | PDF 解析工具（Day16 扩展） |
| 复用 `rag_answer()` 作为第一个 Tool | 企业 Workflow 编排（Day20） |
| 可选 `POST /agent` HTTP 入口 | 前端 UI |

**Day15 = Agent 最小可用内核：能「想步骤 → 调工具 → 看结果 → 给答案」。**

---

## 核心概念：Agent ≠ ChatBot

| | ChatBot（Day04 `/chat`） | Agent（Day15） |
|---|--------------------------|----------------|
| 输入 | 用户消息 | 用户目标 |
| 处理 | 直接 LLM 一次推理 | Planner 分解 → 多步执行 |
| 能力边界 | 仅模型内部知识 | 可调用外部 Tool |
| 典型路径 | User → LLM → Answer | User → Planner → LLM → Tool → Observation → LLM → Answer |
| 本项目例子 | 「什么是 RAG？」 | 「总结一下 Linux.pdf」 |

**ChatBot 会「猜」；Agent 会「查、做、再答」。**

---

## Agent 核心循环

```
User（用户目标）
  │
  ▼
Planner（规划：需要哪些步骤 / 调哪些工具）
  │
  ▼
LLM（决定调用哪个 Tool + 参数，Function Calling）
  │
  ▼
Tool（执行：如 rag_query）
  │
  ▼
Observation（工具返回的观察结果）
  │
  ▼
LLM（根据 Observation 生成最终 Answer）
  │
  ▼
Answer
```

这是 **ReAct / Tool-Use** 的最小形态。Day15 先跑通 **单轮、单工具（RAG）**；Day16 再扩展工具注册表。

---

## 为什么需要 Planner？

### 反例：直接 LLM

用户问：

> 总结一下 Linux.pdf

若走 `POST /chat` 或裸 LLM：
- 模型**没有**读过 `Linux.pdf` 全文
- 只能编造或泛泛而谈
- 无法保证引用 `uploads/` 或 Chroma 中的真实内容

### 正例：Planner 分解

```
用户：总结一下 Linux.pdf
        │
        ▼
Planner 输出计划（示例）：
  Step 1: rag_query(question="Linux.pdf 主要内容", source="linux.pdf")
  Step 2: summarize(observation from Step 1)
        │
        ▼
Executor 执行 Step 1 → 调用 RAG 工具 → 拿到 chunks + 检索结果
        │
        ▼
LLM 根据 Observation 生成总结
```

**Planner 的价值：** 把「一个模糊目标」拆成「可执行、可观测」的步骤，而不是一步到位赌模型幻觉。

Day15 的 Planner 可先做 **轻量版**：
- **方案 A（推荐入门）：** 规则 + 关键词（含 `.pdf` / 「总结」→ 走 `rag_query`）
- **方案 B（进阶）：** 用 LLM + system prompt 输出 JSON 计划 `[{tool, args}]`

两种方案都符合「有 Planner 这一层」；实现时二选一或 A 打底、B 可选。

---

## 在 Sprint 3 中的位置

```
Day15  Agent Core + RAG Tool     ← 今天
Day16  Tool 管理（注册表、多工具）
Day17  Memory（多轮上下文）
Day18~19  MCP
Day20  企业 Workflow
Day21  Release v0.3
```

与 Sprint 2 的关系：

```
Sprint 2  rag_answer()  ──封装为 Tool──►  Day15  agent 调用
Sprint 2  POST /rag      ──保留不变──►     仍可直接调 RAG API
Sprint 2  POST /chat     ──保留不变──►     纯对话入口不变
```

---

## 新增目录结构

```
app/
├── agent/                    # Day15 新增
│   ├── __init__.py           # 导出 run_agent / rag_tool 等
│   ├── planner.py            # 任务规划：用户目标 → 执行计划
│   ├── executor.py           # 执行计划：调 Tool、收集 Observation
│   ├── tools.py              # 工具定义与实现（Day15 仅 rag_query）
│   └── prompt.py             # Agent / Planner 专用 system prompt
├── api/
│   └── agent.py              # 可选：POST /agent
├── rag/
│   └── rag_pipeline.py       # 已有，被 tools.py 复用
└── core/
    └── llm.py                  # 扩展：支持 tools / function calling
```

---

## 模块职责设计

### 1. `prompt.py` — Agent 提示词

| 内容 | 说明 |
|------|------|
| `AGENT_SYSTEM_PROMPT` | 你是企业助手，可调用工具；优先用工具获取事实 |
| `PLANNER_PROMPT` | 将用户目标分解为步骤（若用 LLM Planner） |
| `FINAL_ANSWER_PROMPT` | 根据 Observation 生成最终回答，要求引用来源 |

配置可放入 `app/core/config.py` 或本模块常量，与 Day13 `RAG_SYSTEM_PROMPT` 并列。

### 2. `tools.py` — 工具定义与实现

Day15 **只实现一个工具**：

| 工具名 | 说明 | 底层复用 |
|--------|------|----------|
| `rag_query` | 在知识库中检索并生成带引用的回答 | `rag_answer(question)` |

**OpenAI Function Calling  schema 示例（设计）：**

```json
{
  "type": "function",
  "function": {
    "name": "rag_query",
    "description": "在企业知识库中检索并回答问题，返回 answer 与 sources",
    "parameters": {
      "type": "object",
      "properties": {
        "question": {
          "type": "string",
          "description": "要在知识库中检索的问题"
        }
      },
      "required": ["question"]
    }
  }
}
```

**工具函数签名（设计）：**

```python
def rag_query(question: str) -> dict:
    # 返回 rag_answer(question)，含 answer + sources
```

Day16 将把 `tools.py` 演进为 **工具注册表**（`TOOL_REGISTRY`），Day15 先硬编码一个即可。

### 3. `planner.py` — 任务规划

**输入：** `user_message: str`  
**输出：** `plan: list[PlanStep]`（或等价结构）

```python
# 设计用数据结构（示意）
PlanStep = {
    "tool": "rag_query",
    "args": {"question": "Linux.pdf 主要内容"},
    "reason": "需要从知识库获取文档内容再总结",
}
```

**规划策略（Day15 推荐）：**

| 场景 | Planner 行为 |
|------|----------------|
| 含「总结」「pdf」「文档」「知识库」等 | 计划调用 `rag_query` |
| 明确文件名如 `Linux.pdf` | `question` 中带上文档主题 |
| 纯闲聊（「你好」） | 计划：不调用工具，直接 LLM 回答 |

函数建议：`plan(user_message: str) -> list[PlanStep]`

### 4. `executor.py` — 执行与观察

**职责：**
1. 遍历 `plan` 中的每一步
2. 调用 `tools.py` 中对应函数
3. 收集 **Observation**（工具返回的 JSON / 文本）
4. 将 Observation 交给 LLM 生成最终 Answer

**核心函数（设计）：**

```python
def execute_plan(plan: list[PlanStep]) -> list[Observation]:
    ...

def run_agent(user_message: str) -> AgentResult:
    plan = plan(user_message)
    observations = execute_plan(plan)
    answer = synthesize_answer(user_message, observations)
    return AgentResult(answer=answer, plan=plan, observations=observations, ...)
```

**`AgentResult` 建议字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `answer` | str | 最终回答 |
| `plan` | list | 规划步骤（可观测、可调试） |
| `tool_calls` | list | 实际调用了哪些工具 |
| `sources` | list | 若走了 RAG，透传 `sources` |

### 5. `core/llm.py` 扩展（设计）

当前 `chat()` 仅支持单轮 messages。Day15 需增加：

```python
def chat_with_tools(
    messages: list[dict],
    tools: list[dict],
    system_prompt: str | None = None,
) -> ChatCompletionMessage:
    # client.chat.completions.create(..., tools=tools, tool_choice="auto")
```

或封装 `run_tool_loop()`：LLM 返回 `tool_calls` → 执行 → 把 `role: tool` 消息塞回 messages → 再调 LLM。

**Day15 最小路径：** Executor 可先 **不依赖** LLM 自动选工具，而是由 Planner 直接指定 `rag_query`，LLM 只负责「读 Observation 写总结」。Function Calling 可作为同日进阶或 Day15 后半目标。

---

## 端到端示例

### 用户输入

```
总结一下 Linux.pdf 的主要内容
```

### Planner 输出

```json
[
  {
    "tool": "rag_query",
    "args": { "question": "Linux.pdf 的主要内容是什么？" },
    "reason": "需从知识库检索文档内容"
  }
]
```

### Tool 执行（Observation）

```json
{
  "tool": "rag_query",
  "result": {
    "question": "Linux.pdf 的主要内容是什么？",
    "answer": "根据《linux.pdf》第1页：……",
    "sources": [{ "source": "linux.pdf", "page": 1, "chunk": 1, "score": 0.81 }]
  }
}
```

### 最终 Answer

```
Linux.pdf 主要介绍了……（基于知识库检索结果总结，并注明来源 linux.pdf 第1页）
```

---

## HTTP 接口（可选）

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /agent` | Agent 问答 | 走 Planner + Tool，返回答案 + plan + sources |

**请求：**

```json
{ "message": "总结一下 Linux.pdf" }
```

**响应：**

```json
{
  "answer": "...",
  "plan": [{ "tool": "rag_query", "args": { "question": "..." } }],
  "sources": [{ "source": "linux.pdf", "page": 1, "chunk": 1, "score": 0.81 }]
}
```

与 `POST /rag` 区别：
- `/rag`：固定 RAG 流水线，无规划层
- `/agent`：有 Planner，未来可串联多工具（Day16+）

---

## 与现有模块的依赖关系

```
POST /agent
    → app/api/agent.py
        → app/agent/executor.run_agent()
            → app/agent/planner.plan()
            → app/agent/tools.rag_query()
                → app/rag/rag_pipeline.rag_answer()
            → app/core/llm.chat()  # 总结 Observation
```

**原则：不修改 `rag_pipeline.py` 核心逻辑**，Agent 层只做编排与封装。

---

## 实现清单（待编码）

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 1 | 创建 `app/agent/` 包与 `__init__.py` | `agent/` | ✅ |
| 2 | Agent / Planner 提示词 | `prompt.py` | ✅ |
| 3 | `rag_query` 工具 + schema | `tools.py` | ✅ |
| 4 | `plan()` 任务分解 | `planner.py` | ✅ |
| 5 | `run_agent()` 执行闭环 | `executor.py` | ✅ |
| 6 | `llm.chat_with_tools()` 或等价封装 | `core/llm.py` | ⏭️ Day16 |
| 7 | `POST /agent` + Pydantic 模型 | `api/agent.py`, `schemas.py` | ✅ |
| 8 | `main.py` 注册路由 | `main.py` | ✅ |
| 9 | 联调：Agent 能调用 RAG | — | ✅ |

---

## 测试命令（设计）

```powershell
# 前置：知识库已入库（index_chunks）
python -c "from app.agent.executor import run_agent; import json; print(json.dumps(run_agent('总结一下 test.pdf'), ensure_ascii=False, indent=2))"

# HTTP（实现后）
python -m uvicorn app.main:app --reload
# POST http://127.0.0.1:8000/agent
# Body: {"message": "总结一下 test.pdf"}
```

**对比验证：**

| 入口 | 问「总结 Linux.pdf」 | 期望 |
|------|----------------------|------|
| `POST /chat` | 可能幻觉 | 无真实文档依据 |
| `POST /rag` | 固定检索+回答 | 有 sources，但无「总结」规划语义 |
| `POST /agent` | Planner → rag_query → 总结 | 有 plan + sources + 结构化总结 |

---

## 验收标准（Day15 完成定义）

- [x] `app/agent/` 四文件存在且职责清晰
- [x] `run_agent("总结 test.pdf")` 能调用 `rag_query` 并返回 `sources`
- [x] 响应中包含可观测的 `plan` 或 `tool_calls`
- [x] `POST /chat` 与 `POST /rag` 行为不变（向后兼容）
- [x] 日志可见：plan 步骤、tool 调用、耗时
- [ ] Git Commit：`feat(agent-core)`，Tag：`v0.3-alpha`

---

## 测试命令

```powershell
# 模块调用
python -c "from app.agent.planner import plan; print(plan('总结 test.pdf'))"
python -c "from app.agent.executor import run_agent; import json; print(json.dumps(run_agent('总结 test.pdf'), ensure_ascii=False, indent=2))"

# HTTP
python -m uvicorn app.main:app --reload
# POST http://127.0.0.1:8000/agent
# Body: {"message": "总结一下 test.pdf"}
```

---

## 每日收尾

- [x] 更新 Day15.md、api.md、CODEMAP、roadmap
- [ ] Git Commit：`feat(agent-core)`
- [ ] Tag：`v0.3-alpha`

## 架构图

```
                    User Message
                         │
                         ▼
              ┌─────────────────────┐
              │   planner.py        │  为什么要做？任务分解
              │   plan()            │
              └──────────┬──────────┘
                         │ PlanStep[]
                         ▼
              ┌─────────────────────┐
              │   executor.py       │
              │   execute_plan()    │
              └──────────┬──────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
  ┌─────────────────┐        ┌─────────────────┐
  │  tools.py       │        │  core/llm.py    │
  │  rag_query()    │        │  总结 Observation│
  └────────┬────────┘        └─────────────────┘
           │
           ▼
  ┌─────────────────┐
  │ rag_pipeline.py │
  │ rag_answer()    │
  └─────────────────┘
```

---

## 收获（完成后填写）

- Agent 与 ChatBot 的分水岭是 **Tool + Observation**，不是模型更大
- Planner 解决的是 **「先做什么」**，Executor 解决 **「怎么做」**
- Day15 用 RAG 一个工具跑通闭环，为 Day16 多工具、Day17 记忆打地基

---

## 下一步

Day16 — Tool Registry（`feat(tools)` · v0.3-alpha2）← 设计完成，见 [Day16.md](Day16.md)
