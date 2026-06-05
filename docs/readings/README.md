# Readings

这里用于沉淀官方文档、论文、工程博客和开源项目的精读笔记。

`docs/foundations/` 里的 12 篇文章负责建立 Agent 基础概念；`docs/readings/` 则负责把这些概念背后的原始资料拆开读清楚，记录它解决的问题、核心观点、工程启发和容易误用的地方。

## 推荐结构

```text
docs/readings/
├── README.md
├── 01-anthropic-building-effective-agents.md
├── 02-openai-practical-guide-to-agents.md
├── 03-openai-agents-sdk.md
├── 04-claude-code-overview.md
├── 05-model-context-protocol.md
├── 06-swe-bench.md
├── 07-webarena-visualwebarena.md
└── 08-agentbench-evals-safety.md
```

## 当前进度

| 序号 | 资料 | 状态 |
| --- | --- | --- |
| 01 | [Anthropic: Building Effective Agents](01-anthropic-building-effective-agents.md) | 模板已建立 |
| 02 | [OpenAI: A Practical Guide to Building Agents](02-openai-practical-guide-to-agents.md) | 模板已建立 |
| 03 | [OpenAI Agents SDK](03-openai-agents-sdk.md) | 模板已建立 |

## 笔记模板

```text
# 资料标题

## 一、这篇资料解决什么问题
## 二、核心观点
## 三、对应 Agent 系统里的哪个模块
## 四、对工程实践有什么启发
## 五、容易误用的地方
## 六、适合补充到哪篇 Agent基础知识文章
```

## 维护原则

- 优先读官方文档、经典论文和高质量工程文章。
- 不追求全文翻译，重点记录可复用观点。
- 每篇精读都要能反向连接到 `Agent基础知识` 系列中的一个或多个主题。
