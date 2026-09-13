# LangChain 完整时间线

> 最后更新：2026-06-17 | 信息截止日期标注于各条目末尾

---

## 2022 年：起源

| 时间 | 事件 | 来源 / 可信度 |
|------|------|---------------|
| **2022-10-22** | Harrison Chase 在 GitHub (hwchase17) 上提交 LangChain 的第一个代码版本，约 800 行代码的单文件 Python 包。当时他是 Robust Intelligence 的 ML 工程师，哈佛大学统计与计算机科学专业毕业。项目名 "LangChain" = Language + Chain | CSDN/博客园多方交叉验证 ⭐⭐⭐⭐⭐ |
| **2022-11** | ChatGPT 发布，LLM 应用开发需求爆发，LangChain 作为最早的 LLM 应用框架迅速获得关注 | 公共常识 ⭐⭐⭐⭐⭐ |
| **2022-12** | LangChain 在 GitHub 上快速增长，社区开始贡献代码。早期功能：提示管理、链式调用、基础 LLM 接口 | 多方交叉 ⭐⭐⭐⭐ |

---

## 2023 年：爆发与商业化

| 时间 | 事件 | 来源 / 可信度 |
|------|------|---------------|
| **2023-01~03** | LangChain 成为 GitHub 增长最快的开源项目之一，star 数快速攀升。开发者社区迅速扩大，数百名贡献者 | 多方交叉 ⭐⭐⭐⭐ |
| **2023-06** | OpenAI 发布 gpt-3.5-turbo-0613 和 gpt-4-0613，首次支持 **Function Calling**。LangChain 迅速适配，Agent 模式从 ReAct prompt hack 升级为基于 function calling 的结构化工具调用 | OpenAI 官方 + CSDN ⭐⭐⭐⭐⭐ |
| **2023-07** | LangChain 引入 `langchain-core` 核心模块的早期拆分思路，开始 LCEL (LangChain Expression Language) 的设计 | 官方博客 ⭐⭐⭐⭐ |
| **2023-08** | **LangSmith** 进入内测/beta 阶段，定位为 LLM 应用的可观测性与调试平台（tracing、evaluation） | 官方文档 + 社区 ⭐⭐⭐⭐ |
| **2023-09** | Harrison Chase 辞去 Robust Intelligence 职务，全职投入 LangChain 公司运营 | 多方交叉 ⭐⭐⭐⭐ |
| **2023-10** | **LangServe** 首次发布（v0.0.8），将 LangChain runnable/chain 部署为 REST API（基于 FastAPI） | GitHub PR 记录 ⭐⭐⭐⭐⭐ |
| **2023-10** | **LangGraph** 早期概念/原型出现。LangChain 团队意识到线性 Chain 模式不足以支撑复杂 Agent 需求，开始设计基于图结构的工作流框架 | 多方交叉 ⭐⭐⭐⭐ |
| **2023-10-07** | OpenAI Fine-tuning 支持 Function Calling，进一步强化了结构化工具调用范式 | 站长之家 ⭐⭐⭐⭐ |
| **2023-11** | **LangGraph** 开源发布，以"图结构 + 状态"为核心哲学，支持循环、条件分支、human-in-the-loop | 官方 + CSDN 多方 ⭐⭐⭐⭐ |
| **2023-12** | LangChain GitHub Stars 突破 **50K**，月下载量快速增长 | 社区统计 ⭐⭐⭐ |
| **2023-04** | 🔑 **种子轮**：Benchmark 领投 **1000 万美元** | TechCrunch/腾讯新闻 ⭐⭐⭐⭐⭐ |
| **2023-04** | 🔑 **A 轮**（种子轮一周后）：红杉资本领投 **2000 万美元**，估值 **2 亿美元** | TechCrunch/腾讯新闻 ⭐⭐⭐⭐⭐ |

---

## 2024 年：架构重构与稳定化

