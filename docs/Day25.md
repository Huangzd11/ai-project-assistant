# Day25 — Token / 成本统计设计

> 版本：**v0.4-beta2** | 前置：**Day24 日志 + Request ID**、**Day15/21 Agent API**  
> **定位：AI PM 可观测 — 每次问答可回答「花了多少 Token、多少钱」**

## 学习目标

- [ ] 理解 **Prompt Tokens / Completion Tokens / Total Tokens** 的含义与计费关系
- [ ] 能从 OpenAI 兼容 API 的 `usage` 字段读取真实用量
- [ ] 能用 **单价表** 估算单次请求成本（Cost）
- [ ] 能回答面试高频题：**1000 用户 × 每天 20 次 × 平均 3000 Token → 一天多少钱？**
- [ ] 把用量挂到 API 响应、日志与（可选）前端展示

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| 单次请求 Token + Cost 统计 | 完整计费系统 / 发票 / 多租户账单 |
| 从 LLM `usage` 读取真实 Token | 自研 Tokenizer 精确对齐（仅作兜底） |
| 可配置单价表（`config/pricing.yaml`） | 实时拉取云厂商价格 API |
| `/agent`、`/agent/stream`、`/chat`、`/rag` 返回 usage | 全站历史报表 UI（可只做简单汇总 API） |
| 日成本估算公式 + 示例脚本/文档 | Prometheus / Grafana 大盘 |
| 日志字段 `tokens_in` / `tokens_out` / `cost_usd` | 按用户强制限流（Day25 可选预留） |

**Day25 核心成果：** 任意一次 Agent 问答，响应中可见：

```
本次请求：
  Input: 1450
  Output: 632
  Total: 2082
  Cost: $0.0038
```

并能用同一套数字，推算「1000 用户规模一天多少钱」。

---

## 为什么这是 AI PM 高频能力

技术项目经理在立项 / 评审时常被问：

1. **单次对话成本是多少？**
2. **DAU 上来后，月成本大概多少？**
3. **换更便宜的模型能省多少？**
4. **RAG / Memory 会不会把 Prompt 撑爆？**

没有 Token 统计，只能拍脑袋；有了统计，才能做：

- 模型选型（Turbo vs Plus vs Max）
- Prompt / 上下文裁剪
- 定价与毛利测算
- 容量与预算预警

---

## 核心概念

| 字段 | 含义 | 计费 |
|------|------|------|
| **Prompt Tokens**（Input） | 发给模型的输入：system + history + user + 工具结果 | 按输入单价 |
| **Completion Tokens**（Output） | 模型生成的回答 | 按输出单价（通常更贵） |
| **Total Tokens** | Input + Output | 用于上下文窗口与粗算 |
| **Cost** | 估算费用 | `input×单价_in + output×单价_out` |

```
Cost = (prompt_tokens / 1_000_000) × price_input_per_1M
     + (completion_tokens / 1_000_000) × price_output_per_1M
```

> 本项目默认用 **USD** 展示（面试/作品集通用）；人民币单价可在配置中换算或并列。

---

## 面试题：一天多少钱？

### 题面

> 1000 用户，每人每天 20 次问答，平均每次 3000 Token，一天多少钱？

### 解题框架（必须掌握）

```
日总 Token = 用户数 × 每人每日次数 × 平均 Token/次
日成本     = (日总 Token / 1_000_000) × 综合单价
```

**注意：** 真实计费是 Input/Output **分开**的。粗算时可用「综合单价」；精细算时要拆：

```
假设平均 3000 Token 中：Input 2000 + Output 1000
日 Input  = 1000 × 20 × 2000 = 40,000,000
日 Output = 1000 × 20 × 1000 = 20,000,000
日成本    = 40M × P_in + 20M × P_out
```

### 示例（qwen-plus 内地 ≤128K 档，示意）

配置默认（实现日以 `config/pricing.yaml` 为准，可随时改）：

| 项 | 值（示意） |
|----|------------|
| Input | ¥0.8 / 百万 Token ≈ **$0.11** / 百万（按 7.2 汇率粗换） |
| Output | ¥2.0 / 百万 Token ≈ **$0.28** / 百万 |

```
日 Input  = 40M → 40 × 0.8 = ¥32
日 Output = 20M → 20 × 2.0 = ¥40
日成本    ≈ ¥72
月成本    ≈ ¥72 × 30 ≈ ¥2,160
```

