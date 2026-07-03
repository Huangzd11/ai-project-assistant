from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/")
def root():
    return {"message": "Hello AI"}


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="OK")
