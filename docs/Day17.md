# Day17 — Memory（会话记忆）

> 版本：**v0.3-beta** | Commit：`feat(memory)`  
> **Sprint 3 第三天：Agent 能「记住」，支持多轮 Conversation**

## 学习目标

- [x] 理解 **无 Memory 的 Agent 每轮都会忘记**
- [x] 掌握 **Short Memory**（会话内短期记忆）与 **Long Memory**（跨会话长期记忆）
- [x] 实现 `memory.py`，支持 `session_id` 多轮对话
- [x] 将历史消息注入 LLM，使 Agent 能回答「你是谁」「我刚才说了什么」
- [x] 为 Day20 Conversation API 预留扩展点

---

## 完成内容

| 模块 | 职责 |
|------|------|
| `memory.py` | Short Memory（messages）+ Long Memory（facts）JSON 持久化 |
| `llm.chat_messages()` | 多轮 messages 调用 LLM |
| `executor.run_agent(session_id)` | 读 history → LLM → 写回 memory |
| `POST /agent` | 可选 `session_id` 请求/响应字段 |

**Long Memory：** 规则提取「我是xxx」→ `add_fact()`，注入 system prompt。

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| `app/agent/memory.py` | 向量记忆 / RAG 混合检索（Day22+） |
| Short Memory（会话历史） | MCP（Day18~19） |
| `session_id` + 消息持久化 | 复杂用户画像系统 |
| Long Memory 基础结构（可选写入） | 流式 SSE（Day22+） |
| `executor` / `llm` 接入历史 | 前端聊天 UI |

**Day17 核心成果：同一 `session_id` 下，Agent 能记住本轮对话上下文。**

---

## 为什么 Agent 必须有 Memory？

### 无 Memory（Day15~16 现状）

每次 `POST /agent` 都是**独立单轮**：

```
第 1 轮：用户「我是项目经理」 → Agent「好的」
第 2 轮：用户「我是谁？」       → Agent「我不知道」❌
```

`executor.run_agent(message)` 只传当前一句，`llm.chat()` 只有 system + 单条 user，**没有历史**。

### 有 Memory（Day17 目标）

```
第 1 轮：session_id=abc，用户「我是项目经理」 → 写入 Memory → 回答
第 2 轮：session_id=abc，用户「我是谁？」       → 读出历史 →「你是项目经理」✅
```

**明天还能记住吗？** 取决于 Short vs Long Memory（见下）。

---

## Short Memory vs Long Memory

```
                    Memory
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   Short Memory              Long Memory
   （会话内）                  （跨会话）
          │                       │
   本轮对话 history            用户画像 / 关键事实
   user + assistant 列表       「我是项目经理」
          │                       │
   关闭 session 可清空          持久化到磁盘，明天仍在
```

| 类型 | 存什么 | 生命周期 | Day17 |
|------|--------|----------|-------|
| **Short Memory** | 完整对话轮次 `{role, content}` | 同一 `session_id` 内 | ✅ 必做 |
| **Long Memory** | 提炼后的关键事实 `["用户是项目经理"]` | 跨 session / 跨天 | ⭕ 基础结构 |

### 示例（你的场景）

**今天（session: `work-001`）：**

```
用户：我是项目经理。
Agent：好的，已了解您的角色。
→ Short Memory 追加 2 条消息
→ Long Memory 可选写入 fact: "用户职业：项目经理"
```

**明天（新 session: `work-002`，但同一 user）：**

```
用户：你是谁？（指你知道我是谁吗）
```

- **仅 Short Memory**：新 session → 仍不知道 ❌
- **有 Long Memory**：读出 fact →「您之前提到您是项目经理」✅

Day17 **先做好 Short Memory**；Long Memory 用简单 JSON 存储 + `add_fact()` / `get_facts()` 接口打底即可。

---

## 在 Sprint 3 中的位置

```
Day15  Agent Core
Day16  Tool Registry
Day17  Memory + Conversation     ← 今天
Day18  MCP Client
Day20  企业 Workflow / Conversation 完善
```

---

## 新增模块：`app/agent/memory.py`

### 职责

