# Roadmap

> **第一个月（Day01~30）**：AI Project Assistant **v1.0.0** 已收官 · 工程与文档完成  
> **第二个月（Day31~60）**：升维阶段 · 补原理 / 生产架构 / Solution / 面试表达 · **以理解为主，不大写新功能**

---

## 两个月总览

| 阶段 | 天数 | 定位 | 状态 |
|------|------|------|------|
| 第一个月 | Day01~30 | **AI Application Engineer** — 动手做项目 | ✅ v1.0.0 |
| 第二个月 | Day31~60 | **Technical PM → Solution Architect** — 懂原理、讲方案、过面试 | 📋 规划中 |

### 能力进阶路径（第二个月目标）

```
AI Application Engineer        ← 第一个月（Day01~30 · 已完成）
        ↓
AI Technical PM                ← Sprint 5~6（原理 + 生产架构）
        ↓
AI Solution Architect          ← Sprint 7~8（方案设计 + 面试表达）
```

---

## 最终成果对照（第一个月 · v1.0）

| 类别 | 能力 | 状态 |
|------|------|------|
| 技术 | LLM · Prompt · FastAPI · Docker · RAG · Embedding · Vector DB · Agent · MCP | ✅ |
| 项目 | 方案设计 · 技术选型 · 成本评估 · 风险分析 · 项目交付 | ✅ |
| 产出 | GitHub 项目 · 架构图 · README · mindmap | ✅ |

### 第二个月目标成果（Day60 对照）

| 类别 | 能力 | 状态 |
|------|------|------|
| 原理 | Transformer / 推理 / 幻觉 / RAG vs 微调选型 | 📋 |
| 生产 | 高可用 / 缓存限流 / 观测 / 安全（对照 v1.0 差距） | 📋 |
| 方案 | 完整 Solution 叙事 · 架构图 · 评审话术 | 📋 |
| 求职 | 简历 · STAR · 模拟面试 · Demo 脚本 | 📋 |

---

## Sprint 1（v0.1.x）— 基础链路

- [x] Day01 LLM Basic
- [x] Day02 OpenAI API
- [x] Day03 Ollama
- [x] Day04 FastAPI
- [x] Day05 Docker
- [x] Day06 GitHub
- [x] Day07 Review

## Sprint 2（v0.2.x）— Enterprise RAG

- [x] Day08 Upload + Refactor — `feat(upload)` — v0.2.0-alpha
- [x] Day09 PDF Loader — `feat(pdf-loader)` — v0.2.0-alpha2
- [x] Day10 Chunker — `feat(chunker)` — v0.2.0-beta
- [x] Day11 Embedding — `feat(embedding)` — v0.2.0-beta2
- [x] Day12 ChromaDB — `feat(vector-db)` — v0.2.0-rc
- [x] Day13 RAG Pipeline — `feat(rag)` — v0.2.0
- [x] Day14 Enterprise Release — `release: v0.2 enterprise rag` — v0.2.0

---

## Sprint 3（v0.3.x）— Enterprise AI Agent

> 在 Sprint 2 RAG 知识库之上，构建可规划、可调工具、可记记忆的企业级 Agent。

**目标架构：**

```
用户 → AI Project Assistant
         ├── Chat
         ├── RAG 知识库
         └── Memory
               ↓
         Agent Planner
               ↓
         Tools（PDF / Search / MCP …）
               ↓
            LLM → Answer
```

**目标模块结构：**

```
AI Project Assistant
├── Chat
├── Knowledge Base
├── Agent
├── MCP
└── Tools
```

| Day | 功能 | Git Commit | 版本 |
|-----|------|------------|------|
| Day15 | Agent 基础 + Function Calling | `feat(agent-core)` | v0.3-alpha |
| Day16 | Tool 管理 | `feat(tools)` | v0.3-alpha2 |
| Day17 | Memory | `feat(memory)` | v0.3-beta |
| Day18 | MCP 基础（Client） | `feat(mcp-client)` | v0.3-beta2 |
| Day19 | 真实 MCP Server（Filesystem） | `feat(mcp-server)` | v0.3-rc |
| Day20 | 企业 Agent Workflow | `feat(agent-workflow)` | v0.3 |
| Day21 | Sprint Review + Release | `release(v0.3)` | Release |

**Backlog：**

- [x] Day15 Agent Core — `feat(agent-core)` — v0.3-alpha
- [x] Day16 Tool Registry — `feat(tools)` — v0.3-alpha2
- [x] Day17 Memory — `feat(memory)` — v0.3-beta
- [x] Day18 MCP Client — `feat(mcp-client)` — v0.3-beta2
- [x] Day19 Filesystem MCP — `feat(mcp-server)` — v0.3-rc
- [x] Day20 Agent Workflow — `feat(agent-workflow)` — v0.3
- [x] Day21 Review + Release — `release(v0.3)` — v0.3.0
- [x] Day21_1 Web 前端 — `feat(frontend)` — v0.3.0+
- [x] Day21_2 实时 Tool + SSE — `feat(live-tools,stream)` — v0.3.2

