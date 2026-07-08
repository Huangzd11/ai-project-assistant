# Day02 — 环境变量加载（python-dotenv）
# Day04 — 扩展 LLM 相关配置
# Day08 — 新增 UPLOAD_DIR
#
# 功能：从 .env 读取配置，提供全局常量
# 逻辑：load_dotenv() 在模块导入时执行一次，os.getenv 带默认值

import os

from dotenv import load_dotenv

load_dotenv()

APP_VERSION = "0.3.0"

# Day02/Day03 — OpenAI 兼容 API（云端通义千问 或 本地 Ollama）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:4b")
PROVIDER = os.getenv("PROVIDER", "ollama")

# Day04 — 单轮对话的系统提示词与超时
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "你是一名AI技术项目经理.")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "600"))

# Day08 — PDF 上传保存目录
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Day09 — PDF 解析 JSON 输出目录
PARSED_DIR = os.getenv("PARSED_DIR", "data/parsed")

# Day10 — 文本块拆分（按页）
CHUNKS_DIR = os.getenv("CHUNKS_DIR", "data/chunks")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Day11 — Embedding 向量化
VECTORS_DIR = os.getenv("VECTORS_DIR", "data/vectors")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "512"))

# Day12 — Chroma 向量库
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "knowledge")
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", "5"))

# Day13 — RAG 问答
RAG_SYSTEM_PROMPT = os.getenv(
    "RAG_SYSTEM_PROMPT",
    "你是一名企业知识库助手。请仅根据用户提供的「参考资料」回答问题。"
    "若资料不足以回答，请明确说「根据现有资料无法回答」。"
    "回答时请注明引用来源，格式：根据《文档名》第X页：……",
)

# Day15 — Agent 总结阶段 system prompt（Day21 优化：区分 RAG / 文件 / 失败）
AGENT_ANSWER_PROMPT = os.getenv(
    "AGENT_ANSWER_PROMPT",
    "你是企业 AI Agent 助手。根据下方「工具执行结果」用简洁中文回答用户。"
    "若结果为知识库检索且含 sources，回答中注明文档名与页码。"
    "若结果为项目文件内容（如 README），概括要点，勿逐字复述全文。"
    "若工具失败或 MCP 未启用，如实说明原因，不要编造。",
)

# Day17 — Agent 会话记忆
MEMORY_DIR = os.getenv("MEMORY_DIR", "data/conversations")
MEMORY_MAX_TURNS = int(os.getenv("MEMORY_MAX_TURNS", "10"))

# Day18/19 — MCP Client（默认 Filesystem Server）
MCP_ENABLED = os.getenv("MCP_ENABLED", "false").lower() in {"1", "true", "yes"}
MCP_SERVER_COMMAND = os.getenv("MCP_SERVER_COMMAND", "npx")
MCP_FILESYSTEM_ROOT = os.getenv(
    "MCP_FILESYSTEM_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)
_default_fs_args = f"-y,@modelcontextprotocol/server-filesystem,{MCP_FILESYSTEM_ROOT}"
MCP_SERVER_ARGS = os.getenv("MCP_SERVER_ARGS", _default_fs_args)
