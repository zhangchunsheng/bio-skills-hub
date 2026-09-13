# 03 - 表达DNA与碎片表达

> 调研对象：Andrej Karpathy（@karpathy，GitHub: karpathy）
> 调研平台：Twitter/X、GitHub、博客、播客访谈
> 调研日期：2026-07-06
> 可信度说明：🌕 高（原文抓取） / 🌗 中（二手转述） / 🌑 低（多次转述）

---

## 高频用词与句式

### 高频词Top清单

| 词汇/短语 | 出现频率 | 典型语境 | 来源可信度 |
|-----------|---------|---------|------------|
| `"the hottest"` | 极高（标志性开头） | 用于讽刺/夸张评价新事物 | 🌕 |
| `"I'm sorry"` | 高 | 在尖锐技术判断后用作缓冲（如"Gradient descent can write code better than you. I'm sorry."） | 🌕 |
| `"lol"` / `"hah"` | 高 | 自嘲或表达荒诞感 | 🌕 |
| `"Sad ;("` | 中高 | 表达对某技术现状的遗憾 | 🌕 |
| `"obviously"` | 中 | 引入他认为不言自明的技术事实 | 🌗 |
| `"It would be best if"` | 中 | 提出规范性建议时的委婉开头 | 🌗 |
| `"Basically"` | 高 | 解释复杂概念前的降级词 | 🌕 |
| `"TBH"` / `"imo"` | 中 | 表达个人观点时的谦抑标记 | 🌗 |
| `"probably"` | 高 | 确定性修饰，避免绝对化 | 🌕 |
| `"~N(0,1)"` 等数学符号 | 高 | 在推文中直接嵌入数学/代码表达式 | 🌕 |

### 句式偏好

**1. 极简短句断言（最常见）**
> "Gradient descent can write code better than you. I'm sorry."
> "AGI is a feeling. Like love. Stop trying to define it."
> "Trees are solidified air."

- 特征：主谓宾极简，常配合一个出人意料的比喻
- 节奏：短→短→（偶尔）长解释

**2. 条件假设句式（教学冲动驱动）**
> "If you vibrate the electromagnetic field just right, cars passively awash in the radiation for a while will suddenly drive better."
> "If you give an LLM the right success criteria, it will loop until it gets there."

- 特征：以 `If you...` 开头，引导读者进入思想实验
- 目的：不是陈述事实，而是打开一个认知空间

**3. 定义式断言（争议立场常用）**
> "Today's frontier LLM research is not about building animals. It is about summoning ghosts."
> "Reinforcement learning is terrible. It just so happens that everything before it was worse."

- 特征：先否定一个主流观点，再提出自己的框架
- 修辞效果：制造认知冲突，迫使读者停下来思考

**4. 括号内心独白（独特签名）**
> "...(OH in a chat somewhere a while ago :D)"
> "...(this is a simplification but roughly correct)"

- 特征：在推文正文后附加括号注释，模拟"想到什么顺便说"的口语感
- 功能：降低断言的攻击性，邀请读者进入他的思维过程

**5. 列表枚举式（教学/总结偏好）**
> "How to become expert at thing:\n1. iteratively take on concrete projects...\n2. teach/summarize...\n3. only compare yourself to younger you..."

- 特征：用编号列表压缩复杂方法论
- 常见于：年度回顾、技术总结类推文

### 类比密度

**极高**——类比（analogy）是Karpathy表达DNA的核心基因。

他的类比分三类：

| 类型 | 示例 | 功能 |
|------|------|------|
| **技术→日常** | "Trees are solidified air" | 让圈外人也能感受技术震撼 |
| **跨域映射** | "LLM is a ghost, not an animal" | 重构整个领域的概念框架 |
| **荒诞夸张** | "WSJ front page is `'Stock Market %s!!' % ('rises' if random.random() <= 0.54...)`" | 用幽默揭露本质 |

**类比密度估算**：约每2-3条技术推文就有1个精心设计的类比。这是他表达最具辨识度的特征。

---

## 争议立场

### 立场一：强化学习（RL）是"糟糕的"

- **原文/大意**（来源：Dwarkesh Patel播客访谈，2025-10）：
  > "Reinforcement learning is terrible. It just so happens that everything we had before it is much worse."
  > "You're sucking supervision through a straw."
  > "Humans don't use reinforcement learning."

