# Day31 — Transformer（LLM 基础补强）

> **Sprint 5 · Day31~37** | 前置：**Day01 LLM/Prompt**、**Day11 Embedding**  
> **定位：第二个月最重要的一周 — 补 LLM 原理，目标「能和算法工程师正常沟通」**  
> **方式：理解 + 用自己的话讲清楚，不写代码、不推公式**

## 学习目标

- [ ] 掌握 Transformer 主链路：**Token → Embedding → Self-Attention → FFN → Next Token Prediction**
- [ ] 理解 **为什么 Transformer 替代 RNN**
- [ ] 理解 **为什么 Attention 可以并行**
- [ ] 理解 **Encoder 与 Decoder 的区别**
- [ ] **输出：** 用自己的话解释 Transformer 工作流程（见文末「验收输出」）

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| 直觉理解 + 口述/笔记 | 手写 Attention 矩阵公式推导 |
| 对照 GPT / BERT 等常见架构 | 从零实现 Transformer |
| 与 Day01 Token、Day11 Embedding 串联 | 微调 / 训练代码 |
| 写清 Encoder vs Decoder | CUDA / 分布式训练细节 |

**Day31 核心成果：** 别人问「LLM 怎么生成下一个字」，你能按链路讲清楚，并说出和 RNN 的关键差异。

---

## Sprint 5 在第二个月的位置

```
第二个月 Day31~60
├── Sprint 5（Day31~37）LLM 基础补强     ← 今天 · 最重要的一周
├── Sprint 6（Day39~45）生产级 AI 架构
├── Sprint 7（Day46~52）AI Solution 设计
└── Sprint 8（Day53~60）面试与商业化表达
```

| 维度 | 说明 |
|------|------|
| **本周目标** | 能和算法工程师正常沟通 — 听得懂术语、问得清问题、讲得清取舍 |
| **Day31 角色** | 整栋楼的「地基」：后面 RAG 选型、幻觉、Agent 都建立在「模型怎么工作」之上 |

---

## 一、必须掌握的主链路

```
文本输入
   ↓
 Token          把句子切成模型能处理的离散单元
   ↓
 Embedding      每个 Token 变成向量（带位置信息）
   ↓
 Self-Attention 每个 Token「看」序列里其它 Token，算该关注谁
   ↓
 FFN            对每个位置做非线性变换，提炼特征
   ↓
（重复 N 层：Attention + FFN）
   ↓
 Next Token Prediction   根据当前上下文，预测下一个 Token 的概率分布
   ↓
 采样 / 贪心 → 输出下一个字 → 拼回上下文 → 再预测 …（自回归）
```

### 各步在干什么（一句话）

| 步骤 | 是什么 | 作用 |
|------|--------|------|
| **Token** | 文本 → ID 序列 | 模型只认识数字，不认识「字」本身 |
| **Embedding** | ID → 稠密向量 | 把离散符号变成可计算、可学习的语义空间 |
| **Self-Attention** | 序列内部互相关注 | 让「它」根据上下文理解「它」在当前句中的含义 |
| **FFN** | 前馈神经网络 | 在注意力之后做更复杂的特征组合 |
| **Next Token Prediction** | 输出层 + Softmax | 在词表上给出「下一个 Token 是谁」的概率 |

### 与第一个月项目的对照

| Transformer 概念 | 你已在项目里接触过 |
|--------------------|-------------------|
| Token | Day01 · Day02 · API 的 `usage.prompt_tokens` |
| Embedding | Day11 文本向量化 · Day12 Chroma 检索 |
| Self-Attention | 今天学原理；应用层不直接调 |
| Next Token Prediction | Day02 流式输出 · Day21_2 SSE 逐字返回 |

> **关键区分：** Day11 的 Embedding 是**检索用**的句向量；Transformer 内部的 Embedding 是**模型输入层**，维度与词表绑定，用途不同，名字相同容易混。

---

## 二、Self-Attention 直觉（不推公式）

**问题：** 一句话里，「它」指什么？要靠前后文。

**Self-Attention 做的事：**

```
对于序列中的每一个位置：
  1. 生成 Query（我在找什么）
  2. 生成 Key（我有什么信息）
  3. 生成 Value（我的内容是什么）
  4. 用 Query 和所有 Key 算相似度 → 权重
  5. 用权重对 Value 加权求和 → 得到「看过全局上下文」的新表示
```

