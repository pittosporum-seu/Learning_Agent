# Resources

这里存放 Agent 学习资料索引、阅读清单和外部链接。

## 核心来源

| 资料 | 类型 | 作用 |
| --- | --- | --- |
| [datawhalechina/Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub) | 开源学习路线 | 本仓库 `Agent基础知识` 系列最初围绕它的 Agent 学习路线展开。 |
| Anthropic: Building Effective Agents | 工程文章 | 用于理解 workflow / agent 区分、agent patterns 和从简单系统开始的原则。 |
| OpenAI Agents / Evals / Computer Use | 官方文档 | 用于补充 Agent 构建、评测、观测、安全和 Computer Use 相关内容。 |
| Claude Code Docs | 官方文档 | 用于补充 Coding Agent、Subagents、Skills、Hooks 等工程化主题。 |
| MCP Documentation | 官方文档 | 用于理解 Agent 工具和数据源的统一接口。 |
| SWE-bench / WebArena / AgentBench | Benchmark | 用于补充 Coding Agent、Browser Agent 和 Agent 评测视角。 |
| 《提示词工程已死，Loop Engineering 来了！》 | 文章线索 | 用于补充第 13 篇 Loop Engineering，帮助把 Prompt、工具、状态、验证和人工确认放进闭环工程视角。 |
| 小米 MiMo | 模型服务 | 个性化投研 Agent 系统的模型层，真实密钥由运行环境注入。 |
| 东方财富妙想 Skills | 金融数据与工具能力 | 用于投研 Labs 的候选筛选、行情财务、资讯搜索、自选股和模拟组合接口参考。 |

建议按类型维护：

- 官方文档。
- 经典论文。
- 工程博客。
- 开源项目。
- 工具和 Skill 说明。
- 视频课程。
- 案例复盘。

记录资料时建议补充：

- 资料链接。
- 推荐理由。
- 对应学习阶段。
- 读完后的关键收获。

## 和 Readings 的关系

`resources/` 负责维护资料索引；`docs/readings/` 负责把重点资料整理成结构化精读笔记。

当某个资料值得长期复用时，先在这里记录来源，再在 `docs/readings/` 中补精读。

## 和 Product / Labs 的关系

`docs/product/` 负责定义个性化投研 Agent 系统的愿景、Lab 路线和安全边界；`labs/` 负责把这些设计拆成可运行实验。

涉及真实模型或财经数据时，只记录接口职责和环境变量名称，不记录真实凭据。
