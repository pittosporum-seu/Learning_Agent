# Lab 04: Research RAG Basic

这个 Lab 展示 `RAG` 的最小教学形态：系统先复用 Lab 03 的 mock 工具输出 `candidate_evidence`，再从本地 markdown 知识库中检索策略规则、风险规则和报告模板，把相关片段作为 `retrieved_context` 挂回证据链。

本 Lab 不调用真实向量库、不调用真实模型 API、不调用真实财经 API，也不生成真实股票推荐。它只展示“检索到的上下文如何进入证据化流程”。

## 输入

输入是一段自然语言投研策略，例如：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的电网设备方向股票，生成候选观察池。
```

Lab 04 会先调用 Lab 03 的 `run_finance_tool_use_mock`。如果上游路由结果是 `blocked` 或 `needs_clarification`，本 Lab 会保持 `blocked`，并跳过正常检索。

## 输出

核心输出是结构化 JSON：

- `strategy_spec`: Lab 01 解析出的策略对象。
- `tool_trace`: Lab 03 的 mock 工具调用轨迹。
- `candidate_evidence`: Lab 03 生成的 mock 候选证据。
- `retrieval_trace`: 查询构造、chunk 数量、命中片段和分数。
- `retrieved_context`: 本地文档检索片段，每条包含 `source`、`chunk_id`、`section`、`matched_terms`、`used_for`。
- `augmented_evidence`: 挂载了 `retrieved_context_refs` 的候选证据。
- `final_output`: 本次 RAG 汇总、引用来源、证据缺口和下一步。
- `risk_disclosure`: 财经输出边界提示。

## 本地知识库

| 文件 | 作用 |
| --- | --- |
| `data/strategy_policy.md` | 策略字段完整性、Lab 03 证据交接和证据缺口规则。 |
| `data/risk_policy.md` | 财经输出边界、负面新闻过滤和人工确认规则。 |
| `data/report_template.md` | 观察池报告结构、引用格式和 Lab 05 交接说明。 |

## Demo

运行默认 demo：

```powershell
python labs/04-research-rag-basic/demo/run_demo.py
```

也可以通过统一脚本运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-demo.ps1 -Lab 04-research-rag-basic
```

输出完整 JSON：

```powershell
python labs/04-research-rag-basic/demo/run_demo.py --json
```

## Tests

只运行本 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 04-research-rag-basic
```

运行全部 Lab：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

## 不做什么

- 不接真实向量数据库。
- 不调用真实模型 API。
- 不调用真实行情、新闻或东方财富妙想 Skills。
- 不生成真实投资建议、收益承诺、买卖动作或目标价格。
- 不把检索片段当成绝对事实；每条片段都必须保留来源、chunk id、命中词和用途。

## 和前后 Lab 的关系

- Lab 03 负责 Tool Use，把 mock 财经工具结果转成 `candidate_evidence`。
- Lab 04 负责 RAG，把本地规则和模板片段转成 `retrieved_context`，并和 `candidate_evidence` 关联。
- Lab 05 会引入 User Preference Memory，让用户风险偏好、排除条件和报告风格进入上下文，但仍不能替代证据或安全边界。
