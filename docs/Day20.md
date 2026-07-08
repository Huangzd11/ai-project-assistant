# Day20 — Enterprise Workflow（企业 Agent 工作流）

> 版本：**v0.3** | Commit：`feat(agent-workflow)`  
> **Sprint 3 倒数第二天：Agent 真正像助手一样工作**

## 学习目标

- [x] 理解 **企业 Agent Workflow**：Question → Planner → Need Tool? → Tool → Answer
- [x] 掌握 **意图分类**：闲聊 / 计算 / 知识库 RAG / 项目文件 MCP / PDF 元信息
- [x] 将 Day15~19 散落的 Planner 规则 **收拢为统一工作流引擎**
- [x] 两条典型链路跑通：
  - 「总结 Linux.pdf」→ **RAG** → Answer
  - 「README 里面写了什么」→ **Filesystem MCP** → Answer
- [x] 响应可观测：`workflow` 字段展示路由决策，便于调试与演示

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| `workflow.py` 统一意图分类与编排 | LLM 自主 ReAct 多轮推理 |
| 厘清 RAG vs Filesystem vs Chat 路由 | 多 MCP Server 同时在线 |
| `POST /agent` 返回 `workflow` 元数据 | 前端聊天 UI |
| 完善 Planner 优先级与冲突处理 | 向量长期记忆（Day22+） |
| 文档 + 联调两条示例链路 | 流式 SSE（Day22+） |

**Day20 核心成果：用户随便问一句话，Agent 能判断「要不要调工具、调哪个」，并给出像助手一样的回答。**

---

## 为什么需要 Workflow？

Day15~19 你已经有了：

| Day | 能力 |
|-----|------|
| Day15 | Planner + Executor |
| Day16 | Tool Registry（rag / pdf / calculator） |
| Day17 | Memory（session_id） |
| Day18 | MCP Client |
| Day19 | Filesystem MCP |

但 Planner 规则 **散落在 `planner.py` 和 `bridge.py`**，优先级靠 if-else 堆叠，难以回答：

- 这个问题要不要调工具？
- 为什么走 RAG 而不是 Filesystem？
- 整条链路是怎么决策的？

**Day20 = 加一层 Workflow 引擎**，把「像助手一样工作」的流程显式化。

---

## 企业 Workflow 总览

```
                    Question（用户问题）
                           │
                           ▼
                    ┌─────────────┐
                    │   Planner   │  ← workflow.classify()
                    └──────┬──────┘
                           │
                           ▼
                    Need Tool? ─────────────────┐
                           │                    │
                          Yes                   No
                           │                    │
              ┌────────────┼────────────┐       │
              ▼            ▼            ▼       ▼
         Calculator    Filesystem      RAG    Direct Chat
         (精确计算)    (MCP 读文件)  (知识库)  (Memory+LLM)
              │            │            │       │
              └────────────┴────────────┘       │
                           │                    │
                           ▼                    ▼
                    Tool Observation      LLM 直答
                           │                    │
                           └────────┬───────────┘
                                    ▼
                                 Answer
```

---

## 两条典型示例（今天必须跑通）

### 示例 1：总结 PDF → RAG

```
用户：「帮我总结 Linux.pdf」

Workflow 决策：
  intent = rag
  need_tool = true
  reason = PDF 总结类问题，走知识库检索+生成

执行链：
  Question
    → Planner（识别：总结 + .pdf）
    → rag_query(question="Linux.pdf 的主要内容是什么？")
    → Chroma 检索 Top-K
    → LLM 根据检索结果写总结
    → Answer（含 sources）
```

**不走 Filesystem MCP**——`Linux.pdf` 在 `uploads/` 里，但「总结」语义应走 **已向量化知识库**，不是裸读文件。

### 示例 2：读 README → Filesystem MCP

```
用户：「README 里面写了什么？」

Workflow 决策：
  intent = filesystem
  need_tool = true
  reason = 项目源码文件，走 Filesystem MCP

执行链：
  Question
    → Planner（识别：README + 写了什么）
    → mcp_read_file(path="README.md")
    → Filesystem MCP 读取沙箱内文件
    → LLM 根据文件内容回答
    → Answer
```

