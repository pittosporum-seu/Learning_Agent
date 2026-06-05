# User Profile

这个文件记录投研 Labs 使用的默认用户偏好。它是 mock 配置，不包含真实个人信息。

```yaml
risk_level: medium
preferred_markets:
  - A股
exclude_st: true
max_candidates: 10
preferred_outputs:
  - 候选观察池
  - 证据化报告
requires_human_confirmation:
  - 添加或删除自选股
  - 进入模拟组合
  - 模拟买入
  - 模拟卖出
  - 模拟撤单
  - 启用新 Skill
```

## 使用原则

- 用户偏好只影响筛选边界，不代表投资结论。
- 风险等级默认 `medium`，真实系统中应允许用户查看、修改和清除。
- `exclude_st` 默认开启，用于演示风险过滤。
- `max_candidates` 默认 10，避免候选池过大导致报告不可审阅。
