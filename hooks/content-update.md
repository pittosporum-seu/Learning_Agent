# Content Update Hook

这个钩子用于新增或重写 `Agent基础知识` 系列文章、Product 文档、Labs、Skills、Engineering 清单时复用。

## 触发场景

- 新增一篇 `Agent基础知识 xx` 文章。
- 重写已有文章。
- 从粘贴文本、聊天记录或草稿中整理正式 Markdown。
- 新增或调整 Product、Labs、Skills、Engineering 等长期维护文档。
- 新增真实 API 适配、密钥环境变量或安全边界。
- 新增可运行 demo、测试框架或脚本。

## 执行步骤

1. 确认文章编号、标题和目标文件名。
2. 只保留正式正文，删除过程性内容。
3. 删除写作提示、自检表、聊天痕迹和 `utm_source=chatgpt.com` 等跟踪参数。
4. 将正文写入目标目录。
5. 同步更新：
   - `README.md`
   - `docs/start-here.md`
   - `docs/glossary.md`
   - `docs/foundations/README.md`
   - `docs/series-plan.md`
   - `docs/document-graph.md`
   - `resources/README.md`
   - `roadmap.md`
   - `TODO.md`
   - `docs/product/README.md`
   - `docs/product/lab-plan.md`
   - `docs/product/security-and-secrets.md`
   - `AGENTS.md`
   - 相关目录的 `AGENTS.md`
   - `labs/README.md`
   - 新增目录对应的 README，例如 `docs/readings/README.md`、`docs/patterns/README.md`、`docs/engineering/README.md`、`skills/README.md`
6. 如果新增了维护流程、脚本或目录，同步更新根 README 的仓库结构。
7. 如果涉及真实 API、模型 key、财经数据源或模拟组合，确认：
   - 真实 key 只从环境变量读取。
   - `LLM_API_KEY`、`MIMO_API_KEY`、`XIAOMI_API_KEY`、`MX_APIKEY` 只能出现在说明文档或 `.env.example` 占位中，不能提交真实值。
   - `.env.example` 只保留占位。
   - 测试默认 mock，不依赖真实 key。
   - UI 或报告里有风险提示和人工确认边界。
8. 运行检查：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-secrets.ps1
powershell -ExecutionPolicy Bypass -File scripts/audit-related-docs.ps1
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
```

9. 根据审核结果回看相关文档，修正遗漏的导航、文档图、资源索引或路线状态。
10. 看一眼 `git diff`，确认没有真实密钥、过程性内容或无关改动。
11. 提交并推送到 GitHub。

## 检查重点

- 文章是否出现在根 README 的学习路线中。
- 新增入口、术语或产品案例内容是否同步到 `docs/start-here.md`、`docs/glossary.md` 和 `docs/product/README.md`。
- 文章是否出现在 `docs/foundations/README.md` 的阅读顺序中。
- `docs/series-plan.md` 中对应文章状态是否更新。
- `docs/document-graph.md` 中是否同步文章节点、Lab 节点和维护关系。
- `resources/README.md` 中是否补充重要来源。
- `roadmap.md` 中对应任务是否勾选。
- `TODO.md` 中当前任务状态是否同步。
- 是否误把写作提示、自检表、聊天痕迹放进正式文章。
- 参考链接是否去掉跟踪参数。
- 是否误提交真实 API key、token、cookie、session、password 或真实环境文件。
- 财经相关输出是否包含来源、检索时间、风险提示和人工确认边界。
- 新增或修改 Lab 时，是否提供 demo、tests，并接入统一测试入口。
- 提供 web demo 时，是否能在本地 `127.0.0.1` 启动。
- 真实 API 模式是否可选，且无真实 key 时仍能启动和测试。

## 维护原则

- 正式仓库只保留可长期阅读和复用的内容。
- 草稿生成过程可以在本地存在，但不进入正式文章。
- 每次新增或重写文章都要同步导航、文档图、资源索引和待办状态。
- 每次涉及 Product、Labs、Skills 或脚本变更，都要同步审核相关文档，并运行密钥检查。
- 每个 Lab 的 demo 用于人工试跑，tests 用于自动回归；两者都应能在无真实 API key 的环境下运行。
- Web demo 只作为本地实验入口，默认绑定 `127.0.0.1`。
- 自动检查只负责发现明显问题，最终仍要看一眼 diff。