**不走 RAG**——README 是项目仓库里的 **源码文件**，不是 Chroma 知识库条目。

### 对比表

| 用户说法 | 意图 | 工具 | 为什么 |
|----------|------|------|--------|
| 总结 Linux.pdf | `rag` | `rag_query` | 知识库已向量化，检索+引用 |
| README 写了什么 | `filesystem` | `mcp_read_file` | 读项目根目录文件 |
| 计算 1+2 | `calculator` | `calculator` | 精确数学 |
| Linux.pdf 多少页 | `pdf_read` | `pdf_read` | PDF 元信息/按页读 |
| 你好 | `chat` | （无） | 不需要工具，Memory+LLM |
| 列出 docs 目录 | `filesystem` | `mcp_list_directory` | 列目录 |

---

## 意图分类（Intent）

新增 `app/agent/workflow.py`：

```python
from enum import Enum

class Intent(str, Enum):
    CHAT = "chat"                    # 无需工具，直接 LLM
    CALCULATOR = "calculator"        # 数学计算
    FILESYSTEM = "filesystem"        # MCP 读/列项目文件
    RAG = "rag"                      # 知识库问答/总结 PDF
    PDF_READ = "pdf_read"            # PDF 页数/按页读取
    MCP_EXPLICIT = "mcp_explicit"    # 显式 mcp xxx 命令
```

### 分类优先级（从高到低）

```
1. calculator        — 含计算关键词或纯算式
2. mcp_explicit      — 消息以/含「mcp <tool>」显式命令
3. filesystem        — README / .md/.py 等项目文件（非 PDF 总结）
4. pdf_read          — .pdf + 页数/读取/预览（非总结）
5. rag               — 总结/知识库/如何/什么 + 文档语义
6. chat              — 以上都不匹配
```

### 关键冲突规则（Day20 必须固化）

| 冲突场景 | 正确路由 | 规则 |
|----------|----------|------|
| 「总结 test.pdf」 | RAG | `.pdf` + `总结` → **rag**，优先于 filesystem |
| 「README 写了什么」 | Filesystem | `README` + `写了什么` → **filesystem**，优先于 rag（「什么」是 RAG 关键词） |
| 「读取 Linux.pdf 第 3 页」 | pdf_read | 按页读 → **pdf_read**，不是 rag |
| 「docs 有哪些文档」 | Filesystem | 列目录 → **mcp_list_directory** |

---

## 模块设计

### 新增 `app/agent/workflow.py`

```python
@dataclass
class WorkflowDecision:
    intent: Intent
    need_tool: bool
    steps: list[dict]          # 与现有 plan 步骤格式一致
    route: str                 # 人类可读路由说明，如 "Question → RAG → Answer"
    reason: str                # 决策原因

def classify(user_message: str) -> Intent: ...
def build_workflow(user_message: str) -> WorkflowDecision: ...
```

**逻辑：**

1. `classify()` — 只判断意图，不构造参数
2. `build_workflow()` — 调用 classify + 各 intent 的 plan builder，返回完整决策
3. `planner.plan()` — 变薄，仅 `return build_workflow(msg).steps`（或保留 plan 名，内部调 workflow）

### 改动 `app/agent/planner.py`

```python
# Day20 — Planner 委托给 Workflow 引擎
from app.agent.workflow import build_workflow

def plan(user_message: str) -> list[dict]:
    return build_workflow(user_message).steps
```

原有 `_needs_rag`、`_is_pdf_read` 等函数 **迁入 `workflow.py`**（或 workflow  import planner 私有函数，推荐前者收拢）。

### 改动 `app/agent/executor.py`

```python
from app.agent.workflow import build_workflow

def run_agent(user_message: str, session_id: str | None = None) -> dict:
    workflow = build_workflow(user_message)
    steps = workflow.steps
    ...
    return {
        ...
        "workflow": {
            "intent": workflow.intent.value,
            "need_tool": workflow.need_tool,
            "route": workflow.route,
            "reason": workflow.reason,
        },
    }
```

### 改动 `app/models/schemas.py`

