# Day01 — Prompt 基础练习
# 运行：python examples/prompt_demo.py
#
# 功能：演示 system prompt、few-shot、temperature 对输出的影响
# 逻辑：三个独立实验函数，依次调用 ask() 发送 messages 到 LLM

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("MODEL_NAME")

if not api_key:
    raise SystemExit("请配置 .env 中的 OPENAI_API_KEY（可参考 .env.example）")

client = OpenAI(api_key=api_key, base_url=base_url)


def ask(messages: list, temperature: float = 0.7) -> str:
    """Day01 — 封装单次 LLM 请求，可指定 temperature。"""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def demo_system_prompt():
    """实验1：不同 system 角色 → 回答风格不同。"""
    print("=== 1. System Prompt 对比 ===\n")
    question = "用一句话介绍你自己。"

    for role in ["你是一名严谨的工程师。", "你是一名幽默的博主。"]:
        answer = ask([
            {"role": "system", "content": role},
            {"role": "user", "content": question},
        ])
        print(f"[{role}]")
        print(answer, "\n")


def demo_few_shot():
    """实验2：用示例对话约束输出格式（JSON）。"""
    print("=== 2. Few-shot 格式约束 ===\n")
    answer = ask([
        {
            "role": "system",
            "content": "将用户输入转为 JSON，仅输出 JSON，不要其他文字。",
        },
        {"role": "user", "content": "苹果"},
        {"role": "assistant", "content": '{"item": "苹果", "category": "水果"}'},
        {"role": "user", "content": "笔记本电脑"},
    ])
    print(answer, "\n")


def demo_temperature():
    """实验3：低 temperature 更稳定，高 temperature 更有创造性。"""
    print("=== 3. Temperature 对比 ===\n")
    question = "给我一个创业点子。"
    messages = [{"role": "user", "content": question}]

    for temp in [0.2, 1.0]:
        answer = ask(messages, temperature=temp)
        print(f"[temperature={temp}]")
        print(answer, "\n")


if __name__ == "__main__":
    demo_system_prompt()
    demo_few_shot()
    demo_temperature()
