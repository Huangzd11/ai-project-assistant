from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# API Key 管理 - 企业开发的标准方式（通义千问示例）
# OPENAI_API_KEY=你的Key          # 在 https://bailian.console.aliyun.com/ 获取
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# MODEL_NAME=qwen-plus

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("MODEL_NAME")

if not api_key:
    raise SystemExit(
        "未找到 OPENAI_API_KEY。请在项目根目录创建 .env 文件，"
        "可参考 .env.example 填写你的 API Key、Base URL 和模型名称。"
    )

client = OpenAI(api_key=api_key, base_url=base_url)

# messages 是整个 LLM 应用的核心
# messages 是一个列表，列表中每个元素是一个字典，字典中包含 role 和 content 两个键。
# role 可以是 system、user 或 assistant，分别表示系统角色、用户角色和助手角色。
# content 是字符串，表示消息的内容。
# system 角色用于设定 AI 的个性、角色、目标等 (定义身份和规则)
# user 角色用于输入问题、请求等
# assistant 角色用于输出回答、响应等 (保存历史回答，这样模型才知道聊天上下文)
messages = [
    {
        "role": "system",
        "content": "你是一名AI助手."  # 定义身份和规则
        # "content": "所有回答必须输出JSON."
    }
]

# 实现连续聊天（最核心的代码）
while True:
    question = input("你: ")

    messages.append({
        "role": "user",
        "content": question
    })

    #response = client.chat.completions.create(
    #    model=model,
    #    messages=messages
    #)

    #answer = response.choices[0].message.content

    #print(f"AI: {answer}")

    #messages.append({
    #    "role": "assistant",
    #    "content": answer
    #})

    # Streaming（流式输出）实现一个字一个字出现效果
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

    # 保存历史回答,这样模型才知道聊天上下文
    messages.append({
        "role": "assistant",
        "content": chunk.choices[0].delta.content
    })