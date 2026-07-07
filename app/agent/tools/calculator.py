# Day16 — 计算器工具
#
# 功能：安全计算数学表达式，避免 LLM 算错
# 逻辑：ast 解析仅允许数字与四则运算

import ast
import operator
import re

CALCULATOR_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算数学表达式，支持 + - * / 和括号",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，如 123*456"},
            },
            "required": ["expression"],
        },
    },
}

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


# @brief: 安全计算表达式（仅数字与四则运算）
# @param: expr: 表达式字符串
# @return: 计算结果
def _safe_eval(expr: str) -> float:
    expr = expr.strip().replace(" ", "").replace("×", "*").replace("÷", "/")
    if not re.fullmatch(r"[\d+\-*/().]+", expr):
        raise ValueError(f"不支持的表达式: {expr}")

    node = ast.parse(expr, mode="eval").body

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError(f"不支持的表达式: {expr}")

    return _eval(node)


# @brief: 运行计算器工具
# @param: expression: 数学表达式
# @return: Observation
def run(expression: str) -> dict:
    try:
        result = _safe_eval(expression)
        if result == int(result):
            result = int(result)
        return {
            "ok": True,
            "data": {"expression": expression, "result": result},
            "summary": f"{expression} = {result}",
            "sources": [],
        }
    except (ValueError, ZeroDivisionError, SyntaxError) as exc:
        return {
            "ok": False,
            "data": {"expression": expression},
            "summary": f"计算失败: {exc}",
            "sources": [],
        }


SPEC = {
    "name": "calculator",
    "description": "计算数学表达式，支持 + - * / 和括号",
    "schema": CALCULATOR_TOOL_SCHEMA,
    "run": run,
}