| 时间 | 事件 | 来源 / 可信度 |
|------|------|---------------|
| **2024-01-08** | **LangChain v0.1.0** 正式发布——首个稳定版本。重大架构变更：(1) 拆分 `langchain-core` 核心抽象模块；(2) 第三方集成移至 `langchain-community` 或独立合作伙伴包（如 `langchain-openai`）；(3) LCEL 成为官方推荐范式；(4) 正式语义化版本管理，破坏性变更提升次版本号 | 官方博客 ⭐⭐⭐⭐⭐ |
| **2024-01** | 社区出现批评声浪：博客《Why We No Longer Use LangChain for Our AI Agents》（作者 Fabian Both, Octomind）引发广泛讨论，批评 LangChain 抽象过度、debug 困难、docstring 质量差 | 163.com/网易 ⭐⭐⭐⭐ |
| **2024-03** | OpenAI 发布 GPT-4 Turbo (gpt-4-turbo-2024-04-09)，支持 128K 上下文、JSON Mode、parallel function calling。LangChain 适配更新 | 公共知识 ⭐⭐⭐⭐⭐ |
| **2024-05** | **LangChain v0.2.0** 发布。核心变更：大量旧导入路径迁移（`langchain.vectorstores` → `langchain_community.vectorstores` 等）、移除部分 deprecated API、同步 API 逐步废弃、发布 `langchain-cli` 自动迁移工具 | 官方博客 + 掘金 ⭐⭐⭐⭐⭐ |
| **2024-08** | OpenAI 发布 GPT-4o，原生支持多模态 + 更强的 function calling。LangChain `langchain-openai` 包快速适配 | 公共知识 ⭐⭐⭐⭐⭐ |
| **2024-09-16** | **LangChain v0.3.0** 发布。核心变更：从 Pydantic v1 迁移到 Pydantic v2；进一步清理 deprecated 代码；Python 最低版本提升 | 官方 + 今日头条 ⭐⭐⭐⭐⭐ |
| **2024-12** | LangChain GitHub Stars 突破 **80K+**，月开源下载量突破数千万 | langchaincn.cn ⭐⭐⭐⭐ |

---

## 2025 年：从框架到平台，独角兽诞生

| 时间 | 事件 | 来源 / 可信度 |
|------|------|---------------|
| **2025-01** | LangChain 生态持续扩张，`langchain-classic` 包被引入用于兼容旧版 Legacy Chains | CSDN ⭐⭐⭐⭐ |
| **2025-03** | LangSmith 本地部署方案成熟，金融/医疗等敏感行业合规需求推动 | CSDN ⭐⭐⭐ |
| **2025-07** | TechCrunch 报道 LangChain 正以至少 **10 亿美元估值**进行新一轮融资，IVP 领投 | TechCrunch/腾讯新闻 ⭐⭐⭐⭐⭐ |
| **2025-09** | LangGraph 生态加速，Studio 可视化编辑器、CLI 部署工具链完善 | CSDN 多方 ⭐⭐⭐⭐ |
| **2025-10-20/22** | 🏆 **LangChain v1.0.0 + LangGraph v1.0.0** 正式发布。这不是常规升级，而是**从零重写**。核心变革：(1) `create_agent()` 为唯一核心入口；(2) LCEL 从"推荐方案"升级为"唯一生产级标准范式"，Legacy Chains 彻底淘汰；(3) 引入 **Middleware（中间件）机制**，系统化解决上下文工程问题；(4) 标准 Message 块 + 统一接口；(5) Python 最低版本 3.10+ | 官方 + 博客园 + CSDN 多方 ⭐⭐⭐⭐⭐ |
| **2025-10-21** | 🔑 **B 轮融资**：IVP 领投 **1.25 亿美元**，投后估值 **12.5 亿美元**，正式跻身独角兽。新投资方 CapitalG（Google）、Sapphire Ventures 加入；现有投资方红杉、Benchmark、Amplify 跟投 | 腾讯新闻/TechCrunch ⭐⭐⭐⭐⭐ |
| **2025-11** | **DeepAgents** 开源项目发布（v0.1~v0.3），定位为 LangGraph 之上的高层封装，核心概念：`create_deep_agent()` 一行代码创建复杂智能体，内置任务规划、子代理管理、文件系统、长期记忆等通用能力 | CSDN/博客园多方 ⭐⭐⭐⭐ |

---

## 2026 年（最近6个月）：Agent 工程元年的战略深化

> 🔴 以下为最近 6 个月动态，已标注 ⏰

