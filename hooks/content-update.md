# Content Update Hook

这个钩子用于新增或重写 `Agent基础知识` 系列文章时复用。

触发场景：

- 新增一篇 `Agent基础知识 xx` 文章。
- 重写已有文章。
- 从粘贴文本、聊天记录或草稿中整理正式 Markdown。

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
   - `roadmap.md`
6. 如果新增了维护流程、脚本或目录，同步更新根 README 的仓库结构。
7. 运行内容检查脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-content.ps1
```

8. 检查 Git diff，确认没有无关内容。
9. 提交并推送到 GitHub。

## 检查重点

- 文章是否出现在根 README 的学习路线中。
- 文章是否出现在 `docs/foundations/README.md` 的阅读顺序中。
- `docs/series-plan.md` 中对应文章状态是否更新。
- `roadmap.md` 中对应任务是否勾选。
- 是否误把写作提示、自检表、聊天痕迹放进正式文章。
- 参考链接是否去掉跟踪参数。

## 维护原则

- 正式仓库只保留可长期阅读和复用的内容。
- 草稿生成过程可以在本地存在，但不进入正式文章。
- 每次新增文章都要同步导航，不让 README、roadmap 和 series plan 脱节。
- 自动检查只负责发现明显问题，最终仍要看一眼 diff。