**PM 话术：**

> 「按当前 qwen-plus 单价，1000 DAU、人均 20 次、均 3k Token，粗算日成本约七十元量级；若 Output 占比升高或切到 Max，成本会明显上浮。我们会在每次请求里打点真实 usage，用一周线上数据校准预算。」

---

## 以前 vs 以后

### 以前（Day02 ~ Day24）

```python
response = client.chat.completions.create(...)
return response.choices[0].message.content  # usage 被丢弃
```

- 不知道每次花了多少 Token
- 无法回答成本题，只能查云控制台事后账单
- 流式接口更难拿到 usage

### 以后（Day25）

```
LLM 调用
  → 解析 usage（prompt / completion / total）
  → 查 pricing 表算 cost
  → 写入响应 usage 字段 + 日志
  → （可选）累加到 data/metrics/daily.json
```

---

## 目标架构

```
用户 → POST /agent
         │
         ▼
      run_agent()
         │
         ├─ chat_messages() ──► OpenAI 兼容 API
         │                         │
         │                         └─ usage: {prompt_tokens, completion_tokens, total_tokens}
         │
         ├─ TokenMeter.record(usage, model)
         │      └─ cost = pricing.estimate(...)
         │
         └─ AgentResponse.usage = {
                prompt_tokens, completion_tokens, total_tokens,
                cost_usd, model, currency
              }
```

流式路径：

```
chat_messages_stream(..., stream_options={"include_usage": True})
  → 最后一个 chunk 带 usage
  → SSE 事件 type=usage（在 done 前或并入 done）
```

---

## 数据模型设计

### `UsageInfo`（Pydantic）

```python
class UsageInfo(BaseModel):
    prompt_tokens: int = Field(..., description="Input / Prompt Tokens")
    completion_tokens: int = Field(..., description="Output / Completion Tokens")
    total_tokens: int = Field(..., description="合计")
    cost_usd: float = Field(..., description="估算成本（美元）")
    model: str = Field(..., description="计费所用模型名")
    currency: str = "USD"
```

### API 响应示例

**`POST /agent`：**

```json
{
  "message": "你好",
  "answer": "……",
  "session_id": "work-001",
  "workflow": { "...": "..." },
  "plan": [],
  "tool_calls": [],
  "sources": [],
  "usage": {
    "prompt_tokens": 1450,
    "completion_tokens": 632,
    "total_tokens": 2082,
    "cost_usd": 0.0038,
    "model": "qwen-plus",
    "currency": "USD"
  }
}
```

**`POST /agent/stream`（SSE）：**

```
event: ... workflow / plan / token ...
data: {"type":"usage","usage":{"prompt_tokens":1450,"completion_tokens":632,"total_tokens":2082,"cost_usd":0.0038,"model":"qwen-plus"}}
data: {"type":"done","answer":"...","usage":{...}, ...}
```

**展示文案（前端 / 文档）：**

```
本次请求：
  Input: 1450
  Output: 632
  Cost: $0.0038
```

### 同样挂到

| 接口 | 说明 |
|------|------|
| `POST /chat` | 单轮对话，最干净的 usage 样本 |
| `POST /rag` | 含检索上下文，Prompt 通常更大 |
| `POST /agent` | 主路径（含 Memory / Tool 结果） |
| `POST /agent/stream` | SSE `usage` 事件 |

---

## Token 采集设计

### 非流式（优先，最准）

OpenAI 兼容响应：

```json
{
  "usage": {
    "prompt_tokens": 1450,
    "completion_tokens": 632,
    "total_tokens": 2082
  }
}
```

改造 `app/core/llm.py`：

| 函数 | 现状 | Day25 |
|------|------|-------|
| `chat()` | 返回 `str` | 返回 `(str, UsageInfo)` 或内部写 Meter 后仍返回 str + 侧车 |
| `chat_messages()` | 返回 `str` | 同上 |
| `chat_messages_stream()` | yield `str` | yield 文本；结束时附带 usage（或回调） |

**推荐实现策略（改动可控）：**

1. 新增 `LLMResult(content: str, usage: UsageInfo | None)`
2. `chat` / `chat_messages` 改为返回 `LLMResult`（调用方解包）
3. 流式：`stream_options={"include_usage": True}`，最后一帧读 `chunk.usage`

> 若某本地 Ollama 版本不返回 usage：记 `usage=null` 或用字符粗估兜底，并在日志打 `event=usage_missing`。