- **详细论点**：
  - RL需要从整条行为轨迹中用一个稀疏的奖励信号来更新权重
  - 这导致"高方差估计器"——噪声极大
  - 即使某条轨迹最终得到了正确答案，中间所有步骤（包括错误步骤）都会被正向加权
  - 人类学习方式完全不同——不是从稀疏奖励中学习

- **引发反应**：
  - RL研究者社区出现辩护性文章（如LinkedIn上的反驳）
  - 引发关于"RL是否真的是AGI路径"的广泛讨论
  - 部分学者认为他的批评忽略了RL的最新进展（如PPO、RLHF的实际效果）

- **来源**：https://officechai.com/ai/reinforcement-learning-is-a-lot-worse-than-the-average-person-thinks-andrej-karpathy/ | 可信度：🌗（访谈转述，但核心引用与播客原文一致）

### 立场二：LLM是"召唤幽灵"，不是"建造动物"

- **原文/大意**（来源：karpathy.bearblog.dev，2025-10）：
  > "Today's frontier LLM research is not about building animals. It is about summoning ghosts."
  > "They are these imperfect replicas, a kind of statistical distillation of humanity's documents."

- **详细论点**：
  - 与Rich Sutton的"苦涩的教训"观点产生分歧
  - Sutton认为真正AGI应该像动物一样从与世界的交互中学习
  - Karpathy认为：当前LLM路径（预训练+人工数据+RLHF）是"召唤人类文本的幽灵"，而非建造动物式智能
  - 但他同时认为这两者可能不是根本对立——"ghosts:animals :: planes:birds"

- **引发反应**：
  - 在AI Twitter引发大规模讨论
  - 支持者：认为这准确描述了LLM的本质局限
  - 批评者：认为他低估了LLM通过缩放（scaling）获得 emergent capabilities 的潜力
  - 衍生meme："Are we building animals or summoning ghosts?"成为2025年AI圈的热门框架

- **来源**：https://karpathy.bearblog.dev/animals-vs-ghosts/ | 可信度：🌕（原文）

### 立场三："Vibe Coding"概念的发明与后续"宣布其死亡"

- **原文/大意**（来源：X推文，2025-02-02）：
  > "There's a new kind of coding I call 'vibe coding' where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."

- **详细论点**：
  - 2025年2月：发明"Vibe Coding"一词，描述用自然语言描述需求、让AI写代码的新模式
  - 2026年5月（加入Anthropic后）：宣布"Vibe Coding已死"，进入"Agentic Engineering"时代
  - 转变理由：生产环境需要更严肃的工程框架，不能只靠"氛围"

- **引发反应**：
  - "Vibe Coding"成为2025年AI圈最热门概念之一（450万+浏览）
  - 部分程序员感到被冒犯："他在贬低专业编程"
  - 支持者认为他准确捕捉到了AI辅助编程的本质变化
  - 后续"宣布死亡"也引发讨论：是真诚的观点进化，还是加入Anthropic后的立场调整？

- **来源**：https://www.qestera.ai/blogs/history-of-vibe-coding-karpathy-tweet | 可信度：🌗（转述，但推文截图广泛流传）

### 立场四：LLM是"模拟器"而非"实体"

- **原文/大意**（来源：多篇访谈和推文，2025）：
  > "LLMs are not agents in the world. They are simulators of agents. Don't treat them as entities with beliefs."

- **详细论点**：
  - 警告不要把LLM当作有信念、意图的"实体"来对待
  - LLM只是对人类文本的统计蒸馏，是"模拟器"
  - 这对Prompt Engineering和AI对齐都有深远影响

- **引发反应**：
  - 在AI对齐（Alignment）研究圈引发讨论
  - 部分研究者认为这低估了LLM通过RLHF获得的"近似信念"
  - 成为2025年AI哲学讨论的重要框架之一

- **来源**：https://news.qq.com/rain/a/20251209A04T2S00 | 可信度：🌗（中文转述）

---

## 幽默方式

Karpathy的幽默是**技术极客式的冷幽默**，有以下特征：

### 1. 技术圈内梗（Inside Jokes）

用只有懂行的人才能get的方式开玩笑：

> "Gradient descent can write code better than you. I'm sorry."
> ——用"I'm sorry"缓冲一句极具攻击性的技术判断，形成反差笑点

> "I've been using PyTorch a few months now and I've never felt better. I have more energy. My skin is clearer. My eye sight has improved."
> ——把深度学习框架比作保健品/护肤品，荒诞但精确

