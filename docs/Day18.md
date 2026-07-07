# Day18 — MCP 基础（Client 连接）

> 版本：**v0.3-beta2** | Commit：`feat(mcp-client)`  
> **今年最重要的一天：从「自己写 Tool」到「MCP 统一协议」**

## 学习目标

- [x] 理解 **MCP（Model Context Protocol）** 是什么、解决什么问题
- [x] 理解 **Client / Server / Tool** 三者关系
- [x] 安装 MCP Python SDK，跑通最小 Client 连接
- [x] Agent 能 **连接 MCP Server**，发现并调用外部 Tool
- [x] 为 Day19「自建 MCP Server」打基础

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| MCP 概念 + Python SDK | 自建完整 MCP Server（Day19） |
| `mcp/client.py` 连接 Server | 替换现有 `pdf/rag/calculator` 内置工具 |
| 将 MCP Tool **桥接**进 Tool Registry | 企业 Workflow 编排（Day20） |
| 列出 / 调用 MCP 外部工具 | 前端 UI |
| 配置化 MCP Server 启动命令 | 多 Server 编排（Day20 可选） |

**Day18 核心成果：Agent 不再只会调「自己写的 Tool」，还能调「MCP Server 提供的 Tool」。**

---

## 什么是 MCP？

**MCP（Model Context Protocol）** 是 Anthropic 推动的 **开放协议**，用于让 LLM 应用以统一方式连接外部数据源和工具。

一句话：

> **MCP = AI 应用的「USB 接口」** —— 插上就能用，不用每个 Tool 各写一套集成。

### 以前 vs 现在

```
【以前 · Day16】
LLM / Agent
    ↓
自己写 Tool（pdf_tool.py、rag_tool.py、calculator.py）
    ↓
各项目接口不统一，每加一个能力都要改 Agent

【现在 · Day18+】
LLM / Agent
    ↓
MCP Client（统一协议）
    ↓
MCP Server（独立进程 / 服务）
    ↓
Tool（文件、数据库、GitHub、天气……）
```

| 对比 | 自写 Tool（Day16） | MCP（Day18+） |
|------|-------------------|---------------|
| 集成方式 | 改代码 + `register()` | 连上 MCP Server 即可 |
| 工具提供方 | 本项目 `app/agent/tools/` | 任意符合 MCP 的 Server |
| 协议 | 项目内部约定 | **开放标准** |
| 典型场景 | RAG、PDF、计算器 | 文件系统、Git、Slack、DB…… |

**Day16 的内置 Tool 保留**；MCP 是 **增量能力**，不是替换。

---

## MCP 三要素：Client / Server / Tool

```
┌─────────────┐         MCP 协议          ┌─────────────┐
│ MCP Client  │ ◄──────────────────────► │ MCP Server  │
│ (本项目)    │   list_tools / call_tool │ (独立进程)  │
└──────┬──────┘                          └──────┬──────┘
       │                                          │
       │  Agent / Executor                        │ 暴露 Tool
       ▼                                          ▼
  run_agent()                              read_file / search / ...
```

| 角色 | 在本项目中 | 职责 |
|------|-----------|------|
| **MCP Client** | `app/mcp/client.py` | 连接 Server，列出工具，发起 `call_tool` |
| **MCP Server** | 外部进程（Day18 用官方示例 Server） | 注册并执行具体 Tool |
| **Tool** | Server 暴露的能力 | 有 `name`、`description`、`inputSchema` |

### 通信流程（简化）

```
1. Client 启动，连接 Server（stdio / SSE）
2. Client → Server: tools/list     → 返回可用 Tool 列表
3. Agent 决定调用某 Tool
4. Client → Server: tools/call     → 返回结果（Observation）
5. Agent 将结果交给 LLM 生成 Answer
```

---

## 在 Sprint 3 中的位置

```
Day15  Agent Core
Day16  Tool Registry（内置 Tool）
Day17  Memory
Day18  MCP Client 连接外部 Server    ← 今天
Day19  自建 MCP Server 接入项目能力
Day20  企业 Agent Workflow
Day21  Release v0.3
```

与 Day16 的关系：

```
app/agent/tools/registry.py
    ├── rag_tool / pdf_tool / calculator   ← Day16 内置
    └── mcp_bridge（动态注册 MCP tools）    ← Day18 桥接
```

---

## 新增目录结构

