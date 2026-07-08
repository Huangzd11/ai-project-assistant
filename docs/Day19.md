# Day19 — 真实 MCP Server 接入（Filesystem）

> 版本：**v0.3-rc** | Commit：`feat(mcp-server)`  
> **从「演示 Server」到「真正能用」：插上 Filesystem MCP，Agent 直接读项目文件**

## 学习目标

- [x] 理解 Day18 与 Day19 的分工：Client 已就绪，今天换 **真实 MCP Server**
- [x] 接入 **Filesystem MCP**，让 Agent 能读本地文件（README、docs、代码）
- [x] 掌握 MCP Server **配置化切换**（Filesystem / GitHub / SQLite / Postgres）
- [x] Planner 识别「查看 README」「读取文件」等自然语言意图
- [x] 跑通完整链路：**Question → Filesystem MCP → Answer**

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| 切换为 `@modelcontextprotocol/server-filesystem` | 自建 Python MCP Server（Day22+ 可选） |
| 配置允许访问目录（沙箱） | 替换内置 `rag/pdf/calculator` |
| Planner 路由 `read_file` / `list_directory` | 多 Server 同时在线编排（Day20 可选） |
| 自然语言：「看看 README」→ 读文件 → 回答 | 前端 UI |
| 文档列出 GitHub / SQLite / Postgres 换服示例 | 生产级权限审计系统 |

**Day19 核心成果：用户问「README 写了什么」，Agent 通过 Filesystem MCP 读取并回答，无需你再写 `readme_tool.py`。**

---

## Day18 vs Day19

| 对比 | Day18 | Day19 |
|------|-------|-------|
| MCP Server | `server-everything`（演示用） | `server-filesystem`（真实场景） |
| 典型工具 | `echo`、`get-sum` | `read_file`、`list_directory` |
| 触发方式 | 显式 `mcp echo hello` | 自然语言 + 显式 `mcp read_file README.md` |
| 业务价值 | 验证 Client / 桥接 | **读项目文件、答用户问题** |

---

## 什么是「真实 MCP」？

Day18 你学会了 **Client 怎么连 Server**。  
Day19 换的是 **Server 本身**——社区已写好、可直接用的能力包：

```
用户：「帮我看看 README 写了什么」
         │
         ▼
    Agent Planner
         │ 识别：需要读文件
         ▼
    mcp_read_file（Registry 桥接）
         │
         ▼
    MCP Client（Day18 已有）
         │ stdio 协议
         ▼
    Filesystem MCP Server（今天接入）
         │ 沙箱内读 README.md
         ▼
    文件内容 → LLM 总结 → Answer
```

### 以后不用自己写 Tool

| 能力 | 自写 Tool（Day16） | 接 MCP Server（Day19+） |
|------|-------------------|------------------------|
| 读 README | 写 `readme_tool.py` | Filesystem MCP `read_file` |
| 查 GitHub Issue | 写 `github_tool.py` | GitHub MCP |
| 查 SQLite | 写 `sql_tool.py` | SQLite MCP |
| 查 Postgres | 写 `db_tool.py` | Postgres MCP |

**原则：** 有成熟 MCP Server 就 **接**，没有或要强定制再 **写**。

---

## Filesystem MCP 工具一览

官方包：`@modelcontextprotocol/server-filesystem`

| 工具名 | 作用 | Day19 是否用 |
|--------|------|-------------|
| `read_file` | 读取文件内容 | ✅ 核心 |
| `list_directory` | 列出目录 | ✅ 推荐 |
| `directory_tree` | 目录树 JSON | 可选 |
| `search_files` | 按 glob 搜索 | 可选 |
| `get_file_info` | 文件元信息 | 可选 |
| `write_file` | 写入文件 | ⚠️ 教学可关（只读场景） |
| `list_allowed_directories` | 查看沙箱目录 | 调试用 |

桥接进 Registry 后名称带前缀：`mcp_read_file`、`mcp_list_directory` …

---

## 配置设计

### 环境变量（`.env`）

```env
# Day19 — 启用 Filesystem MCP
MCP_ENABLED=true
MCP_SERVER_COMMAND=npx

# 注意：逗号分隔；最后一项为「允许访问的绝对路径」（沙箱根目录）
# Windows 示例（用正斜杠或双反斜杠）：
MCP_SERVER_ARGS=-y,@modelcontextprotocol/server-filesystem,E:/2026/learn/ai-project-assistant

# 新增（推荐）：单独配置沙箱根目录，代码里拼进 args
MCP_FILESYSTEM_ROOT=E:/2026/learn/ai-project-assistant
```

### `config.py` 建议

```python
# Day19 — Filesystem MCP 沙箱根目录（绝对路径）
MCP_FILESYSTEM_ROOT = os.getenv(
    "MCP_FILESYSTEM_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)

# 默认 Server 改为 filesystem（若未手动覆盖 MCP_SERVER_ARGS）
_default_fs_args = f"-y,@modelcontextprotocol/server-filesystem,{MCP_FILESYSTEM_ROOT}"
MCP_SERVER_ARGS = os.getenv("MCP_SERVER_ARGS", _default_fs_args)
```

