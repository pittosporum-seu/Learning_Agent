# Investment Research Case

这个目录规划投研 Agent Labs 共用的案例材料。

当前阶段先固化材料结构，具体 mock 数据在 Lab 01-03 实现时补齐。

计划文件：

- `strategy_request.md`: 用户自然语言策略样例。
- `strategy_policy.md`: 策略解析规则和边界。
- `risk_policy.md`: 风险提示、禁用输出和人工确认规则。
- `user_profile.md`: 用户偏好、风险承受能力、排除行业和候选数量。
- `mock_universe.csv`: mock 股票池。
- `mock_prices.csv`: mock 行情数据。
- `mock_news.md`: mock 新闻、公告和研报摘要。
- `report_template.md`: 证据化投研报告模板。

共享案例的默认策略：

```text
找最近 60 日趋势较强、回撤较低、没有明显负面新闻的半导体和人工智能方向股票，生成候选观察池。
```

所有 Lab 都应该遵守两个边界：

- 不把候选股票输出包装成确定性投资建议。
- 不在仓库中保存真实 API Key、账户凭据或个人隐私数据。
