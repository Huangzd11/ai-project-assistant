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

# 步骤 A：打开 PDF，逐页提取文本，返回 pages 列表。
def load_pdf_pages(pdf_path: str | Path) -> list[dict]:
    pdf_path = Path(pdf_path)   # 将 pdf_path 转换为 Path 对象
    if not pdf_path.is_file():   # 判断 pdf_path 是否为文件 
        raise FileNotFoundError(f"PDF 不存在: {pdf_path}")
    doc = fitz.open(pdf_path)   # 打开 PDF 文件
    pages = []   # 初始化 pages 列表
    try:
        for i in range(doc.page_count):   # 遍历每一页
            text = doc[i].get_text().strip()   # 获取页面文本
            pages.append({"page": i + 1, "content": text})  # page 从 1 开始
    finally:
        doc.close()   # 关闭 PDF 文件
    return pages   # 返回 pages 列表

# 步骤 B：将 pages 列表保存为 JSON 文件。
def save_parsed_json(
    pdf_path: str | Path,
    pages: list[dict],
    output_dir: str | Path = PARSED_DIR,
) -> Path:
    pdf_path = Path(pdf_path)   # 将 pdf_path 转换为 Path 对象
    out_dir = ensure_dir(output_dir)   # 确保输出目录存在：复用 Day08 app/core/files.py
    json_name = pdf_path.stem + ".json"   # pdf_path.stem：只要文件名不带扩展名，.json：输出文件名
    output_path = out_dir / json_name

    payload = {   # 构建 JSON 数据
        "source": pdf_path.name,
        "total_pages": len(pages),
        "pages": pages,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2) # ensure_ascii=False：中文不要变成 \u4e2d
    return output_path

# 步骤 C：对外一行调用，串联 A → B。
def parse_pdf(
    pdf_path: str | Path,
    output_dir: str | Path = PARSED_DIR,
) -> Path:
    pages = load_pdf_pages(pdf_path)
    return save_parsed_json(pdf_path, pages, output_dir)