**直觉图：**

```
句子:  [我] [喜欢] [吃] [苹果]
                ↑
         「苹果」这个位置会：
         - 高权重关注「吃」（动词搭配）
         - 低权重关注「我」（距离远但仍有语法关系）
```

**Multi-Head Attention：** 多套 Q/K/V 并行，相当于「从不同角度」看同一句话（语法、指代、搭配等），最后拼起来。

---

## 三、为什么 Transformer 替代 RNN

| 维度 | RNN / LSTM | Transformer |
|------|------------|-------------|
| **信息传递** | 按时间步串行，隐状态一步步传 | 任意两 Token 可直接 Attention 相连 |
| **长距离依赖** | 路径长，容易梯度消失/遗忘 | 一步 Attention 可达任意距离 |
| **训练并行** | 时间维串行，GPU 吃不满 | 序列长度维可大规模并行 |
| **扩展性** | 堆层数、加参数收益有限 | 堆层数 + 大数据预训练效果显著（GPT 路线） |

**一句话：** RNN 像「传话游戏」，越远越容易失真；Transformer 像「圆桌会议」，每个词可以直接问其它所有词。

**为什么 LLM 时代选 Transformer：**

1. **算力友好** — 并行训练大模型才可行  
2. **效果友好** — 长上下文、大规模预训练表现更好  
3. **工程友好** — 架构统一（Decoder-only / Encoder-only），生态成熟  

---

## 四、为什么 Attention 可以并行

**RNN 不能并行的原因：**  
时刻 `t` 依赖 `t-1` 的隐状态，必须按顺序算。

**Self-Attention 可以并行的原因：**

```
输入: 整句 Token 序列 [x1, x2, x3, ..., xn] 一次性进模型

Attention 计算本质是矩阵运算：
  Q = X · Wq
  K = X · Wk
  V = X · Wv
  Attention = softmax(QK^T / √d) · V

→ 所有位置同时算，GPU 最擅长这种大批量矩阵乘
```

**注意：**

| 阶段 | 是否并行 |
|------|----------|
| **训练** | 整段序列并行（配合 Mask 防止偷看未来） |
| **推理（生成）** | 仍要逐个 Token 自回归生成；但**每步内**对已生成长度做 Attention 可并行算 |

这就是为什么「训练快、推理贵」—— 生成时要反复跑前向，且上下文越来越长。

---

## 五、Encoder 与 Decoder 的区别

原始论文 **「Attention Is All You Need」** 是 **Encoder-Decoder** 架构（机器翻译）。

```
Encoder                          Decoder
────────                         ────────
读整句源语言                      读已生成的目标语言 + Encoder 输出
双向 Self-Attention              带 Mask 的单向 Self-Attention
（每个词能看左右）                （只能看左边，不能偷看未来）
        │                                │
        └──────── Cross-Attention ───────┘
                 （Decoder 问 Encoder：源句里哪部分有用？）
```

| 组件 | 输入 | Attention 特点 | 典型用途 |
|------|------|------------------|----------|
| **Encoder** | 完整输入序列 | 双向：左右文都看 | 理解、分类、抽取（BERT） |
| **Decoder** | 已生成部分 + 条件 | 单向：只看过去 | 文本生成（GPT） |
| **Encoder-Decoder** | 源 + 目标 | Encoder 双向 + Decoder 单向 + Cross-Attn | 翻译、摘要（T5、BART） |

### 和常见大模型的对应

| 模型类型 | 结构 | 你调 API 时 |
|----------|------|-------------|
| **GPT 系列** | Decoder-only | `chat.completions` 自回归生成 |
| **BERT 类** | Encoder-only | 嵌入/分类（非生成） |
| **T5 / BART** | Encoder-Decoder | 翻译、摘要等 |

**本项目（通义 / Ollama chat）：** 本质是 **Decoder-only 大模型** — 给 messages，模型按 Next Token Prediction 一个字一个字往下生成。

---

## 六、完整工作流程（分层理解）

### 训练阶段（简化）

```
1. 准备大量文本
2. Tokenize → Token 序列
3. Embedding + 位置编码
4. 堆叠 N × (Self-Attention + FFN)
5. 输出层：预测每个位置的「下一个 Token」
6. 与真实下一个 Token 算损失，反向传播更新权重
```

### 推理阶段（你每天在用的）