| 时间 | 事件 | 来源 / 可信度 |
|------|------|---------------|
| **2026-01** ⏰ | Harrison Chase 接受红杉资本对话，提出 **"2026 年是 Long-Horizon Agents 元年"**。核心观点：AI 从 Talkers（对话框）时代进入 Doers（做事）时代，长程智能体需要持久执行、状态管理、human-in-the-loop | 腾讯新闻/InfoQ ⭐⭐⭐⭐⭐ |
| **2026-01** ⏰ | Harrison Chase 发文警告：**2026 是 "Agent 工程" 分水岭**，传统软件公司的生存考验开始。核心论点：Agent 行为由代码+模型共同决定，非确定性打破了传统软件工程的前提 | 企鹅号/InfoQ ⭐⭐⭐⭐⭐ |
| **2026-02** ⏰ | LangSmith 正式品牌化升级，定位从 "LangChain 可观测性工具" 扩展为 **"framework-agnostic agent engineering platform"**（框架无关的智能体工程平台） | langsmith.com 官网 ⭐⭐⭐⭐⭐ |
| **2026-03** ⏰ | DeepAgents v0.4.x 发布，引入 **Skill 机制**（类似 Claude Code 的 Skill 系统），支持自定义 Skill 目录 + SKILL.md 定义 | 博客园/CSDN ⭐⭐⭐⭐ |
| **2026-03-10** ⏰ | **LangServe 仓库被归档（archived）**，标记为 read-only。部署能力整合进 LangGraph Cloud/LangGraph Platform | GitHub langserve repo ⭐⭐⭐⭐⭐ |
| **2026-04** ⏰ | LangChain + LangGraph 1.0 教程生态成熟，社区大规模迁移完成。`langchain-classic` 包用于渐进迁移 | CSDN 多方 ⭐⭐⭐⭐ |
| **2026-05** ⏰ | DeepAgents v0.4.3 稳定版。三层产品线清晰：<br>- **DeepAgents**：高层封装，开箱即用复杂智能体<br>- **LangChain**：中层，自定义 Agent 模块<br>- **LangGraph**：底层，完全自定义工作流 | 博客园/CSDN ⭐⭐⭐⭐ |
| **2026-06** ⏰ | LangChain 官网数据：月开源下载 **1 亿+**，模型/工具集成 **1000+**，GitHub Stars **90K+** | langchaincn.cn 官网 ⭐⭐⭐⭐⭐ |
| **2026-06** ⏰ | LangSmith 已支持 OpenAI、Anthropic、DeepSeek 等多框架追踪，不再是 LangChain 专属 | langsmith.com ⭐⭐⭐⭐⭐ |

---

## 融资历程汇总

| 轮次 | 时间 | 金额 | 估值 | 领投 | 跟投/参投 |
|------|------|------|------|------|-----------|
| 种子轮 | 2023-04 | $10M | — | Benchmark | — |
| A 轮 | 2023-04 | $20M | $200M | 红杉资本 | — |
| B 轮 | 2025-10 | $125M | $1.25B | IVP | CapitalG, Sapphire Ventures, 红杉, Benchmark, Amplify |

---

## 版本发布时间线

| 版本 | 发布时间 | 核心变更 |
|------|----------|----------|
| 0.0.x 系列 | 2022-10 ~ 2023-12 | 早期快速迭代，基础链、Agent、Memory、RAG |
| **v0.1.0** | 2024-01-08 | 首个稳定版；拆分 langchain-core / langchain-community / 合作伙伴包；LCEL 引入；正式语义化版本 |
| **v0.2.0** | 2024-05 | 导入路径大迁移；deprecated API 移除；同步 API 逐步废弃；langchain-cli 迁移工具 |
| **v0.3.0** | 2024-09-16 | Pydantic v1 → v2；进一步清理；Python 版本提升 |
| **v1.0.0** | 2025-10-20/22 | 从零重写；create_agent() 统一入口；LCEL 唯一标准范式；Middleware 机制；Legacy Chains 彻底淘汰 |

---

## 关键产品线时间线

### LangGraph
- **2023-11**：开源发布，图结构 + 状态哲学
- **2024 全年**：快速迭代，checkpoint、human-in-the-loop、子图支持
- **2025-10**：**v1.0.0** 与 LangChain v1.0 同步发布
- **2026**：LangGraph Cloud / Platform 成为部署首选，LangServe 被归档

### LangSmith
- **2023-08**：内测/beta，LLM 可观测性 + 调试
- **2024~2025**：功能扩展（Playground、Prompt Management、Evaluation）
- **2026**：升级为 framework-agnostic 平台，支持非 LangChain 框架

