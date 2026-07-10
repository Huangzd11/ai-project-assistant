# Day02 思维导图 — OpenAI 兼容 API 与多轮对话

> Sprint：Sprint 1 · 基础链路  ·  对应文档：[docs/Day02.md](../docs/Day02.md)

## 导图（Mermaid）

在支持 Mermaid 的编辑器（VS Code / GitHub / Typora）中可直接预览。

```mermaid
mindmap
  root((Day02 OpenAI 兼容 API 与多轮对话))
    术语定义与作用
      messages
        定义: [{role, content}, ...] 对话历史列表
        作用: 多轮对话的核心数据结构
      OpenAI 兼容 API
        定义: 统一 chat.completions 接口形态
        作用: 一套代码可切云端/本地
      stream
        定义: 流式逐 Token/字返回
        作用: 降低首字延迟，改善体验
      .env
        定义: 本地环境变量文件
        作用: 存放 Key，避免硬编码密钥
    学习目标
      从 .env 读 Key/BaseURL/模型名
      维护 messages 实现多轮对话
      使用 stream=True 流式输出
    重点
      messages 状态机
      环境变量配置
      流式输出体验
    要点
      每轮把 assistant 回复 append 回 messages
      Key 只放 .env
      stream 与非 stream 同一套 messages
    难点
      流式拼接与异常中断处理
      上下文过长时的截断策略（后续再做）
    使用的技术与选型理由
      openai Python SDK
        为什么: 官方兼容客户端，切换 BaseURL 即可
      python-dotenv
        为什么: 安全加载密钥，符合工程习惯
    总结收获
      掌握「配置 + messages + 流式」最小闭环
      一句话: 把 Day01 概念落到可运行的多轮 CLI：配置、历史、流式三件套。
```

## 结构化速览

### 术语

| 术语 | 定义/解析 | 作用 |
|------|-----------|------|
| messages | [{role, content}, ...] 对话历史列表 | 多轮对话的核心数据结构 |
| OpenAI 兼容 API | 统一 chat.completions 接口形态 | 一套代码可切云端/本地 |
| stream | 流式逐 Token/字返回 | 降低首字延迟，改善体验 |
| .env | 本地环境变量文件 | 存放 Key，避免硬编码密钥 |

### 学习目标

- 从 .env 读 Key/BaseURL/模型名
- 维护 messages 实现多轮对话
- 使用 stream=True 流式输出

### 重点

- messages 状态机
- 环境变量配置
- 流式输出体验

### 要点

- 每轮把 assistant 回复 append 回 messages
- Key 只放 .env
- stream 与非 stream 同一套 messages

### 难点

- 流式拼接与异常中断处理
- 上下文过长时的截断策略（后续再做）

### 技术与为什么用

- **openai Python SDK**：官方兼容客户端，切换 BaseURL 即可
- **python-dotenv**：安全加载密钥，符合工程习惯

### 总结收获

- 掌握「配置 + messages + 流式」最小闭环

**一句话：** 把 Day01 概念落到可运行的多轮 CLI：配置、历史、流式三件套。
