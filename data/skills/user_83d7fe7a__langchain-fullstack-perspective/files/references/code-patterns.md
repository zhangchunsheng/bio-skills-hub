# 代码模式速查：7种范式

> 看到代码就知道是哪个范式，知道该用在哪。

---

## 模式A：LCEL管道（v1.0标准范式）

**用在哪**：简单RAG、文本转换、分类——任何线性流水线。

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

chain = (
    ChatPromptTemplate.from_template("用{style}风格重写: {text}")
    | ChatOpenAI(model="gpt-4o")
    | StrOutputParser()
)
result = chain.invoke({"style": "古文", "text": "今天天气不错"})
```

**交互举例**：
- 用户："我只想做个简单的文本分类，用什么？"
- 回答："LCEL管道就够了。`prompt | model | parser`三步走，不需要Agent也不需要Graph。"

---

## 模式B：RAG链（LCEL组装）

**用在哪**：需要检索增强的问答——但记住，检索质量>生成质量。

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma

# 自己组装，不要用load_qa_chain
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | ChatPromptTemplate.from_template(
        "基于以下上下文回答问题。如果上下文没有答案，说'我不知道'。\n\n上下文: {context}\n问题: {question}"
    )
    | ChatOpenAI(model="gpt-4o")
    | StrOutputParser()
)
result = rag_chain.invoke("什么是Harness？")
```

**交互举例**：
- 用户："为什么我的RAG回答总是在胡说八道？"
- 回答："先别调prompt，先看检索质量。用retriever单独检索看看返回的文档对不对——90%的RAG问题出在检索不在生成。"

---

## 模式C：Tool定义（v1.0标准）

**铁律**：docstring是LLM看到的功能说明，写清楚！

```python
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """搜索网络获取最新信息。输入应该是具体的搜索关键词。"""
    # 你的搜索实现
    return f"搜索结果: {query}"

@tool
def read_file(path: str) -> str:
    """读取本地文件内容。输入是文件的绝对路径。"""
    with open(path, 'r') as f:
        return f.read()

@tool
def calculate(expression: str) -> str:
    """计算数学表达式。输入是合法的数学表达式字符串，如'2+3*4'。"""
    import ast
    return str(ast.literal_eval(expression))
```

**交互举例**：
- 用户："我的Agent总是选错工具，怎么办？"
- 回答："检查你的docstring。LLM选工具全靠docstring理解功能——如果你写的是`def search(q)`配docstring `搜索`，模型根本不知道什么时候该用它。改成`搜索网络获取最新信息，当需要查找实时数据或用户提问涉及最新事件时使用`。"

---

## 模式D：create_agent（v1.0统一入口）

**用在哪**：需要LLM动态选择工具的场景——记住设max_iterations！

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

agent = create_agent(
    model=ChatOpenAI(model="gpt-4o"),
    tools=[search_web, calculate],
    max_iterations=10,        # 必须设上限！防止无限循环
    max_execution_time=60,    # 最多执行60秒
)
result = agent.invoke({"messages": ["123*456等于多少？顺便搜一下这个数字的含义"]})
```

**交互举例**：
- 用户："我该用Agent还是用Chain？"
- 回答："看你的任务需不需要LLM自己决定下一步。如果流程是固定的（检索→生成），用Chain。如果LLM需要根据情况选择不同工具，用Agent。大多数新手会过度使用Agent——能用Chain解决的别上Agent。"

---

## 模式E：LangGraph StateGraph（复杂工作流）

**用在哪**：需要循环、条件分支、状态管理的复杂工作流——Agent做不了的场景。

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]
    next_action: str

def agent_node(state: State):
    # Agent决策逻辑
    return {"messages": ["思考结果"], "next_action": "search"}

def search_node(state: State):
    # 搜索逻辑
    return {"messages": ["搜索结果"], "next_action": "respond"}

def router(state: State) -> str:
    return state["next_action"]

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("search", search_node)
graph.add_conditional_edges("agent", router, {"search": "search", "respond": END})
graph.add_edge("search", "agent")  # 循环回来
graph.set_entry_point("agent")
app = graph.compile()
```

**交互举例**：
- 用户："我的Agent需要在某些步骤暂停等人审核，怎么做？"
- 回答："这就是LangGraph的Checkpointer——见模式F。Agent本身做不到暂停，Graph才行。"

---

## 模式F：Human-in-the-Loop（LangGraph Checkpointer）

**用在哪**：任何需要人工审批的Agent操作——生产环境的标配。

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer, interrupt_before=["approve_node"])

# 执行到approve_node前暂停
config = {"configurable": {"thread_id": "thread-1"}}
result = app.invoke({"messages": ["删除所有临时文件"]}, config)

# 人工审核后继续
app.update_state(config, {"approved": True}, as_node="approve_node")
result = app.invoke(None, config)  # 继续执行
```

**交互举例**：
- 用户："我的Agent要发邮件，但我怕它发错，怎么加审核？"
- 回答："用LangGraph的`interrupt_before`，在发邮件节点前暂停。人工在LangSmith或你的UI里审核通过后，`update_state`继续执行。这不是可选项——发邮件这种不可逆操作必须有人工审核。"

---

## 模式H：国产模型集成（v1.0兼容）

**用在哪**：需要调用国产大模型（DeepSeek/通义千问/Kimi/智谱GLM）的场景。

> ⚠️ 核心原则：LangChain不区分模型来源，通过 `base_url` 指向不同端点即可。

```python
# ✅ DeepSeek（推荐：性价比高，API稳定）
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-xxxx",                    # DeepSeek API Key
    base_url="https://api.deepseek.com",   # DeepSeek官方端点
)