```python
class AgentWorkflowInfo(BaseModel):
    intent: str = Field(..., description="意图：chat/rag/filesystem/...")
    need_tool: bool = Field(..., description="是否调用了工具")
    route: str = Field(..., description="路由链路说明")
    reason: str = Field(..., description="决策原因")

class AgentResponse(BaseModel):
    ...
    workflow: AgentWorkflowInfo | None = Field(None, description="工作流决策（Day20）")
```

---

## 目录结构（Day20 后）

```
app/agent/
├── workflow.py      # Day20 新增 — 意图分类 + 编排
├── planner.py       # Day20 变薄 — 委托 workflow
├── executor.py      # Day20 — 返回 workflow 元数据
├── memory.py
├── prompt.py
└── tools/
```

---

## `build_workflow` 伪代码

```python
def build_workflow(user_message: str) -> WorkflowDecision:
    intent = classify(user_message)

    if intent == Intent.CALCULATOR:
        steps = [_step_calculator(user_message)]
        return WorkflowDecision(
            intent=intent, need_tool=True, steps=steps,
            route="Question → Calculator → Answer",
            reason="数学计算意图",
        )

    if intent == Intent.MCP_EXPLICIT:
        step = plan_mcp_step(user_message)
        return WorkflowDecision(
            intent=intent, need_tool=True, steps=[step],
            route="Question → MCP → Answer",
            reason="用户显式指定 MCP 工具",
        )

    if intent == Intent.FILESYSTEM:
        step = plan_filesystem_step(user_message)
        return WorkflowDecision(
            intent=intent, need_tool=True, steps=[step],
            route="Question → Filesystem MCP → Answer",
            reason="读取/列出项目源码文件",
        )

    if intent == Intent.PDF_READ:
        steps = [_step_pdf_read(user_message)]
        return WorkflowDecision(
            intent=intent, need_tool=True, steps=steps,
            route="Question → PDF Tool → Answer",
            reason="PDF 页数或按页读取",
        )

    if intent == Intent.RAG:
        steps = [_step_rag(user_message)]
        return WorkflowDecision(
            intent=intent, need_tool=True, steps=steps,
            route="Question → RAG Search → Summary → Answer",
            reason="知识库检索与总结",
        )

    # CHAT
    return WorkflowDecision(
        intent=Intent.CHAT, need_tool=False, steps=[],
        route="Question → Memory → LLM → Answer",
        reason="无需工具，直接对话",
    )
```

---

## API 响应示例（Day20）

### RAG 总结 PDF

```json
{
  "message": "帮我总结 Linux.pdf",
  "answer": "Linux.pdf 主要介绍了……",
  "session_id": null,
  "workflow": {
    "intent": "rag",
    "need_tool": true,
    "route": "Question → RAG Search → Summary → Answer",
    "reason": "知识库检索与总结"
  },
  "plan": [
    {
      "tool": "rag_query",
      "args": { "question": "Linux.pdf 的主要内容是什么？" },
      "reason": "需要从知识库获取文档内容"
    }
  ],
  "tool_calls": [{ "tool": "rag_query" }],
  "sources": [{ "source": "Linux.pdf", "page": 1, "chunk": 1, "score": 0.75 }]
}
```

### Filesystem 读 README

```json
{
  "message": "README 里面写了什么？",
  "answer": "README 介绍了本项目是 30 天 AI 学习仓库……",
  "workflow": {
    "intent": "filesystem",
    "need_tool": true,
    "route": "Question → Filesystem MCP → Answer",
    "reason": "读取/列出项目源码文件"
  },
  "plan": [
    {
      "tool": "mcp_read_file",
      "args": { "path": "README.md" },
      "reason": "读取文件 README.md"
    }
  ],
  "tool_calls": [{ "tool": "mcp_read_file" }],
  "sources": []
}
```

### 纯闲聊

```json
{
  "message": "你好",
  "answer": "你好！我是企业知识库助手……",
  "workflow": {
    "intent": "chat",
    "need_tool": false,
    "route": "Question → Memory → LLM → Answer",
    "reason": "无需工具，直接对话"
  },
  "plan": [],
  "tool_calls": [],
  "sources": []
}
```

---

