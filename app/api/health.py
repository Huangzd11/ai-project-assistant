# Day04 — 健康检查接口
#
# 功能：服务探活与欢迎页
# 逻辑：
#   GET /       → 简单 JSON 欢迎信息
#   GET /health → 返回 {"status": "OK"}，供 Docker/K8s 探活

from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/")
def root():
    return {"message": "Hello AI"}


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="OK")
