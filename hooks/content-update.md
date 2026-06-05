# Content Update Hook

这个钩子用于新增或重写 `Agent基础知识` 系列文章时复用。

触发场景：

- 新增一篇 `Agent基础知识 xx` 文章。
- 重写已有文章。
- 从粘贴文本、聊天记录或草稿中整理正式 Markdown。
- 新增或调整 Product、Labs、Skills、Engineering 等长期维护文档。

## 执行步骤

1. 确认文章编号、标题和目标文件名。
2. 只保留正式正文，从 `# Agent基础知识 xx| ...` 开始。
3. 删除过程性内容，例如：
   - 写文章注意事项。
   - 交付前自检。
   - 聊天语气说明。
   - `utm_source=chatgpt.com` 等跟踪参数。
4. 将正文写入 `docs/foundations/xx-topic-slug.md`。
5. 同步更新：
   - `README.md`
   - `docs/foundations/README.md`
   - `docs/series-plan.md`
   - `docs/document-graph.md`
   - `resources/README.md`
   - `roadmap.md`
   - `TODO.md`
   - `docs/product/README.md`
   - `labs/README.md`
   - 新增目录对应的 README，例如 `docs/readings/README.md`、`docs/patterns/README.md`、`docs/engineering/README.md`、`skills/README.md`
6. 如果新增了维护流程、脚本或目录，同步更新根 README 的仓库结构。
7. 运行内容检查和相关文档审核脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-secrets.ps1
powershell -ExecutionPolicy Bypass -File scripts/audit-related-docs.ps1
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

8. 根据审核结果回看相关文档，修正遗漏的导航、文档图、资源索引或路线状态。
9. 提交并推送到 GitHub。

## 检查重点

- 文章是否出现在根 README 的学习路线中。
- 文章是否出现在 `docs/foundations/README.md` 的阅读顺序中。
- `docs/series-plan.md` 中对应文章状态是否更新。
- `docs/document-graph.md` 中是否同步文章节点和维护关系。
- `resources/README.md` 中是否补充重要来源。
- `roadmap.md` 中对应任务是否勾选。
- `TODO.md` 中当前任务状态是否同步。
- 是否误把写作提示、自检表、聊天痕迹放进正式文章。
- 参考链接是否去掉跟踪参数。
- 是否误提交真实 API Key、Token、Cookie、Session、Password 或真实环境文件。
- 财经相关输出是否包含来源、检索时间、风险提示和人工确认边界。
- 新增或修改 Lab 时，是否提供 demo、tests，并接入统一测试入口。

## 维护原则

- 正式仓库只保留可长期阅读和复用的内容。
- 草稿生成过程可以在本地存在，但不进入正式文章。
- 每次新增或重写文章都要同步导航、文档图、资源索引和待办状态，不让 README、TODO、roadmap、series plan 和 document graph 脱节。
- 每次涉及 Product、Labs、Skills 或脚本变更，都要同步审核相关文档，并运行密钥检查。
- 每个 Lab 的 demo 用于人工试跑，tests 用于自动回归；两者都应该能在无真实 API Key 的环境下运行。
- 自动检查只负责发现明显问题，最终仍要看一眼 diff。