```
1. 用户 Prompt → Tokenize
2. 模型前向 → 得到词表概率分布
3. 选一个 Token（贪心 / 采样 + Temperature）
4. 把新 Token 拼到上下文末尾
5. 重复 2~4，直到 EOS 或达到 max_tokens
```

**这就是 Day02 `stream=True` 背后的事：** 每生成一小段就推给你，而不是等整段算完。

---

## 七、用自己的话解释（验收输出模板）

> 学习完成后，用下面结构**自己写一版**（不要照抄），能讲给同事/面试官听即过关。

### 模板（填空式）

```
1. 输入一句话，先被切成 Token，再变成 Embedding 向量。

2. 模型多层 Self-Attention，让每个词根据整句上下文更新自己的表示；
   FFN 再做进一步变换。N 层堆叠后，表示里已经融合了长距离语义。

3. 最后一层输出对词表每个 Token 的得分，Softmax 变成概率，
   这就是 Next Token Prediction。

4. 生成时一次只出一个 Token，拼回去再预测下一个，直到结束。
   所以叫自回归（Autoregressive）。

5. Transformer 取代 RNN，主要是因为 Attention 能并行、
   长距离依赖更直接，适合大规模预训练。

6. GPT 这类聊天模型是 Decoder-only；BERT 是 Encoder-only；
   翻译类常用 Encoder-Decoder。
```

### 参考示例（约 150 字，仅供对照）

> 用户输入先变成 Token，再嵌入成向量。Transformer 用 Self-Attention 让序列里每个词都能直接「看到」其它词，经过多层 Attention 和 FFN 后，模型对「下一个词是什么」给出概率分布。生成时逐个 Token 往外吐，所以流式 API 能一字一字返回。它取代 RNN，是因为训练可并行、长依赖更好学；GPT 属于 Decoder-only，专门做生成，而我们项目调的 chat 模型就是这一路。

---

## 八、自测清单（和算法工程师沟通前）

- [ ] 能画出 **Token → Embedding → Attention → FFN → Next Token** 五步
- [ ] 能说出 RNN 的两个痛点（串行、长依赖）
- [ ] 能解释训练并行 vs 推理自回归的区别
- [ ] 能区分 Encoder / Decoder / Decoder-only
- [ ] 能说明 Day11 Embedding 与 Transformer Embedding 不是同一回事
- [ ] 被问「Attention 复杂度」时能答：序列长度 n 时 roughly O(n²)（了解即可）

---

## 九、常见面试 / 沟通问题

| 问题 | 要点 |
|------|------|
| Transformer 和 RNN 最大区别？ | 并行 + 直接建模长依赖 |
| Self-Attention 解决什么问题？ | 动态加权上下文，不依赖固定长度隐状态 |
| 为什么 GPT 生成不能一次出整句？ | 自回归：下一个 Token 依赖已生成部分 |
| 上下文窗口是什么？ | 模型一次能处理的 Token 上限，和显存/架构有关 |
| RAG 和 Transformer 什么关系？ | RAG 在模型**外挂知识**；Transformer 是**生成引擎** |

---

## 十、与后续 Day 的衔接

| 后续 Day | 与 Day31 的关系 |
|----------|-----------------|
| Day32 RAG vs 微调 vs Prompt | 建立在「模型是预训练生成器」之上 |
| Day33 Token 与上下文窗口 | 深入 Day31 第一步 Token |
| Day34 推理参数 | 深入 Next Token 的采样策略 |
| Day35 幻觉 | 生成机制天然会「编造」，需 RAG/引用约束 |
| Day36 Embedding 升维 | 区分模型内 Embedding vs 检索 Embedding |

---

## 十一、推荐资料（可选）

| 资料 | 用途 |
|------|------|
| 论文 *Attention Is All You Need*（2017） | 源头，看架构图即可 |
| Jay Alammar — *The Illustrated Transformer* | 直觉图解（强烈推荐） |
| 3Blue1Brown — Attention 相关视频 | 可视化 Q/K/V |

---

## 小结

Day31 是 Sprint 5 的地基：**Token → Embedding → Self-Attention → FFN → Next Token Prediction** 这条链，就是你在 Day02 调 API、Day21_2 看流式输出时，屏幕背后正在发生的事。搞懂它，后面谈 RAG、幻觉、成本、选型才不会「只会用不会讲」。

**今日交付：** 完成「第七节 · 用自己的话解释」独立写一版，并通过第八节自测清单。
