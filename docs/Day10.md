# Day10 — Chunk 切分（LangChain Text Splitter）

> 版本：**v0.2.0-beta** | Commit：`feat(chunker)`

## 学习目标

- [x] 理解为什么 RAG 需要把「页」再切成「块（Chunk）」
- [x] 使用 **LangChain Text Splitter**，不手写切分逻辑
- [x] 掌握 `chunk_size` 与 `chunk_overlap` 的含义与取舍
- [x] 将 Day09 的 `data/parsed/*.json` 转为带 `chunk_id` 的块列表

---

## 完成内容

### 核心模块

| 函数 | 职责 |
|------|------|
| `split_page_text()` | 单页文本 → `RecursiveCharacterTextSplitter` 切块 |
| `chunk_document()` | 遍历 pages，分配全局 `chunk_id` |
| `save_chunks_json()` | 写入 `data/chunks/{name}.json` |
| `chunk_pdf()` | 门面函数：读 parsed → 切分 → 写盘 |

### 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CHUNK_SIZE` | `500` | 每块目标最大字符数 |
| `CHUNK_OVERLAP` | `50` | 相邻块重叠字符数，避免切分点断句 |

### 实测验证

```powershell
python -c "from app.rag.chunker import chunk_pdf; print(chunk_pdf('data/parsed/test.json'))"
# 输出：data\chunks\test.json
```

`data/chunks/test.json`（3 块，空页 page 4 已跳过）：

```json
{
  "source": "test.pdf",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "total_chunks": 3,
  "chunks": [
    { "chunk_id": 1, "page": 1, "content": "..." },
    { "chunk_id": 2, "page": 2, "content": "..." },
    { "chunk_id": 3, "page": 3, "content": "..." }
  ]
}
```

---

## 在 Sprint 2 中的位置

```
Day08  uploads/test.pdf
Day09  data/parsed/test.json     ✅
Day10  data/chunks/test.json     ✅
Day11  Embedding                 ← 下一步
```

---

## 处理流程

```
data/parsed/test.json → 每页 content → LangChain Splitter → data/chunks/test.json
```

---

## 目录与配置

| 路径 | 说明 |
|------|------|
| `app/rag/chunker.py` | 切分核心逻辑 |
| `data/parsed/` | Day09 输入 |
| `data/chunks/` | Day10 输出 |
| `CHUNKS_DIR` | 默认 `data/chunks` |

---

## 实现清单

| # | 任务 | 状态 |
|---|------|------|
| 1 | `langchain-text-splitters` | ✅ |
| 2 | `data/chunks/.gitkeep` | ✅ |
| 3 | `CHUNK_SIZE` / `CHUNK_OVERLAP` / `CHUNKS_DIR` | ✅ |
| 4 | `split_page_text` | ✅ |
| 5 | `chunk_document` | ✅ |
| 6 | `chunk_pdf` | ✅ |
| 7 | Day09 → Day10 联调 | ✅ |

---

## 测试命令

```powershell
# 前置：Day09 已产出 data/parsed/test.json
python -c "from app.rag.chunker import chunk_pdf; print(chunk_pdf('data/parsed/test.json'))"
```

---

## 每日收尾

- [x] 更新 README、CODEMAP、roadmap、solution-design、api.md
- [x] `.gitignore` 忽略 `data/chunks/*.json`
- [ ] Git Commit：`feat(chunker): split pages with LangChain Text Splitter`
- [ ] Tag：`v0.2.0-beta`

---

## 收获

- Page 是 PDF 边界，Chunk 是 RAG 检索边界
- `chunk_overlap` 在切分点保留上下文，提升检索完整性
- LangChain `RecursiveCharacterTextSplitter` 避免手写切分踩坑

---

## 下一步

Day11 — Embedding（`feat(embedding)`，v0.2.0-beta2）
