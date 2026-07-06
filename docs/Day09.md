# Day09 — PDF 解析（PyMuPDF）

> 版本：**v0.2.0-alpha2** | Commit：`feat(pdf-loader)`

## 学习目标

- [x] 理解 RAG 流水线中「文档解析」环节的作用
- [x] 使用 PyMuPDF 按页提取 PDF 纯文本
- [x] 将解析结果保存为 JSON，供 Day10 Chunk 使用
- [x] 在 `app/rag/` 下实现可复用的 `pdf_loader` 模块

---

## 完成内容

### 核心模块

| 函数 | 职责 |
|------|------|
| `load_pdf_pages()` | fitz 打开 PDF，逐页 `get_text()` |
| `save_parsed_json()` | 写入 `data/parsed/{name}.json` |
| `parse_pdf()` | 门面函数，串联 A → B |

### 实测验证

```powershell
python -c "from app.rag.pdf_loader import parse_pdf; print(parse_pdf('uploads/test.pdf'))"
# 输出：data\parsed\test.json
```

`data/parsed/test.json` 示例（4 页，中文正常，空页保留）：

```json
{
  "source": "test.pdf",
  "total_pages": 4,
  "pages": [
    { "page": 1, "content": "【知识文档】..." },
    { "page": 4, "content": "" }
  ]
}
```

---

## 在 Sprint 2 中的位置

```
Day08  POST /upload        uploads/test.pdf
Day09  PDF Loader    →     data/parsed/test.json   ✅
Day10  Chunker       →     文本切分（下一步）
```

---

## 技术选型：PyMuPDF

选用 PyMuPDF（`import fitz`），按页 `get_text()` 速度快，满足 RAG 纯文本提取需求。

---

## 处理流程

```
uploads/xxx.pdf → fitz.open → 每页 get_text() → data/parsed/xxx.json
```

---

## 目录与配置

| 路径 | 说明 |
|------|------|
| `app/rag/pdf_loader.py` | 解析核心逻辑 |
| `uploads/` | 原始 PDF（Day08） |
| `data/parsed/` | 解析 JSON（Day09） |
| `PARSED_DIR` | 环境变量，默认 `data/parsed` |

---

## 实现清单

| # | 任务 | 状态 |
|---|------|------|
| 1 | `requirements.txt` 添加 pymupdf | ✅ |
| 2 | `data/parsed/.gitkeep` | ✅ |
| 3 | `load_pdf_pages` | ✅ |
| 4 | `save_parsed_json` | ✅ |
| 5 | `parse_pdf` | ✅ |
| 6 | `PARSED_DIR` 配置 | ✅ |
| 7 | Day08 → Day09 联调 | ✅ |

---

## 测试命令

```powershell
# 1. 上传或复制 PDF 到 uploads/
# 2. 解析
python -c "from app.rag.pdf_loader import parse_pdf; print(parse_pdf('uploads/test.pdf'))"
# 3. 查看 data/parsed/test.json
```

---

## 每日收尾

- [x] 更新 README、CODEMAP、roadmap、solution-design
- [x] `.gitignore` 忽略 `data/parsed/*.json`
- [ ] Git Commit：`feat(pdf-loader): extract per-page text with PyMuPDF`
- [ ] Tag：`v0.2.0-alpha2`

---

## 收获

- 掌握 PyMuPDF 按页提取：`fitz.open` → `page.get_text()` → `doc.close()`
- 理解 RAG 摄入链路：原始 PDF 与结构化 JSON 分目录存放
- 页码从 1 开始、空页保留，为 Day10 Chunk 溯源打基础

---

## 下一步

Day10 — Chunk 切分（`feat(chunker)`，v0.2.0-beta）
