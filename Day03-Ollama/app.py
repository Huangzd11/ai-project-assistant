from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1"
    # timeout=600.0,
)

stream = client.chat.completions.create(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": "介绍一下自己。 /no_think",
        }
    ],
    # max_tokens=256,
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)

print()