---

## Sprint 4（v1.0）— Engineering + Interview

> **主题：** 从「能跑的 Agent」到「能部署、能演示、能写进简历、能讲方案、能面试」的完整交付物。  
> **Release：** AI Project Assistant **v1.0**

### Goal

完成 **v1.0 Release**，达到：

| 维度 | 标准 |
|------|------|
| 可以部署 | Docker Compose 一键启动，Nginx 反代，配置可管理 |
| 可以演示 | 浏览器完整链路可复现，有固定 Demo 脚本 |
| 可以写进简历 | README / 作品集包装到位，亮点可量化 |
| 可以讲技术方案 | 有架构设计文档，能画链路、讲权衡 |
| 可以应对 AI 创业公司面试 | 模拟面试 + 项目故事线熟练 |

### v1.0 最终项目能力

```
AI Project Assistant
├── Chat
├── RAG
├── Agent
├── MCP
├── Docker
├── Logging
├── Monitoring
├── Deployment
├── README
├── Architecture
└── Demo
```

### 演示主链路（Demo Flow）

```
上传 PDF → 提问 → RAG 检索 → Agent 调用工具 → 返回答案 + 引用来源
```

浏览器端已具备聊天、上传、workflow / sources 展示与 SSE 流式输出（Day21_1 / Day21_2）；Sprint 4 已完成**工程化补齐**与**作品集包装**，工程版本定为 **v1.0.0**。

### Backlog

| Day | 主题 | 输出 | 版本 |
|-----|------|------|------|
| Day22 | Docker Compose | 一键启动（API + Chroma + Ollama） | v0.4-alpha ✅ |
| Day23 | Nginx + Reverse Proxy | 部署能力（反代、静态资源、生产入口） | v0.4-alpha2 ✅ |
| Day24 | 日志 + 配置管理 | 工程化（结构化日志、环境分层） | v0.4-beta ✅ |
| Day25 | Token / 成本统计 | AI PM 能力（用量可观测、成本估算） | v0.4-beta2 ✅ |
| Day26 | 架构设计文档 | Solution 能力（方案文档、架构图） | v0.4-rc ✅ |
| Day27 | README + GitHub 包装 | 作品集（徽章、Quick Start） | v0.4 ✅ |
| — | **工程收官** | 版本对齐、成果清单 | **v1.0.0** ✅ |
| Day28~30 | 简历 / 面试 / 投递（可选） | 并入第二个月 Sprint 8 | ⏸ → Sprint 8 |

- [x] Day22 Docker Compose — `feat(docker-compose)` — v0.4-alpha — [Day22.md](Day22.md)
- [x] Day23 Nginx 反代 — `feat(nginx)` — v0.4-alpha2 — [Day23.md](Day23.md)
- [x] Day24 日志与配置 — `feat(logging,config)` — v0.4-beta — [Day24.md](Day24.md)
- [x] Day25 Token / 成本 — `feat(token-metrics)` — v0.4-beta2 — [Day25.md](Day25.md)
- [x] Day26 架构文档 — `docs(architecture)` — v0.4-rc — [Day26.md](Day26.md) · [architecture.md](architecture.md) · [solution-design.md](solution-design.md)
- [x] Day27 README / GitHub — `docs(readme,portfolio)` — v0.4 — [Day27.md](Day27.md) · [README.md](../README.md)
- [x] **v1.0.0 Release** — 工程与文档收官 — [CHANGELOG.md](CHANGELOG.md)

### Sprint 4 与 Sprint 3 的分工

| Sprint 3（已完成） | Sprint 4（已完成 → v1.0） |
|-------------------|---------------------------|
| Agent / Workflow / Tool / MCP / RAG 核心能力 | Compose / Nginx / 部署 |
| Web UI + SSE 流式 | 日志、Token 成本 |
| 实时 Tool（天气 / 新闻 / 体育） | 架构文档、README 包装 ✅ |
| v0.3.x 功能交付 | **v1.0.0 工程收官** |

---

## 第二个月（Day31~60）— 升维：原理 · 生产 · 方案 · 面试

> **主题：** 在 **AI Project Assistant v1.0** 之上升维，不另起炉灶做大项目。  
> **方式：** 以「理解 + 文档 + 表达」为主；必要时做小实验或文档增补，**默认不大规模写新功能**。  
> **载体：** 仍以本仓库为案例，对照 Day01~27 已实现能力做原理解读与方案深化。

### 四个 Sprint 总览