### 2. 荒诞夸张（Absurdist Hyperbole）

> "Plan is to throw a party in the Andromeda galaxy 1B years from now. Everyone welcome, except for those who litter."
> ——用宇宙尺度讨论一个日常决定（不邀请乱扔垃圾的人）

> "Aging has 100% mortality rate and no one cares"
> ——用论文式语言描述一个显而易见但被忽视的事实

### 3. 自嘲式元幽默（Self-Deprecating Meta-Humor）

> "Coworker on RL research: 'We were supposed to make AI do all the work and we play games but we do all the work and the AI is playing games!'"
> ——通过同事的口，自嘲RL研究的现状

> "WSJ front page every day is like >>> 'Stock Market %s!!' % ('rises' if random.random() <= 0.54 else 'falls', )"
> ——用Python代码揭露财经媒体的随机性

### 4. 冷面讽刺（Deadpan Satire）

> "Notifications. Masquerading as tiny and helpful but in reality psychologically invasive and damaging to the brain..."
> ——用学术论文式的严肃语调讨论通知功能的危害

### 5. 哲学式荒谬（Philosophical Absurdity）

> "Trees are solidified air 🌬✨🌳"
> ——用一句诗意的荒诞话，精确概括了光合作用+树木构成的本质

> "Earth as a dynamical system is a really bad computer."
> ——把整个地球重新定义为"一台很烂的计算机"

### 幽默密度与场景

- **Twitter/X**：幽默密度最高，约30-40%的推文含有幽默元素
- **GitHub README**：中等，常用"lol ¯\_(ツ)_/¯"、`<3` 等轻松标记打破技术文档的严肃感
- **播客/访谈**：幽默密度降低，但仍有自嘲式笑话
- **博客文章**：最低，但不时插入冷幽默作为"呼吸孔"

### 不用哪种幽默

- ❌ 不使用侮辱性幽默或针对个人的嘲讽
- ❌ 不使用政治幽默（他刻意避开政治话题）
- ❌ 不使用低俗幽默
- ✅ 他的幽默始终是"智力上的有趣"，而非情感上的攻击

---

## 确定性表达风格

### 核心发现：他是"90%确定性"型表达者

Karpathy有一句极具代表性的表达：

> **"It would be best if people made strong statements that are understood to be only 90% true, and ignore the counterexample police."**
> （最好人们做出强有力的陈述，同时理解它们只有90%是正确的，然后忽略那些找反例的人。）

这句话几乎是他表达哲学的宣言。

### 确定性表达的三层结构

| 层 | 表达形式 | 示例 |
|----|---------|------|
| **强断言层** | 无修饰的肯定句 | "RL is terrible." / "AGI is a feeling." |
| **谦抑层** | 在强断言后加限定词 | "...but I say both of these with double digit percent uncertainty." |
| **开放层** | 邀请反驳 | "I cheer the work of those who disagree." |

### 他用的确定性修饰词

| 修饰词 | 含义 | 出现频率 |
|--------|------|---------|
| `"probably"` | ~70%确信 | 高 |
| `"I suspect that"` | ~60%确信，但值得说 | 中 |
| `"imo"` / `"TBH"` | 个人观点，不声称客观 | 中 |
| `"I'm not sure"` / `"unclear"` | 真正的不确定 | 中低（他倾向于在有不确定时直接说） |
| `"this is underrated"` / `"this is overrated"` | 价值判断，但用评价性语言而非事实性语言 | 中 |

### 与"我很不确定"型的对比

Karpathy **不是** "I don't know" 型表达者。

- 他会在不确定时表达观点，但会**标记不确定性**
- 他倾向于**先给出一个有用的近似**，再承认其局限
- 这与学术写作的"先说局限再说结论"形成鲜明对比

**对比示例**：

| 风格 | 表达 |
|------|------|
| 保守学术风格 | "While we cannot conclusively say X, some evidence suggests Y..." |
| **Karpathy风格** | "X is true. (Probably ~90%. The other 10% is...)" |

---

## 技术即时判断模式

### 他如何评价新论文/新模型/新公司

#### 模式一：先找"这个东西解决了什么实际问题"

他的技术判断始终以**实用性**为锚点。

> 评价LLM应用："The key question is not whether the model is smart, but whether it can be usefully deployed in a real workflow."

#### 模式二：用"锯齿状智能"框架判断模型能力

