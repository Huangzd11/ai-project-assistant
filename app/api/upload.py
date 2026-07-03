from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
def upload_pdf():
    """PDF 上传接口（Day8 后续实现）。"""
    return {"message": "upload endpoint - coming soon"}
