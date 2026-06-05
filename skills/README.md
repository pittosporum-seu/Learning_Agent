# Skills

这里用于存放可复用 Skill 示例。

第 10 篇 [Skills：把提示词升级成可复用能力包](../docs/foundations/10-skills.md) 讲的是概念；这个目录用于把文章里的方法沉淀成可复用的 `SKILL.md` 示例。

## 推荐结构

```text
skills/
├── README.md
├── code-review/
│   └── SKILL.md
├── research-report/
│   └── SKILL.md
├── rag-answer/
│   └── SKILL.md
├── etl-debugging/
│   └── SKILL.md
└── agent-article-writing/
    └── SKILL.md
```

## 优先补充的 Skill

- `agent-article-writing`: 固化 `Agent基础知识` 系列文章的写作结构。
- `code-review`: 固化代码审查步骤、输出格式和风险检查项。
- `etl-debugging`: 固化数据链路排查流程、SQL 证据和安全边界。

## 维护原则

- 每个 Skill 都应有明确触发场景和禁用场景。
- 不把一次性提示词直接塞进 Skill，要先抽象成稳定流程。
- 高风险动作必须写清楚人工确认点。
- Skill 示例可以先写说明，不急着绑定真实工具。

