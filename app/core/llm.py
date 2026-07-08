# Day02 — OpenAI SDK 调用 LLM（messages 结构）
# Day04 — 封装为 chat() 函数，供 FastAPI 调用
# Day13 — 支持可选 system_prompt（RAG 专用）
# Day14 — LLM 异常映射为友好错误
# Day17 — chat_messages() 多轮对话
# Day21_2 — chat_messages_stream() SSE 流式输出
#
# 功能：统一 LLM 推理入口
# 逻辑：
#   1. 用 config 中的 Key / BaseURL 创建 OpenAI 客户端
#   2. 组装 system + user 两条 message
#   3. 调用 chat.completions.create，返回文本内容
#
# 说明：切换 OPENAI_BASE_URL 即可在 Ollama / 通义千问之间迁移
from typing import Iterator

from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError

from app.core.config import (
    MODEL_NAME,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    REQUEST_TIMEOUT,
    SYSTEM_PROMPT,
)
from app.core.exceptions import LLMTimeoutError, LLMUnavailableError
from app.core.logger import logger

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
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message},
            ],
        )
        content = response.choices[0].message.content or ""
        if not content:
            logger.warning("LLM returned empty content  model=%s", MODEL_NAME)
        return content
    except APITimeoutError as exc:
        logger.error("LLM timeout  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMTimeoutError() from exc
    except APIConnectionError as exc:
        logger.error("LLM connection failed  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc
    except OpenAIError as exc:
        logger.error("LLM error  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc


# @brief: 多轮对话，传入完整 messages（不含 system）
# @param: messages: 历史 + 当前 user 消息列表
# @param: system_prompt: 可选 system 提示词
# @return: 模型回答文本
def chat_messages(messages: list[dict], system_prompt: str | None = None) -> str:
    prompt = system_prompt or SYSTEM_PROMPT
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": prompt}, *messages],
        )
        content = response.choices[0].message.content or ""
        if not content:
            logger.warning("LLM returned empty content  model=%s", MODEL_NAME)
        return content
    except APITimeoutError as exc:
        logger.error("LLM timeout  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMTimeoutError() from exc
    except APIConnectionError as exc:
        logger.error("LLM connection failed  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc
    except OpenAIError as exc:
        logger.error("LLM error  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc


# @brief: 多轮对话流式输出，逐 token yield
# @param: messages: 历史 + 当前 user 消息列表
# @param: system_prompt: 可选 system 提示词
# @return: 文本片段迭代器
def chat_messages_stream(
    messages: list[dict],
    system_prompt: str | None = None,
) -> Iterator[str]:
    prompt = system_prompt or SYSTEM_PROMPT
    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": prompt}, *messages],
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta
    except APITimeoutError as exc:
        logger.error("LLM timeout  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMTimeoutError() from exc
    except APIConnectionError as exc:
        logger.error("LLM connection failed  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc
    except OpenAIError as exc:
        logger.error("LLM error  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc
