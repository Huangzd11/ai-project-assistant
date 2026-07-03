import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:4b")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "你是一名AI技术项目经理.")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "600"))
