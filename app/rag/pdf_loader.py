# Day09 — PDF 解析（PyMuPDF）
#
# 功能：PDF → 按页文本 → JSON
# 逻辑：
#   load_pdf_pages   — fitz 逐页 get_text()
#   save_parsed_json — 写入 data/parsed/*.json
#   parse_pdf        — 对外一行调用
#
# 详见 docs/Day09.md

import json
from pathlib import Path

import fitz

from app.core.config import PARSED_DIR
from app.core.files import ensure_dir


# @brief: 打开 PDF，逐页提取文本
# @param: pdf_path: PDF 文件路径
# @return: pages 列表 [{page, content}, ...]
def load_pdf_pages(pdf_path: str | Path) -> list[dict]:
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF 不存在: {pdf_path}")
    doc = fitz.open(pdf_path)
    pages = []
    try:
        for i in range(doc.page_count):
            text = doc[i].get_text().strip()
            pages.append({"page": i + 1, "content": text})
    finally:
        doc.close()
    return pages


# @brief: 将 pages 列表保存为 JSON 文件
# @param: pdf_path: 源 PDF 路径（用于 source 字段与输出文件名）
# @param: pages: 按页文本列表
# @param: output_dir: 输出目录，默认 PARSED_DIR
# @return: 输出 JSON 路径
def save_parsed_json(
    pdf_path: str | Path,
    pages: list[dict],
    output_dir: str | Path = PARSED_DIR,
) -> Path:
    pdf_path = Path(pdf_path)
    out_dir = ensure_dir(output_dir)
    output_path = out_dir / f"{pdf_path.stem}.json"

    payload = {
        "source": pdf_path.name,
        "total_pages": len(pages),
        "pages": pages,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return output_path


# @brief: PDF 解析门面，串联 load_pdf_pages → save_parsed_json
# @param: pdf_path: PDF 文件路径
# @param: output_dir: 输出目录，默认 PARSED_DIR
# @return: 输出 JSON 路径
def parse_pdf(
    pdf_path: str | Path,
    output_dir: str | Path = PARSED_DIR,
) -> Path:
    pages = load_pdf_pages(pdf_path)
    return save_parsed_json(pdf_path, pages, output_dir)
