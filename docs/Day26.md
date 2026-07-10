# Day26 — 架构设计文档（设计）

> 版本：**v0.4-rc** | 前置：**Day22~25 工程化**、**Day13 RAG**、**Day15~21 Agent**  
> **定位：AI Solution 能力 — 用两份文档讲清「为什么做、怎么做、风险在哪」**

## 学习目标

- [ ] 能写清 **项目背景** 与 **为什么需要知识库（RAG）**
- [ ] 能论证 **FastAPI / Chroma / Ollama / MCP** 的选型理由（对比备选）
- [ ] 能画出 **Client → FastAPI → Agent → RAG → Vector DB** 主链路
- [ ] 能识别并给出对策：**Token 成本、幻觉、Chunk 大小** 等风险
- [ ] 理解 Solution 岗文档与「日记式 DayXX.md」的区别：面向评审 / 面试 / 交付

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| 新增 `docs/architecture.md`（架构视图） | 重写全部 Day01~25 日记 |
| 升级 `docs/solution-design.md`（方案决策） | 画复杂 UML / C4 全套工具链 |
| 统一主链路图 + 部署图 + 风险表 | 新功能开发 |
| 与 README / CODEMAP 交叉引用 | 商业 BRD / 完整 PRD |

**Day26 核心成果：** 面试或方案评审时，打开两份文档即可讲完：背景 → 选型 → 架构 → 风险。

---

## 两份文档如何分工

仓库里已有早期 `docs/solution-design.md`（偏雏形，链路仍停在部分旧图）。Day26 **不另起炉灶重复三遍**，而是明确分工：

| 文档 | 读者 | 回答的问题 | 语气 |
|------|------|------------|------|
| **`architecture.md`** | 工程师 / 架构面试官 | **系统长什么样？请求怎么走？模块边界？** | 结构、图、分层、数据流 |
| **`solution-design.md`** | Solution / PM / 评审 | **为什么这样选？业务价值？风险与演进？** | 决策、对比、取舍、路线图 |

```
solution-design.md          architecture.md
（Why / What / Trade-off）    （How / Where / Flow）
        │                           │
        └──────────┬────────────────┘
                   ▼
            作品集 / 面试 / Day27 README 入口
```

**原则：**

- 架构图、模块表、部署拓扑 → 以 `architecture.md` 为权威
- 选型理由、知识库必要性、风险与优化、演进路线 → 以 `solution-design.md` 为权威
- 已有 `solution-design.md`：**重构升级到 v0.4-rc**，删掉过时「仅 Browser→Ollama」表述，对齐当前 Agent + Nginx + Token

---

## 目标交付物大纲

### A. `docs/architecture.md`（新建）

建议目录：

```markdown
# Architecture — AI Project Assistant

1. 文档目的与范围
2. 系统上下文（谁调用谁）
3. 逻辑架构（分层）
4. 主请求链路（必须有）
   Client → Nginx → FastAPI → Agent → RAG → Vector DB → LLM
5. 关键子链路
   - 文档入库：Upload → Parse → Chunk → Embed → Chroma
   - 工具调用：Workflow → Tool Registry → MCP / Weather / …
   - 流式：SSE /agent/stream
6. 部署架构（Compose：nginx / api / chroma / ollama）
7. 横切能力：日志 Request ID、Token usage、配置分层
8. 目录与模块映射（链到 CODEMAP.md）
9. 非目标 / 边界
```

**主链路图（实现日必须出现）：**

```
Client (Browser / curl)
    │
    ▼
Nginx (:80)                 ← 静态资源 + 反代
    │
    ▼
FastAPI (api:8000)
    │
    ▼
Agent (workflow + executor + memory)
    │
    ├─► Tool Registry ──► MCP / Weather / News / …
    │
    └─► RAG Pipeline
            │
            ▼
        Vector DB (Chroma)
            │
            ▼
        Top-K chunks → Prompt → LLM (Ollama / 通义)
            │
            ▼
        Answer + sources + usage(cost)
```

**部署图（简）：**

```
┌─ docker compose ─────────────────────────┐
│  nginx ──► api ──► chroma                │
│              └──► ollama (profile)       │
│              └──► 通义 API（外网）         │
└──────────────────────────────────────────┘
```

---

### B. `docs/solution-design.md`（升级）

建议目录（覆盖你点名的内容）：

```markdown
# AI Solution Design（v0.4-rc）

1. 项目背景
   1.1 业务目标（企业知识助手 + Agent）
   1.2 用户与场景
   1.3 约束（个人/小团队、本地+云双模）

2. 为什么需要知识库？
   - 纯 LLM：知识截止、易幻觉、无法引用内部 PDF
   - RAG：可更新、可溯源、可控成本
   - 对比表：Fine-tune / 长上下文塞全文 / RAG

3. 技术选型（Why）
   3.1 FastAPI（vs Flask / Django）
   3.2 Chroma（vs FAISS / Milvus / pgvector）
   3.3 Ollama（vs 仅云端；与通义切换策略）
   3.4 MCP（vs 自研插件协议）
   3.5 其他：Nginx、Compose、React（点到为止）

4. 架构设计（摘要 + 指向 architecture.md）
   - 主链路 ASCII 图（与 architecture 一致，避免两套图）

5. 风险与优化
   5.1 Token 成本（Day25 计量、模型降级、上下文裁剪）
   5.2 幻觉（强制引用、无命中拒答、sources）
   5.3 Chunk 大小（500/50 现状、过大过小症状、调参建议）
   5.4 其他：SSE 缓冲、向量漂移、MCP 安全沙箱

6. 演进路线（v0.4 → v1.0 → 可选多租户/评测）
7. 相关文档索引
```

---

