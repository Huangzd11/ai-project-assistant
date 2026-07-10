# AI Solution Design

> 版本：**v1.0.0** | 架构结构视图见 [architecture.md](architecture.md)  
> **本文回答：为什么做？为什么这样选？风险与演进是什么？**  
> 面向：AI Solution / 技术项目经理评审与面试口述。

---

## 1. 项目背景

### 1.1 业务目标

构建可演示、可部署的 **企业 AI 项目助手**：

- 基于内部 **PDF 知识库** 做可溯源问答（RAG）
- 通过 **Agent + Tool** 完成天气、新闻、计算、读项目文件等任务
- 以 **统一 HTTP API + Web UI** 交付，并具备日志、成本等工程化能力

本仓库同时是 **30 天 AI 技术项目经理** 实战作品：从 LLM 接入一路做到 Compose / Nginx / Token 统计与方案文档。

### 1.2 用户与场景

| 角色 | 典型问题 |
|------|----------|
| 业务用户 | 「test.pdf 里怎么开 telnet？」「北京天气？」「README 写了什么？」 |
| 开发 / 演示 | 一键 `docker compose up`，浏览器打开 `http://localhost` |
| AI PM / Solution | 「1000 用户一天多少钱？」「为什么用 RAG 而不是微调？」 |

### 1.3 约束

| 维度 | 约束 |
|------|------|
| 团队 | 个人 / 小团队，优先可维护、可讲清 |
| 部署 | 本地 Docker Compose；LLM 支持本地 Ollama 与云端通义 |
| 数据 | 以 PDF 与项目文件为主，非海量向量检索集群 |
| 预算 | 开发期可控；生产需能估算 Token 成本（Day25） |

### 1.4 设计原则

1. **接口统一**：业务不绑定某一家模型（OpenAI Compatible）
2. **分层清晰**：API / Agent / RAG / 向量库可替换
3. **渐进演进**：先 chat，再 RAG，再 Agent/MCP，再工程化
4. **可观测**：Request ID、日志落盘、Token/Cost 可见
5. **可溯源**：知识库回答尽量带 `sources`，降低幻觉信任成本

---

## 2. 为什么需要知识库？

### 2.1 问题

企业文档（手册、规范、PDF）**不在公网模型训练语料里**，且会持续更新。若只用裸 LLM：

- 知识截止 / 不知道内部条款  
- 容易 **幻觉**（编造步骤、页码）  
- 无法给出「根据《xx》第 n 页」的引用  

### 2.2 方案对比

| 方案 | 优点 | 缺点 | 本项目结论 |
|------|------|------|------------|
| 纯 LLM | 实现简单 | 无内部知识、易幻觉 | 仅适合闲聊（`/chat`） |
| 全文塞进 Prompt | 实现快 | Token 爆炸、超上下文窗口 | **不可规模化** |
| Fine-tune | 风格/领域贴合 | 贵、慢、文档一变就要再训 | **不做** |
| **RAG** | 可更新、可引用、成本相对可控 | 依赖切块与检索质量 | **采用** |

### 2.3 面试一句话

> 企业 PDF 会变，我们要的是**可溯源的答案**，不是把模型再训练一遍。RAG 用检索把相关片段注入 Prompt，并用 `sources` 约束幻觉、控制 Token。

### 2.4 本项目 RAG 落点

```
Upload PDF → Parse → Chunk → Embed → Chroma
Question → Top-K → Prompt → LLM → Answer + sources
```

详情：[Day13.md](Day13.md)、[architecture.md](architecture.md) §5.1。

---

## 3. 技术选型

每项按统一结构：**场景 → 对比 → 理由 → 边界**。

### 3.1 FastAPI（HTTP 网关）

**场景：** 需要类型安全的 REST、自动 OpenAPI、后续 SSE 流式。

| 候选 | 适合 | 不适合本项目的点 |
|------|------|------------------|
| Flask | 极简脚本 | 校验与文档要自拼 |
| Django | 全栈 CMS | 对纯 API + AI 过重 |
| **FastAPI** | AI/API 服务、Pydantic、ASGI | — |

**选择理由：**

- Pydantic 契约清晰，Swagger 开箱即用（`/docs`）
- Uvicorn ASGI，天然适合 SSE（`/agent/stream`）
- 与 Python AI 生态（OpenAI SDK、Chroma、MCP）同语言栈