### LangServe
- **2023-10**：首次发布，基于 FastAPI 的 REST API 部署
- **2024~2025**：持续维护但逐步被 LangGraph 部署方案替代
- **2026-03-10**：**仓库归档（archived）**，被 LangGraph Platform 取代

### DeepAgents
- **2025-11**：开源发布（v0.1~0.3），`create_deep_agent()` 一行创建复杂智能体
- **2026-03**：v0.4.x 引入 Skill 机制
- **2026-05**：v0.4.3 稳定版，三层产品线定位明确

---

## OpenAI API 变化对 LangChain 的影响

| 时间 | OpenAI 变化 | 对 LangChain 的影响 |
|------|------------|-------------------|
| **2023-06** | Function Calling 发布 (gpt-3.5-turbo-0613, gpt-4-0613) | Agent 从 ReAct prompt hack → 结构化工具调用；LangChain Agent API 重大重构 |
| **2023-10** | Fine-tuning 支持 Function Calling | 更精准的结构化输出，减少 token 消耗 |
| **2023-11** | GPT-4 Turbo (128K, JSON Mode) | 长上下文 + 结构化输出，LangChain RAG 管道优化 |
| **2024-03** | GPT-4 Turbo 正式 + Parallel Function Calling | LangChain 支持多工具并行调用 |
| **2024-08** | GPT-4o (多模态 + 强 Function Calling) | LangChain 适配多模态输入，Agent 能力增强 |
| **2024-09** | o1 推理模型 | LangChain 适配推理模型的不同调用模式 |
| **2025-02** | GPT-4.5 / o3 系列 | 持续适配新模型能力 |
| **2025-04** | Responses API / Agents SDK | OpenAI 官方进入 Agent 框架领域，与 LangChain 形成竞争 |

---

## 社区增长关键节点

| 时间 | 指标 | 数据 |
|------|------|------|
| 2022-12 | GitHub Stars | 快速突破 5K |
| 2023-06 | GitHub Stars | ~20K |
| 2023-12 | GitHub Stars | ~50K |
| 2024-12 | GitHub Stars | ~80K+ |
| 2026-06 | GitHub Stars | **90K+** |
| 2026-06 | 月开源下载 | **1 亿+** |
| 2026-06 | 模型/工具集成 | **1000+** |

---

## 主要争议与批评

1. **抽象过度（2024-01 起）**：Octomind 的 Fabian Both 发文《Why We No Longer Use LangChain》，批评 LangChain 抽象层过厚、debug 困难、简单任务反而更复杂。引发社区广泛讨论。
2. **版本迁移痛苦（2024-05~09）**：v0.1→v0.2→v0.3 连续大版本迁移，导入路径变更频繁，社区抱怨升级成本高。
3. **与 OpenAI 竞争（2025-04 起）**：OpenAI 发布 Agents SDK，官方下场做 Agent 框架，与 LangChain 形成直接竞争。
4. **LangServe 归档（2026-03）**：LangServe 仓库被归档，部分用户困惑于部署方案的变更。

---

## 2025-2026 战略方向

1. **Agent 工程化**：从"实验项目"走向"生产系统"，LangChain v1.0 + LangGraph v1.0 是标志性里程碑
2. **三层产品线**：DeepAgents（高层）→ LangChain（中层）→ LangGraph（底层），覆盖从快速原型到深度定制
3. **Long-Horizon Agents**：Harrison Chase 明确 2026 年方向是长程智能体——持久执行、状态管理、人机协作
4. **平台化**：LangSmith 从 LangChain 专属工具升级为框架无关的 Agent 工程平台
5. **Skill 生态**：DeepAgents 引入 Skill 机制，类似插件/扩展系统
6. **与 OpenAI 竞合**：既适配 OpenAI 新模型/SDK，又保持框架独立性

---

*信息源说明：本时间线排除了知乎、微信公众号、百度百科。主要来源包括：LangChain 官方博客、GitHub 仓库记录、TechCrunch、CSDN/博客园/掘金（交叉验证）、腾讯新闻/InfoQ 转载。标注 ⭐⭐⭐⭐⭐ 为多方交叉验证的高可信度信息，⭐⭐⭐ 为单一来源或需要进一步验证的信息。*