| Sprint | 主题 | 核心目标 | 天数 |
|--------|------|----------|------|
| Sprint 5 | LLM 基础与推理机制 | **补基础** — 从「会调 API」到「懂模型在干什么」 | Day31~38 |
| Sprint 6 | 生产级 AI 架构 | **工程化升级** — 从「本地能跑」到「想象线上怎么扛」 | Day39~45 |
| Sprint 7 | AI Solution 设计 | **架构与方案** — 从「有项目」到「能独立出方案、过评审」 | Day46~52 |
| Sprint 8 | 面试与商业化表达 | **跳槽冲刺** — 从「会做」到「能讲、能卖、能过面」 | Day53~60 |

### 第一个月 vs 第二个月

| 维度 | 第一个月（Day01~30） | 第二个月（Day31~60） |
|------|----------------------|----------------------|
| 主线 | 实现 AI Project Assistant | 解读与升维同一项目 |
| 产出 | 代码 · 部署 · Demo · README | 原理笔记 · 方案文档 · 面试材料 |
| 角色 | Application Engineer | Technical PM / Solution Architect |
| Day 文档 | `docs/DayXX.md` + 实现 | `docs/DayXX.md` 以学习笔记为主（待写） |
| 思维导图 | [mindmap/Day01~27](../mindmap/README.md) | mindmap/Day31~60（待生成） |

---

## Sprint 5（Day31~38）— LLM 基础与推理机制

> **核心目标：补基础** — 第二个月**最重要的一周（Day31~37）**；目标：**能和算法工程师正常沟通**。

| Day | 主题 | 输出（设计） | 状态 |
|-----|------|--------------|------|
| Day31 | Transformer 主链路 | Token→Embedding→Attention→FFN→Next Token；口述工作流程 | 📋 — [Day31.md](Day31.md) |
| Day32 | 预训练 / 微调 / Prompt / RAG 选型 | 对比表：何时 RAG、何时微调、何时纯 Prompt | 📋 |
| Day33 | Tokenization 与上下文窗口 | 笔记：Token 计费、中文切分、上下文截断策略 | 📋 |
| Day34 | 推理参数与生成控制 | 笔记：Temperature / Top-p / 停止条件 / 流式 | 📋 |
| Day35 | 幻觉成因与缓解 | 对照本项目：RAG 引用、拒答、Workflow 边界 | 📋 |
| Day36 | Embedding 与向量检索原理 | 升维 Day11~12：相似度、维度、召回与精度 | 📋 |
| Day37 | Agent 原理（ReAct / Tool / Planning） | 对照 Day15~20：规则 Planner vs LLM 自主规划 | 📋 |
| Day38 | Sprint 5 Review | 原理知识串联 + 自测 Q&A 清单 | 📋 |

**Backlog：**

- [ ] Day31 Transformer — [Day31.md](Day31.md)
- [ ] Day32 选型对比（RAG vs 微调 vs Prompt）
- [ ] Day33 Token 与上下文
- [ ] Day34 推理参数
- [ ] Day35 幻觉与缓解
- [ ] Day36 Embedding 原理升维
- [ ] Day37 Agent 原理
- [ ] Day38 Sprint 5 Review

---

## Sprint 6（Day39~45）— 生产级 AI 架构

> **核心目标：工程化升级** — 对照 v1.0 现状，补齐「若上生产还缺什么」的认知。

| Day | 主题 | 输出（设计） | 状态 |
|-----|------|--------------|------|
| Day39 | 生产架构全景 | 分层图：入口 / 应用 / 向量库 / 模型 / 观测 | 📋 |
| Day40 | 高可用与扩缩容 | 笔记：多实例、健康检查、Compose → K8s 想象 | 📋 |
| Day41 | 缓存 / 限流 / 降级 | 笔记：Embedding 缓存、API 限流、LLM 降级策略 | 📋 |
| Day42 | 向量库生产选型 | 对照：Chroma embedded / server / 托管服务 | 📋 |
| Day43 | 观测体系 | 衔接 Day24：日志 / 指标 / Trace / 告警 | 📋 |
| Day44 | 安全与合规 | 密钥、MCP 沙箱、Prompt 注入、上传校验 | 📋 |
| Day45 | Sprint 6 Review | 「v1.0 → 生产 gap 清单」 | 📋 |

**Backlog：**

- [ ] Day39 生产架构全景
- [ ] Day40 高可用与扩缩容
- [ ] Day41 缓存 / 限流 / 降级
- [ ] Day42 向量库生产选型
- [ ] Day43 观测体系
- [ ] Day44 安全与合规
- [ ] Day45 Sprint 6 Review

---

## Sprint 7（Day46~52）— AI Solution 设计

> **核心目标：架构与方案** — 深化 Day26，能独立交付 Solution 级文档。