| 函数 / 类 | 职责 |
|-----------|------|
| `ConversationMemory` | 管理单个 session 的消息列表 |
| `get_memory(session_id)` | 获取或创建会话记忆 |
| `append(session_id, role, content)` | 追加一条消息 |
| `get_messages(session_id, limit)` | 取出最近 N 轮用于 LLM |
| `clear(session_id)` | 清空会话（可选 API） |
| `add_fact(session_id, fact)` | Long Memory：写入关键事实（可选） |
| `get_facts(session_id)` | Long Memory：读取事实列表（可选） |

### 存储设计（学习项目）

```
data/
├── conversations/          # Short Memory
│   └── {session_id}.json
└── memory/                 # Long Memory（可选）
    └── {session_id}.json
```

**Short Memory JSON 示例：**

```json
{
  "session_id": "work-001",
  "messages": [
    { "role": "user", "content": "我是项目经理" },
    { "role": "assistant", "content": "好的，已了解。" }
  ],
  "updated_at": "2026-07-07T10:00:00"
}
```

**Long Memory JSON 示例：**

```json
{
  "session_id": "work-001",
  "facts": [
    "用户是项目经理"
  ]
}
```

Day17 可用**内存 dict + 可选落盘**；重启服务后仍记得则用 JSON 文件。

---

## Conversation 模型

一次 **Conversation** = 一个 `session_id` + 多条消息。

```
Conversation
├── session_id: str          # 客户端传入或服务端生成
├── messages: list[dict]     # Short Memory
└── facts: list[str]         # Long Memory（可选）
```

**HTTP 契约扩展：**

```json
// 请求
{
  "message": "我是谁？",
  "session_id": "work-001"
}

// 响应
{
  "message": "我是谁？",
  "answer": "您是项目经理。",
  "session_id": "work-001",
  "plan": [],
  "sources": []
}
```

`session_id` 可选：不传则每次新会话（兼容 Day15~16）；传入则多轮记忆。

---

## 与现有模块的集成

### 1. `llm.py` — 支持多轮 messages

当前 `chat(message)` 只有单条 user。Day17 需增加：

```python
def chat_messages(
    messages: list[dict],
    system_prompt: str | None = None,
) -> str:
    # messages 已含 history + 当前 user，前面加 system
```

参考 Day02 `examples/chat_demo.py` 的 `messages` 列表模式。

### 2. `executor.py` — 读写的位置

```
run_agent(message, session_id=None)
  │
  ├─ 1. memory = get_memory(session_id)
  ├─ 2. history = memory.get_messages(limit=MEMORY_MAX_TURNS)
  ├─ 3. facts = memory.get_facts()  # Long Memory 注入 system 或首条 user
  ├─ 4. plan → tools → answer（与 Day16 相同）
  ├─ 5. memory.append("user", message)
  └─ 6. memory.append("assistant", answer)
```

**历史注入方式（二选一）：**

| 方案 | 做法 | 推荐 |
|------|------|------|
| A | `chat_messages(history + [当前 user])` | ✅ 标准 |
| B | 把 history 拼进单条 user 字符串 | 入门可用 |

有工具调用时：当前轮 user 仍是本次 `message`；工具 Observation 拼进 assistant 前的 user 或单独 assistant 消息（Day17 可简化：工具路径仍用 Observation prompt，但**前后轮**走 history）。

### 3. `api/agent.py` — 接收 session_id

`AgentRequest` 增加可选字段 `session_id: str | None`。

### 4. `config.py` — 配置项

```python
MEMORY_DIR = "data/conversations"
MEMORY_MAX_TURNS = 10          # Short Memory 最多保留几轮（user+assistant 算 2 条）
MEMORY_ENABLE_LONG = False     # Day17 可先 False，接口预留
```

---

## 端到端流程