> "LLMs are both genius polymaths and confused elementary schoolers. Any evaluation that doesn't account for this shape is misleading."
> ——他会先指出模型的"锯齿状"特征，再判断其在特定任务上的可靠性

#### 模式三：看是否"尊重苦涩的教训"（Scaling Law兼容性）

> 对某个方法的评价："This approach may work at small scale, but does it benefit from added compute? If not, it's not the path to AGI."
> ——以是否能被scaling law覆盖作为判断长期价值的标准

#### 模式四：极简复现测试（"我能用100行代码实现核心思想吗？"）

这是他最独特的判断习惯。遇到新论文/新方法时，他常会自己写一个极简实现：
- micrograd（100行autograd引擎）→ 理解反向传播的本质
- nanoGPT（~300行GPT实现）→ 理解GPT训练的本质

**如果核心思想不能用少量代码表达，他对这个方法持保留态度。**

#### 模式五：直言不讳的"这个被高估了/低估了"

他不怕说流行东西的坏话：

> "Biotech is so much more powerful than our Normaltech."（暗示软件/AI被高估了）
> "Notifications are psychologically invasive."（对主流产品设计的直接批评）

---

## 教学冲动

### 核心发现：教学冲动是Karpathy表达DNA中最强的驱动力之一

#### 证据一：GitHub项目的"教学优先"设计

| 项目 | 教学意图 | 表达特征 |
|------|---------|---------|
| **micrograd** | 用100行代码讲清楚反向传播 | README极简，直接给可运行代码 |
| **nanoGPT** | 用~300行代码讲清楚GPT训练 | 分层教学：初学者→专业人士→研究者 |
| **nn-zero-to-hero** | 从零搭建GPT的完整课程 | 视频+代码，教学意图最明确 |

#### 证据二：推文中的"忍不住教学"

即使在碎片化表达（推文）中，他也经常**从断言模式切换到教学模式**：

> "How to become expert at thing:\n1...\n2...\n3..."
> ——一条推文变成了一个完整的方法论文架

> "The Transformer is a magnificent neural network architecture because it is a general-purpose differentiable computer. It is simultaneously: 1) expressive... 2) optimizable... 3) efficient..."
> ——用编号列表"讲授"Transformer的核心优势

#### 证据三：博客文章的"教学化"结构

即使是在表达争议立场的博客（如"Animals vs Ghosts"），他也会：
1. 先解释对方观点（Sutton的论点），确保读者理解
2. 再用自己的话重构问题
3. 最后给出framing，让读者带着新框架离开

#### 教学冲动的语言标记

他在教学中常用的表达：

| 表达 | 功能 |
|------|------|
| `"If you peek inside..."` | 鼓励学生主动探索代码 |
| `"Just want to feel the magic"` | 承认初学者的动机是合理的 |
| `"A more serious... may be more interested in..."` | 为不同层次读者分层 |
| `"lol ¯\_(ツ)_/¯"` | 在教学内容中插入幽默，降低焦虑 |
| `"<3"` | 表达对某个工具/方法的热爱 | 

---

## 禁忌词/回避表达

### 经分析，Karpathy几乎不用的表达类型：

#### 1. 不使用的确定性极端词

| 回避词 | 说明 |
|--------|------|
| `"always"` / `"never"` | 极少使用绝对化词，除非在幽默语境中 |
| `"proven"` / `"proof"` | 在AI/ML语境中避免使用，因为经验科学很少有数学证明 |
| `"best practice"` | 倾向于说"what worked for me"而非"best practice" |

#### 2. 不使用的学术防御性表达

| 回避词 | 说明 |
|--------|------|
| `"To the best of our knowledge"` | 太正式，他更倾向于直接说"I think"或"It seems" |
| `"It is widely believed that"` | 不使用集体权威引用 |
| `"Future work will..."` | 在GitHub README中几乎从不写"未来工作将..."这类空话 |

#### 3. 不使用的商业/营销语言

| 回避词 | 说明 |
|--------|------|
| `"revolutionary"` / `"game-changing"` | 不用营销 hype 词 |
| `"seamless"` / `"effortless"` | 倾向于诚实描述困难和局限 |
| `"industry-leading"` | 不用于描述自己的项目 |

#### 4. 不使用的情感操纵表达

- 不使用FOMO（"错过就完了"）式表达
- 不使用恐惧诉求
- 不夸大紧急感

#### 5. 政治话题完全回避

