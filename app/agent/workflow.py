# Day20 — Agent 工作流引擎
#
# 功能：意图分类 + 统一编排，作为 Planner 唯一真相源
# 逻辑：classify → build_workflow → steps + workflow 元数据

import re
from dataclasses import dataclass
from enum import Enum

from app.mcp.bridge import (
    match_filesystem_intent,
    match_mcp_explicit_intent,
    plan_filesystem_step,
    plan_mcp_step,
)

RAG_KEYWORDS = ("总结", "文档", "知识库", "资料", "根据", "telnet", "如何", "什么")
PDF_READ_KEYWORDS = ("多少页", "几页", "页数", "读取", "解析", "打开", "预览")
CALC_KEYWORDS = ("计算", "等于", "加", "减", "乘", "除")
CALC_PATTERN = re.compile(r"[\d+\-*/().\s×÷]+")

# @brief: 意图枚举
class Intent(str, Enum):
    CHAT = "chat"
    CALCULATOR = "calculator"
    FILESYSTEM = "filesystem"
    RAG = "rag"
    PDF_READ = "pdf_read"
    MCP_EXPLICIT = "mcp_explicit"

# @brief: 工作流决策
@dataclass
class WorkflowDecision:
    intent: Intent
    need_tool: bool
    steps: list[dict]
    route: str
    reason: str

# @brief: 提取 PDF 文件名
# @param: message: 用户消息
# @return: PDF 文件名
def _extract_pdf_name(message: str) -> str | None:
    match = re.search(r"([\w\-.]+\.pdf)", message, re.I)
    return match.group(1) if match else None

# @brief: 检查是否为计算意图
# @param: message: 用户消息
# @return: 是否为计算意图
def _is_calculator_intent(message: str) -> bool:
    if any(keyword in message for keyword in CALC_KEYWORDS):
        return True
    expr = message.strip()
    for prefix in ("计算", "算一下", "求"):
        if expr.startswith(prefix):
            expr = expr[len(prefix) :].strip()
    return bool(CALC_PATTERN.fullmatch(expr) and re.search(r"\d", expr))

# @brief: 提取计算表达式
# @param: message: 用户消息
# @return: 计算表达式
def _extract_expression(message: str) -> str:
    expr = message.strip()
    for prefix in ("计算", "算一下", "求"):
        if expr.startswith(prefix):
            expr = expr[len(prefix) :].strip()
    expr = expr.replace("等于多少", "").replace("是多少", "").strip()
    expr = expr.replace("×", "*").replace("÷", "/")
    return expr.rstrip("?？.")

# @brief: 检查是否为 PDF 读取意图
# @param: message: 用户消息
# @return: 是否为 PDF 读取意图
def _is_pdf_read_intent(message: str) -> bool:
    if not _extract_pdf_name(message):
        return False
    if any(keyword in message for keyword in PDF_READ_KEYWORDS):
        return True
    if re.search(r"第\s*\d+\s*页", message):
        return True
    return False

# @brief: 提取页码
# @param: message: 用户消息
# @return: 页码
def _extract_page(message: str) -> int | None:
    match = re.search(r"第\s*(\d+)\s*页", message)
    return int(match.group(1)) if match else None

# @brief: 检查是否需要 RAG
# @param: message: 用户消息
# @return: 是否需要 RAG
def _needs_rag(message: str) -> bool:
    lower = message.lower()
    if any(keyword in lower for keyword in RAG_KEYWORDS):
        return True
    if ".pdf" in lower and "总结" in message:
        return True
    return False

# @brief: 构建 RAG 问题
# @param: message: 用户消息
# @return: RAG 问题
def _build_rag_question(message: str) -> str:
    filename = _extract_pdf_name(message)
    if filename:
        return f"{filename} 的主要内容是什么？"
    return message

# @brief: 检查是否为 MCP 显式意图
# @param: message: 用户消息
# @return: 是否为 MCP 显式意图
def _is_mcp_explicit_intent(message: str) -> bool:
    return match_mcp_explicit_intent(message)

# @brief: 检查是否为文件系统意图
# @param: message: 用户消息
# @return: 是否为文件系统意图
def _is_filesystem_intent(message: str) -> bool:
    return match_filesystem_intent(message)

