# Day03 — 本地 Ollama 模型调用

## 目标

- 通过 OpenAI 兼容接口连接本地 Ollama
- 演示流式调用本地模型 `qwen3:4b`
- 理解云端 API 与本地部署的差异

## 核心代码

示例见 [`examples/ollama_demo.py`](../examples/ollama_demo.py)。

```python
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
```

## 启动方式

**前置条件：** 已安装并启动 Ollama，且已拉取模型。

```powershell
ollama pull qwen3:4b
ollama serve
python examples/ollama_demo.py
```

> 本地 `qwen3:4b` 首次推理可能较慢，属正常现象。可在 prompt 末尾加 `/no_think` 减少等待时间。

## 要点

- Ollama 提供 OpenAI 兼容的 `/v1` 端点，无需修改 SDK 调用方式
- `api_key` 可填任意字符串（Ollama 不校验）
- 本地模型适合开发调试，生产环境需考虑 GPU 资源与并发