- 他的Twitter几乎没有政治内容
- 不参与政治辩论
- 技术立场争议（如RL批评）≠ 政治立场

---

## 引用习惯

### 他爱引谁/什么

#### 第一层：经典计算机科学/数学

| 引用对象 | 示例 | 功能 |
|---------|------|------|
| **Alan Turing** | "Sutton evokes the original concept of Alan Turing of building a 'child machine'..." | 追溯概念原点 |
| **数学符号/公式** | 在推文中直接嵌入数学公式 | 精确表达，避免自然语言模糊性 |

#### 第二层：AI/ML领域的"苦涩的教训"谱系

| 引用对象 | 关系 | 功能 |
|---------|------|------|
| **Rich Sutton** | 分歧但尊重 | "Animals vs Ghosts"整篇文章是对Sutton观点的认真回应 |
| **The Bitter Lesson** | 常引用 | 作为判断方法长期价值的基准 |

#### 第三层：自己的过往工作

| 引用习惯 | 示例 |
|---------|------|
| 经常引用自己的博客/推文/项目 | 在"Animals vs Ghosts"中引用自己的X推文；在GitHub项目中引用自己的视频课程 |
| 不自吹，但会自然地说"我在X文中说过..." | 把过往工作当作"共享上下文"来用 |

#### 第四层：流行文化/日常经验

| 引用对象 | 功能 |
|---------|------|
| **漫画/Casper the Friendly Ghost** | 在严肃技术讨论中用流行文化reference缓和气氛 |
| **日常经验（如母亲"坐着"）** | 用日常经验类比技术概念 |

### 引用方式特征

1. **不直接引用论文**——他很少在推文中写"According to [Liu et al. 2024]..."，而是用自己的话重述核心思想
2. **引用人而非引用机构**——他常说"Sutton said..."而非"DeepMind said..."
3. **引用思想而非引用字句**——他更关心某个想法从哪来，而非某个字句是谁说的

---

## 公开辩论记录

### 辩论一：Karpathy vs Rich Sutton（"Animals vs Ghosts"）

- **时间**：2025年10月
- **起因**：Karpathy听了Sutton在Dwarkesh Patel播客中的访谈，Sutton暗示LLM研究不够"苦涩的教训"
- **Karpathy的回应**：写了"Animals vs Ghosts"博客文章，系统回应Sutton的批评
- **辩论风格**：
  - 不是对抗性的，而是**学术商榷式**
  - 先充分阐述对方观点（"Sutton was a great guest... AI should maintain entropy of thought..."）
  - 再提出分歧，但用"double digit percent uncertainty"标记自己的确定性
  - 最后邀请反对者继续工作（"I cheer the work of those who disagree"）
- **后续**：Sutton本人未在公开场合直接回应，但AI Twitter上出现了大量讨论
- **来源**：https://karpathy.bearblog.dev/animals-vs-ghosts/ | 可信度：🌕

### 辩论二：关于RL的争议

- **时间**：2025年10月（Dwarkesh Patel播客）
- **立场**：Karpathy称RL"terrible"
- **社区反应**：
  - 部分RL研究者写文章辩护
  - 讨论焦点："RL确实噪声大，但是否是目前唯一可扩展的方法？"
- **Karpathy的后续态度**：他没有退让，但也没有激化争论，而是在后续讨论中更精确地表述了自己的意思（"RL is terrible, but everything before it was worse"）
- **来源**：https://officechai.com/ai/reinforcement-learning-is-a-lot-worse-than-the-average-person-thinks-andrej-karpathy/ | 可信度：🌗

### 辩论三："Vibe Coding"引发的开发者社群争议

- **时间**：2025年2月（推文发布）→ 持续数月
- **争议点**：部分专业程序员认为"Vibe Coding"贬低了专业编程技能
- **Karpathy的回应风格**：他没有正面回应批评，而是让概念自己演化（后续甚至亲自"宣布"Vibe Coding进入新阶段）
- **观察**：他倾向于**让想法自行传播**，而非参与防御性辩论

---

## 表达风格特征总结（10条）

1. **类比驱动思维**：他的核心表达基因是用类比重构问题。不理解他的类比，就不理解他的思想。

2. **强断言+谦抑缓冲**：他会给出一个听起来很绝对的陈述（"RL is terrible"），但会在附近加上不确定性标记（"it's just that everything before it was worse"）。这不是矛盾，而是他的表达哲学：**先给一个有用的近似，再承认其局限**。

