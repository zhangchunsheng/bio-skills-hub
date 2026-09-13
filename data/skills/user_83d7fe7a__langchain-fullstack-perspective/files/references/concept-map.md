# LangChain 生态概念地图

> 学习LangChain最大的痛苦不是API难，而是概念太多、层次太深、版本变迁太快。这张地图帮你建立正确的心理模型。

---

## 概念层级金字塔

```
                    ┌─────────────┐
                    │  DeepAgents  │  ← 一行代码创建复杂Agent（高层封装）
                    └──────┬──────┘
                           │
               ┌───────────┼───────────┐
               │     create_agent()     │  ← v1.0统一Agent入口（中层）
               └───────────┬───────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │              LangGraph              │  ← 图编排，状态机（底层控制）
        └──────────────────┬──────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                   LCEL                    │  ← 管道语法，组件粘合剂（基础设施层）
    └──────────────────────┬──────────────────────┘
                           │
  ┌──────────┬─────────┬───┴───┬──────────┬──────────┐
  │Runnable  │ChatModel│Retriever│Tool     │OutputParser│  ← 原子组件
  └──────────┴─────────┴───────┴──────────┴──────────┘
```

## 5组易混淆概念

| 易混淆概念 | 区别 | 记忆口诀 |
|-----------|------|----------|
| **Chain vs LCEL** | Chain是旧范式的类（如LLMChain），LCEL是管道语法`prompt \| model \| parser` | Chain是对象，LCEL是语法 |
| **Agent vs Graph** | Agent让LLM自己决定下一步，Graph让开发者画好流程图 | Agent=LLM做决策，Graph=你画流程图 |
| **State vs Memory** | State是LangGraph的节点间共享数据，Memory是对话历史 | State=工作流变量，Memory=聊天记录 |
| **Tool vs Skill** | Tool是单个函数（如搜索），Skill是一组能力的集合（DeepAgents概念） | Tool=锤子，Skill=工具箱 |
| **Middleware vs Hook** | Middleware在Agent Loop中拦截修改消息（如压缩、验证），Hook是事件回调 | Middleware=中间人修改，Hook=旁观者记录 |

## 版本生死表

| 概念/API | v0.1 | v0.2 | v0.3 | v1.0 | 状态 |
|---------|------|------|------|------|------|
| `LLMChain` | ✅ | ⚠️deprecated | ❌ | ❌ | **已死**，用LCEL替代 |
| `AgentExecutor` | ✅ | ✅ | ⚠️ | ❌ | **已死**，用`create_agent`或LangGraph替代 |
| `initialize_agent` | ✅ | ⚠️deprecated | ❌ | ❌ | **已死** |
| LCEL管道语法 | 🆕 | ✅ | ✅ | ✅ | **活着**，但降级为底层基础设施 |
| `create_agent()` | - | - | - | 🆕 | **活着**，v1.0统一入口 |
| LangGraph StateGraph | - | - | ✅ | ✅ | **活着**，底层控制首选 |
| DeepAgents | - | - | - | - | **新**，高层封装 |
| `load_qa_chain` | ✅ | ⚠️ | ❌ | ❌ | **已死**，黑箱RAG |
| `from langchain.llms` | ✅ | ⚠️ | ❌ | ❌ | **已死**，用`langchain_openai`等独立包 |
| Callback系统 | ✅ | ✅ | ⚠️ | ❌ | **已死**，被Middleware替代 |

### 导入路径铁律

每次看到`from langchain.xxx`而不是`from langchain_xxx`的导入——立刻警觉这是过时代码。集成类组件一律从独立包导入：

```python
# ❌ 死代码（v0.1时代）
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# ✅ 正确（v0.2+）
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
```

## 学习路径

