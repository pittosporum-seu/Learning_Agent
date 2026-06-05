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
│   ├── investment_research_case/
│   └── testing/
├── 01-strategy-intake/
│   ├── README.md
│   ├── demo/
│   ├── src/
│   ├── tests/
│   └── web/
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

当前已实现 Lab 01，后续按 Lab 02、Lab 03 继续推进。

## 当前状态

- [x] [Lab 01: Strategy Intake](01-strategy-intake/README.md)
- [ ] Lab 02: Strategy Agent Loop
- [ ] Lab 03: Finance Tool Use Mock
- [ ] Lab 04-12: 按 [Lab 总计划](../docs/product/lab-plan.md) 推进

## Demo 与测试

启动 Lab 01 网页 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-web.ps1 -Lab 01-strategy-intake -Port 8765
```

打开：

```text
http://127.0.0.1:8765/
```

运行 Lab 01 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 01-strategy-intake
```

传入自定义策略：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 01-strategy-intake -Request "筛选市盈率小于20的银行股。"
```

运行全部 Lab 测试：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

只运行某个 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 01-strategy-intake
```

## 统一要求

- 每个 Lab 先支持 mock，真实 API 接入放到显式开关之后。
- 所有候选股票输出都必须带风险提示。
- 真实密钥只从环境变量读取，不写入仓库。
- 涉及自选股、模拟组合、Skill 启用的动作必须保留人工确认。
- 每个可运行 Lab 都应提供 demo 和 tests，并接入统一测试入口。