**边界：** 超高并发网关可再前置专用 LB；当前 Compose + Nginx 足够演示与中小流量。

### 3.2 Chroma（向量库）

**场景：** PDF Chunk 向量化后做 Top-K 语义检索，需可持久化、可 Docker 化。

| 候选 | 适合 | 不适合 |
|------|------|--------|
| FAISS | 本地极简实验 | 元数据/服务化弱 |
| **Chroma** | 学习与中小原型、Python 友好 | 超大规模集群运维 |
| Milvus / pgvector | 生产海量、强一致 | 对本阶段过重 |

**选择理由：**

- 嵌入式与 Server 双模式（本地 / Compose 已打通，Day22）
- 与 Embedding、元数据（source/page）集成简单
- 满足「可演示的企业知识库」而非亿级向量

**边界：** 数据量与 QPS 上去后，可迁移 pgvector/Milvus，检索接口保持 `search()` 抽象。

### 3.3 Ollama + 通义（双模 LLM）

**场景：** 开发要零/低成本试错；演示与生产要稳定、中文效果好。

| 候选 | 适合 | 代价 |
|------|------|------|
| **仅云端** | 效果稳 | 开发期 Token 费用、需网络与 Key |
| **仅 Ollama** | 离线、免费 API 费 | 机器要求、效果/速度参差 |
| **双模（本项目）** | 开发本地、演示可切通义 | 需维护一套 OpenAI 兼容封装 |

**选择理由：**

- `OPENAI_BASE_URL` 切换，业务代码不改（`app/core/llm.py`）
- Compose：默认读 `.env` 通义；`--profile local-llm` 启 Ollama
- 符合「先本地验证，再云端交付」的 PM 节奏

**边界：** 本地小模型能力有限；关键路径建议通义 `qwen-plus` 等，并用 Day25 看成本。

### 3.4 MCP（外部工具协议）

**场景：** 让 Agent 读取项目文件等能力，且不希望为每个数据源写一套私有插件协议。

| 候选 | 适合 | 不适合 |
|------|------|--------|
| 自研 HTTP 插件 | 完全可控 | 生态割裂、重复造轮子 |
| Function Calling 硬编码 | 简单工具 | 难跨产品复用 |
| **MCP** | 标准 Tools/Resources、可插拔 Server | 生态仍在演进 |

**选择理由：**

- 用标准 Client 接 Filesystem MCP（Day18/19），再 **bridge** 进现有 Tool Registry
- FastAPI 仍是对外唯一 HTTP 入口；MCP 是 Agent 的工具提供层，不替代网关
- 简历/面试可讲清「协议 vs 自研插件」的取舍

**边界：** 必须限制 `MCP_FILESYSTEM_ROOT` 沙箱；容器默认 `MCP_ENABLED=false`（无 Node 时）。

### 3.5 其他（点到为止）

| 技术 | 作用 |
|------|------|
| Nginx | 统一入口、静态资源、SSE 反代（Day23） |
| Docker Compose | 一键拉起 api + chroma + 可选 ollama（Day22） |
| React + Vite | 聊天 / 上传 / workflow / usage 展示（Day21） |
| OpenAI Compatible API | 行业标准调用形态，降低供应商锁定 |

---

## 4. 架构设计（摘要）

权威结构图与部署拓扑见 **[architecture.md](architecture.md)**。此处仅保留与方案评审一致的主链路：

```
Client → Nginx → FastAPI → Agent → RAG → Vector DB (Chroma) → LLM
                              └─ Tool Registry / MCP / …
                                    → Answer + sources + usage
```

| 能力阶段 | 版本 | 要点 |
|----------|------|------|
| LLM + API | v0.1 | FastAPI、Ollama/通义 |
| 企业 RAG | v0.2 | Upload → Chroma → `/rag` |
| Enterprise Agent | v0.3 | Workflow、Memory、MCP、Web、SSE |
| 工程化 | v0.4 → **v1.0** | Compose、Nginx、日志、Token、方案文档、README |

---

## 5. 风险与优化

### 5.1 Token 成本

