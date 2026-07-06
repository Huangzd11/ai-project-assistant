# Day09 — PDF 解析（PyMuPDF）
#
# 功能：PDF → 按页文本 → JSON
# 逻辑：
#   load_pdf_pages   — fitz 逐页 get_text()
#   save_parsed_json — 写入 data/parsed/*.json
#   parse_pdf        — 对外一行调用

import json
from pathlib import Path

import fitz

from app.core.config import PARSED_DIR
from app.core.files import ensure_dir


def load_pdf_pages(pdf_path: str | Path) -> list[dict]:
    """步骤 A：打开 PDF，逐页提取文本，返回 pages 列表。"""
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF 不存在: {pdf_path}")

    doc = fitz.open(pdf_path)
    pages = []
    try:
        for i in range(doc.page_count):
            text = doc[i].get_text().strip()
            pages.append({"page": i + 1, "content": text})  # page 从 1 开始
    finally:
        doc.close()

    return pages


def save_parsed_json(
    pdf_path: str | Path,
    pages: list[dict],
    output_dir: str | Path = PARSED_DIR,
) -> Path:
    """步骤 B：将 pages 列表保存为 JSON 文件。"""
    pdf_path = Path(pdf_path)
    out_dir = ensure_dir(output_dir)
    json_name = pdf_path.stem + ".json"
    output_path = out_dir / json_name

    payload = {
        "source": pdf_path.name,
        "total_pages": len(pages),
        "pages": pages,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return output_path


def parse_pdf(
    pdf_path: str | Path,
    output_dir: str | Path = PARSED_DIR,
) -> Path:
    """步骤 C：对外一行调用，串联 A → B。"""
    pages = load_pdf_pages(pdf_path)
    return save_parsed_json(pdf_path, pages, output_dir)
