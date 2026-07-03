"""Day03 — 本地 Ollama 流式调用示例"""

from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1",
)

stream = client.chat.completions.create(
    model="qwen3:4b",
    messages=[
        {"role": "user", "content": "介绍一下自己。 /no_think"},
    ],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)

print()
