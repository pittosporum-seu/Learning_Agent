# Agent 基础知识系列规划

这个文件用于维护 `Agent基础知识` 系列文章的整体规划。

系列先按 12 篇推进：前 6 篇讲基础概念，后 6 篇讲工程化和真实 Agent 系统。写作主线从 Workflow / Agent 区分开始，逐步推进到 Agent Loop、Tool Use、RAG、Memory、MCP、Harness、Coding Agent、Subagent、Skills、Browser Agent、Evaluation 和 Safety。

## 系列总规划

| 篇数 | 主题 | 核心问题 | 状态 |
| --- | --- | --- | --- |
| 01 | Workflow vs Agent | 什么时候该用 Agent，什么时候不该用？ | 已完成 |
| 02 | Agent Loop | Agent 为什么不是一次性回答，而是循环执行？ | 已完成 |
| 03 | Tool Use | 工具调用到底怎么发生？模型和宿主程序怎么配合？ | 已完成 |
| 04 | RAG | RAG 和普通问答有什么区别？为什么要 chunk、embed、retrieve？ | 已完成 |
| 05 | Memory | Agent 到底该记什么？Memory 和上下文有什么区别？ | 已完成 |
| 06 | MCP | MCP 到底解决了什么问题？为什么越来越重要？ | 已完成 |
| 07 | Agent Harness | 为什么 Claude Code / Codex 这类产品强在工程底座？ | 已完成 |
| 08 | Coding Agent | Coding Agent 为什么最容易落地？怎么理解 Shell、文件编辑、测试反馈？ | 已完成 |
| 09 | Subagent / Multi-Agent | 多 Agent 什么时候有用？什么时候反而添乱？ | 已完成 |
| 10 | Skills | Skill 和 Prompt、Tool、MCP 有什么区别？ | 已完成 |
| 11 | Browser / Computer Use Agent | Browser Agent 为什么难？视觉、点击、失败恢复怎么处理？ | 计划中 |
| 12 | Evaluation / Trace / Safety | 怎么判断 Agent 真有用？怎么避免瞎跑、越权、退化？ | 计划中 |

## 写作节奏

先不要一口气写完 12 篇，可以按三组推进。

```text
第一组：基础概念
01 Workflow vs Agent
02 Agent Loop
03 Tool Use

第二组：知识与能力扩展
04 RAG
05 Memory
06 MCP

第三组：工程落地
07 Harness
08 Coding Agent
09 Subagent / Multi-Agent
10 Skills
11 Browser Agent
12 Eval / Safety
```

## 每篇固定结构

每篇文章尽量保持一致的阅读体验：

```text
1. 这篇解决什么问题
2. 参考资料里的核心观点
3. 用中文重新讲清楚
4. Mermaid 图解释
5. 结合真实工作场景举例
6. 最后给一个判断标准 / 提示词模板
```

## 剩余重点选题

### 11 Browser / Computer Use Agent

重点讲 Browser Agent 为什么比 API Tool 更脆弱：

- DOM、截图、视觉理解和动作日志分别解决什么问题。
- 点击、滚动、输入、等待为什么容易失败。
- 登录、付款、删除、发布等高风险动作为什么必须限制。
- Browser Agent 适合什么任务，不适合什么任务。

### 12 Evaluation / Trace / Safety

重点讲 Agent 从 Demo 走向可靠系统时必须补上的工程环节：

- 固定测试集。
- Trace 和工具调用日志。
- 成本、延迟、失败原因统计。
- 权限边界和人工确认节点。
- 回归测试，防止提示词或工具改动后能力退化。
