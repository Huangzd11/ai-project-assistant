# Day11 — Embedding（文本向量化）

> 版本：**v0.2.0-beta2** | Commit：`feat(embedding)`

## 学习目标

- [x] 理解 Chunk（文本）与 Vector（向量）的关系
- [x] 掌握 Embedding 的作用：把语义相近的文本映射到相近的向量
- [x] 实现 **本地**（BAAI/bge-small）与 **云端**（通义 Embedding API）两种方案
- [x] 将 Day10 的 `data/chunks/*.json` 转为 `data/vectors/*.json`

---

## 完成内容

### 核心模块

| 函数 | 职责 |
|------|------|
| `_get_local_model()` | 懒加载 `SentenceTransformer`，避免重复初始化 |
| `embed_text()` | 单条文本 → `list[float]`（`local` / `dashscope`） |
| `embed_chunks_list()` | 遍历 chunks，生成 `{chunk, page, embedding}` |
| `save_vectors_json()` | 写入 `data/vectors/{name}.json` |
| `embed_chunks()` | 门面：读 chunks JSON → 向量化 → 写盘 |

### 方案选型

| 方案 | 模型 | 切换方式 |
|------|------|----------|
| **本地**（默认） | `BAAI/bge-small-zh-v1.5` | `EMBEDDING_PROVIDER=local` |
| **云端** | 通义 `text-embedding-v3` | `EMBEDDING_PROVIDER=dashscope` |

### 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `VECTORS_DIR` | `data/vectors` | 向量 JSON 输出目录 |
| `EMBEDDING_PROVIDER` | `local` | `local` 或 `dashscope` |
| `EMBEDDING_MODEL` | `BAAI/bge-small-zh-v1.5` | 本地模型；云端改为 `text-embedding-v3` |
| `EMBEDDING_DIMENSION` | `512` | 云端可选维度（本地由模型决定） |

### 实测验证

```powershell
python -c "from app.rag.embedder import embed_chunks; print(embed_chunks('data/chunks/test.json'))"
# 输出：data\vectors\test.json
```

`data/vectors/test.json`（3 条向量，512 维）：

```json
{
  "source": "test.pdf",
  "provider": "local",
  "model": "BAAI/bge-small-zh-v1.5",
  "dimension": 512,
  "total_vectors": 3,
  "vectors": [
    { "chunk": 1, "page": 1, "embedding": [-0.013, 0.041, ...] },
    { "chunk": 2, "page": 2, "embedding": [...] },
    { "chunk": 3, "page": 3, "embedding": [...] }
  ]
}
```

---

## 在 Sprint 2 中的位置

```
Day08  uploads/test.pdf
Day09  data/parsed/test.json     ✅
Day10  data/chunks/test.json     ✅
Day11  data/vectors/test.json    ✅
Day12  ChromaDB 入库             ← 下一步
```

**学习链路：**

```
Chunk（文本块）→ Embedding 模型 → Vector（浮点数组）
```

---

## 处理流程

```
data/chunks/test.json
    → 读取 chunks[]
    → 对每条 content 调用 embed_text()
    → 组装 { chunk, page, embedding }
    → 写入 data/vectors/test.json
```

---

## 目录与配置

| 路径 | 说明 |
|------|------|
| `app/rag/embedder.py` | Embedding 核心逻辑 |
| `data/chunks/` | Day10 输入 |
| `data/vectors/` | Day11 输出 |

---

## 实现清单

| # | 任务 | 状态 |
|---|------|------|
| 1 | `sentence-transformers` 依赖 | ✅ |
| 2 | `data/vectors/.gitkeep` | ✅ |
| 3 | `config.py` Embedding 配置 | ✅ |
| 4 | `embed_text()` local + dashscope | ✅ |
| 5 | `embed_chunks_list` / `save_vectors_json` / `embed_chunks` | ✅ |
| 6 | Day10 → Day11 联调 | ✅ |

---

## 测试命令

```powershell
# 本地方案
pip install sentence-transformers

# 单步
python -c "from app.rag.embedder import embed_chunks; print(embed_chunks('data/chunks/test.json'))"

# 完整链路（Day09 → Day11）
python -c "from app.rag.pdf_loader import parse_pdf; from app.rag.chunker import chunk_pdf; from app.rag.embedder import embed_chunks; print(embed_chunks(chunk_pdf(parse_pdf('uploads/test.pdf'))))"
```

**云端方案：** `.env` 中设置 `EMBEDDING_PROVIDER=dashscope`、`EMBEDDING_MODEL=text-embedding-v3` 及百炼 API Key。

---

## 每日收尾

- [x] 更新 README、CODEMAP、roadmap、solution-design、api.md
- [x] `.gitignore` 忽略 `data/vectors/*.json`
- [ ] Git Commit：`feat(embedding): vectorize chunks with bge-small or DashScope`
- [ ] Tag：`v0.2.0-beta2`

---

## 收获

- Embedding 把「语义」变成可计算的「距离」，是向量检索的基础
- 本地 `bge-small` 与云端通义 API 可通过 `EMBEDDING_PROVIDER` 切换，业务代码不变
- 向量 JSON 是 Day12 ChromaDB 入库的直接输入

---

## 下一步

Day12 — ChromaDB（`feat(vector-db)`，v0.2.0-rc）
