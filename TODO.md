# TODO

这个文件是 `Learning_Agent` 仓库的主待办板。

GitHub Issues 适合公开协作和长期追踪；这个 `TODO.md` 适合跟仓库内容一起版本化，记录当前阶段真正要推进的事项。后续如果某个任务需要多人协作或讨论，可以按 `.github/ISSUE_TEMPLATE/task.md` 创建 GitHub Issue。

## 使用规则

- `P0`: 当前最应该推进的任务。
- `P1`: 重要，但可以排在 P0 后。
- `P2`: 有价值，但不阻塞当前学习路线。
- 每个任务尽量写清楚产出文件和验收标准。
- 完成任务后同步更新 `roadmap.md`、`docs/document-graph.md` 和相关 README。

## Doing

当前没有进行中的任务。下一步从 `Next` 中选择 P0 任务推进。

## Next

| 优先级 | 任务 | 产出 | 验收标准 |
| --- | --- | --- | --- |
| P0 | 补 labs 最小实验骨架 | `labs/01-minimal-agent-loop/`、`labs/02-tool-use/`、`labs/03-rag-basic/` | 先写 README 和 mock 代码，不接真实模型 API |
| P0 | 补第一批 Skill 示例 | `skills/agent-article-writing/SKILL.md`、`skills/code-review/SKILL.md`、`skills/etl-debugging/SKILL.md` | 每个 Skill 有触发场景、禁用场景、步骤、输出格式和风险边界 |
| P1 | 补工程化清单第一批 | `docs/engineering/permission-boundary.md`、`trace-and-logging.md`、`evaluation-checklist.md` | 每篇是短清单，包含上线前检查项 |
| P1 | 补设计模式第一批 | `docs/patterns/workflow-vs-agent.md`、`orchestrator-workers.md`、`human-in-the-loop.md` | 每篇说明适用场景、不适用场景和评测方式 |

## Backlog

| 优先级 | 任务 | 产出 | 说明 |
| --- | --- | --- | --- |
| P1 | 建立术语表 | `docs/glossary.md` | 汇总 Agent、Workflow、Harness、Skill、Trace 等术语 |
| P1 | 建立引用检查机制 | `scripts/check-links.ps1` | 先检查 Markdown 中的明显坏链接和跟踪参数 |
| P2 | 做 GitHub Issues 迁移 | GitHub Issues | 将 `TODO.md` 中长期任务迁到 Issues |
| P2 | 补更多 benchmark 阅读笔记 | `docs/readings/` | SWE-bench、WebArena、AgentBench、OSWorld 等 |

## Done

| 时间 | 任务 | 提交 |
| --- | --- | --- |
| 2026-06-05 | 完成 `Agent基础知识` 01-12 篇正文 | `181d374` |
| 2026-06-05 | 新增文档图和相关文档审核 hook | `4e361c1` |
| 2026-06-05 | 新增 readings / patterns / engineering / skills 扩展骨架 | `905b7fa` |
| 2026-06-05 | 建立仓库待办机制和 GitHub Issue 任务模板 | 本轮提交 |
| 2026-06-05 | 补第一批 readings 精读模板 | 本轮提交 |
