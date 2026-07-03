# Day02 — 命令行连续对话

## 目标

- 从 `.env` 读取 API Key、Base URL、模型名
- 维护 `messages` 列表实现多轮对话
- 使用 `stream=True` 实现流式逐字输出

## 核心代码

示例见 [`examples/chat_demo.py`](../examples/chat_demo.py)。

## messages 结构

`messages` 是整个 LLM 应用的核心数据结构：

```python
messages = [
    {"role": "system", "content": "你是一名AI助手."},
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮你的？"},
]
```

| 角色 | 用途 |
|------|------|
| `system` | 设定 AI 个性、角色、规则 |
| `user` | 用户输入 |
| `assistant` | 模型历史回答，维持上下文 |

## 启动方式

**前置条件：** 在 [阿里云百炼](https://bailian.console.aliyun.com/) 获取 API Key。

```powershell
pip install -r requirements.txt
copy .env.example .env    # 填写 OPENAI_API_KEY 等
python examples/chat_demo.py
```

## 技术栈

- OpenAI Python SDK（兼容通义千问 DashScope）
- python-dotenv
