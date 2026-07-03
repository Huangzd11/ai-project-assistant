# Day01 — LLM 基础概念与 Prompt

## 目标

- 理解大语言模型（LLM）的基本工作原理
- 掌握 Prompt 编写基础：system / user / assistant 角色
- 了解 Token、上下文窗口、温度等核心概念

## 学习内容

| 概念 | 说明 |
|------|------|
| LLM | 基于 Transformer 的生成式语言模型 |
| Prompt | 输入给模型的指令与上下文 |
| System Prompt | 定义 AI 身份、规则与行为边界 |
| 上下文窗口 | 模型一次能处理的最大 Token 数 |

## 练习

运行 [`examples/prompt_demo.py`](../examples/prompt_demo.py)，体验以下三个实验：

1. **System Prompt**：同一问题，不同角色设定，观察回答风格变化
2. **Few-shot**：通过示例约束输出为 JSON 格式
3. **Temperature**：对比 `0.2` 与 `1.0` 的回答创造性差异

```powershell
pip install -r requirements.txt
copy .env.example .env    # 填写云端 API Key
python examples/prompt_demo.py
```

## 状态

已完成。Day02 的 `chat_demo.py` 进一步演示了 messages 多轮对话实战。
