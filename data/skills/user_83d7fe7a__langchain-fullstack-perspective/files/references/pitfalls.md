# 踩坑手册：这些坑我替你踩过了

> LangChain的坑分两种：一种是文档写了但你没看，另一种是文档根本没写。这里主要记录第二种。

---

## 🔴 致命坑（会导致生产事故）

### 坑1：langchain-experimental的安全黑洞

`langchain-experimental`包不参与漏洞赏金计划，里面有些工具直接exec()用户输入。

**具体案例**：`PythonREPL`和`PythonAstREPLTool`会将用户输入直接当作Python代码执行——如果你的Agent把用户输入传给了这些工具，攻击者可以通过对话执行任意系统命令。

```python
# ❌ 危险：用户输入直接执行
from langchain_experimental.tools import PythonREPLTool
tool = PythonREPLTool()  # 不参与漏洞赏金，安全无保障

# ✅ 安全：沙箱执行
from langchain_experimental.utilities import PythonREPL
# 如果必须用，至少在Docker容器里跑，限制网络和文件访问
```

**行动**：安全审查时直接把`langchain-experimental`排除在依赖列表之外。

### 坑2：CVE-2025-68664（LangGrinch）——密钥泄露

`dumps()`/`dumpd()`会序列化整个对象图，包括环境变量中的API Key。

**具体场景**：你在用LangGraph的`dumps()`做状态持久化（比如存到数据库），序列化结果里包含了你环境变量中的OPENAI_API_KEY、ANTHROPIC_API_KEY等。如果你的日志系统记录了这些序列化结果，或者你的数据库访问控制不够严格——密钥就泄露了。

```python
# ❌ 危险：序列化可能包含环境变量
from langgraph.serde import dumps
state_json = dumps(graph_state)  # 可能包含API keys

# ✅ 修复：升级到langchain-core补丁版本，且不要将dumps结果写入日志
```

**影响范围**：langchain-core 8亿次下载的攻击面。

### 坑3：旧版Memory模块的状态泄漏

`ConversationBufferMemory`、`ConversationSummaryMemory`在v0.x时代是Agent的标配，但它们会在多用户场景下互相污染状态。

**具体场景**：你的Web服务用了全局的Memory实例，用户A的对话历史出现在用户B的上下文里。这不是假设——这是真实的生产事故。

```python
# ❌ 危险：共享Memory实例
memory = ConversationBufferMemory()  # 全局实例
# 用户A和用户B的对话互相可见

# ✅ 安全：每个会话独立Memory
def get_agent(session_id: str):
    memory = ConversationBufferMemory()  # 每次新建
    return agent  # 绑定到独立会话
```

---

## 🟡 恶心坑（不会出事但极其浪费时间）

### 坑4：导入路径的幽灵

**症状**：代码跑不起来，报`ImportError`，但你Google搜到的教程说就是这么写的。

**根因**：LangChain从v0.1到v0.2，大量导入路径变了，但Google搜索排名前三的教程还是旧写法。

**铁律**：看到`from langchain.xxx`（不是`from langchain_core.xxx`）的导入，立刻警觉这是过时代码。集成类组件一律从独立包导入。

```python
# ❌ 这些全部已死
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma

# ✅ 正确
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
```

### 坑5：LCEL的隐式类型转换

**症状**：`prompt | model | parser`报错，但错误信息极其难懂，看不出哪一步出了问题。

**根因**：ChatPromptTemplate输出ChatMessages，但你用了StrOutputParser期望字符串——LCEL不会提前告诉你类型不匹配。

```python
# ❌ 类型不匹配，报错信息晦涩
chain = prompt | model | StrOutputParser()  # 如果prompt输出类型和parser期望类型不一致

# ✅ 显式类型转换
from langchain_core.runnables import RunnablePassthrough
chain = prompt | model | StrOutputParser()  # 确保每一步的输出类型和下一步的输入类型匹配

# 调试技巧：分步调试
result1 = prompt.invoke({"text": "hello"})  # 看类型
result2 = model.invoke(result1)              # 看类型
result3 = parser.invoke(result2)             # 定位问题
```

### 坑6：Agent的无限循环

**症状**：Agent不停调用工具但永远不完成任务，API费用飙升。

**根因**：Agent Loop没有设置上限。模型会陷入"观察→思考→行动→观察"的死循环，尤其ReAct模式。

```python
# ❌ 没有安全网
agent = create_agent(model=model, tools=tools)

# ✅ 必须设上限
agent = create_agent(
    model=model,
    tools=tools,
    max_iterations=10,        # 最多循环10次
    max_execution_time=60,    # 最多执行60秒
)
```

### 坑7：Streaming的同步/异步陷阱

**症状**：FastAPI中用`.stream()`导致整个服务卡住。

**根因**：同步`.stream()`是阻塞迭代器，在异步框架中会阻塞事件循环。

```python
# ❌ 在FastAPI中用同步stream
for chunk in chain.stream({"text": "hello"}):
    yield chunk  # 阻塞事件循环！

# ✅ 在异步框架中必须用astream
async for chunk in chain.astream({"text": "hello"}):
    yield chunk  # 非阻塞
```

### 坑8：Callback → Middleware迁移

**症状**：你在v0.x代码中用了Callback，升级到v1.0后发现行为不一致。

**根因**：v1.0中Callback系统被Middleware替代。Callback的嵌套执行顺序（on_llm_start → on_chain_start → ... → on_chain_end → on_llm_end）容易搞混，Middleware更直观。

```python
# ❌ 旧范式（v0.x）
class MyCallback(BaseCallbackHandler):
    def on_llm_start(self, ...): pass
    def on_chain_end(self, ...): pass

# ✅ 新范式（v1.0）
from langchain.middleware import RubricMiddleware
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[RubricMiddleware(rubric="输出必须包含来源", max_retries=3)]
)
```

---

## 🟢 新手坑（每个初学者都会掉）

### 坑9："五行代码做RAG"的幻觉

教程里`load_qa_chain`五分钟跑通，但生产RAG要考虑：分块策略、重叠窗口、检索质量、重排、混合检索、元数据过滤……

**清醒认知**：五分钟能跑的RAG demo，生产级需要至少两周打磨检索质量。Demo和生产的差距是LangChain最大的幻觉。

### 坑10：过度依赖高层封装

`RetrievalQA`、`VectorDBQA`——这些高层链看起来方便，但出问题时你完全不知道内部发生了什么。v0.2后这些都被标记deprecated，v1.0彻底移除。

**正确姿势**：用LCEL自己组装`retriever | prompt | model | parser`，每一步你都看得见。

### 坑11：忽略Token计数

LangChain不会自动告诉你一次调用花了多少token——直到你收到API账单。

**从第一天起**就接入LangSmith或自己写Callback统计token，不要等到账单爆炸。