```
app/
├── mcp/                        # Day18 新增
│   ├── __init__.py
│   ├── client.py               # MCP Client 封装
│   └── bridge.py               # MCP Tool → Registry 桥接
├── agent/
│   ├── tools/
│   │   └── registry.py         # Day18 可选：register_mcp_tools()
│   └── executor.py             # 已支持 registry.run，一般不改
└── core/
    └── config.py               # MCP_SERVER_COMMAND 等配置
```

**Day19** 再增加 `app/mcp/server.py`（把 RAG/PDF 暴露为 MCP Server）。

---

## 依赖安装

### Python MCP SDK

```powershell
pip install mcp
```

`requirements.txt` 追加：

```
# Day18 — MCP Client
mcp
```

官方文档：[Model Context Protocol](https://modelcontextprotocol.io/)

### 示例 MCP Server（Day18 联调用）

可用官方或社区 Server 做 **Client 侧** 验证，例如：

| Server | 用途 | 启动方式（示例） |
|--------|------|------------------|
| `@modelcontextprotocol/server-everything` | 官方测试 Server | `npx`（需 Node.js） |
| 简易 Python Server | Day19 自建 | 明天 |

Day18 **重点在 Client**；Server 先用现成示例即可。

---

## 模块设计

### 1. `app/mcp/client.py` — MCP Client 封装

**职责：**
- 按配置启动/连接 MCP Server（stdio 传输为主）
- `list_tools()` → 返回 Tool 列表
- `call_tool(name, arguments)` → 返回 MCP 结果
- 连接生命周期管理（connect / disconnect）

**设计接口：**

```python
class MCPClient:
  async def connect(self) -> None: ...
  async def list_tools(self) -> list[dict]: ...
  async def call_tool(self, name: str, arguments: dict) -> dict: ...
  async def close(self) -> None: ...
```

**stdio 连接示例（设计）：**

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-everything"],
)
```

> 学习项目也可用 `python path/to/simple_server.py` 作为 Server 命令。

### 2. `app/mcp/bridge.py` — 桥接到 Tool Registry

**职责：** 把 MCP Server 上的 Tool **动态注册**到 Day16 `registry`。

```python
# 伪代码
async def register_mcp_tools(client: MCPClient) -> int:
    tools = await client.list_tools()
    for t in tools:
        register({
            "name": f"mcp_{t.name}",      # 避免与内置 tool 重名
            "description": t.description,
            "schema": t.inputSchema,
            "run": lambda **kw: asyncio.run(client.call_tool(t.name, kw)),
        })
    return len(tools)
```

**命名约定：** MCP 工具加前缀 `mcp_`，如 `mcp_read_file`，与 `rag_query` 区分。

**Observation 格式：** 与 Day16 统一：

```python
{
    "ok": True,
    "data": mcp_result,
    "summary": str(mcp_result),
    "sources": [],
}
```

### 3. `config.py` — MCP 配置

```python
MCP_ENABLED = os.getenv("MCP_ENABLED", "false").lower() == "true"
MCP_SERVER_COMMAND = os.getenv("MCP_SERVER_COMMAND", "npx")
MCP_SERVER_ARGS = os.getenv("MCP_SERVER_ARGS", "-y,@modelcontextprotocol/server-everything")
```

`.env.example`：

```env
# Day18 — MCP Client
MCP_ENABLED=false
MCP_SERVER_COMMAND=npx
MCP_SERVER_ARGS=-y,@modelcontextprotocol/server-everything
```

### 4. Planner / Executor（Day18 改动最小）

**方案 A（推荐 Day18）：** 启动时 `register_mcp_tools()`，Planner 规则增加「若用户问 MCP 能力相关 → 选 `mcp_xxx`」。

**方案 B（进阶）：** LLM 根据 `list_tools()` 动态选工具（Day20）。

Day18 验收可用 **显式测试**：

```powershell
python -c "from app.mcp.client import ...; asyncio.run(test_list_tools())"
```

或 HTTP：`POST /agent` 消息触发已注册的 MCP 工具。

### 5. 异步注意

MCP Python SDK 以 **asyncio** 为主；FastAPI 路由本身支持 async。

可选策略：
- `api/agent.py` 改为 `async def`，Client 全 async
- 或在 sync 代码里 `asyncio.run()` 包装（简单但不宜高频）

Day18 推荐：**MCP Client 模块 async，启动时同步 bootstrap 注册工具列表**。

---

## 端到端示例（设计）

```
用户：用 MCP 查一下当前时间（或 Server 提供的 echo 工具）

