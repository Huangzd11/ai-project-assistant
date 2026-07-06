# Day13 — RAG Pipeline（检索增强生成）

> 版本：**v0.2.0** | Commit：`feat(rag)`

## 学习目标

- [x] 理解 RAG 完整链路：检索 + 生成
- [x] 将 Day12 `search()` 结果注入 Prompt，调用 Day04 `llm.chat()`
- [x] 实现带 **来源溯源** 的回答格式（文档名 + 页码）
- [x] 完成 Sprint 2 企业知识库问答最小可用版本

---

## 完成内容

### 核心模块

| 函数 | 职责 |
|------|------|
| `format_context()` | 检索结果 → Prompt 参考资料 |
| `build_rag_prompt()` | 拼接 user prompt |
| `extract_sources()` | 按 source+page 去重来源 |
| `rag_answer()` | 门面：search → prompt → llm → 返回 |

### HTTP 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /rag` | 知识库问答 | 返回答案 + sources |

### 实测验证

```powershell
# 前置：index_chunks 已入库
python -c "from app.rag.rag_pipeline import rag_answer; import json; print(json.dumps(rag_answer('telnet'), ensure_ascii=False, indent=2))"
```

```json
{
  "question": "telnet",
  "answer": "根据《test.pdf》第1页：ASR1803开启telnetd的步骤包括……",
  "sources": [
    { "source": "test.pdf", "page": 2, "chunk": 2, "score": 0.6835 },
    { "source": "test.pdf", "page": 1, "chunk": 1, "score": 0.62 }
  ]
}
```

---

## 完整 RAG 链路

```
Question → Embedding → Search → Chunk → Prompt → LLM → Answer + sources
```

---

## 实现清单

| # | 任务 | 状态 |
|---|------|------|
| 1 | `RAG_SYSTEM_PROMPT` 配置 | ✅ |
| 2 | `llm.chat(system_prompt=...)` | ✅ |
| 3 | `rag_pipeline.py` | ✅ |
| 4 | `POST /rag` + Pydantic 模型 | ✅ |
| 5 | 联调问答 | ✅ |

---

## 测试命令

```powershell
# 模块调用
python -c "from app.rag.rag_pipeline import rag_answer; import json; print(json.dumps(rag_answer('如何开启 telnet'), ensure_ascii=False, indent=2))"

# HTTP
python -m uvicorn app.main:app --reload
# POST http://127.0.0.1:8000/rag  Body: {"question":"如何开启 telnet？"}
```

---

## 每日收尾

- [x] 更新 README、CODEMAP、roadmap、solution-design、api.md
- [ ] Git Commit：`feat(rag): complete RAG pipeline with cited answers`
- [ ] Tag：`v0.2.0`

---

## 收获

- RAG = Retrieval + Augmented + Generation，检索与生成解耦便于调试
- System Prompt 约束「仅根据参考资料」可降低幻觉
- `sources` 数组支持前端单独展示引用来源

---

## 下一步

Day14 — Test & Release（`release(v0.2.0)`）
