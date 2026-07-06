# Day04 — 健康检查接口
# Day14 — Swagger 描述完善
#
# 功能：服务探活与欢迎页
# 逻辑：
#   GET /       → 简单 JSON 欢迎信息
#   GET /health → 返回 {"status": "OK"}，供 Docker/K8s 探活

from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter(tags=["health"])


# @brief: 服务欢迎页
# @return: {"message": "Hello AI"}
@router.get("/", summary="服务欢迎页", include_in_schema=False)
def root():
    return {"message": "Hello AI"}


# @brief: 健康检查探活
# @return: HealthResponse
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    response_description="服务正常时返回 status=OK，供 Docker/K8s 探活",
)
def health():
    return HealthResponse(status="OK")
