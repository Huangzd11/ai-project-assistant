# Day02 — 命令行连续对话（OpenAI 兼容 API + 流式输出）
# 运行：python examples/chat_demo.py
#
# 功能：终端多轮对话，逐字流式打印 AI 回答
# 逻辑：
#   1. 从 .env 加载 API Key / Base URL / 模型名
#   2. 维护 messages 列表（system + 历史 user/assistant）
#   3. 每轮：用户输入 → stream 请求 → 拼接 chunk → 追加到 messages

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("MODEL_NAME")

if not api_key:
    raise SystemExit(
        "未找到 OPENAI_API_KEY。请在项目根目录创建 .env 文件，"
        "可参考 .env.example 填写你的 API Key、Base URL 和模型名称。"
    )

client = OpenAI(api_key=api_key, base_url=base_url)

messages = [
    {
        "role": "system",
        "content": "你是一名AI助手.",
    }
]

while True:
    question = input("你: ")

    messages.append({
        "role": "user",
        "content": question
    })

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    full_answer = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_answer += content
    print()

    messages.append({
        "role": "assistant",
        "content": full_answer
    })
