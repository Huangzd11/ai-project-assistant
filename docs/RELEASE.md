# Release v1.0.0

> 30 天 AI 技术项目经理实战 · 工程与文档收官  
> Day28~30（简历 / 模拟面试 / 投递）**暂不设计**，不影响本版本交付。

## 版本

- **Tag 建议：** `v1.0.0`
- **APP_VERSION：** `1.0.0`（`GET /health`）

## 最终成果

### 技术能力

LLM · Prompt · FastAPI · Docker · RAG · Embedding · Vector DB · Agent · MCP

### 项目能力

方案设计 · 技术选型 · 成本评估 · 风险分析 · 项目交付

### 输出成果

| 产出 | 位置 |
|------|------|
| GitHub 项目 | 本仓库 + [LICENSE](../LICENSE) |
| 架构图 | [architecture.md](architecture.md) |
| README | [../README.md](../README.md) |
| 方案设计 | [solution-design.md](solution-design.md) |
| API / 变更 | [api.md](api.md) · [CHANGELOG.md](CHANGELOG.md) |

## 快速验证

```powershell
docker compose up -d --build
Invoke-RestMethod http://localhost/health
# version == 1.0.0
```

## 相关

- [CHANGELOG.md](CHANGELOG.md)
- [roadmap.md](roadmap.md)