### 流式 usage 注意

- DashScope / OpenAI：`stream=True` 时需显式 `stream_options={"include_usage": True}`
- 最后一个 chunk 可能 `choices=[]`，usage 在顶层
- 前端在 `done` 或独立 `usage` 事件展示即可

### Agent 多段 LLM 调用

当前 Agent 主路径通常 **1 次** 总结调用；若未来 Planner 也调 LLM：

```
request_usage = sum(各次 LLM usage)
```

Day25：**按「一次 HTTP 请求」聚合**，在 `TokenMeter` 用 request 级累加器（可挂 `contextvars`，与 Day24 Request ID 同生命周期）。

---

## 成本估算（Pricing）

### `config/pricing.yaml` 草案

```yaml
# 单价：美元 / 百万 Token（估算用，非账单权威）
# 汇率与官方价会变，以阿里云百炼控制台为准
default_model: qwen-plus
fx_cny_per_usd: 7.2

models:
  qwen-plus:
    input_per_1m_usd: 0.11    # ≈ ¥0.8 / 1M
    output_per_1m_usd: 0.28   # ≈ ¥2.0 / 1M
  qwen-turbo:
    input_per_1m_usd: 0.04
    output_per_1m_usd: 0.08
  qwen-max:
    input_per_1m_usd: 0.33
    output_per_1m_usd: 1.33
  # 本地 Ollama：成本记 0（电费/机器另算）
  qwen3:4b:
    input_per_1m_usd: 0.0
    output_per_1m_usd: 0.0
```

### `app/core/pricing.py`（设计）

```python
def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = load_pricing()[model]  # fallback default_model
    return (
        prompt_tokens / 1_000_000 * rates.input_per_1m_usd
        + completion_tokens / 1_000_000 * rates.output_per_1m_usd
    )
```

### 环境变量覆盖（可选）

```env
# Day25
PRICING_FILE=config/pricing.yaml
COST_CURRENCY=USD
```

---

## 日志与可观测（衔接 Day24）

```
INFO ... request_id=abc event=llm_usage model=qwen-plus
     prompt_tokens=1450 completion_tokens=632 total_tokens=2082 cost_usd=0.0038
```

- 与 `request_id` 同条链路，方便对账
- ERROR 路径无 usage 时不硬造数字

---

## 日成本估算工具（AI PM 交付物）

### 方式 A：文档公式（必做）

见上文「面试题」章节，写入 README / Day25 使用指南。

### 方式 B：简易 API（推荐做）

`GET /metrics/cost-estimate?users=1000&queries_per_user=20&avg_total_tokens=3000&input_ratio=0.67`

```json
{
  "users": 1000,
  "queries_per_user": 20,
  "avg_total_tokens": 3000,
  "input_ratio": 0.67,
  "model": "qwen-plus",
  "daily_prompt_tokens": 40000000,
  "daily_completion_tokens": 20000000,
  "daily_cost_usd": 10.0,
  "monthly_cost_usd": 300.0,
  "formula": "daily = users × qpu × (in×P_in + out×P_out)"
}
```

### 方式 C：脚本（可选）

```powershell
python scripts/estimate_cost.py --users 1000 --qpu 20 --avg-tokens 3000
```

---

## 前端展示（轻量）

在聊天气泡下方增加一行（不改整体布局风格）：

```
Input 1450 · Output 632 · Cost $0.0038
```

- 流式：收到 `usage` / `done.usage` 后渲染
- 无 usage（本地模型未返回）时隐藏该行

---

## 实现日文件清单（预览）

| 文件 | 职责 |
|------|------|
| `config/pricing.yaml` | 模型单价表 |
| `app/core/pricing.py` | 加载单价、估算 cost |
| `app/core/token_meter.py` | 请求级累加、构建 UsageInfo |
| `app/core/llm.py` | 解析 `usage`；流式 `include_usage` |
| `app/models/schemas.py` | `UsageInfo`；响应字段扩展 |
| `app/api/agent.py` / `chat.py` / `rag.py` | 返回 usage |
| `app/agent/executor.py` | 聚合并写入响应 / SSE |
| `app/api/metrics.py`（可选） | 日成本估算 API |
| `frontend/src/App.jsx` | 展示 Input/Output/Cost |
| `.env.example` | Day25 配置项 |
| `docs/Day25.md` | 设计 + 使用指南 + 面试题 |