# @brief: 创建聊天决策
# @param: reason: 原因
# @return: 聊天决策
def _chat_decision(reason: str) -> WorkflowDecision:
    return WorkflowDecision(
        intent=Intent.CHAT,
        need_tool=False,
        steps=[],
        route="Question → Memory → LLM → Answer",
        reason=reason,
    )

# @brief: 分类意图
# @param: message: 用户消息
# @return: 意图
def classify(message: str) -> Intent:
    if _is_calculator_intent(message):
        return Intent.CALCULATOR
    if _is_mcp_explicit_intent(message):
        return Intent.MCP_EXPLICIT
    if _is_filesystem_intent(message):
        return Intent.FILESYSTEM
    if _is_pdf_read_intent(message):
        return Intent.PDF_READ
    if _needs_rag(message):
        return Intent.RAG
    return Intent.CHAT

# @brief: 创建计算步骤
# @param: message: 用户消息
# @return: 计算步骤
def _step_calculator(message: str) -> dict:
    return {
        "tool": "calculator",
        "args": {"expression": _extract_expression(message)},
        "reason": "需要精确数学计算",
    }

# @brief: 创建 PDF 读取步骤
# @param: message: 用户消息
# @return: PDF 读取步骤
def _step_pdf_read(message: str) -> dict:
    filename = _extract_pdf_name(message)
    args: dict = {"filename": filename}
    page = _extract_page(message)
    if page is not None:
        args["page"] = page
    return {
        "tool": "pdf_read",
        "args": args,
        "reason": "需要读取 PDF 文件内容或页数",
    }

# @brief: 创建 RAG 步骤
# @param: message: 用户消息
# @return: RAG 步骤
def _step_rag(message: str) -> dict:
    return {
        "tool": "rag_query",
        "args": {"question": _build_rag_question(message)},
        "reason": "需要从知识库获取文档内容",
    }

# @brief: 构建工作流
# @param: message: 用户消息
# @return: 工作流决策
def build_workflow(message: str) -> WorkflowDecision:
    intent = classify(message)

    if intent == Intent.CALCULATOR:
        return WorkflowDecision(
            intent=intent,
            need_tool=True,
            steps=[_step_calculator(message)],
            route="Question → Calculator → Answer",
            reason="数学计算意图",
        )

    if intent == Intent.MCP_EXPLICIT:
        step = plan_mcp_step(message)
        if not step:
            return _chat_decision("MCP 未启用或工具不可用，降级为直接对话")
        return WorkflowDecision(
            intent=intent,
            need_tool=True,
            steps=[step],
            route="Question → MCP → Answer",
            reason="用户显式指定 MCP 工具",
        )

    if intent == Intent.FILESYSTEM:
        step = plan_filesystem_step(message)
        if not step:
            return _chat_decision("Filesystem MCP 未启用，降级为直接对话")
        return WorkflowDecision(
            intent=intent,
            need_tool=True,
            steps=[step],
            route="Question → Filesystem MCP → Answer",
            reason="读取/列出项目源码文件",
        )

    if intent == Intent.PDF_READ:
        return WorkflowDecision(
            intent=intent,
            need_tool=True,
            steps=[_step_pdf_read(message)],
            route="Question → PDF Tool → Answer",
            reason="PDF 页数或按页读取",
        )

    if intent == Intent.RAG:
        return WorkflowDecision(
            intent=intent,
            need_tool=True,
            steps=[_step_rag(message)],
            route="Question → RAG Search → Summary → Answer",
            reason="知识库检索与总结",
        )

    return WorkflowDecision(
        intent=Intent.CHAT,
        need_tool=False,
        steps=[],
        route="Question → Memory → LLM → Answer",
        reason="无需工具，直接对话",
    )

# @brief: 将工作流决策转换为字典
# @param: decision: 工作流决策
# @return: 字典
def workflow_to_dict(decision: WorkflowDecision) -> dict:
    return {
        "intent": decision.intent.value,
        "need_tool": decision.need_tool,
        "route": decision.route,
        "reason": decision.reason,
    }