## 实现清单（待编码）

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 1 | `Intent` + `WorkflowDecision` + `classify` | `agent/workflow.py` | ✅ |
| 2 | `build_workflow` 统一编排 | `agent/workflow.py` | ✅ |
| 3 | Planner 委托 workflow | `agent/planner.py` | ✅ |
| 4 | Executor 返回 `workflow` 字段 | `agent/executor.py` | ✅ |
| 5 | `AgentWorkflowInfo` 模型 | `models/schemas.py` | ✅ |
| 6 | 冲突规则单测 / 联调两条示例 | 脚本或手动 | ✅ |
| 7 | 更新 api.md / CODEMAP / README | `docs/` | ✅ |

---

## 测试命令

### 前置

```powershell
# .env
MCP_ENABLED=true
MCP_FILESYSTEM_ROOT=E:/2026/learn/ai-project-assistant

# 知识库已入库 Linux.pdf（Sprint 2 流程）
ollama serve
python -m uvicorn app.main:app --reload
```

### 1. RAG 总结 PDF

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"帮我总结 Linux.pdf"}'
```

期望：`workflow.intent = "rag"`，`plan` 含 `rag_query`，`sources` 非空。

### 2. Filesystem 读 README

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"README 里面写了什么？"}'
```

期望：`workflow.intent = "filesystem"`，`plan` 含 `mcp_read_file`。

### 3. 纯闲聊

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"你好"}'
```

期望：`workflow.need_tool = false`，`plan = []`。

### 4. 模块自测（分类）

```powershell
python -c "
from app.agent.workflow import classify, build_workflow
cases = [
    '帮我总结 Linux.pdf',
    'README 里面写了什么',
    '计算 1+2',
    '你好',
]
for c in cases:
    w = build_workflow(c)
    print(c, '->', w.intent.value, w.route)
"
```

---

## 验收标准（Day20 完成定义）

- [x] 存在 `app/agent/workflow.py`，Planner 不再堆叠复杂 if-else
- [x] `classify` 能正确区分 rag / filesystem / chat 等意图
- [x] 「总结 Linux.pdf」→ `rag_query`，带 `sources`
- [x] 「README 里面写了什么」→ `mcp_read_file`（MCP 启用时）
- [x] 「你好」→ 无工具直答，`workflow.need_tool=false`
- [x] `POST /agent` 响应含 `workflow` 字段
- [x] 内置工具与 Day17 Memory 仍正常
- [ ] Git Commit：`feat(agent-workflow)`，Tag：`v0.3`

---

## 架构图（Sprint 3 完整）

```
                         POST /agent
                              │
                              ▼
                    ┌──────────────────┐
                    │  workflow.py     │  Day20
                    │  classify + plan │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         calculator    mcp_read_file    rag_query
         (Day16)       (Day18/19)       (Day16)
              │              │              │
              └──────────────┴──────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    executor      │  + Memory (Day17)
                    │  observation→LLM │
                    └────────┬─────────┘
                             ▼
                          Answer
                    + workflow 元数据
```

---

## 常见坑

1. **「什么」误触发 RAG** — README 类问题必须在 filesystem 规则里优先于 RAG 关键词
2. **PDF 总结误走 pdf_read** — 「总结 xxx.pdf」应走 rag，不是 pdf_read
3. **MCP 未启用** — filesystem 意图应降级为 chat 或友好提示，避免 plan 指向不存在工具
4. **README 全文过长** — 可选截断 `summary` 再喂 LLM（与 Day19 相同）
5. **workflow 与 plan 不一致** — `build_workflow` 应作为唯一真相源，planner 不要重复逻辑

---

## 收获（完成后填写）

- Workflow 让 Agent 决策过程 **可解释、可演示、可调试**
- RAG 与 Filesystem 分工：知识库 vs 项目源码
- `match_filesystem_intent` 与 MCP 在线状态解耦，避免「什么」误触发 RAG
- MCP 未启用时 filesystem 意图 **降级为 chat**，不崩溃

---

## 下一步

Day21 — Sprint Review + Release（`release(v0.3)`）：CHANGELOG、全链路验收、打 Tag `v0.3.0`