---

## 验收标准

- [ ] `POST /agent` 响应含 `usage.prompt_tokens` / `completion_tokens` / `total_tokens` / `cost_usd`
- [ ] 日志中同 `request_id` 可看到 `event=llm_usage`
- [ ] `POST /agent/stream` 能拿到 usage（独立事件或 `done` 内）
- [ ] 更换 `pricing.yaml` 单价后，cost 随之变化
- [ ] 文档/API 能算出「1000×20×3000」日成本示例
- [ ] 前端（若实现）展示 Input / Output / Cost
- [ ] Ollama 无 usage 时不崩溃（null 或 0 + 警告日志）

---

## 测试命令（实现后）

```powershell
# 单次 Agent
Invoke-RestMethod -Uri http://localhost/agent -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"用一句话介绍你自己"}' | ConvertTo-Json -Depth 5

# 期望 usage:
# prompt_tokens / completion_tokens / total_tokens / cost_usd

# 日成本估算（若实现 metrics API）
Invoke-RestMethod "http://localhost/metrics/cost-estimate?users=1000&queries_per_user=20&avg_total_tokens=3000"

# 日志
Select-String -Path logs/app.log -Pattern "llm_usage" | Select-Object -Last 5
```

---

## 风险与对策

| 风险 | 对策 |
|------|------|
| 流式不返回 usage | `stream_options.include_usage`；不支持则标记 `usage=null` |
| 官方单价变更 | 单价放 yaml，文档注明「估算非账单」 |
| Agent 多次 LLM | request 级 Meter 累加 |
| 汇率波动 | 配置 `fx_cny_per_usd`；默认展示 USD |
| 泄露定价敏感信息 | 仅返回估算 cost，不返回 API Key |

---

## 与 Sprint 4 后续的关系

| Day | 衔接 |
|-----|------|
| Day24 | Request ID 串联 usage 日志 |
| Day26 架构文档 | 「可观测性」章节含 Token / Cost 数据流 |
| Day27 README | Quick Start 展示一次真实 usage 截图 |
| Day28 简历 | 关键词：Token 成本治理、AI 用量可观测 |

---

## 小结

Day25 把 LLM 调用从「只拿文本」升级为「文本 + **用量 + 成本**」。对 AI 技术项目经理而言，这不是锦上添花，而是能回答 **单次多少钱、规模化一天多少钱、换模型能省多少** 的基础能力。实现上优先打通 `usage` 采集与 `pricing` 估算，再挂到 Agent API / 日志 / 轻量前端与日成本估算公式。

---

## 使用指南（实现后）

### 单次请求 usage

```powershell
Invoke-RestMethod -Uri http://localhost/agent -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"用一句话介绍你自己"}' | ConvertTo-Json -Depth 5
```

响应示例字段：

```json
"usage": {
  "prompt_tokens": 1450,
  "completion_tokens": 632,
  "total_tokens": 2082,
  "cost_usd": 0.0038,
  "model": "qwen-plus",
  "currency": "USD"
}
```

前端气泡展示：`Input 1450 · Output 632 · Cost $0.0038`

### 日成本估算（面试题）

```powershell
# API
Invoke-RestMethod "http://localhost/metrics/cost-estimate?users=1000&queries_per_user=20&avg_total_tokens=3000"

# 脚本
python scripts/estimate_cost.py --users 1000 --qpu 20 --avg-tokens 3000
```

默认按 Input 占比 0.67 拆分，单价读 `config/pricing.yaml`。

### 实现文件清单

| 文件 | 职责 |
|------|------|
| `config/pricing.yaml` | 模型单价表 |
| `app/core/pricing.py` | 成本估算 |
| `app/core/token_meter.py` | UsageInfo 构建与日志 |
| `app/core/llm.py` | 解析 API usage；流式 include_usage |
| `app/api/metrics.py` | `GET /metrics/cost-estimate` |
| `frontend/src/App.jsx` | 展示 Input / Output / Cost |

### 验收清单

- [x] `/agent`、`/chat`、`/rag` 响应含 usage
- [x] `/agent/stream` 发 `usage` 事件并写入 `done`
- [x] 日志 `event=llm_usage`
- [x] `GET /metrics/cost-estimate` 可算 1000×20×3000
- [x] 前端展示本次请求成本
- [x] 无 usage 时不崩溃（warning + null）