### Windows 注意

1. **必须绝对路径**，不能用 `./` 相对路径
2. 路径含空格时用引号或换配置方式
3. 若 `npx` 在 PowerShell 异常，可试 `MCP_SERVER_COMMAND=cmd`，`MCP_SERVER_ARGS=/c,npx,-y,@modelcontextprotocol/server-filesystem,<路径>`

### 安全：allowed directories

Filesystem Server **只允许**启动参数里列出的目录。  
不要把 `C:\` 整盘放开；教学场景建议 **仅项目根目录**。

---

## 其他真实 MCP Server（换配置即可）

Day19 **主交付 Filesystem**；以下仅作扩展参考，改 `.env` 的 `MCP_SERVER_ARGS` 即可切换（一次只连一个 Server，与 Day18 一致）：

| Server | 包名 / 命令 | 典型场景 |
|--------|------------|----------|
| **Filesystem** | `@modelcontextprotocol/server-filesystem` + 目录路径 | 读 README、列目录 |
| **GitHub** | `@modelcontextprotocol/server-github` + `GITHUB_TOKEN` | Issue、PR、仓库文件 |
| **SQLite** | `@modelcontextprotocol/server-sqlite` + `.db` 路径 | 本地库查询 |
| **Postgres** | `@modelcontextprotocol/server-postgres` + 连接串 | 企业库查询 |

示例（GitHub，需 Token）：

```env
MCP_SERVER_ARGS=-y,@modelcontextprotocol/server-github
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxx
```

> Day19 验收以 **Filesystem + README** 为准；GitHub/DB 作为课后扩展。

---

## 目录与代码改动（设计）

```
app/
├── mcp/
│   ├── client.py          # Day18 已有，一般不改
│   ├── bridge.py          # Day19：增强 plan_mcp_step（read_file 参数）
│   ├── runtime.py         # Day18 已有
│   └── __init__.py        # 可选：从 MCP_FILESYSTEM_ROOT 拼 args
├── agent/
│   └── planner.py         # Day19：文件读取意图路由
└── core/
    └── config.py          # MCP_FILESYSTEM_ROOT、默认 filesystem args
```

**不新增 `app/mcp/server.py`**——今天用的是 **外部** Filesystem Server，不是自建。

---

## Planner 路由设计

### 优先级（在 calculator 之后、mcp 显式命令之前或之后按你实现）

```
plan(user_message)
  1. calculator（Day16）
  2. filesystem 自然语言（Day19 新增）  ← 今天重点
  3. mcp 显式命令 mcp read_file xxx（Day18 扩展）
  4. pdf_read（Day16）
  5. rag_query（Day16）
  6. [] 直答
```

### 自然语言意图（建议关键词）

| 用户说法 | 规划步骤 |
|----------|----------|
| 「看看 README」「README 写了什么」 | `mcp_read_file` path=`README.md` |
| 「列出 docs 目录」「项目有哪些文档」 | `mcp_list_directory` path=`docs` |
| 「读取 docs/Day18.md」 | `mcp_read_file` path=`docs/Day18.md` |
| `mcp read_file README.md` | 显式 MCP（Day18 `plan_mcp_step` 扩展） |

### `_extract_file_path` 提示逻辑

```python
import re

def _extract_file_path(message: str) -> str | None:
    # 1. 显式路径 docs/Day18.md
    m = re.search(r"([\w./\\-]+\.(md|txt|py|json|yml))", message, re.I)
    if m:
        return m.group(1).replace("\\", "/")
    # 2. README 特例
    if re.search(r"readme", message, re.I):
        return "README.md"
    # 3. docs 目录
    if "docs" in message.lower() and ("目录" in message or "列出" in message):
        return "docs"
    return None
```

### `_plan_filesystem_step` 伪代码

```python
def _plan_filesystem_step(user_message: str) -> dict | None:
    from app.mcp.bridge import is_mcp_enabled, list_mcp_tool_names
    if not is_mcp_enabled():
        return None
    tools = list_mcp_tool_names()
    path = _extract_file_path(user_message)
    if not path:
        return None
    if path.endswith("/") or path == "docs" and "目录" in user_message:
        if "mcp_list_directory" in tools:
            return {"tool": "mcp_list_directory", "args": {"path": path}, ...}
    if "mcp_read_file" in tools:
        return {"tool": "mcp_read_file", "args": {"path": path}, ...}
    return None