Agent Planner → { tool: "mcp_echo", args: { "message": "hello" } }
    ↓
registry.run("mcp_echo", message="hello")
    ↓
mcp bridge → MCP Client.call_tool("echo", {...})
    ↓
MCP Server 执行 → 返回 Observation
    ↓
LLM 总结 → Answer
```

---

## HTTP / 调试接口（可选）

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /mcp/tools` | 列出已连接 MCP Server 的 Tool | 调试 |
| `POST /mcp/call` | 直接调用 MCP Tool | 调试 |

Day18 非必须；模块自测即可。

---

## 实现清单（待编码）

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 1 | `pip install mcp`，更新 requirements | `requirements.txt` | ✅ |
| 2 | MCP 环境变量 | `config.py`, `.env.example` | ✅ |
| 3 | `MCPClient` connect / list / call | `mcp/client.py` | ✅ |
| 4 | MCP → Registry 桥接 | `mcp/bridge.py` | ✅ |
| 5 | 应用启动时可选加载 MCP tools | `main.py` / `mcp/__init__.py` | ✅ |
| 6 | Planner 识别 MCP 工具 | `planner.py` | ✅ |
| 7 | 联调：Agent 调用 MCP Server 工具 | — | ✅ |

---

## 测试命令（设计）

```powershell
# 1. 安装
pip install mcp

# 2. 启用 MCP（.env）
# MCP_ENABLED=true

# 3. 列出 MCP 工具（模块测试）
python -c "import asyncio; from app.mcp.client import MCPClient; ..."

# 4. 查看 Registry 是否含 mcp_ 前缀工具
python -c "import app.agent.tools; from app.agent.tools.registry import list_names; print([n for n in list_names() if n.startswith('mcp_')])"

# 5. Agent 调用（需 Ollama/通义 + MCP Server 运行）
python -m uvicorn app.main:app --reload
```

---

## 验收标准（Day18 完成定义）

- [x] 能解释 MCP Client / Server / Tool 三者关系
- [x] 已安装 `mcp` SDK
- [x] `MCPClient` 能连接示例 MCP Server 并 `list_tools()`
- [x] 至少成功 `call_tool` 一次（`mcp echo hello` → `Echo: hello`）
- [x] MCP 工具已桥接进 Tool Registry（`mcp_` 前缀）
- [x] Agent / `registry.run` 能调用 MCP 工具并返回结果
- [x] 内置 Tool（rag/pdf/calculator）仍正常工作
- [ ] Git Commit：`feat(mcp-client)`，Tag：`v0.3-beta2`

---

## 架构图

```
                    POST /agent
                         │
                         ▼
                  ┌─────────────┐
                  │  executor   │
                  └──────┬──────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  tools/registry.py  │
              └──────────┬──────────┘
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
      rag_tool      pdf_tool     mcp_bridge
                                      │
                                      ▼
                              ┌───────────────┐
                              │ mcp/client.py │
                              └───────┬───────┘
                                      │ MCP 协议
                                      ▼
                              ┌───────────────┐
                              │  MCP Server   │
                              │  (外部进程)    │
                              └───────────────┘
```

---

## 常见坑

1. **未装 Node.js** — 部分官方 Server 用 `npx` 启动，需 Node 或换 Python Server
2. **MCP 工具与内置 tool 重名** — 加 `mcp_` 前缀
3. **async 在 sync 路由里乱用** — 统一在 bridge 层处理事件循环
4. **Server 未启动就 connect** — 先确认 command/args 正确
5. **Day18 与 Day19 混淆** — 今天写 **Client**，明天写 **Server**

---

## 收获（完成后填写）

- MCP 是 Tool 的「标准化插座」，降低集成成本
- Client 在本项目，Server 可来自社区或自建（Day19）
- Registry 桥接模式让 MCP 与 Day16 内置 Tool 共存
- MCP stdio Client 需固定后台事件循环（`mcp/runtime.py`），sync Agent 通过 `run_on_background` 跨线程调度

---

## 下一步

Day19 — MCP Server 接入（`feat(mcp-server)` · v0.3-rc）：把项目 RAG/PDF 能力暴露为 MCP Server