| Day | 主题 | 输出（设计） | 状态 |
|-----|------|--------------|------|
| Day46 | Solution 方法论 | 模板：背景 → 目标 → 方案 → 选型 → 风险 → 里程碑 | 📋 |
| Day47 | 企业知识库方案（案例深拆） | 以 AI Project Assistant 写完整 Solution 叙事 | 📋 |
| Day48 | 技术选型与对比表 | 文档：FastAPI / Chroma / Ollama / MCP 备选与权衡 | 📋 |
| Day49 | 非功能需求 | 成本（Day25）、SLA、合规、可维护性 | 📋 |
| Day50 | 架构图绘制 | C4 / 部署图 / 数据流（升级 architecture.md） | 📋 |
| Day51 | 方案评审模拟 | 模拟 Q&A：为什么不用 X、风险怎么控 | 📋 |
| Day52 | Sprint 7 Review | Solution 文档定稿 checklist | 📋 |

**Backlog：**

- [ ] Day46 Solution 方法论
- [ ] Day47 企业知识库方案深拆
- [ ] Day48 技术选型对比表
- [ ] Day49 非功能需求
- [ ] Day50 架构图升级
- [ ] Day51 方案评审模拟
- [ ] Day52 Sprint 7 Review

**已有基础（第一个月）：** [Day26.md](Day26.md) · [architecture.md](architecture.md) · [solution-design.md](solution-design.md)

---

## Sprint 8（Day53~60）— 面试与商业化表达

> **核心目标：跳槽冲刺** — 把 60 天学习打包成可投递、可面试的叙事。（承接原 Day28~30 可选内容）

| Day | 主题 | 输出（设计） | 状态 |
|-----|------|--------------|------|
| Day53 | 简历项目描述 | 量化亮点：v1.0、Compose、RAG、Agent、成本可观测 | 📋 |
| Day54 | STAR 与 Demo 脚本 | 30 秒 / 3 分钟 / 10 分钟三版演示稿 | 📋 |
| Day55 | 技术深挖 Q&A（RAG / Agent / MCP） | 自测题 + 参考回答 | 📋 |
| Day56 | PM / 架构类面试题 | 成本估算、选型、风险、迭代路线 | 📋 |
| Day57 | 模拟面试（技术向） | 录音/自问自答一轮 | 📋 |
| Day58 | 模拟面试（Solution / PM 向） | 方案讲解 + 白板架构 | 📋 |
| Day59 | 投递与作品集收口 | GitHub / README / 链接清单 | 📋 |
| Day60 | 60 天总复盘 | 能力对照表 + 下一步学习路线 | 📋 |

**Backlog：**

- [ ] Day53 简历项目描述
- [ ] Day54 STAR 与 Demo 脚本
- [ ] Day55 技术深挖 Q&A
- [ ] Day56 PM / 架构面试题
- [ ] Day57 模拟面试（技术）
- [ ] Day58 模拟面试（Solution）
- [ ] Day59 投递收口
- [ ] Day60 60 天总复盘

---

## 工程化改进（全周期）

| 项 | 说明 | 状态 |
|----|------|------|
| 统一虚拟环境 | 共享依赖管理，monorepo 结构 | ✅ |
| `.env.example` | 提供配置模板，避免密钥泄露 | ✅ |
| 错误处理 | 统一超时、模型不可用等异常响应 | ✅ Day14 |
| 请求耗时日志 | 中间件记录 | ✅ Day14 |
| Web 前端 | React + Vite 聊天界面 | ✅ Day21_1 |
| SSE 流式 API | `POST /agent/stream` 逐字返回 | ✅ Day21_2 |
| docker-compose | API + Chroma + Ollama 一键编排 | ✅ Day22 |
| Nginx 反代 | 生产部署入口 | ✅ Day23 |
| 结构化日志 + 配置分层 | 工程化运维 | ✅ Day24 |
| Token / 成本统计 | AI PM 可观测 | ✅ Day25 |
| 架构 / 方案文档 | Solution 交付 | ✅ Day26 |
| README / GitHub 包装 | 作品集门面 | ✅ Day27 |
| **v1.0.0 Release** | 30 天工程收官 | ✅ |
| 学习思维导图 | [mindmap/Day01~27](../mindmap/README.md) | ✅ |
| CI/CD | 自动化测试与镜像构建 | 可选 |
| **第二个月 Day31~60** | 原理 / 生产 / 方案 / 面试 | 📋 规划中 |
| mindmap Day31~60 | 第二个月思维导图 | 📋 待生成 |

---

## 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Ollama 文档](https://github.com/ollama/ollama)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [阿里云百炼](https://bailian.console.aliyun.com/)
- [MCP 规范](https://modelcontextprotocol.io/)
