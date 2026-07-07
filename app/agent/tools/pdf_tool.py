# Day16 — PDF 工具
#
# 功能：读取 uploads/ 下 PDF，返回页数与文本内容
# 逻辑：load_pdf_pages → 构造 summary，供 Planner + Executor 使用

from pathlib import Path

from app.core.config import UPLOAD_DIR
from app.rag.pdf_loader import load_pdf_pages

PDF_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "pdf_read",
        "description": "读取并解析 PDF 文件，返回页数与文本内容",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "PDF 文件名，如 linux.pdf"},
                "page": {
                    "type": "integer",
                    "description": "可选，指定读取的页码；不传则返回全部页",
                },
            },
            "required": ["filename"],
        },
    },
}


# @brief: 运行 PDF 读取工具
# @param: filename: PDF 文件名
# @param: page: 可选页码
# @return: Observation
def run(filename: str, page: int | None = None) -> dict:
    safe_name = Path(filename).name
    pdf_path = Path(UPLOAD_DIR) / safe_name
    if not pdf_path.is_file():
        return {
            "ok": False,
            "data": {},
            "summary": f"PDF 文件 {safe_name} 不存在，请先上传至 uploads/",
            "sources": [],
        }

    all_pages = load_pdf_pages(pdf_path)
    total_pages = len(all_pages)

    if page is not None:
        pages = [item for item in all_pages if item["page"] == page]
        if not pages:
            return {
                "ok": False,
                "data": {"source": safe_name, "total_pages": total_pages},
                "summary": f"{safe_name} 不存在第 {page} 页",
                "sources": [],
            }
    else:
        pages = all_pages

    data = {
        "source": safe_name,
        "total_pages": total_pages,
        "pages": pages,
    }
    if page is not None:
        preview = pages[0]["content"][:200]
        summary = f"{safe_name} 第 {page} 页（共 {total_pages} 页）：{preview}"
        sources = [{"source": safe_name, "page": page, "chunk": 0, "score": 1.0}]
    else:
        first_preview = pages[0]["content"][:120] if pages else ""
        summary = f"{safe_name} 共 {total_pages} 页。第1页预览：{first_preview}"
        sources = [{"source": safe_name, "page": 1, "chunk": 0, "score": 1.0}] if pages else []

    return {
        "ok": True,
        "data": data,
        "summary": summary,
        "sources": sources,
    }


SPEC = {
    "name": "pdf_read",
    "description": "读取并解析 PDF 文件，返回页数与文本内容",
    "schema": PDF_TOOL_SCHEMA,
    "run": run,
}
