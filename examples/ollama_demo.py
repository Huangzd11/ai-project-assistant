# Day03 — 本地 Ollama 流式调用
# 运行：python examples/ollama_demo.py（需先 ollama serve）
#
# 功能：通过 OpenAI 兼容端点调用本地 qwen3:4b
# 逻辑：
#   1. base_url 指向 Ollama 的 /v1 接口
#   2. api_key 填任意字符串（Ollama 不校验）
#   3. stream 模式逐块打印；/no_think 可加速 qwen3 推理

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
