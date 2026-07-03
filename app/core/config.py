# Day02 — 环境变量加载（python-dotenv）
# Day04 — 扩展 LLM 相关配置
# Day08 — 新增 UPLOAD_DIR
#
# 功能：从 .env 读取配置，提供全局常量
# 逻辑：load_dotenv() 在模块导入时执行一次，os.getenv 带默认值

import os

from dotenv import load_dotenv

load_dotenv()

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