```
Client                    Agent                     Memory
  │                         │                          │
  │ POST /agent             │                          │
  │ session_id=work-001     │                          │
  │ message="我是项目经理"   │                          │
  ├────────────────────────►│ get_messages(work-001)   │
  │                         ├─────────────────────────►│ []
  │                         │ plan → tool → llm        │
  │                         │ append user + assistant  │
  │                         ├─────────────────────────►│ 保存 2 条
  │◄────────────────────────┤                          │
  │                         │                          │
  │ POST /agent             │                          │
  │ session_id=work-001     │                          │
  │ message="我是谁？"       │                          │
  ├────────────────────────►│ get_messages(work-001)   │
  │                         ├─────────────────────────►│ [user, assistant, ...]
  │                         │ llm 带 history 回答       │
  │◄────────────────────────┤「您是项目经理」          │
```

---

## 实现清单（待编码）

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 1 | `ConversationMemory` + 文件读写 | `agent/memory.py` | ✅ |
| 2 | `MEMORY_DIR` / `MEMORY_MAX_TURNS` 配置 | `config.py` | ✅ |
| 3 | `chat_messages()` 多轮 LLM | `core/llm.py` | ✅ |
| 4 | `run_agent(message, session_id)` | `executor.py` | ✅ |
| 5 | `session_id` 请求/响应模型 | `schemas.py` | ✅ |
| 6 | `POST /agent` 接入 session | `api/agent.py` | ✅ |
| 7 | Long Memory `facts` 接口（可选） | `memory.py` | ✅ |
| 8 | 多轮联调：「我是项目经理」→「我是谁」 | — | ✅ |

---

## 测试命令（设计）

```powershell
# 模块：Memory 读写
python -c "
from app.agent.memory import get_memory
m = get_memory('test-session')
m.append('user', '我是项目经理')
m.append('assistant', '好的')
print(m.get_messages())
"

# HTTP 多轮
python -m uvicorn app.main:app --reload

# 第 1 轮
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post -ContentType application/json `
  -Body '{"message":"我是项目经理","session_id":"work-001"}'

# 第 2 轮（同一 session_id）
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent -Method Post -ContentType application/json `
  -Body '{"message":"我是谁？","session_id":"work-001"}'
```

**期望：** 第 2 轮回答能体现「项目经理」，而非「我不知道」。

---

## 验收标准（Day17 完成定义）

- [x] `memory.py` 实现 Short Memory 读写
- [x] `POST /agent` 支持可选 `session_id`
- [x] 同一 `session_id` 连续两轮，第二轮能利用第一轮上下文
- [x] `MEMORY_MAX_TURNS` 限制历史长度，防止 token 爆炸
- [x] 不传 `session_id` 时行为与 Day16 兼容（单轮无记忆）
- [x] Long Memory 接口预留（`facts` 读写 + 「我是xxx」规则提取）
- [ ] Git Commit：`feat(memory)`，Tag：`v0.3-beta`

---

## 每日收尾

- [x] 更新 Day17.md、api.md、CODEMAP、roadmap
- [ ] Git Commit：`feat(memory)`
- [ ] Tag：`v0.3-beta`

---

## 架构图

```
POST /agent { message, session_id? }
        │
        ▼
┌───────────────┐     ┌─────────────────┐
│  executor.py  │◄───►│   memory.py     │
│  run_agent()  │     │ Short / Long    │
└───────┬───────┘     └────────┬────────┘
        │                      │
        │               data/conversations/
        ▼
┌───────────────┐
│  llm.py       │
│ chat_messages │  ← history + 当前 user
└───────────────┘
```

---

## 常见坑

1. **只存 user 不存 assistant** — 历史不完整，LLM 上下文断裂
2. **session_id 每次随机** — 客户端需固定传同一 id
3. **历史无限增长** — 必须 `MEMORY_MAX_TURNS` 截断
4. **工具路径忘记写 Memory** — 有 tool 和无 tool 分支都要 append
5. **并发写同一 JSON** — Day17 单进程可忽略；生产需锁或 DB

---

## 收获（完成后填写）

- Memory 是 Agent「像人」的关键，Tool 解决「能做」，Memory 解决「记得」
- Short Memory = 会话上下文；Long Memory = 跨天用户画像
- `session_id` 是 Conversation 的钥匙

---

## 下一步

Day18 — MCP Client（`feat(mcp-client)` · v0.3-beta2）
