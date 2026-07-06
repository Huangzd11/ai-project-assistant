# Day04 — FastAPI 应用入口
# Day08 — 重构：路由拆分到 app/api/，注册 upload 路由
#
# 功能：创建 FastAPI 实例，挂载各 API 路由模块
# 逻辑：main.py 只做组装，不包含业务逻辑
# 启动：python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

from fastapi import FastAPI

from app.api import chat, health, rag, upload

app = FastAPI(title="AI Project Assistant", version="0.2.0")

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(rag.router)