```
阶段1：基础（1-2周）
├── 理解Runnable接口 → 万物皆Runnable
├── 掌握LCEL管道语法 → prompt | model | parser
├── 学会用ChatModel + PromptTemplate → 最基础的LLM调用
└── 用LangSmith追踪你的第一次调用 → 可观测性从第一天开始
  📚 推荐资源：
  · 官方文档「Introduction - LangChain」：https://python.langchain.com/docs/introduction/
  · DeepLearning.AI「LangChain for LLM Application Development」（官方联合课程）
  · LangChain GitHub examples/ 目录（可直接跑通的最小示例）

阶段2：检索增强（1-2周）
├── Document + TextSplitter → 文档处理
├── Embeddings + VectorStore → 向量存储与检索
├── Retriever接口 → 统一检索抽象
└── 构建一个完整RAG Chain → 检索→重排→生成
  📚 推荐资源：
  · 官方文档「RAG - LangChain」：https://python.langchain.com/docs/tutorials/rag/
  · Pinecone「Building RAG Pipelines」系列教程（实践导向）
  · LlamaIndex vs LangChain对比博客（理解各自边界）

阶段3：Agent（2-3周）
├── Tool定义与绑定 → @tool装饰器 / StructuredTool
├── create_agent() → v1.0统一Agent入口
├── Middleware机制 → 验证、压缩、反馈注入
└── 理解Agent Loop → 思考→行动→观察循环
  📚 推荐资源：
  · 官方博客「Agent Architecture Overview」（v1.0）：https://blog.langchain.dev/
  · LangChain GitHub「agents」目录源码阅读
  · Harrison Chase播客访谈（了解设计动机）

阶段4：图编排（2-3周）
├── StateGraph → 定义状态和节点
├── 条件边与循环 → 复杂工作流
├── Checkpointer → 持久化与人工审核
└── 子图 → 多Agent协作
  📚 推荐资源：
  · LangGraph官方文档：https://langchain-ai.github.io/langgraph/
  · LangGraph GitHub examples/state_graph/ 目录

阶段5：生产化（持续）
├── LangSmith全链路追踪 → 调试与评估
├── Human-in-the-Loop设计 → 安全与可控
├── 错误处理与Fallback → 生产可靠性
└── 渐进式下沉 → 从DeepAgents到LangGraph
  📚 推荐资源：
  · LangSmith文档：https://docs.smith.langchain.com/
  · LangChain Discord #langsmith频道（真实踩坑案例）
  · awesome-langchain GitHub（社区精选资源列表）
```

> 📌 资源说明：以上推荐基于skill内部评估，URL和课程内容可能随官方更新变化，使用前建议核实。

---

## 不适用场景（快速判断）

遇到以下场景，这个skill的参考价值会大幅下降：

| 场景 | 原因 | 建议替代方案 |
|------|------|-------------|
| 纯Python SDK调用（单次LLM调用，无编排） | 这个skill覆盖的是「组合」，不是「单次」 | 直接用 `openai` / `deepseek` SDK，不引入LangChain |
| 非LangChain框架选型 | skill基于LangChain生态，无法客观评估其他框架 | 用LlamaIndex skill、CrewAI skill、OpenAI Agents SDK文档 |
| LangChain源码级别调试 | skill是应用视角，不是源码贡献指南 | LangChain GitHub Issues + Discord #contributing频道 |
| 实时Bug修复（需要立刻出解法） | skill提供的是框架性思维，不是点对点debug | Stack Overflow + LangChain GitHub Issues |
| 最新版本（> v1.0）特性咨询 | 调研截止2026-06-17，v1.0之后的变化未覆盖 | 官方Changelog + LangSmith Release Notes |

---

## 反模式快速入口（Top5高危场景）

遇到以下场景时，优先检查这些问题：

| # | 高危场景 | 必查坑项 | 快速修复 |
|---|---------|---------|---------|
| 1 | Agent停不下来（死循环） | 坑6（无限循环） | 加 `max_iterations=10` |
| 2 | 上线后发现API Key泄露 | 坑2（CVE-2025-68664） | 检查 `dumps()` 是否含环境变量 |
| 3 | 多用户对话互相串 | 坑3（Memory状态泄漏） | 每个会话独立Memory实例 |
| 4 | 代码报错`ImportError` | 坑4（导入路径幽灵） | 改用 `langchain_xxx` 独立包 |
| 5 | FastAPI + LangChain卡死 | 坑7（Streaming同步陷阱） | 改用 `.astream()` |


