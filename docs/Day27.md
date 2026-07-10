# Day27 — GitHub 包装（设计与实现）

> 版本：**v0.4.0** | 前置：**Day26 架构/方案文档**  
> **定位：作品集门面 — 让仓库第一眼像可交付产品，而不是作业文件夹**

## 目标

GitHub 访客 30 秒内应能回答：

1. 这是什么产品？  
2. 怎么跑起来？  
3. 架构长什么样？  
4. 做到哪一版了？  

## 交付清单

| 项 | 动作 | 状态 |
|----|------|------|
| README | 产品化重写：介绍 / 架构图 / Quick Start / 结构 / 功能 / Roadmap | ✅ |
| 架构图 | README 内嵌主链路 ASCII（权威图仍在 architecture.md） | ✅ |
| Roadmap | README 摘要表 + 链到 docs/roadmap.md；Day27 标完成 | ✅ |
| API 文档 | 升级 docs/api.md 至 v0.4（stream / usage / metrics） | ✅ |
| 版本记录 | CHANGELOG 增加 v0.4.0；APP_VERSION=0.4.0 | ✅ |
| LICENSE | 增加 MIT | ✅ |
| 徽章 | README 顶部 version / python / FastAPI | ✅ |

## README 必备章节（已实现）

1. 项目介绍  
2. 功能亮点  
3. 架构图  
4. 快速开始（Compose + 本地）  
5. 项目结构  
6. 功能展示（响应示例 / 成本估算）  
7. API 文档入口  
8. Roadmap  
9. 版本记录  

## 边界

| 做 | 不做 |
|----|------|
| 门面文档与版本对齐 | 真实产品截图拍摄（可后续补 `docs/images/`） |
| 精简 README，Day 日记留在 docs/ | 重写全部 Day01~26 |
| MIT License | 正式 GitHub Release 打 tag（可选；工程已定版 v1.0.0） |

## 验收

- [x] README 含介绍、架构、Quick Start、结构、功能、Roadmap  
- [x] api.md / CHANGELOG 反映 v0.4  
- [x] roadmap Day27 完成  
- [x] 仓库根目录有 LICENSE  

## 小结

Day27 把 Sprint 4 的工程成果收成 **GitHub 作品集首页**。面试官或招聘方可从 README 直接进入架构、API 与成本故事，无需翻阅几十篇 Day 日志。
