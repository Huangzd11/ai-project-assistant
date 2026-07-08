# Day16 — Agent 工具包入口（启动时注册全部工具）
#
# 功能：导入时 bootstrap 注册表，供 Executor 通过 registry.run 调用
# 逻辑：register(rag / pdf / calculator / weather / news)

from app.agent.tools.calculator import SPEC as CALC_SPEC
from app.agent.tools.news_tool import SPEC as NEWS_SPEC
from app.agent.tools.pdf_tool import SPEC as PDF_SPEC
from app.agent.tools.rag_tool import SPEC as RAG_SPEC
from app.agent.tools.registry import get_schemas, list_names, register, run
from app.agent.tools.sports_tool import SPEC as SPORTS_SPEC
from app.agent.tools.weather_tool import SPEC as WEATHER_SPEC

register(RAG_SPEC)
register(PDF_SPEC)
register(CALC_SPEC)
register(WEATHER_SPEC)
register(NEWS_SPEC)
register(SPORTS_SPEC)

__all__ = ["register", "run", "list_names", "get_schemas"]
