# Labs

这里用于把 `Agent基础知识` 系列落到一个连续场景里：个性化投资调研 Agent 系统。

完整计划见：[个性化投研 Agent Lab 总计划](../docs/product/lab-plan.md)。

## 主线场景

用户用自然语言描述投资研究策略，系统解析成结构化策略，规划投研流程，调用 mock 或真实财经工具获取证据，生成带风险提示的观察池报告；当某个流程稳定后，再沉淀为可复用 Skill。

默认示例策略：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的半导体和人工智能方向股票，生成候选观察池。
```

## 规划目录

```text
labs/
├── README.md
├── shared/
│   └── investment_research_case/
├── 01-strategy-intake/
├── 02-strategy-agent-loop/
├── 03-finance-tool-use-mock/
├── 04-research-rag-basic/
├── 05-user-preference-memory/
├── 06-skill-registry/
├── 07-skill-generation/
├── 08-mx-skills-adapter/
├── 09-research-planner/
├── 10-evidence-report/
├── 11-simulation-portfolio/
└── 12-evaluation-safety/
```

当前只固化计划和共享案例目录，具体 Lab 会按顺序实现。

## 统一要求

- 每个 Lab 先支持 mock，真实 API 接入放到显式开关之后。
- 所有候选股票输出都必须带风险提示。
- 真实密钥只从环境变量读取，不写入仓库。
- 涉及自选股、模拟组合、Skill 启用的动作必须保留人工确认。
