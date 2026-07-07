# Day15 — Agent 提示词
#
# 功能：Agent Planner / Executor 使用的 system prompt 默认值
# 逻辑：config.py 可通过环境变量覆盖

# @brief: Executor 根据工具 Observation 生成最终回答
FINAL_ANSWER_PROMPT = (
    "你是企业知识库助手。根据下方「工具执行结果」回答用户。"
    "若结果含 sources，回答中注明文档名与页码。"
    "若工具未找到内容，如实告知。"
)
