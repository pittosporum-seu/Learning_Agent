# Labs

这里用于把 `Agent基础知识` 系列落到一个连续场景里：个性化投资调研 Agent 系统。

完整计划见：[个性化投研 Agent Lab 总计划](../docs/product/lab-plan.md)。整体展示框架见：[Agent 学习展示框架](../docs/product/showcase-framework.md)。

## 主线场景

用户用自然语言描述投资研究策略，系统解析成结构化策略，规划投研流程，调用 mock 或真实财经工具获取证据，生成带风险提示的观察池报告；当某个流程稳定后，再沉淀为可复用 Skill。

默认示例策略：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。
```

## 规划目录

```text
labs/
├── README.md
├── shared/
│   ├── investment_research_case/
│   └── testing/
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

## 当前状态

- [x] [Lab 01: Strategy Intake + Workflow/Agent Router](01-strategy-intake/README.md)
  - 规则基线解析和 `routing_decision`。
  - 展示 workflow / agent / needs_clarification / blocked 的判断原因。
  - 可配置模型解析模式、本地 Web demo 和测试。
- [x] [Lab 02: Strategy Agent Loop](02-strategy-agent-loop/README.md)
  - 最小 Observe-Decide-Act Loop。
  - 根据 `StrategySpec` 生成 mock 投研计划。
  - 保留 structured trace、阻断和 max-turn 保护。
- [x] [Lab 03: Finance Tool Use Mock](03-finance-tool-use-mock/README.md)
  - 注册 `select_candidates`、`fetch_market_data`、`search_finance_news` 三个 mock 工具。
  - 展示工具选择、入参、返回、`tool_trace` 和 `candidate_evidence`。
  - 只生成 mock 观察池证据，不生成投资建议。
- [x] [Lab 04: Research RAG Basic](04-research-rag-basic/README.md)
  - 用本地 markdown 知识库展示 RAG。
  - 生成 `retrieval_trace`、`retrieved_context` 和 `augmented_evidence`。
  - 将策略规则、风险规则和报告模板挂回 Lab 03 的 mock 证据。
- [x] [Lab 05: User Preference Memory](05-user-preference-memory/README.md)
  - 用本地 mock 偏好展示 Memory。
  - 生成 `memory_snapshot`、`memory_trace` 和 `preference_adjusted_evidence`。
  - Memory 只调整候选证据视图，不覆盖原始证据、来源或风险提示。
- [x] [Lab 06: Skill Registry](06-skill-registry/README.md)
  - 用本地 mock Skill 元数据展示 Skill Registry。
  - 生成 `skill_selection_trace`、`selected_skills` 和 `disabled_skills`。
  - 高风险、证据不足、缺少风险提示或需要人工确认时禁用 Skill。
- [x] [Lab 07: Skill Generation](07-skill-generation/README.md)
  - 从 Lab 06 的 mock Skill Registry 输出生成可审查 Skill draft。
  - 生成 `generated_skill_draft`、`skill_draft_markdown` 和 `draft_review`。
  - 草稿只进入人工 review，不自动启用，也不写入本地 runtime 配置目录。
- [x] [Lab 08: MX Skills Adapter](08-mx-skills-adapter/README.md)
  - 用统一 adapter contract 串起 Lab 03 mock tools 和未来真实东方财富妙想 Skills。
  - 生成 `adapter_trace` 和 `safety_gate`。
  - 默认只使用 mock adapter，real stub 不读取 key、不发请求，并被安全门阻断。
- [ ] Lab 09-12: 按 [Lab 总计划](../docs/product/lab-plan.md) 推进。

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

运行 Lab 02 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 02-strategy-agent-loop
```

运行 Lab 03 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 03-finance-tool-use-mock
```

运行 Lab 04 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 04-research-rag-basic
```

运行 Lab 05 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 05-user-preference-memory
```

运行 Lab 06 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 06-skill-registry
```

运行 Lab 07 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 07-skill-generation
```

运行 Lab 08 demo：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 08-mx-skills-adapter
```

运行全部 Lab 测试：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

只运行某个 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 08-mx-skills-adapter
```

## 统一要求

- 每个 Lab 先支持 mock，真实 API 接入必须放在显式开关之后。
- 真实模型解析可以用于语义补全，但测试必须能在无 key 情况下通过。
- 所有候选观察池输出都必须带风险提示。
- 真实密钥只从环境变量读取，不写入仓库。
- 涉及自选股、模拟组合、Skill 启用的动作必须保留人工确认。
- 每个可运行 Lab 都应提供 demo 和 tests，并接入统一测试入口。
- 每次新增 Lab 后，同步更新 README、文档图、TODO 和相关产品文档。
