# Engineering

这里用于沉淀 Agent 工程化清单。

`Agent基础知识` 系列讲清楚概念和原理；`docs/engineering/` 则把这些内容落成上线前可以检查的工程项，例如权限、上下文、Trace、评测、安全和成本。

## 推荐结构

```text
docs/engineering/
├── README.md
├── permission-boundary.md
├── context-management.md
├── trace-and-logging.md
├── evaluation-checklist.md
├── safety-guardrails.md
├── human-in-the-loop.md
└── cost-latency.md
```

## 清单模板

```text
# 清单名称

## 一、它解决什么工程风险
## 二、上线前必须检查什么
## 三、推荐做法
## 四、常见误区
## 五、和哪些 Agent 模块相关
```

## 维护原则

- 工程清单要短、明确、可执行。
- 每一项最好能对应 Trace、Eval、权限或运行日志里的证据。
- 优先沉淀上线前会真正用到的检查项。

