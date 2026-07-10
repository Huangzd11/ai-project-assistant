# -*- coding: utf-8 -*-
"""Generate Day01~Day27 mindmap markdown files under mindmap/."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "mindmap"

# Each entry: day, title, sprint, terms[{name,def,role}], goals, focus, points, hard,
# harvest, tech[{name,why}], summary
DAYS = []


def d(**kwargs):
    DAYS.append(kwargs)


d(
    day="01",
    title="LLM 基础概念与 Prompt",
    sprint="Sprint 1 · 基础链路",
    terms=[
        ("LLM", "基于 Transformer 的生成式大语言模型", "理解输入→预测下一 Token→生成文本的基本工作方式"),
        ("Prompt", "输入给模型的指令与上下文", "决定模型「做什么、怎么答」"),
        ("System Prompt", "定义 AI 身份、规则与行为边界", "约束角色与输出风格"),
        ("Token", "模型计费与上下文的基本单位", "影响成本与上下文窗口占用"),
        ("Temperature", "采样随机性参数", "控制回答创造性 vs 确定性"),
        ("Few-shot", "用少量示例约束输出格式", "不改模型权重即可引导行为"),
    ],
    goals=["理解 LLM 基本工作原理", "掌握 system/user/assistant 角色", "了解 Token、上下文窗口、温度"],
    focus=["Prompt 工程入门", "角色设定对输出的影响", "Temperature 与 Few-shot 实验"],
    points=["同一问题换 System Prompt 风格会变", "Few-shot 可约束 JSON 等格式", "低温更稳、高温更发散"],
    hard=["把「感觉」写成可复现的 Prompt 实验", "理解 Token 与中文分词的关系"],
    harvest=["建立 LLM 应用的心智模型", "会用 Prompt 做最小可控实验"],
    tech=[("Python 示例脚本", "零依赖理解概念，不引入框架噪音")],
    summary="从概念到实验：先懂 LLM/Prompt/Token，再动手改 System、Few-shot、Temperature。",
)

d(
    day="02",
    title="OpenAI 兼容 API 与多轮对话",
    sprint="Sprint 1 · 基础链路",
    terms=[
        ("messages", "[{role, content}, ...] 对话历史列表", "多轮对话的核心数据结构"),
        ("OpenAI 兼容 API", "统一 chat.completions 接口形态", "一套代码可切云端/本地"),
        ("stream", "流式逐 Token/字返回", "降低首字延迟，改善体验"),
        (".env", "本地环境变量文件", "存放 Key，避免硬编码密钥"),
    ],
    goals=["从 .env 读 Key/BaseURL/模型名", "维护 messages 实现多轮对话", "使用 stream=True 流式输出"],
    focus=["messages 状态机", "环境变量配置", "流式输出体验"],
    points=["每轮把 assistant 回复 append 回 messages", "Key 只放 .env", "stream 与非 stream 同一套 messages"],
    hard=["流式拼接与异常中断处理", "上下文过长时的截断策略（后续再做）"],
    harvest=["掌握「配置 + messages + 流式」最小闭环"],
    tech=[
        ("openai Python SDK", "官方兼容客户端，切换 BaseURL 即可"),
        ("python-dotenv", "安全加载密钥，符合工程习惯"),
    ],
    summary="把 Day01 概念落到可运行的多轮 CLI：配置、历史、流式三件套。",
)

d(
    day="03",
    title="本地 Ollama 模型调用",
    sprint="Sprint 1 · 基础链路",
    terms=[
        ("Ollama", "本地大模型运行与管理工具", "无云 Key 也能跑通对话"),
        ("OpenAI 兼容端点", "Ollama 提供 /v1 chat 接口", "与 Day02 代码几乎零改动切换"),
        ("本地 vs 云端", "隐私/成本/延迟/能力的权衡", "选型时的核心对比维度"),
    ],
    goals=["用 OpenAI 兼容接口连本地 Ollama", "流式调用本地模型", "理解云端与本地差异"],
    focus=["BaseURL 指向 11434", "模型拉取与命名", "本地部署取舍"],
    points=["api_key 可填占位符 ollama", "同一 SDK 切换云端/本地", "本地适合开发与隐私场景"],
    hard=["本机资源不足时的模型选型", "容器访问宿主机 Ollama 网络（Day05）"],
    harvest=["具备「一套代码、两种部署」的切换能力"],
    tech=[
        ("Ollama", "本地推理简单、生态好、兼容 OpenAI API"),
        ("qwen 等开源模型", "中文场景够用，学习成本低"),
    ],
    summary="证明架构可迁移：改 BaseURL 就能从通义切到本地 Ollama。",
)

d(
    day="04",
    title="FastAPI HTTP 服务",
    sprint="Sprint 1 · 基础链路",
    terms=[
        ("FastAPI", "现代 Python Web 框架", "把 LLM 能力暴露为 HTTP API"),
        ("Pydantic", "请求/响应数据校验模型", "契约清晰、自动生成 OpenAPI"),
        ("分层架构", "config / models / llm / app 分离", "可测、可维护、可扩展"),
        ("Uvicorn", "ASGI 服务器", "运行 FastAPI 应用"),
    ],
    goals=["把 LLM 封装成 HTTP API", "用 Pydantic 定义契约", "分层组织代码"],
    focus=["API 边界设计", "配置与业务分离", "Swagger 自文档"],
    points=["/chat /health /models 最小接口集", "超时与错误需可预期", "配置走环境变量"],
    hard=["同步 LLM 调用阻塞与超时设计", "异常映射为友好 HTTP 状态码"],
    harvest=["从脚本进化为可被前端/其他服务调用的 API"],
    tech=[
        ("FastAPI", "类型提示友好、自带 OpenAPI、异步生态成熟"),
        ("Pydantic", "校验与文档一体，减少手写 schema"),
    ],
    summary="LLM 能力产品化第一步：HTTP + 契约 + 分层。",
)

d(
    day="05",
    title="Docker 容器化部署",
    sprint="Sprint 1 · 基础链路",
    terms=[
        ("Docker 镜像", "应用与依赖的只读打包", "保证「我这能跑」可复现"),
        ("容器", "镜像的运行实例", "隔离进程与端口"),
        ("host.docker.internal", "容器访问宿主机的特殊主机名", "连宿主机 Ollama"),
        (".dockerignore", "构建时排除无关文件", "减小上下文、加快构建"),
    ],
    goals=["把 FastAPI 打成镜像", "理解 build/run 流程", "处理容器访问宿主机网络"],
    focus=["Dockerfile 最小可用", "端口映射", "环境变量注入"],
    points=["监听 0.0.0.0 而非 127.0.0.1", "Key 用 -e 注入不进镜像", "镜像版本与代码版本对齐"],
    hard=["Windows 下宿主机网络与路径", "镜像体积与依赖（torch 等）"],
    harvest=["具备单容器交付能力，为 Compose 打基础"],
    tech=[
        ("Docker", "环境一致、部署标准、面试高频"),
        ("python:slim 基础镜像", "体积与兼容性平衡"),
    ],
    summary="把 Day04 服务装进容器：可构建、可运行、可传给别人。",
)

d(
    day="06",
    title="GitHub 与项目规范",
    sprint="Sprint 1 · 基础链路",
    terms=[
        ("Git / GitHub", "版本控制与远程托管", "协作、作品集、可追溯"),
        ("README", "仓库门面文档", "30 秒讲清是什么、怎么跑"),
        ("开发规范", "提交、分支、文档约定", "降低协作与回顾成本"),
        ("monorepo", "单仓多模块结构", "学习项目统一管理代码与文档"),
    ],
    goals=["创建并推送 GitHub 仓库", "编写专业 README", "建立 AI 项目开发规范"],
    focus=["远程仓库对齐", "文档体系", "密钥不入库"],
    points=[".env 必须 gitignore", "README 含 Quick Start", "commit message 表达意图"],
    hard=["从「作业文件夹」到「可展示仓库」的叙事", "文档与代码同步"],
    harvest=["项目具备公开托管与规范雏形"],
    tech=[
        ("GitHub", "作品集主阵地，招聘方常看"),
        ("Markdown 文档体系", "低成本、可版本化"),
    ],
    summary="工程可见性：代码上云 + README + 规范，开始像产品仓库。",
)

d(
    day="07",
    title="Review（Day01~06 回顾）",
    sprint="Sprint 1 · 基础链路",
    terms=[
        ("Sprint Review", "阶段回顾与验收", "对齐目标、查漏补缺"),
        ("前置条件", "进入下一阶段必须具备的能力", "避免带着缺口进 RAG"),
    ],
    goals=["回顾 Day01~06 知识链", "检查代码/文档/示例一致", "确认 Day08 RAG 前置就绪"],
    focus=["知识串联", "遗留问题修复", "示例补齐"],
    points=["Prompt→API→Ollama→FastAPI→Docker→GitHub 一条链", "示例脚本与文档对齐", "不急着加新功能"],
    hard=["诚实面对「会用但讲不清」的概念", "文档滞后于代码"],
    harvest=["Sprint 1 闭环：能讲、能跑、能托管"],
    tech=[("既有技术栈复盘", "巩固选型理由，为 Sprint 2 铺路")],
    summary="停下来验收：基础链路打通，再进入企业 RAG。",
)

d(
    day="08",
    title="项目重构 + PDF 上传",
    sprint="Sprint 2 · Enterprise RAG",
    terms=[
        ("app/ 分层", "api / core / models / rag / main", "为 RAG 与 Agent 扩展留空间"),
        ("multipart 上传", "表单文件上传协议", "浏览器/客户端传 PDF"),
        ("uploads/", "原始文件落盘目录", "后续解析与入库的输入源"),
    ],
    goals=["重构为 app/ 分层", "实现 POST /upload", "保存 PDF 并返回元信息"],
    focus=["目录重构迁移", "上传校验", "日志记录"],
    points=["只收 PDF、校验扩展名", "文件名安全处理", "上传是 RAG 流水线入口"],
    hard=["扁平结构迁移不破坏可运行性", "大文件与磁盘路径约定"],
    harvest=["从 Demo API 进入「有数据入口」的企业形态"],
    tech=[
        ("FastAPI UploadFile", "原生支持 multipart，简单可靠"),
        ("分层包结构", "后续 Day09~13 模块有家"),
    ],
    summary="Sprint 2 开门：结构重整 + 知识库原料入口（上传）。",
)

d(
    day="09",
    title="PDF 解析（PyMuPDF）",
    sprint="Sprint 2 · Enterprise RAG",
    terms=[
        ("文档解析", "PDF→纯文本/结构化页", "RAG 流水线第一环"),
        ("按页提取", "保留 page 元数据", "为引用溯源准备页码"),
        ("parsed JSON", "中间产物落盘", "解耦解析与切分"),
    ],
    goals=["理解解析在 RAG 中的位置", "用 PyMuPDF 按页抽文本", "输出 data/parsed/*.json"],
    focus=["页级结构", "可复用 pdf_loader", "中间产物可检查"],
    points=["解析失败要可观测", "保留 source/page", "门面函数串起 load→save"],
    hard=["扫描版 PDF 无文本层", "复杂排版噪声"],
    harvest=["知识库有了「可读文本」中间层"],
    tech=[
        ("PyMuPDF (fitz)", "按页提取快、API 清晰、适合学习项目"),
    ],
    summary="把 PDF 变成带页码的文本 JSON，为 Chunk 做准备。",
)

d(
    day="10",
    title="Chunk 切分",
    sprint="Sprint 2 · Enterprise RAG",
    terms=[
        ("Chunk", "检索与向量化的文本块", "粒度影响召回与上下文质量"),
        ("chunk_size", "单块目标长度", "太大噪声多、太小语义碎"),
        ("chunk_overlap", "块间重叠", "减轻边界切断语义"),
        ("RecursiveCharacterTextSplitter", "按分隔符递归切分", "比硬切字符更稳"),
    ],
    goals=["理解为何页还要再切块", "用 LangChain Splitter", "掌握 size/overlap 取舍"],
    focus=["切分策略", "chunk_id 全局编号", "与 Day09 产物衔接"],
    points=["overlap 不是越大越好", "保留 page 元数据", "切分结果可人工抽查"],
    hard=["中文标点与分隔符选择", "表格/代码块被切断"],
    harvest=["建立「检索粒度」产品直觉"],
    tech=[
        ("langchain-text-splitters", "成熟切分器，避免手写边界 bug"),
    ],
    summary="页→块：为 Embedding 准备合适粒度的文本单元。",
)

d(
    day="11",
    title="Embedding（文本向量化）",
    sprint="Sprint 2 · Enterprise RAG",
    terms=[
        ("Embedding", "文本→稠密向量", "语义相近则向量相近"),
        ("本地 Embedding", "如 BGE 小模型本地推理", "无 Key、可离线"),
        ("云端 Embedding", "通义等 API", "省本机算力、按量计费"),
        ("维度", "向量长度", "须与后续向量库一致"),
    ],
    goals=["理解 Chunk 与 Vector 关系", "实现 local/dashscope 双模式", "输出 data/vectors"],
    focus=["语义相似度直觉", "双 Provider 切换", "懒加载模型"],
    points=["同一语料换模型向量不可混用", "批量 embed 注意内存", "向量 JSON 便于调试"],
    hard=["首次下载模型慢", "中英混合语料效果差异"],
    harvest=["打通「文本可计算相似度」关键一步"],
    tech=[
        ("sentence-transformers + BGE", "中文效果好、本地可跑"),
        ("DashScope Embedding API", "与 LLM 同生态，部署简单"),
    ],
    summary="把语义变成向量，为向量库检索铺路。",
)

d(
    day="12",
    title="Chroma 向量检索",
    sprint="Sprint 2 · Enterprise RAG",
    terms=[
        ("向量数据库", "存向量并做相似度检索", "RAG 的记忆体"),
        ("Collection", "向量集合/表", "按知识库隔离数据"),
        ("Top-K", "返回最相似的 K 条", "召回量与噪声的权衡"),
        ("cosine", "余弦相似度", "常用语义相似度度量"),
    ],
    goals=["理解向量库角色", "掌握 Collection/Insert/Query", "实现问句→检索 Top-K"],
    focus=["持久化", "按 source 去重入库", "Day12 不接 LLM"],
    points=["先检索后生成，边界清晰", "metadata 带 source/page", "embedded vs server 模式（Day22）"],
    hard=["重复入库污染", "空库与无命中处理"],
    harvest=["最小检索链路可独立验收"],
    tech=[
        ("Chroma", "嵌入式友好、API 简单、适合学习与中小项目"),
    ],
    summary="纯检索日：问句向量化→Top-K，不生成答案。",
)

d(
    day="13",
    title="RAG Pipeline（检索增强生成）",
    sprint="Sprint 2 · Enterprise RAG",
    terms=[
        ("RAG", "检索增强生成", "用外部知识降低幻觉、可溯源"),
        ("Context 注入", "把检索结果写入 Prompt", "让 LLM 基于资料回答"),
        ("Citation / sources", "文档名+页码引用", "企业场景可审计"),
        ("知识库问答", "限定资料范围的问答", "Sprint 2 核心交付"),
    ],
    goals=["打通检索+生成", "注入 Prompt 并调用 LLM", "返回答案与来源"],
    focus=["Prompt 设计", "无资料时的拒答", "sources 契约"],
    points=["资料不足要明确说无法回答", "sources 始终为数组", "RAG ≠ 搜索引擎"],
    hard=["检索噪声导致胡编", "上下文超长截断"],
    harvest=["企业知识库最小可用闭环"],
    tech=[
        ("自研 rag_pipeline", "链路清晰可控，便于教学与面试讲解"),
        ("既有 llm.chat", "复用 Day04，避免重复造轮子"),
    ],
    summary="Sprint 2 功能高潮：检索→Prompt→LLM→带引用的答案。",
)

d(
    day="14",
    title="企业化优化与 Release v0.2",
    sprint="Sprint 2 · Enterprise RAG",
    terms=[
        ("可观测", "日志/耗时/状态可查", "出问题能定位"),
        ("可排错", "统一异常与友好错误", "用户与运维都可读"),
        ("可交付", "文档/Swagger/Docker/Tag", "像产品而不是作业"),
        ("Release", "版本冻结与发布", "Sprint 收官仪式"),
    ],
    goals=["补齐日志异常文档 Docker", "完善引用与 Swagger", "发布 v0.2.0"],
    focus=["不写新功能", "工程收尾", "验收清单"],
    points=["请求中间件记耗时", "LLM 异常映射 503/504", "Tag 与 CHANGELOG"],
    hard=["抵制继续加功能的冲动", "文档与实现严格对齐"],
    harvest=["Enterprise RAG 可对外演示与交付"],
    tech=[
        ("Swagger/OpenAPI", "零成本接口说明书"),
        ("Git Tag", "版本锚点，便于回滚与简历写版本"),
    ],
    summary="把 Day08~13 包装成可交付的 v0.2 企业 RAG。",
)

d(
    day="15",
    title="Agent Core（Planner + Tool）",
    sprint="Sprint 3 · Enterprise AI Agent",
    terms=[
        ("Agent", "能规划并调用工具完成目标的系统", "比 ChatBot 多「行动」"),
        ("Planner", "任务分解/选工具", "决定要不要调工具、调哪个"),
        ("Tool / Function Calling", "外部能力封装", "让 LLM 触达知识库等系统"),
        ("Observation", "工具返回结果", "供 LLM 总结成最终答案"),
    ],
    goals=["区分 Agent 与 ChatBot", "实现 Planner→Tool→Answer 循环", "能调 RAG 工具"],
    focus=["最小 Agent 闭环", "为 Registry/Memory 留扩展点"],
    points=["不是每问都调工具", "工具结果要再经 LLM 总结", "计划步骤可观测"],
    hard=["规则 Planner 的边界与误判", "工具失败时的诚实回答"],
    harvest=["从问答机器人迈向可行动 Agent"],
    tech=[
        ("自研 Planner+Executor", "教学清晰，先规则后可升级 ReAct"),
        ("RAG 作为首个 Tool", "复用 Sprint 2 成果"),
    ],
    summary="Sprint 3 开门：Agent = 规划 + 工具 + 观察 + 回答。",
)

d(
    day="16",
    title="Tool Registry（工具注册表）",
    sprint="Sprint 3 · Enterprise AI Agent",
    terms=[
        ("Tool Registry", "工具名→实现的注册中心", "新增工具不改 Executor 核心"),
        ("LLM→Tool→LLM", "企业 AI 通用模式", "模型负责推理，工具负责执行"),
        ("pdf_tool / calculator", "除 RAG 外的能力扩展", "证明 Registry 可扩展"),
    ],
    goals=["理解 Registry 价值", "重构硬编码 handlers", "实现多工具并由 Planner 选择"],
    focus=["注册而非 if-else 膨胀", "工具 schema/描述", "Planner 路由"],
    points=["工具失败要返回可总结的错误", "命名稳定便于日志", "一个工具一件事"],
    hard=["工具选择冲突", "不安全表达式（计算器需沙箱）"],
    harvest=["Agent 具备可插拔工具体系"],
    tech=[
        ("Registry 模式", "开闭原则：对扩展开放、对修改关闭"),
    ],
    summary="工具工程化：注册表让 Agent 可持续加能力。",
)

d(
    day="17",
    title="Memory（会话记忆）",
    sprint="Sprint 3 · Enterprise AI Agent",
    terms=[
        ("Short Memory", "会话内 messages 历史", "支持多轮「你刚才说」"),
        ("Long Memory", "跨轮事实 facts", "记住「我是谁」类稳定信息"),
        ("session_id", "会话标识", "隔离不同用户/对话线程"),
    ],
    goals=["理解无 Memory 则每轮失忆", "实现 Short/Long Memory", "POST /agent 支持 session_id"],
    focus=["历史注入 LLM", "facts 提取与注入 system", "JSON 持久化"],
    points=["限制 MEMORY_MAX_TURNS 防爆上下文", "敏感信息不乱记", "session 文件可清理"],
    hard=["事实抽取规则脆弱", "长对话 Token 成本上升"],
    harvest=["Agent 具备多轮对话产品形态"],
    tech=[
        ("JSON 文件 Memory", "零依赖、易调试，适合学习阶段"),
        ("chat_messages 多轮 API", "与 OpenAI messages 模型对齐"),
    ],
    summary="让 Agent「记得住」：session + short/long memory。",
)

d(
    day="18",
    title="MCP 基础（Client）",
    sprint="Sprint 3 · Enterprise AI Agent",
    terms=[
        ("MCP", "Model Context Protocol 模型上下文协议", "统一连接外部工具/资源"),
        ("MCP Client", "连接并调用 Server 的一方", "本项目 Agent 侧"),
        ("MCP Server", "暴露 tools/resources 的一方", "可替换、可配置"),
        ("桥接 Registry", "MCP Tool → 本地 Tool Registry", "Agent 无感调用外部工具"),
    ],
    goals=["理解 MCP 解决什么问题", "跑通 Client 连接", "把 MCP Tool 桥进 Registry"],
    focus=["协议思维", "Client/Server/Tool 关系", "配置化启动命令"],
    points=["内置工具与 MCP 工具可并存", "MCP_ENABLED 开关", "先连通再换真实 Server"],
    hard=["stdio 进程生命周期", "Windows 下 npx/命令路径"],
    harvest=["从「自己写死 Tool」到「协议化扩展」"],
    tech=[
        ("MCP Python SDK", "官方协议实现，生态对齐"),
        ("桥接模式", "不推翻现有 Registry，平滑接入"),
    ],
    summary="协议日：Agent 学会连接「外部工具世界」。",
)

d(
    day="19",
    title="Filesystem MCP Server",
    sprint="Sprint 3 · Enterprise AI Agent",
    terms=[
        ("Filesystem MCP", "读写本地文件的官方 Server", "Agent 可读 README/代码"),
        ("沙箱根目录", "允许访问的路径边界", "安全底线"),
        ("配置化换服", "改命令即可换 GitHub/SQLite 等", "体现 MCP 价值"),
    ],
    goals=["接入真实 Filesystem Server", "自然语言读项目文件", "掌握换服配置思路"],
    focus=["沙箱权限", "Planner 识别读文件意图", "端到端演示"],
    points=["只开放项目根或更小范围", "读文件≠ RAG 知识库", "失败要可解释"],
    hard=["路径穿越与权限", "大文件读入上下文爆炸"],
    harvest=["完整链路：问题→MCP 读文件→回答"],
    tech=[
        ("@modelcontextprotocol/server-filesystem", "官方、成熟、演示说服力强"),
        ("npx 拉起 Server", "无需自建 Server 即可用"),
    ],
    summary="MCP 从概念到能用：插上文件系统，Agent 能看项目。",
)

d(
    day="20",
    title="Enterprise Workflow",
    sprint="Sprint 3 · Enterprise AI Agent",
    terms=[
        ("Workflow", "意图分类与路由引擎", "统一散落的 Planner 规则"),
        ("意图 Intent", "chat/rag/mcp/calc 等", "决定走哪条能力链"),
        ("可观测 workflow 字段", "响应中展示路由决策", "调试与演示必备"),
    ],
    goals=["统一意图分类与编排", "跑通 RAG 与 Filesystem 两条主链", "响应带 workflow 元数据"],
    focus=["优先级与冲突", "闲聊不调工具", "企业助手行为"],
    points=["路由错误比模型差更伤体验", "workflow.reason 要人能读", "边界：不做完整 ReAct 多轮"],
    hard=["意图歧义（总结 PDF vs 读 README）", "工具链优先级设计"],
    harvest=["Agent 像「会分工的助手」而非单工具脚本"],
    tech=[
        ("规则 Workflow 引擎", "可控、可测、易讲清，适合 v0.3"),
    ],
    summary="把 Day15~19 收拢成可观测的企业工作流。",
)

d(
    day="21",
    title="Sprint Review + Release v0.3（含 Web/SSE）",
    sprint="Sprint 3 · Enterprise AI Agent",
    terms=[
        ("Sprint Review", "能力打磨与发布", "可观测、可排错、可交付"),
        ("Web UI", "React 聊天界面", "浏览器演示主入口"),
        ("SSE", "Server-Sent Events 单向流", "逐字输出、实现简单"),
        ("实时 Tool", "天气/新闻/体育等外部数据", "与 RAG 知识库分工"),
    ],
    goals=["文档与 Prompt 收尾", "发布 v0.3.0", "补齐前端与流式/实时工具（21_1/21_2）"],
    focus=["交付包装", "演示链路", "版本与健康检查"],
    points=["/health 带版本号", "前端展示 sources/workflow", "流式与同步 API 并存"],
    hard=["SSE 与代理缓冲", "实时 API 不稳定时的降级"],
    harvest=["可浏览器演示的企业 Agent v0.3"],
    tech=[
        ("React + Vite", "轻量、热更新快、适合内嵌管理端"),
        ("SSE", "比 WebSocket 简单，满足单向流式"),
        ("Open-Meteo / RSS / TheSportsDB", "免 Key 或低门槛，适合学习演示"),
    ],
    summary="Sprint 3 收官：Agent 可交付，并具备 Web + 流式 + 实时工具。",
)

d(
    day="22",
    title="Docker Compose 一键启动",
    sprint="Sprint 4 · Engineering",
    terms=[
        ("Compose", "多容器编排", "一键拉起 api+chroma(+ollama)"),
        ("服务发现", "容器名作主机名", "api 连 chroma:8000"),
        ("profile", "可选服务组", "local-llm / redis 按需启用"),
        ("健康检查", "healthcheck + depends_on", "保证启动顺序正确"),
    ],
    goals=["理解多容器编排", "区分 Chroma embedded/server", "一条命令启动可演示环境"],
    focus=["网络与卷", "环境变量对齐", "双模式 LLM"],
    points=["默认通义、profile 启 Ollama", "数据卷持久化", "端口冲突要排查"],
    hard=["镜像构建网络与体积", "Windows 路径与 CRLF entrypoint"],
    harvest=["本地栈从「多条 docker run」变成一键 Compose"],
    tech=[
        ("Docker Compose", "本地/演示标准编排，学习成本低于 K8s"),
        ("Chroma Server", "与 API 进程解耦，更接近生产形态"),
    ],
    summary="工程化启动：Compose 把 API、向量库、可选 LLM 编成一体。",
)

d(
    day="23",
    title="Nginx 反向代理",
    sprint="Sprint 4 · Engineering",
    terms=[
        ("反向代理", "客户端只认入口，后端对用户透明", "统一域名/端口与安全边界"),
        ("静态资源托管", "Nginx 直接返回前端 dist", "动静分离"),
        ("HTTPS / 域名", "证书与 server_name", "生产访问形态"),
        ("SSE 反代", "关闭 proxy_buffering", "保证流式不被攒包"),
    ],
    goals=["用户→Nginx→FastAPI", "托管前端静态页", "理解 HTTPS/域名位置"],
    focus=["唯一对外入口", "API 内网化", "上传大小与超时"],
    points=["api 可不映射宿主机 8000", "SPA try_files", "client_max_body_size"],
    hard=["SSE 缓冲导致无流式感", "80 端口占用"],
    harvest=["具备「像产品一样」的统一访问入口"],
    tech=[
        ("Nginx", "反代与静态托管事实标准"),
        ("多阶段 Dockerfile", "前端 build 进镜像，交付自包含"),
    ],
    summary="部署入口日：一个 localhost 同时服务 UI 与 API。",
)

d(
    day="24",
    title="日志 + 配置管理",
    sprint="Sprint 4 · Engineering",
    terms=[
        ("INFO/WARNING/ERROR", "日志分级", "正常/可恢复/需排查"),
        ("配置分层", "yaml 默认 + .env 覆盖", "密钥与默认值分离"),
        ("Request ID", "单次请求唯一 ID", "串联全链路日志"),
        ("Trace ID", "跨服务链路 ID", "了解即可，本日透传"),
    ],
    goals=["分级日志落盘", "config/ + .env 分层", "实现 Request ID"],
    focus=["app.log vs error.log", "contextvars 注入", "轮转防撑盘"],
    points=["响应头 X-Request-ID", "错误响应可带回 request_id", "禁止打 Key"],
    hard=["async 下 context 传递", "日志过多（SSE）需节制"],
    harvest=["出问题能用 request_id 在日志里「跟单」"],
    tech=[
        ("logging dictConfig + RotatingFileHandler", "标准库即可，无额外运维依赖"),
        ("contextvars", "异步友好的请求上下文"),
        ("PyYAML", "可读的默认配置文件"),
    ],
    summary="可观测基础：分级落盘 + 配置分层 + Request ID。",
)

d(
    day="25",
    title="Token / 成本统计",
    sprint="Sprint 4 · Engineering",
    terms=[
        ("Prompt / Completion Tokens", "输入与输出 Token", "计费与上下文占用"),
        ("usage", "API 返回的用量字段", "真实计量来源"),
        ("Cost 估算", "Token × 单价", "AI PM 核心问题"),
        ("单价表", "pricing.yaml", "可配置、可演示"),
    ],
    goals=["读懂 usage", "估算单次与日成本", "挂到 API/日志/可选前端"],
    focus=["可观测成本", "面试算账题", "不建完整计费系统"],
    points=["流式也要汇总 usage", "缺 usage 时有兜底策略", "成本字段进日志"],
    hard=["不同厂商计价单位差异", "工具调用多轮累计"],
    harvest=["能回答「这次花多少、一天大概多少」"],
    tech=[
        ("从 API usage 读取", "比自研 tokenizer 更贴近账单"),
        ("pricing.yaml", "演示友好、易改单价"),
    ],
    summary="AI PM 视角：Token 与钱变成可度量指标。",
)

d(
    day="26",
    title="架构设计文档",
    sprint="Sprint 4 · Engineering",
    terms=[
        ("架构文档", "系统如何构成与协作", "面试/评审讲清「怎么做」"),
        ("方案设计", "背景、选型、风险与对策", "讲清「为什么」"),
        ("技术选型", "对比备选后的决策", "Solution 岗核心能力"),
        ("风险分析", "幻觉/成本/Chunk 等", "有对策才算方案"),
    ],
    goals=["写清背景与为何要 RAG", "论证选型", "画出主链路并给风险对策"],
    focus=["面向评审而非日记", "图文一致", "与 README 交叉引用"],
    points=["两份文档分工：architecture vs solution-design", "主链路一张图讲完", "风险表要可执行"],
    hard=["避免写成流水账 Day 汇总", "权衡要诚实写取舍"],
    harvest=["具备可对外讲的 Solution 材料"],
    tech=[
        ("Markdown + ASCII/示意图", "低成本、Git 可追踪"),
        ("既有实现反推文档", "文档与代码一致，防空谈"),
    ],
    summary="Solution 能力日：背景→选型→架构→风险，两份文档讲完。",
)

d(
    day="27",
    title="README + GitHub 包装",
    sprint="Sprint 4 · Engineering",
    terms=[
        ("作品集门面", "README 第一眼体验", "30 秒回答是什么/怎么跑/到哪版"),
        ("Quick Start", "最短可运行路径", "降低试用成本"),
        ("徽章 Badge", "版本/技术栈标识", "提升专业观感"),
        ("CHANGELOG / LICENSE", "版本记录与开源许可", "交付完整性"),
    ],
    goals=["产品化重写 README", "对齐 Roadmap/API/版本", "仓库像可交付产品"],
    focus=["叙事清晰", "链接到架构与 Day 文档", "演示路径固定"],
    points=["顶部即产品定位", "Compose 一键启动写进 Quick Start", "避免作业口吻"],
    hard=["信息过载 vs 信息不足", "截图/演示与真实能力一致"],
    harvest=["v0.4/v1.0 作品集门面就绪，工程收官"],
    tech=[
        ("GitHub README 作为产品首页", "招聘与合作方第一触点"),
        ("MIT LICENSE", "常见开源许可，降低使用顾虑"),
    ],
    summary="包装收官：让仓库第一眼像产品，而不是作业文件夹。",
)


def esc(s: str) -> str:
    return s.replace('"', "'").replace("\n", " ")


def render(day: dict) -> str:
    title = day["title"]
    root = f"Day{day['day']} {title}"
    lines = [
        f"# Day{day['day']} 思维导图 — {title}",
        "",
        f"> Sprint：{day['sprint']}  ·  对应文档：[docs/Day{day['day']}.md](../docs/Day{day['day']}.md)",
        "",
        "## 导图（Mermaid）",
        "",
        "在支持 Mermaid 的编辑器（VS Code / GitHub / Typora）中可直接预览。",
        "",
        "```mermaid",
        "mindmap",
        f"  root(({esc(root)}))",
        "    术语定义与作用",
    ]
    for name, definition, role in day["terms"]:
        lines.append(f"      {esc(name)}")
        lines.append(f"        定义: {esc(definition)}")
        lines.append(f"        作用: {esc(role)}")

    lines.append("    学习目标")
    for g in day["goals"]:
        lines.append(f"      {esc(g)}")

    lines.append("    重点")
    for x in day["focus"]:
        lines.append(f"      {esc(x)}")

    lines.append("    要点")
    for x in day["points"]:
        lines.append(f"      {esc(x)}")

    lines.append("    难点")
    for x in day["hard"]:
        lines.append(f"      {esc(x)}")

    lines.append("    使用的技术与选型理由")
    for name, why in day["tech"]:
        lines.append(f"      {esc(name)}")
        lines.append(f"        为什么: {esc(why)}")

    lines.append("    总结收获")
    for x in day["harvest"]:
        lines.append(f"      {esc(x)}")
    lines.append(f"      一句话: {esc(day['summary'])}")

    lines.extend(
        [
            "```",
            "",
            "## 结构化速览",
            "",
            "### 术语",
            "",
            "| 术语 | 定义/解析 | 作用 |",
            "|------|-----------|------|",
        ]
    )
    for name, definition, role in day["terms"]:
        lines.append(f"| {name} | {definition} | {role} |")

    lines.extend(["", "### 学习目标", ""])
    for g in day["goals"]:
        lines.append(f"- {g}")

    lines.extend(["", "### 重点", ""])
    for x in day["focus"]:
        lines.append(f"- {x}")

    lines.extend(["", "### 要点", ""])
    for x in day["points"]:
        lines.append(f"- {x}")

    lines.extend(["", "### 难点", ""])
    for x in day["hard"]:
        lines.append(f"- {x}")

    lines.extend(["", "### 技术与为什么用", ""])
    for name, why in day["tech"]:
        lines.append(f"- **{name}**：{why}")

    lines.extend(["", "### 总结收获", ""])
    for x in day["harvest"]:
        lines.append(f"- {x}")
    lines.extend(["", f"**一句话：** {day['summary']}", ""])
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = [
        "# 学习思维导图索引",
        "",
        "> Day01 ~ Day27 每日知识结构：术语、目标、重点/要点/难点、技术选型与收获。",
        "",
        "| Day | 主题 | 文件 |",
        "|-----|------|------|",
    ]
    for day in DAYS:
        path = OUT / f"Day{day['day']}.md"
        path.write_text(render(day), encoding="utf-8")
        index.append(
            f"| Day{day['day']} | {day['title']} | [Day{day['day']}.md](Day{day['day']}.md) |"
        )
        print("wrote", path.name)
    (OUT / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print("wrote README.md, total", len(DAYS))


if __name__ == "__main__":
    main()