## 「为什么需要知识库」设计要点（实现日必写透）

| 方案 | 优点 | 缺点 | 本项目结论 |
|------|------|------|------------|
| 纯 LLM | 简单 | 无内部知识、幻觉 | 仅适合闲聊 |
| 全文塞进 Prompt | 实现快 | Token 爆、超窗口 | 不可规模化 |
| Fine-tune | 风格/领域贴合 | 贵、慢、难更新 | 不做 |
| **RAG** | 可更新、可引用、成本可控 | 检索质量依赖切块/向量 | **采用** |

一句话（面试）：

> 「企业 PDF 会变，我们要的是**可溯源的答案**，不是把模型再训练一遍；RAG 用检索把相关片段注入 Prompt，并用 sources 约束幻觉。」

---

## 技术选型论证模板（每项统一结构）

实现日对 FastAPI / Chroma / Ollama / MCP 均按同一模板写：

1. **场景需求**（要解决什么）
2. **候选对比**（2~3 个备选）
3. **选择理由**（3~5 条）
4. **代价 / 何时换掉**（诚实写边界）

示例（Chroma）：

| 候选 | 适合 | 不适合 |
|------|------|--------|
| FAISS | 本地极简 | 缺元数据/服务化 |
| **Chroma** | 学习/中小原型、易持久化 | 超大规模集群 |
| Milvus / pgvector | 生产海量 | 运维重 |

本项目选 Chroma：与 Python 栈契合、Compose 可 Server 模式、满足 PDF 知识库原型。

---

## 风险与优化（实现日表格骨架）

| 风险 | 现象 | 对策（已有 / 建议） |
|------|------|---------------------|
| **Token 成本** | 用户↑费用↑ | Day25 usage + cost-estimate；裁剪 Memory；小模型做路由 |
| **幻觉** | 编造页码/条款 | RAG 无命中拒答；回答要求引用；返回 sources |
| **Chunk 过大** | 检索噪声、超上下文 | 减小 `CHUNK_SIZE`，提高 Top-K 质量 |
| **Chunk 过小** | 语义破碎 | 增大 chunk / overlap；按标题切 |
| SSE 被缓冲 | 流式「卡住」 | Nginx `proxy_buffering off`（Day23） |
| 密钥泄露 | .env 进 Git | `.gitignore` + `.env.example` |
| MCP 读盘越权 | 工具读到敏感路径 | `MCP_FILESYSTEM_ROOT` 沙箱 |

---

## 与现有文档的关系

| 现有 | Day26 动作 |
|------|------------|
| `docs/solution-design.md` | **升级重写**核心章节，版本标 v0.4-rc |
| `docs/architecture.md` | **新建** |
| `docs/CODEMAP.md` | 仅交叉链接，不重复贴全目录 |
| `docs/Day13/15/22~25.md` | 作为细节附录链接 |
| `README.md` | Day27 再包装；Day26 可加一行「架构见 docs/…」 |

---

## 实现日文件清单

| 文件 | 动作 |
|------|------|
| `docs/Day26.md` | 本设计 + 实现后验收说明 |
| `docs/architecture.md` | **新建** |
| `docs/solution-design.md` | **升级** |
| `docs/roadmap.md` | Day26 标完成 |
| `README.md` | 可选：增加 Architecture 链接（轻量） |

---

## 验收标准

- [ ] 存在 `docs/architecture.md`，含主链路 **Client → FastAPI → Agent → RAG → Vector DB**
- [ ] `docs/solution-design.md` 含：项目背景、为何知识库、FastAPI/Chroma/Ollama/MCP 选型、风险与优化
- [ ] 两份文档无互相矛盾的旧架构描述（如「仅有单轮 chat」）
- [ ] 风险表至少覆盖：**Token 成本、幻觉、Chunk 大小**
- [ ] 可被用于 5~10 分钟 Solution 面试口述提纲

---

## 面试口述提纲（设计附赠）

1. **背景**：企业要问内部 PDF，不能只靠公网模型  
2. **为何 RAG**：可更新、可引用、比微调便宜  
3. **选型**：FastAPI 网关；Chroma 向量；Ollama/通义双模；MCP 接外部工具  
4. **架构**：Client→Nginx→FastAPI→Agent→RAG→Chroma→LLM  
5. **风险**：成本用 Day25 计量；幻觉靠 sources；Chunk 可调参  

---

## 小结

Day26 不写新功能，而是把 Sprint 1~4 的工程成果 **沉淀为 Solution 文档资产**：`architecture.md` 讲清结构与数据流，`solution-design.md` 讲清决策与风险。这是 AI 技术项目经理 / Solution 岗位的核心表达能力——能画图、能对比、能谈取舍。

---

## 使用指南（实现后）

### 交付物

| 文件 | 说明 |
|------|------|
| [architecture.md](architecture.md) | 主链路、分层、部署、横切能力 |
| [solution-design.md](solution-design.md) | 背景、为何知识库、选型、风险、演进 |
| 本文 | 设计过程与验收 |

### 怎么读（面试前 10 分钟）

1. 打开 `solution-design.md` §1~3、§5、§7（背景 → 选型 → 风险 → 口述提纲）  
2. 打开 `architecture.md` §4~6（主链路 + 部署）  
3. 需要抠代码时再看 `CODEMAP.md`

### 验收清单

- [x] `docs/architecture.md` 含 Client → FastAPI → Agent → RAG → Vector DB
- [x] `docs/solution-design.md` 含背景、知识库必要性、FastAPI/Chroma/Ollama/MCP、风险（Token/幻觉/Chunk）
- [x] 已去除过时「仅单轮 chat / 仅 v0.2」权威表述
- [x] README 增加架构/方案入口链接
- [x] roadmap 标记 Day26 完成