| 项 | 说明 |
|----|------|
| **风险** | DAU 与上下文变长后，云端费用线性上升 |
| **现象** | 月账单超预期；Memory/RAG 把 Prompt 撑大 |
| **已有对策** | Day25：`usage`（prompt/completion/total）+ `cost_usd`；`GET /metrics/cost-estimate`；`scripts/estimate_cost.py` |
| **优化建议** | 裁剪 Short Memory 轮数；RAG Top-K 与 chunk 控长；路由用小模型、总结用大模型；本地 Ollama 做开发 |

**面试题口径（1000×20×3000）：**  
日成本 ≈ 拆分 Input/Output 后按单价估算（见 Day25），不要只用「平均 Token × 一个模糊单价」。

### 5.2 幻觉问题

| 项 | 说明 |
|----|------|
| **风险** | 模型编造文档内容或页码，用户误信 |
| **现象** | 无依据的「根据第 x 页」；知识库未命中仍强答 |
| **已有对策** | RAG system prompt 要求基于参考资料；无命中返回明确提示；响应带 `sources` |
| **优化建议** | 答案后处理校验引用；低分检索降权；关键场景人工抽检；评测集（后续） |

### 5.3 Chunk 大小优化

| 项 | 说明 |
|----|------|
| **现状** | 默认 `CHUNK_SIZE=500`，`CHUNK_OVERLAP=50`（可经 `.env` 调整） |
| **过大** | 单块噪声多、易超上下文、检索「看起来相关其实稀释」 |
| **过小** | 语义破碎、同一段落拆散、回答缺上下文 |
| **调参建议** | 先看坏例再改：问答不准 → 略增 chunk 或 overlap；总 Token 高 → 减 size 或 Top-K；按标题/页边界切优于纯固定长度（后续可增强） |

### 5.4 其他风险

| 风险 | 对策 |
|------|------|
| SSE 被 Nginx 缓冲，前端不「逐字」 | `proxy_buffering off`（Day23） |
| 密钥进 Git | `.gitignore` + `.env.example` |
| MCP 读盘越权 | `MCP_FILESYSTEM_ROOT` 沙箱；默认关闭 |
| 向量与模型漂移 | 换 Embedding 模型需重建索引 |
| Docker Hub 拉取失败 | 镜像加速 / 重试；开发可用本地 uvicorn |

---

## 6. 演进路线

```
v0.1  LLM + FastAPI + Docker
  ↓
v0.2  企业 RAG（PDF → Chroma → 引用）
  ↓
v0.3  Agent + Memory + MCP + Web + SSE
  ↓
v0.4    Compose + Nginx + 日志 + Token + 方案/架构 + README
  ↓
v1.0    工程与文档收官（当前）   ← 你在这里
  ↓
（可选）Day28~30 简历 / 面试 / 投递 — 暂不设计
```

**可选下一阶段（未承诺）：**

- RAG 评测集与回归  
- 多租户 / API Key  
- pgvector 或托管向量服务  
- OpenTelemetry 完整 Trace  
- Day28~30 求职材料（按需）

---

## 7. 面试口述提纲（5~10 分钟）

1. **背景**：内部 PDF 问答 + 工具型助手，不能只靠公网模型  
2. **为何 RAG**：可更新、可引用、比微调便宜；对比塞全文与纯 LLM  
3. **选型**：FastAPI 网关；Chroma 向量；Ollama/通义双模；MCP 接外部工具  
4. **架构**：Client → Nginx → FastAPI → Agent → RAG → Chroma → LLM  
5. **风险**：成本用 Token 计量；幻觉靠 sources；Chunk 可调参  

---

## 8. 相关文档

| 文档 | 用途 |
|------|------|
| [architecture.md](architecture.md) | 结构、链路、部署 |
| [CODEMAP.md](CODEMAP.md) | 文件级 Day 索引 |
| [roadmap.md](roadmap.md) | 进度与 Sprint |
| [Day13.md](Day13.md) | RAG 细节 |
| [Day22.md](Day22.md) ~ [Day27.md](Day27.md) | Sprint 4 工程日志 |
| [api.md](api.md) | 接口说明 |
| [CHANGELOG.md](CHANGELOG.md) | 版本记录 |
| [README.md](../README.md) | 快速开始 · v1.0 成果 |

---

*文档版本：v1.0.0 | 30 天收官*
