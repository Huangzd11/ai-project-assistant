# Day12 — Vector Database（Chroma 向量检索）

> 版本：**v0.2.0-rc** | Commit：`feat(vector-db)`  
> **范围：纯检索，不接 LLM**

## 学习目标

- [x] 理解向量数据库在 RAG 中的角色：持久化 + 相似度检索
- [x] 掌握 Chroma 的 **Collection / Insert / Query** 核心 API
- [x] 实现「问题 → Embedding → Search → Top5」最小检索链路
- [x] 明确 Day12 与 Day13 的边界：今天只返回检索结果，不生成回答

---

## 完成内容

### 核心模块


| 函数                           | 职责                                  |
| ---------------------------- | ----------------------------------- |
| `get_chroma_client()`        | `PersistentClient` → `data/chroma/` |
| `get_or_create_collection()` | 获取/创建 Collection（cosine）            |
| `build_records()`            | 合并 chunks + vectors → Chroma 记录     |
| `insert_documents()`         | 按 source 去重后 `collection.add`       |
| `search()`                   | `embed_text` → `query` → Top-K 结果   |
| `index_chunks()`             | 入库门面                                |




### 关键参数


| 参数                  | 默认值           | 说明            |
| ------------------- | ------------- | ------------- |
| `CHROMA_DIR`        | `data/chroma` | Chroma 持久化目录  |
| `CHROMA_COLLECTION` | `knowledge`   | Collection 名称 |
| `SEARCH_TOP_K`      | `5`           | 默认返回条数        |




### 实测验证

```powershell
python -c "from app.rag.vector_store import index_chunks; print(index_chunks('data/chunks/test.json'))"
# 输出：3

python -c "from app.rag.vector_store import search; r=search('telnet'); print(r['results'][0]['chunk'], r['results'][0]['score'])"
# 输出：2 0.6835（Top1 命中 telnet 相关 chunk）
```

检索结果示例：

```json
{
  "query": "telnet",
  "top_k": 5,
  "results": [
    {
      "rank": 1,
      "score": 0.6835,
      "chunk": 2,
      "page": 2,
      "source": "test.pdf",
      "content": "工具选择telnet终端：..."
    }
  ]
}
```

---



## 在 Sprint 2 中的位置

```
Day08  uploads/test.pdf
Day09  data/parsed/test.json
Day10  data/chunks/test.json
Day11  data/vectors/test.json
Day12  data/chroma/              ✅
Day13  Retrieve → LLM Answer     ← 下一步
```

**今日链路（无 LLM）：**

```
Question → embed_text() → Chroma.query(top_k=5) → Top5
```

---



## 实现清单


| #   | 任务                                    | 状态  |
| --- | ------------------------------------- | --- |
| 1   | `chromadb` 依赖                         | ✅   |
| 2   | `data/chroma/.gitkeep` + `.gitignore` | ✅   |
| 3   | `config.py` Chroma 配置                 | ✅   |
| 4   | `vector_store.py` 入库 + 检索             | ✅   |
| 5   | Day11 → Day12 联调                      | ✅   |


---



## 测试命令

```powershell
pip install chromadb

# 入库（前置：chunks + vectors 已存在）
python -c "from app.rag.vector_store import index_chunks; print(index_chunks('data/chunks/test.json'))"

# 纯检索
python -c "from app.rag.vector_store import search; import json; r=search('如何开启 telnet'); open('search_result.json','w',encoding='utf-8').write(json.dumps(r,ensure_ascii=False,indent=2))"
```

---



## 每日收尾

- [x] 更新 README、CODEMAP、roadmap、solution-design、api.md
- [x] `.gitignore` 忽略 `data/chroma/*`
- [x] Git Commit：`feat(vector-db): Chroma insert and top-k search without LLM`
- [x] Tag：`v0.2.0-rc`

---



## 收获

- 向量数据库解决「存」和「找」，不负责「答」
- Chroma 将 embedding + 原文 + metadata 绑定，检索即可溯源
- Top-K 检索是 RAG 核心；Day13 只需在前面加 LLM 生成层

---



## 下一步

Day13 — RAG Pipeline（`feat(rag)`，v0.2.0）：`search()` → Prompt → `llm.chat()` → 最终回答