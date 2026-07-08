# Day16 — Agent 任务规划
# Day18 — MCP 显式调用（mcp read_file README.md）
# Day19 — Filesystem 自然语言（看看 README）
#
# 功能：将用户目标分解为可执行的工具调用计划
# 逻辑：按意图路由 calculator → filesystem → mcp 显式 → pdf_read → rag_query

import re

RAG_KEYWORDS = ("总结", "文档", "知识库", "资料", "根据", "telnet", "如何", "什么")
PDF_READ_KEYWORDS = ("多少页", "几页", "页数", "读取", "解析", "打开", "预览")
CALC_KEYWORDS = ("计算", "等于", "加", "减", "乘", "除")
CALC_PATTERN = re.compile(r"[\d+\-*/().\s×÷]+")


# @brief: 从消息中提取 PDF 文件名
# @param: message: 用户消息
# @return: 文件名或 None
def _extract_pdf_name(message: str) -> str | None:
    match = re.search(r"([\w\-.]+\.pdf)", message, re.I)
    return match.group(1) if match else None


# @brief: 判断是否为计算意图
# @param: message: 用户消息
# @return: 是否计算
def _is_calculator(message: str) -> bool:
    if any(keyword in message for keyword in CALC_KEYWORDS):
        return True
    expr = message.strip()
    for prefix in ("计算", "算一下", "求"):
        if expr.startswith(prefix):
            expr = expr[len(prefix) :].strip()
    return bool(CALC_PATTERN.fullmatch(expr) and re.search(r"\d", expr))


# @brief: 提取计算表达式
# @param: message: 用户消息
# @return: 表达式字符串
def _extract_expression(message: str) -> str:
    expr = message.strip()
    for prefix in ("计算", "算一下", "求"):
        if expr.startswith(prefix):
            expr = expr[len(prefix) :].strip()
    expr = expr.replace("等于多少", "").replace("是多少", "").strip()
    expr = expr.replace("×", "*").replace("÷", "/")
    return expr.rstrip("?？.")

# @brief: 判断是否为 PDF 读取意图
# @param: message: 用户消息
# @return: 是否读 PDF
def _is_pdf_read(message: str) -> bool:
    if not _extract_pdf_name(message):
        return False
    if any(keyword in message for keyword in PDF_READ_KEYWORDS):
        return True
    if re.search(r"第\s*\d+\s*页", message):
        return True
    return False

# @brief: 提取 PDF 页码（可选）
# @param: message: 用户消息
# @return: 页码或 None
def _extract_page(message: str) -> int | None:
    match = re.search(r"第\s*(\d+)\s*页", message)
    return int(match.group(1)) if match else None

# @brief: 判断是否需要走知识库检索
# @param: message: 用户消息
# @return: 是否需要 RAG
def _needs_rag(message: str) -> bool:
    lower = message.lower()
    if any(keyword in lower for keyword in RAG_KEYWORDS):
        return True
    if ".pdf" in lower and "总结" in message:
        return True
    return False

# @brief: 从用户消息构造 RAG 检索问题
# @param: message: 用户消息
# @return: 检索问题文本
def _build_rag_question(message: str) -> str:
    filename = _extract_pdf_name(message)
    if filename:
        return f"{filename} 的主要内容是什么？"
    return message

# @brief: 规划执行步骤
# @param: user_message: 用户目标
# @return: 计划步骤列表，每步含 tool / args / reason
def plan(user_message: str) -> list[dict]:
    from app.mcp.bridge import plan_filesystem_step, plan_mcp_step

    if _is_calculator(user_message):
        return [
            {
                "tool": "calculator",
                "args": {"expression": _extract_expression(user_message)},
                "reason": "需要精确数学计算",
            }
        ]

    fs_step = plan_filesystem_step(user_message)
    if fs_step:
        return [fs_step]

    mcp_step = plan_mcp_step(user_message)
    if mcp_step:
        return [mcp_step]

    if _is_pdf_read(user_message):
        filename = _extract_pdf_name(user_message)
        args: dict = {"filename": filename}
        page = _extract_page(user_message)
        if page is not None:
            args["page"] = page
        return [
            {
                "tool": "pdf_read",
                "args": args,
                "reason": "需要读取 PDF 文件内容或页数",
            }
        ]

    if _needs_rag(user_message):
        return [
            {
                "tool": "rag_query",
                "args": {"question": _build_rag_question(user_message)},
                "reason": "需要从知识库获取文档内容",
            }
        ]

    return []
