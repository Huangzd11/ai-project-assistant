# Day06 — GitHub 与项目规范

## 学习目标

- [x] 创建 GitHub 仓库
- [x] 本地 Git 初始化
- [x] 提交代码到 GitHub
- [x] 编写专业 README
- [x] 建立 AI 项目开发规范

## 完成内容

### 1. 创建 GitHub 仓库

- 仓库地址：[https://github.com/Huangzd11/ai-project-assistant](https://github.com/Huangzd11/ai-project-assistant)
- 项目由 `ai-tech-pm-30days` 重命名为 `ai-project-assistant`，与 monorepo 结构对齐

### 2. 本地 Git 与远程配置

```powershell
git remote set-url origin https://github.com/Huangzd11/ai-project-assistant.git
git add .
git commit -m "refactor: restructure project as monorepo layout"
git push -u origin main
```

### 3. 专业 README

完善后的 README 包含：

| 章节 | 说明 |
|------|------|
| 项目简介 | 目标、适用人群、已完成阶段 |
| 技术栈 | 各层技术选型一览 |
| 当前功能 | Day02 ~ Day05 能力说明 |
| 学习进度 | 与 roadmap 同步的打勾清单 |
| 项目结构 | 目录树 + 核心文件职责 |
| 快速开始 | 安装、对话、API、Docker |
| 环境变量 | 配置项说明 |
| 文档索引 | 指向 docs 各文档 |

### 4. AI 项目开发规范

详见 [development-standards.md](development-standards.md)，涵盖：

- 目录与代码分层规范
- Git 提交与分支约定
- 环境变量与密钥管理
- 文档编写要求

### 5. 同步完善的文档

| 文档 | 说明 |
|------|------|
| [roadmap.md](roadmap.md) | 学习路线打勾进度 |
| [solution-design.md](solution-design.md) | AI 方案设计雏形 |
| [architecture.png](architecture.png) | 请求链路结构图 |

## 收获

- 掌握 AI 项目从本地开发到 GitHub 托管的完整流程
- 理解 monorepo 结构对学习与迭代的便利性
- 建立文档驱动开发习惯：代码 + 工作日志 + 方案设计同步演进

## 下一步

Day08 RAG — 文档切片、向量检索、知识库问答。