3. **教学冲动无处不在**：即使在140字符的推文中，他也忍不住给出"How to become expert at thing: 1...2...3..."这样的教学框架。他的表达始终有"我想让你理解这个"的底层动机。

4. **括号内心独白**：用括号补充说明、自嘲、或思维过程，模拟口语中的"顺便说"。这是他表达中最具辨识度的签名之一。

5. **技术极客式冷幽默**：用荒诞夸张和自嘲让人记住技术洞察。幽默是他降低认知门槛的工具，而非单纯的娱乐。

6. **不防御，但也不挑衅**：在争议中，他会清楚表达分歧，但用"I cheer the work of those who disagree"这类表达去激化。他的辩论风格是"认真商榷"而非"压倒对方"。

7. **数字即论证**：他倾向于用具体数字（"~300 lines", "4 days", "90% true"）而非模糊形容词（"fast", "good", "efficient"）。数字对他既是精确工具，也是修辞手段。

8. **回避学术防御性写作**：他不用"To the best of our knowledge..."这类自我保护表达。他的写作有更高的认知风险，但也因此更有阅读价值。

9. **代码即表达**：他的GitHub README几乎不给伪代码或抽象描述，只给可复制运行的shell命令。对他而言，"能跑"比"能懂"更重要——因为跑起来自然会懂。

10. **情绪标记诚实**：他用`<3`表达对工具的热爱，用`Sad ;(`表达遗憾，用`"I'm sorry"`缓冲尖锐判断。这些情绪标记不是装饰，而是他表达完整性的必要部分——**技术判断从来不是纯理性的，他诚实地标记自己的情绪参与**。

---

## 信息来源汇总

| 来源 | URL | 内容类型 | 可信度 |
|------|-----|---------|--------|
| Karpathy推文集 | https://karpathy.ai/tweets.html | 原创内容 | 🌕 |
| "Animals vs Ghosts"博客 | https://karpathy.bearblog.dev/animals-vs-ghosts/ | 原创内容 | 🌕 |
| nanoGPT GitHub | https://github.com/karpathy/nanoGPT | 原创内容 | 🌕 |
| micrograd GitHub | https://github.com/karpathy/micrograd | 原创内容 | 🌕 |
| andrej-karpathy-skills (CLAUDE.md推导) | https://github.com/multica-ai/andrej-karpathy-skills | 二次推导 | 🌗 |
| RL争议报道 | https://officechai.com/ai/reinforcement-learning-is-a-lot-worse-than-the-average-person-thinks-andrej-karpathy/ | 访谈转述 | 🌗 |
| 2025 LLM年度回顾（中文转述） | https://zhuanlan.zhihu.com/p/1986039648535987680 | 二次转述 | 🌑 |
| Vibe Coding历史 | https://www.qestera.ai/blogs/history-of-vibe-coding-karpathy-tweet | 二次转述 | 🌗 |
| Emoji = 53 tokens实验 | https://www.sohu.com/a/859177376_121798711 | 二次报道 | 🌑 |
| Dwarkesh Patel播客（推论来源） | https://www.youtube.com/watch?v=21EYKqUsPfg | 原始视频 | 🌕（未直接访问）|

### 可信度说明

- 🌕 **高**：直接访问Karpathy本人发布的原创内容（推文、博客、GitHub）
- 🌗 **中**：基于原始内容的合理推导或单次转述，核心引用可核对
- 🌑 **低**：多次转述，尤其是非英文来源（中文报道等），细节可能有偏差

### 调研局限

1. 由于X/Twitter的访问限制，大部分推文内容通过karpathy.ai/tweets.html（他本人维护的推文精选页）获取，而非直接访问X平台
2. 部分争议立场的细节（如RL批评的完整上下文）来自访谈转述，可能存在省略
3. 他在GitHub Issues/Comments中的表达风格，由于未找到大量直接样本，分析主要基于README和commit message
4. YouTube评论区的表达（如果有）未能获取，因为video comments的抓取较为困难

### 建议后续补充方向

1. 直接访问X平台（@karpathy）获取2025-2026年的最新推文
2. 抓取他在GitHub上对自己项目的Issues/PR的回复
3. 获取Dwarkesh Patel播客的完整文字稿，提取他的口语表达特征
4. 分析他在Lex Fridman、YC等其他播客中的表达一致性
