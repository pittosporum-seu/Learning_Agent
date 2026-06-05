# Patterns

这里用于整理 Agent 设计模式。

`docs/foundations/` 解释概念是什么；`docs/patterns/` 更像可查手册，用来回答“这个任务应该用哪种模式做”。

## 推荐结构

```text
docs/patterns/
├── README.md
├── workflow-vs-agent.md
├── prompt-chaining.md
├── routing.md
├── orchestrator-workers.md
├── evaluator-optimizer.md
├── agentic-rag.md
├── plan-execute-verify.md
└── human-in-the-loop.md
```

## 每个模式建议回答

- 它解决什么问题。
- 什么时候适合用。
- 什么时候不该用。
- 需要哪些工具、状态和权限边界。
- 如何评测这个模式是否有效。
- 对应哪些 `Agent基础知识` 文章。

## 维护原则

- 优先记录可复用判断标准，而不是堆框架名。
- 每个模式都要写清楚边界和失败场景。
- 设计模式应服务于真实任务，不为了显得复杂而引入 Agent。