```

### `plan_mcp_step` 扩展（显式命令）

Day18 已支持 `mcp echo hello`。Day19 扩展：

```
mcp read_file README.md
mcp list_directory docs
```

`read_file` 的 schema 通常要求 `path` 字符串；`plan_mcp_step` 把 `rest` 整段作为 `path`。

---

## 请求链路（完整）

```
POST /agent
  {"message": "帮我看看 README 写了什么"}
        │
        ▼
  planner._plan_filesystem_step()
        │ tool: mcp_read_file, args: {path: "README.md"}
        ▼
  executor → registry.run("mcp_read_file", path="README.md")
        ▼
  bridge._make_mcp_runner → MCPClient.call_tool("read_file", {...})
        ▼
  Filesystem Server（npx 子进程）读沙箱内 README.md
        ▼
  summary: 文件全文或截断
        ▼
  LLM 根据「工具执行结果」生成中文回答
```

---

## 实现清单（待编码）

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 1 | `MCP_FILESYSTEM_ROOT` + 默认 filesystem args | `config.py`, `.env.example` | ✅ |
| 2 | bootstrap 使用新默认 Server | `mcp/__init__.py` | ✅ |
| 3 | Planner 文件意图路由 | `agent/planner.py` | ✅ |
| 4 | `plan_mcp_step` 支持 `read_file` / `list_directory` | `mcp/bridge.py` | ✅ |
| 5 | 联调：`POST /agent` 读 README | — | ✅ |
| 6 | 更新 api.md / CODEMAP / README | `docs/` | ✅ |

---

## 测试命令

### 1. 配置

```powershell
# .env
MCP_ENABLED=true
MCP_FILESYSTEM_ROOT=E:/2026/learn/ai-project-assistant
```

### 2. 启动

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. 查看 MCP 工具（应有 read_file）

```powershell
Invoke-RestMethod http://127.0.0.1:8000/mcp/status
```

### 4. Agent 自然语言读 README

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"帮我看看 README 写了什么"}'
```

期望：`plan` 含 `mcp_read_file`，`answer` 能概括 README 内容。

### 5. 显式 MCP 命令

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/agent `
  -Method Post -ContentType "application/json" `
  -Body '{"message":"mcp read_file README.md"}'
```

### 6. 模块自测（无 LLM）

```powershell
$env:MCP_ENABLED="true"
python -c "
import app.agent.tools
from app.mcp import bootstrap_mcp_sync, shutdown_mcp
from app.agent.tools.registry import run
import asyncio
bootstrap_mcp_sync()
r = run('mcp_read_file', path='README.md')
print(r.get('summary', '')[:500])
asyncio.run(shutdown_mcp())
"
```

---

## 验收标准（Day19 完成定义）

- [x] `.env` 配置 Filesystem MCP，启动后 `/mcp/status` 可见 `mcp_read_file` 等
- [x] `registry.run('mcp_read_file', path='README.md')` 能返回文件内容
- [x] `POST /agent` + 「看看 README」能走 Planner → MCP → 回答
- [x] 内置 `rag_query` / `pdf_read` / `calculator` 仍正常
- [x] 能说明 Filesystem 沙箱目录的作用
- [ ] Git Commit：`feat(mcp-server)`，Tag：`v0.3-rc`

---

## 架构图

```
                    POST /agent
                 「看看 README」
                         │
                         ▼
                  ┌─────────────┐
                  │  planner    │  Day19 文件意图
                  └──────┬──────┘
                         │ mcp_read_file
                         ▼
                  ┌─────────────┐
                  │  registry   │
                  └──────┬──────┘
                         ▼
                  ┌─────────────┐
                  │ mcp/bridge  │  Day18
                  └──────┬──────┘
                         ▼
                  ┌─────────────┐
                  │ mcp/client  │
                  └──────┬──────┘
                         │ MCP 协议 (stdio)
                         ▼
                  ┌─────────────────────┐
                  │ server-filesystem   │  ← Day19 真实 Server
                  │ (npx 子进程)         │
                  │ 只读沙箱内 README.md │
                  └─────────────────────┘
                         │
                         ▼
                      Answer
```

---

## 常见坑

1. **未配置 allowed directory** — Filesystem Server 启动报错，至少传一个绝对路径
2. **相对路径** — `README.md` 相对沙箱根可以，但沙箱根本身必须绝对路径
3. **文件过大** — `read_file` 全文进 LLM 可能超长；可先截断 summary 或只读前 N 字符（可选优化）
4. **与 RAG 混淆** — 「总结 test.pdf」走 `rag_query`；「看 README」走 Filesystem；Planner 关键词要分清
5. **Windows npx** — 第一次慢是 npm 下载；失败时查 Node 版本与路径格式

---

## 收获（完成后填写）

- 真实 MCP = 换 `.env` 就能接 Filesystem / GitHub / DB，不必每个能力写 Tool
- Filesystem MCP 适合「读项目文件、列目录」；RAG 适合「已向量化知识库问答」
- 沙箱目录是安全边界，生产环境最小权限开放
- 默认 MCP Server 从 `server-everything` 切换为 `server-filesystem`

---

## 下一步

Day20 — 企业 Agent Workflow（`feat(agent-workflow)` · v0.3）：多工具编排、可选多 MCP Server、Conversation 工作流完善
