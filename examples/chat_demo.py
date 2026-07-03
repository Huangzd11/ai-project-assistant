from openai import OpenAI
import os
from dotenv import load_dotenv

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
