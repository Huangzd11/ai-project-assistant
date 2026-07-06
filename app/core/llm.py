# Day02 — OpenAI SDK 调用 LLM（messages 结构）
# Day04 — 封装为 chat() 函数，供 FastAPI 调用
# Day13 — 支持可选 system_prompt（RAG 专用）
#
# 功能：统一 LLM 推理入口
# 逻辑：
#   1. 用 config 中的 Key / BaseURL 创建 OpenAI 客户端
#   2. 组装 system + user 两条 message
#   3. 调用 chat.completions.create，返回文本内容
#
# 说明：切换 OPENAI_BASE_URL 即可在 Ollama / 通义千问之间迁移

from openai import OpenAI

from app.core.config import (
    MODEL_NAME,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    REQUEST_TIMEOUT,
    SYSTEM_PROMPT,
)

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    timeout=REQUEST_TIMEOUT,
)


# @brief: 单轮对话，传入用户消息，返回模型回答
# @param: message: 用户输入文本
# @param: system_prompt: 可选 system 提示词，默认 SYSTEM_PROMPT
# @return: 模型回答文本
def chat(message: str, system_prompt: str | None = None) -> str:
    prompt = system_prompt or SYSTEM_PROMPT
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message},
        ],
    )
    return response.choices[0].message.content or ""
