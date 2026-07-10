# Day02 — OpenAI SDK 调用 LLM（messages 结构）
# Day04 — 封装为 chat() 函数，供 FastAPI 调用
# Day13 — 支持可选 system_prompt（RAG 专用）
# Day14 — LLM 异常映射为友好错误
# Day17 — chat_messages() 多轮对话
# Day21_2 — chat_messages_stream() SSE 流式输出
# Day25 — 解析 usage，返回 Token / Cost
#
# 功能：统一 LLM 推理入口
# 逻辑：
#   1. 用 config 中的 Key / BaseURL 创建 OpenAI 客户端
#   2. 组装 system + user 两条 message
#   3. 调用 chat.completions.create，返回文本 + usage
#
# 说明：切换 OPENAI_BASE_URL 即可在 Ollama / 通义千问之间迁移
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

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
from app.core.token_meter import UsageInfo, usage_from_openai

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
    timeout=REQUEST_TIMEOUT,
)

# @brief: LLM 结果
@dataclass
class LLMResult:
    content: str
    usage: UsageInfo | None = None


def _raise_llm_error(exc: Exception) -> None:
    if isinstance(exc, APITimeoutError):
        logger.error("event=llm_timeout  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMTimeoutError() from exc
    if isinstance(exc, APIConnectionError):
        logger.error("event=llm_connection_failed  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc
    if isinstance(exc, OpenAIError):
        logger.error("event=llm_error  model=%s  error=%s", MODEL_NAME, exc)
        raise LLMUnavailableError() from exc
    raise exc


# @brief: 单轮对话，传入用户消息，返回模型回答 + usage
# @param: message: 用户输入文本
# @param: system_prompt: 可选 system 提示词，默认 SYSTEM_PROMPT
# @return: LLMResult
def chat(message: str, system_prompt: str | None = None) -> LLMResult:
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
            logger.warning("event=llm_empty_content  model=%s", MODEL_NAME)
        usage = usage_from_openai(getattr(response, "usage", None), model=MODEL_NAME)
        if usage is None:
            logger.warning("event=usage_missing  model=%s  mode=chat", MODEL_NAME)
        return LLMResult(content=content, usage=usage)
    except (APITimeoutError, APIConnectionError, OpenAIError) as exc:
        _raise_llm_error(exc)
        raise  # pragma: no cover


# @brief: 多轮对话，传入完整 messages（不含 system）
# @param: messages: 历史 + 当前 user 消息列表
# @param: system_prompt: 可选 system 提示词
# @return: LLMResult
def chat_messages(messages: list[dict], system_prompt: str | None = None) -> LLMResult:
    prompt = system_prompt or SYSTEM_PROMPT
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": prompt}, *messages],
        )
        content = response.choices[0].message.content or ""
        if not content:
            logger.warning("event=llm_empty_content  model=%s", MODEL_NAME)
        usage = usage_from_openai(getattr(response, "usage", None), model=MODEL_NAME)
        if usage is None:
            logger.warning("event=usage_missing  model=%s  mode=chat_messages", MODEL_NAME)
        return LLMResult(content=content, usage=usage)
    except (APITimeoutError, APIConnectionError, OpenAIError) as exc:
        _raise_llm_error(exc)
        raise  # pragma: no cover


# @brief: 多轮对话流式输出；yield 文本片段，最后 yield UsageInfo | None
# @param: messages: 历史 + 当前 user 消息列表
# @param: system_prompt: 可选 system 提示词
# @return: 文本片段与末尾 usage 的迭代器
def chat_messages_stream(
    messages: list[dict],
    system_prompt: str | None = None,
) -> Iterator[str | UsageInfo | None]:
    prompt = system_prompt or SYSTEM_PROMPT
    try:
        create_kwargs: dict = {
            "model": MODEL_NAME,
            "messages": [{"role": "system", "content": prompt}, *messages],
            "stream": True,
        }
        # OpenAI / 通义兼容：流式末包返回 usage
        create_kwargs["stream_options"] = {"include_usage": True}
        try:
            stream = client.chat.completions.create(**create_kwargs)
        except (TypeError, OpenAIError) as exc:
            # 部分本地服务不支持 stream_options
            logger.warning("event=stream_options_unsupported  error=%s", exc)
            create_kwargs.pop("stream_options", None)
            stream = client.chat.completions.create(**create_kwargs)

        usage: UsageInfo | None = None
        for chunk in stream:
            raw_usage = getattr(chunk, "usage", None)
            if raw_usage is not None:
                usage = usage_from_openai(raw_usage, model=MODEL_NAME)
            choices = getattr(chunk, "choices", None) or []
            if not choices:
                continue
            delta = choices[0].delta.content or ""
            if delta:
                yield delta

        if usage is None:
            logger.warning("event=usage_missing  model=%s  mode=stream", MODEL_NAME)
        yield usage
    except (APITimeoutError, APIConnectionError, OpenAIError) as exc:
        _raise_llm_error(exc)
        raise  # pragma: no cover