# ✅ 通义千问（阿里云）
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus",
    api_key="sk-xxxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# ✅ Kimi（月之暗面）
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="moonshot-v1-128k",
    api_key="sk-xxxx",
    base_url="https://api.moonshot.cn/v1",
)

# ✅ 智谱GLM（清华智谱）
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="glm-4",
    api_key="sk-xxxx",
    base_url="https://open.bigmodel.cn/api/paas/v4",
)

# ✅ 本地模型（Ollama）
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
)

# ⚠️ 统一集成示例（动态切换模型）
def create_llm(provider: str, api_key: str):
    configs = {
        "deepseek": {"model": "deepseek-chat", "base_url": "https://api.deepseek.com"},
        "qwen":    {"model": "qwen-plus",    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
        "kimi":    {"model": "moonshot-v1-128k", "base_url": "https://api.moonshot.cn/v1"},
        "zhipu":   {"model": "glm-4",          "base_url": "https://open.bigmodel.cn/api/paas/v4"},
    }
    cfg = configs.get(provider)
    if not cfg:
        raise ValueError(f"不支持的provider: {provider}")
    return ChatOpenAI(api_key=api_key, **cfg)
```

**交互举例**：
- 用户："我想用DeepSeek接入LangChain，怎么配？"
- 回答："三步：`pip install langchain-openai`，`from langchain_openai import ChatOpenAI`，然后 `ChatOpenAI(model='deepseek-chat', api_key='sk-xxx', base_url='https://api.deepseek.com')`。LangChain不区分模型来源，关键是 `base_url` 指向正确端点。"

---

## 模式G：Middleware（v1.0新范式）

**用在哪**：需要自动质量验证的Agent——Loop 2的核心实现。

> ⚠️ LangChain v1.0 **没有** `RubricMiddleware`（该 API 不存在）。以下用 LangChain 真实 API 实现等效的输出验证。

```python
from langchain.agents import create_agent
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage

# ✅ 方案1：自定义 RunnableLambda 中间件（推荐）
# 功能：输出被评分，无来源则自动重试
def output_validator(chain_input):
    response = chain_input.get("output", "")
    # 检查是否包含引用标记（如 URL、[]编号、脚注等）
    has_source = any([
        "http" in response.lower(),
        "【" in response, "[" in response and "]" in response,
        "来源：" in response, "Source:" in response
    ])
    if not has_source:
        raise ValueError(
            "OUTPUT_VALIDATION_FAILED: 输出缺少来源引用，"
            "请重新生成并注明信息出处。"
        )
    return chain_input

agent = create_agent(
    model=ChatOpenAI(model="gpt-4o"),
    tools=[search_web, calculate],
    middleware=[],
    max_iterations=10,
)

# ✅ 方案2：PIIMiddleware（LangChain v1.0 真实内置中间件）
# 用于检测输出中的敏感信息并触发人工审核
from langchain.middleware import HumanInTheLoopMiddleware, PIIMiddleware

agent_with_halt = create_agent(
    model=ChatOpenAI(model="gpt-4o"),
    tools=[search_web, calculate],
    middleware=[
        HumanInTheLoopMiddleware(),   # 遇特定关键词暂停，等人工确认
        PIIMiddleware(),              # 检测到 PII 自动中断
    ],
    max_iterations=10,
)
```

**内置 Middleware 速查**（LangChain v1.0 真实 API）：

| Middleware | 用途 | 适用场景 |
|-----------|------|---------|
| `HumanInTheLoopMiddleware` | 关键词触发人工审核 | 不可逆操作（发邮件/删除/支付）|
| `PIIMiddleware` | 检测个人信息 | 涉及用户数据的场景 |
| `ToolRetryMiddleware` | 工具调用失败自动重试 | 网络不稳定环境 |
| `ModelRetryMiddleware` | 模型调用失败自动重试 | API 不稳定场景 |
| `LLMToolSelectorMiddleware` | 动态选择工具 | 减少 Token 消耗 |
| `SummarizationMiddleware` | 自动压缩对话历史 | 长对话节省上下文 |
| 自定义 `RunnableLambda` | 任意验证逻辑 | 输出质量检查、来源验证 |

**⚠️ 安全注意**：Agent 的 API Key 存储和传输是高危区。LangChain v1.0 历史上出现过 [CVE-2025-68664（LangGrinch）密钥泄露漏洞](https://nvd.nist.gov/vuln/detail/CVE-2025-68664)，根因是将 Key 硬编码在 Agent 配置中。
- 正确做法：`os.environ["DEEPSEEK_API_KEY"]` 读取，不要硬编码 `api_key="sk-xxx"`
- 参见 `pitfalls.md → 坑2` 完整防御方案

**交互举例**：
- 用户："我的Agent经常输出没有来源的内容，怎么让它自动检查？"
- 回答："LangChain v1.0 没有 RubricMiddleware，用自定义 RunnableLambda 实现验证逻辑（见方案1）。对于发邮件等不可逆操作，用 HumanInTheLoopMiddleware 暂停等人审核——这是 Loop 2（Verification Loop）的正确实现。"
