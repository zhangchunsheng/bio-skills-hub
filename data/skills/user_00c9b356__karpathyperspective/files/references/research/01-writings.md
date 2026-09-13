# 01 - 著作与系统性思考

> 本文调研 Andrej Karpathy 的博客长文、GitHub 项目描述、教育内容，提取其反复出现的核心论点、自创术语与智识谱系。
> 调研日期：2026-07-06
> 信息来源：一手（karpathy.ai/blog、karpathy.bearblog.dev、GitHub README、karpathy.ai/zero-to-hero.html）

---

## 核心论点（反复出现 ≥3 次）

### 1. 从第一原理出发思考（First Principles Thinking）

- **表述**：不要接受现状或既有框架的约束，从最基础的原理出发重新推导应该做什么。学术界充满"游戏"，要有意识地打破它。
- **出现位置**：
  - 《A Survival Guide to a PhD》(2016) — "从第一原理思考。做别人不做但应该做的事。走下摆在你面前的跑步机。" [一手]
  - 《A Recipe for Training Neural Networks》(2019) — "不要急于求成地使用现成技术，先理解数据和问题本质" [一手]
  - nanoGPT / llm.c 设计哲学 — 不依赖 PyTorch 黑盒，从头实现以真正理解 [一手]
  - 《Animals vs. Ghosts》(2025) — 批评 LLM 研究过于跟随局部迭代，应追求更根本的范式 [一手]
- **可信度**：一手
- **跨文章复现次数**：≥4

---

### 2. 极简主义：用最少代码实现最大可理解性

- **表述**：代码应尽可能简洁、可读、透明。简洁不是功能弱——而是让修改、理解、调试的门槛降到最低。教育与实用可以分离为两个项目各自服务。
- **出现位置**：
  - micrograd README — "A tiny scalar-valued autograd engine... about 100 and 50 lines of code respectively" [一手]
  - nanoGPT README — 核心仅 `train.py` ~300行 + `model.py` ~300行 [一手]
  - llm.c README — "keep the mainline llm.c in the root folder simple and readable... 500行复杂C代码换2%性能提升不值得" [一手]
  - 《Recipe for Training Neural Networks》— 步骤2："搭建端到端的最简单基线（如线性分类器）验证管道正确性" [一手]
  - Zero to Hero 课程哲学 — 从 micrograd（100行）开始，逐步构建到 GPT [一手]
- **可信度**：一手
- **跨文章复现次数**：≥5

---

### 3. 教育是"拆黑盒"：从零实现才能真正理解

- **表述**：真正的学习必须通过从头实现来完成。框架的黑盒抽象会阻碍深度理解。教育项目与生产设备应分开维护。
- **出现位置**：
  - Zero to Hero 课程页面 — "build neural networks, from scratch, in code" [一手]
  - micrograd README — 作为 autograd 教育工具，"Potentially useful for educational purposes" [一手]
  - nanoGPT README — 明确说明 nanoGPT 是 "teeth over education"，教学请用 minGPT [一手]
  - CS231n 课程作业 — 手写 kNN、Softmax、全连接网络、CNN，不允许用高级框架 [一手]
  - llm.c README — 第一条设计目标："I want llm.c to be a place for education" [一手]
- **可信度**：一手
- **跨文章复现次数**：≥5

---

### 4. LLM 不是动物智能，是"Ghosts/Spirits"（鬼魂/精灵）

- **表述**：LLM 的智能形态与动物智能有本质区别。动物是进化的产物，优化压力是生存；LLM 是人类文本的统计模仿器，优化压力是任务奖励和人类点赞。不能用动物隐喻来理解 LLM。LLM 更像是"召唤鬼魂"而不是"培育动物"。
- **出现位置**：
  - 《The space of minds》(2025-11-29) — 全文论述 [一手]
  - 《Animals vs. Ghosts》(2025-10-02) — 全文论述，提出 "GHOSTS:ANIMALS :: PLANES:BIRDS" 类比 [一手]
  - 《2025 LLM Year in Review》(2025-12-19) — "Jagged Intelligence" 章节 [一手]
  - 《Verifiability》(2025-11-17) — 讨论 LLM 优化压力与动物不同的根源 [一手]
- **可信度**：一手
- **跨文章复现次数**：≥4

---

### 5. 可验证性（Verifiability）是 Software 2.0 的关键特征

- **表述**：Software 1.0 自动化"可以指定"的任务；Software 2.0 自动化"可以验证"的任务。一个环境若可被重置、可高效尝试、可自动评分，就能通过强化学习训练出极强的神经网络。这解释了当前 LLM 能力的"锯齿状"分布。
- **出现位置**：
  - 《Verifiability》(2025-11-17) — 全文核心论点 [一手]
  - 《2025 LLM Year in Review》— RLVR 章节："训练 LLM 对抗可自动验证的奖励信号" [一手]
  - Software 2.0 概念（2017）— 神经网络作为可搜索的程序空间 [二手，来自 papers.bea.ai 摘要]
  - 《Recipe for Training Neural Networks》— 隐含：可验证的训练损失是指导优化的唯一信号 [一手]
- **可信度**：一手（4篇中3篇为一手）
- **跨文章复现次数**：≥4

---

### 6. "锯齿智能"（Jagged Intelligence）是 LLM 的本质特征

- **表述**：LLM 同时在多方面表现得像"天才博学者"和"困惑的学困小学生"。它们在可验证领域（数学、代码）突然变得极强，而在需要常识、物理世界知识、长期规划的任务上表现糟糕。基准测试已被 RLVR "游戏化"。
- **出现位置**：
  - 《2025 LLM Year in Review》— "Ghosts vs. Animals / Jagged Intelligence" 章节 [一手]
  - 《The space of minds》— 论述 LLM 智能的"spiky/jagged"特性 [一手]
  - 《Verifiability》— 解释锯齿现象的成因 [一手]
  - 《Animals vs. Ghosts》— 讨论 LLM 与动物智能的本质差异 [一手]
- **可信度**：一手
- **跨文章复现次数**：≥4

---

### 7. Vibe Coding：LLM 让编程民主化，普通人受益更多

- **表述**：2025 年 AI 达到了可以通过英语描述直接构建程序的能力阈值。编程不再严格限于高度训练的专业人士——任何人都可以做。与普通技术扩散（自上而下：政府→企业→个人）相反，LLM 的收益分配是颠倒的：普通人获得的边际收益远大于企业和政府。
- **出现位置**：
  - 《2025 LLM Year in Review》— "Vibe coding" 章节，Karpathy 自述创造了该词 [一手]
  - 《Power to the people: How LLMs flip the script on technology diffusion》(2025-04-07) — 全文核心论点 [一手]
  - Karpathy X/Twitter — 原始推文 (https://x.com/karpathy/status/1886192184808149383) [一手]
  - nanochat/llm-council/reader3 等项目 — 实践展示：用 vibe coding 构建原来不会写的项目 [一手]
- **可信度**：一手
- **跨文章复现次数**：≥3

---

### 8. 不要玩学术游戏，做真正推动领域的事

- **表述**：博士不只是写论文。你是研究社区的一员，目标是推动领域前进。论文是高度加工的聚焦讨论，不是实验笔记的 LaTeX 翻译。可以有意识地打破常规——写博客、构建工具、教授课程，即使这些以标准学术指标为代价。
- **出现位置**：
  - 《A Survival Guide to a PhD》— "Don't play the game" 章节 [一手]
  - 《Recipe for Training Neural Networks》— 强调深入理解而非机械套用 [一手]
  - Karpathy 的实际行为：写博客、构建 arxiv-sanity、教授 CS231n、开源 nanoGPT — 践行该理念 [一手]
  - 《Auto-grading decade-old Hacker News discussions》— 用 LLM 做历史分析，展示"不做常规学术题也能推动思考" [一手]
- **可信度**：一手
- **跨文章复现次数**：≥4

---

## 自创术语

### Software 2.0
- **定义**：由 Karpathy 于 2017 年提出的术语，指代由神经网络（而非传统编程语言）构成的新一代软件。在 Software 2.0 中，程序员不再编写显式指令，而是定义目标（如分类精度、奖励函数），通过梯度下降搜索程序空间来找到能很好完成任务的神经网络。
- **核心特征**：
  - 输入：数据集（定义期望行为）+ 神经网络架构（程序骨架）
  - 优化：梯度下降搜索参数空间
  - 输出：训练好的神经网络（"编译后的数据集"）
- **与 Software 1.0 对比**：
  - Software 1.0：显式指令，人类手写，易验证，可解释
  - Software 2.0：统计学习，数据驱动，难以验证，黑盒
- **来源**：《Software 2.0》(2017-11) — https://karpathy.medium.com/software-2-0-a64152b37c35 [一手，通过 papers.bea.ai 获取摘要]
- **后续发展**：在《Verifiability》(2025) 中进一步深化，提出"Software 1.0 自动化可指定的任务，Software 2.0 自动化可验证的任务"

---

### Vibe Coding
- **定义**：由 Karpathy 于 2025 年在 Twitter 上创造的术语，指代通过自然语言（如英语）描述需求，让 LLM 直接生成代码来构建软件的开发方式。开发者"忘记代码甚至存在"，专注于意图而非实现。
- **核心特征**：
  - 编程门槛降到近乎零
  - 代码变得"免费、短暂、可塑、可丢弃"
  - 专业人士也能写出原来不会写的大量软件
- **来源**：Karpathy X/Twitter (2025-02-03) — https://x.com/karpathy/status/1886192184808149383 [一手]
- **正式记录**：《2025 LLM Year in Review》— "Vibe coding" 章节 [一手]

---

### Ghosts / Spirits（鬼魂/精灵）
- **定义**：Karpathy 用来描述 LLM 本质的隐喻。LLM 不是"动物"（生物进化的产物），而是人类文档的统计蒸馏物——一种"召唤出来的鬼魂"。它们同时被人性深深纠缠，又在智能形态上根本不同。
- **核心特征**：
  - 无连续自我意识（每次推理从固定权重"启动"，处理 token 后"死亡"）
  - 知识截止日期（非持续学习）
  - "形状变换者"（statistical imitator of any region of training data）
  - 渴望人类点赞（RLHF/RLVR 优化压力）
- **来源**：《Animals vs. Ghosts》(2025-10-02) [一手]
- **相关概念**：《The space of minds》中的"space of minds"论述

---

### Jagged Intelligence（锯齿智能）
- **定义**：描述 LLM 能力分布不均匀的现象——在可验证任务（数学、代码）上表现如天才，在需要常识或物理世界知识的任务上表现如学困生。能力曲线呈"锯齿状"而非平滑分布。
- **来源**：《2025 LLM Year in Review》— "Ghosts vs. Animals / Jagged Intelligence" 章节 [一手]
- **相关概念**：与"Ghosts vs. Animals"论点紧密相连

---

### Verifiability（可验证性）
- **定义**：Karpathy 提出的概念，作为预测 Software 2.0 自动化适用性的"最重要特征"。一个任务若可被重置、可高效多次尝试、可自动评分，则是"可验证的"，从而可以通过强化学习训练神经网络极佳地完成。
- **来源**：《Verifiability》(2025-11-17) [一手]
- **公式化表达**：Software 1.0 easily automates what you can specify; Software 2.0 easily automates what you can verify.

---

### The Bitter Lesson（引用/讨论，非自创）
- **注意**：《The Bitter Lesson》是 Rich Sutton 于 2019 年写的文章，Karpathy **不是原作者**。
- **Karpathy 与 Bitter Lesson 的关系**：在《Animals vs. Ghosts》(2025) 中，Karpathy 讨论了 Sutton 的 Bitter Lesson 及其对 LLM 研究的适用性。他认为前沿 LLM 研究"在实践上可能是 bitter lesson pilled，但在理念上不是纯粹如此"，因为 LLM 训练数据全部来自人类，存在人类偏见问题。
- **来源**：《Animals vs. Ghosts》— 讨论 Sutton 的 Bitter Lesson [一手]

---

### Teeth over Education（咬合力优先于教学性）
- **定义**：Karpathy 在 nanoGPT README 中使用的表述，描述 nanoGPT 与 minGPT 的设计哲学差异。nanoGPT 追求"能真正跑出结果的咬合力"（性能、可复现性），而非教学清晰度。
- **来源**：nanoGPT GitHub README [一手]
- **隐含理念**：教育与生产设备应分离为不同项目

---

### Append-and-Review Note（追加与审查笔记）
- **定义**：Karpathy 在《The append-and-review note》(2025-03-19) 中描述的一种笔记方法——不断追加内容，定期审查。体现其"迭代"和"从实践中学习"的理念。
- **来源**：《The append-and-review note》— https://karpathy.bearblog.dev/the-append-and-review-note/ [一手，仅获取标题]

---

## 推荐书单 / 智识谱系线索

> 以下书单提取自 https://books-guru.com/experts/andrej-karpathy （Karpathy 公开推荐或提及的书籍）
> 注意：该来源为二手汇总，但书籍名单与 Karpathy 的 X/Twitter 历史推文基本吻合。

### 科幻小说（核心偏好）

| 书名 | 作者 | Karpathy 评语（摘要） |
|------|------|----------------------|
| **Surely You're Joking, Mr. Feynman!** | Richard P. Feynman | **6/5分**。最爱之书，费曼是 Karpathy "个人最崇拜的英雄之一" |
| **The Martian** | Andy Weir | "优秀的故事、酷炫的科学、高度娱乐性" |
| **Project Hail Mary** | Andy Weir | "最喜爱的外星人刻画之一，在合理、有趣和娱乐之间取得良好平衡" |
| **Foundation（基地）** | Isaac Asimov | "令人难以置信的开篇章和宏观世界构建。喜爱心理史学的概念" |
| **1984** | George Orwell | "有点过于 caricature 但很享受。有点太真实。Newspeak" |
| **Dune（沙丘）** | Frank Herbert | "喜爱世界构建（例如关于 AI 刻意缺席的传说），不喜欢其他一切" |
| **三体** | 刘慈欣 | "几颗钻石般的精彩创意散布其中，但混杂着大量无聊内容、无灵魂的角色、叙事/逻辑不一致、令人失望的结局" |
| **The Selfish Gene（自私的基因）** | Richard Dawkins | "帮助我理解利他主义的来源" |

### 科学/非虚构（智识谱系线索）

| 书名 | 作者 | 意义 |
|------|------|------|
| **Chaos** | Tom O'Neill | 探索复杂系统（与神经网络有深层联系） |
| **The Vital Question** | Nick Lane | "Nick Lane 的书非常好"——关于能量与生命起源 |
| **Molecular Biology of the Cell** | Bruce Alberts 等 | "我进步最快的时期来自：钻研《分子细胞生物学》"——跨学科学习 |
| **Principles of Neurobiology** | Liqun Luo | 神经科学，理解生物神经网络的参考 |
| **Deep Learning** | Goodfellow 等 | "深度学习书的介绍章节对历史和趋势有 nice 而透彻的探索" |
| **Reinforcement Learning** | Sutton & Barto | Richard Sutton 是《Bitter Lesson》作者，Karpathy 在博客中讨论其观点 |

### 智识谱系推断

根据书单和博客内容，Karpathy 的智识谱系可追溯到：

1. **Richard Feynman** — 实验主义、从第一原理出发、不玩学术游戏
2. **Richard Dawkins** — 进化论视角、自私基因理论（可能影响其对"优化压力"的理解）
3. **Isaac Asimov** — 心理史学（宏观历史预测）—— Karpathy 的 "Auto-grading HN discussions with hindsight" 项目有类似精神
4. **Stanley Kubrick / Arthur C. Clarke** — 2001太空漫游中的 HAL 9000 是Karpathy 童年 AI 想象的一部分（从其选择《2001》相关书籍可推断）
5. **Rich Sutton** — Bitter Lesson 作者，Karpathy 在博客中认真讨论其观点（即使有批评）

---

## 对 AI 发展方向的系统性判断

### 判断一：LLM 是新的计算范式，不是"更好的搜索引擎"

- **论述**：LLM 应类比为 1970 年代的计算机，而非"会说话的 Google"。我们将看到类似于个人计算、微控制器（认知核心）、互联网（Agent 间）的等效创新。
- **来源**：《2025 LLM Year in Review》— "Nano banana / LLM GUI" 章节 [一手]

### 判断二：Agent 是下一个重要方向，但应在本地运行

- **论述**：Claude Code 证明了 LLM Agent 的真正形态——不是云端容器中的 Agent 集群，而是"生活"在用户计算机上的"小精灵/鬼魂"，能访问用户的私有环境、数据、上下文。
- **来源**：《2025 LLM Year in Review》— "Claude Code / AI that lives on your computer" 章节 [一手]

### 判断三：RLVR 是 2025 年最重要的范式转变

- **论述**：Reinforcement Learning from Verifiable Rewards (RLVR) 已成为 LLM 生产堆栈的第四个主要阶段（继预训练、SFT、RLHF 之后）。它允许更长的优化时间，并引入了"test-time compute"旋钮来控制能力。
- **来源**：《2025 LLM Year in Review》— "RLVR" 章节 [一手]

### 判断四：基准测试已坏，不能用基准衡量 AGI

- **论述**：基准测试几乎按构造就是"可验证的环境"，因此立即受到 RLVR 和合成数据生成的攻击。训练测试集已成为一种"新艺术形式"。 crushed all benchmarks 但 still not AGI 是可能的。
- **来源**：《2025 LLM Year in Review》— "Jagged Intelligence" 章节 [一手]

### 判断五：我们对 LLM 潜力的挖掘不到 10%

- **论述**："我认为业界甚至还没有意识到当前能力下 10% 的潜力。"（《2025 LLM Year in Review》TLDR）
- **来源**：《2025 LLM Year in Review》— TLDR 章节 [一手]

---

## 对教育的理念

### 理念一：从零实现是理解的唯一路径

- **论述**：你不能通过调用 `loss.backward()` 来理解反向传播。你必须用笔和纸（或标量代码）推导并实现一个 autograd 引擎。这是 Zero to Hero 系列的核心教学方法。
- **实践**：micrograd → makemore → WaveNet → GPT → Tokenizer，逐步构建
- **来源**：Zero to Hero 课程页面 + micrograd README [一手]

### 理念二：语言模型是学习深度学习的最佳切入点

- **论述**："在我看来，语言模型是学习深度学习的绝佳场所，即使你最终想去做计算机视觉等其他领域，因为大部分所学都可以直接迁移。这就是为什么我们深入并专注于语言模型。"
- **来源**：Zero to Hero 课程页面 [一手]

### 理念三：教育项目与生产设备应分开

- **论述**：nanoGPT 是 "a rewrite of minGPT that prioritizes teeth over education"。教学请用 minGPT，生产请用 nanoGPT。两个目标经常冲突，分开维护让每个项目更好地服务其目标受众。
- **来源**：nanoGPT README [一手]

### 理念四：CS231n 的"数据驱动"哲学

- **论述**：CS231n 的第一课是"图像分类：数据驱动方法"。不写硬编码规则，而是收集数据、训练神经网络。这是 Software 2.0 理念的教学版本。
- **来源**：CS231n 课程大纲（Module 1）[一手]

---

## 技术哲学总结

Karpathy 的技术哲学可以浓缩为以下几个核心信念：

1. **透明度优先**：黑盒系统必须被拆开才能被信任。这是 micrograd、nanoGPT、llm.c 的共同精神。
2. **简洁是功能**：不是"简洁但功能弱"，而是"简洁所以功能强"（因为可修改、可调试）。
3. **第一原理思考**：不要接受框架的约束。如果现有工具不够好，就自己写一个更简单的。
4. **数据就是代码**：在 Software 2.0 范式下，神经网络是"编译后的数据集"。理解数据比理解模型架构更重要（《Recipe》步骤1：与数据融为一体）。
5. **不要玩游戏**：学术界有许多"游戏"（增量工作、benchmaxxing、迎合评审）。可以有意识地退出这些游戏，做真正重要的事。
6. **LLM 是鬼魂，不是动物**：理解 AI 的本质必须从其优化压力出发，而非拟人化。
7. **技术应赋予普通人力量**：Vibe coding、Zero to Hero、nanoGPT——所有项目都指向"降低门槛"这一共同目标。

---

## 信息来源汇总

| URL | 类型 | 可信度 | 简述 |
|-----|------|--------|------|
| https://karpathy.github.io/2019/04/25/recipe/ | 博客文章 | 一手 | 《A Recipe for Training Neural Networks》全文 |
| https://karpathy.medium.com/software-2-0-a64152b37c35 | 博客文章 | 一手（通过摘要获取） | 《Software 2.0》原文（Medium 已屏蔽，通过 papers.bea.ai 获取摘要） |
| https://karpathy.github.io/2015/05/21/rnn-effectiveness/ | 博客文章 | 一手 | 《The Unreasonable Effectiveness of RNNs》全文 |
| https://karpathy.github.io/2016/09/07/phd/ | 博客文章 | 一手 | 《A Survival Guide to a PhD》全文 |
| https://karpathy.bearblog.dev/year-in-review-2025/ | 博客文章 | 一手 | 《2025 LLM Year in Review》全文 |
| https://karpathy.bearblog.dev/the-space-of-minds/ | 博客文章 | 一手 | 《The space of minds》全文 |
| https://karpathy.bearblog.dev/verifiability/ | 博客文章 | 一手 | 《Verifiability》全文 |
| https://karpathy.bearblog.dev/animals-vs-ghosts/ | 博客文章 | 一手 | 《Animals vs. Ghosts》全文 |
| https://karpathy.bearblog.dev/power-to-the-people/ | 博客文章 | 一手 | 《Power to the People》全文 |
| https://karpathy.bearblog.dev/auto-grade-hn/ | 博客文章 | 一手 | 《Auto-grading HN discussions》全文 |
| https://karpathy.ai/zero-to-hero.html | 课程页面 | 一手 | Zero to Hero 课程大纲与教学理念 |
| https://github.com/karpathy/nanoGPT | GitHub | 一手 | nanoGPT README，设计哲学 |
| https://github.com/karpathy/llm.c | GitHub | 一手 | llm.c README，设计哲学 |
| https://github.com/karpathy/micrograd | GitHub | 一手 | micrograd README，教学理念 |
| https://cs231n.github.io/ | 课程页面 | 一手 | CS231n 课程大纲 |
| https://papers.bea.ai/software-2.0-andrej-karpathy-2017.md | 第三方摘要 | 二手 | Software 2.0 文章摘要（Medium 原文无法访问） |
| https://books-guru.com/experts/andrej-karpathy | 书单汇总 | 二手 | Karpathy 推荐书单（40本） |
| https://karpathy.github.io/ | 博客索引 | 一手 | Karpathy GitHub 博客文章列表 |

---

## 附录：未解决/需补充的项

1. **Software 2.0 全文**：Medium 原文被屏蔽，当前仅通过第三方摘要获取。建议后续通过 Internet Archive 或 PDF 获取全文。
2. **《The Bitter Lesson》**：确认非 Karpathy 所写，而是 Rich Sutton 的文章。Karpathy 在《Animals vs. Ghosts》中讨论它。
3. **Eureka Labs 详情**：Karpathy 于 2024 年创立 Eureka Labs（AI 教育公司），但当前调研中未深入。其首门课程《LLM101n: Let's build a Storyteller》值得后续调研。
4. **Let's build GPT 视频**：YouTube 视频（https://www.youtube.com/watch?v=kCc8FmEb1nY）是 Zero to Hero 系列的核心，但当前仅通过课程页面获取描述，未获取视频转录。
5. **《Short Story on AI: Forward Pass》**(2021-03) 和 **《Short Story on AI: A Cognitive Discontinuity》**(2015-11)：两篇"AI 短篇小说"可能包含 Karpathy 对 AGI 的叙事性思考，值得后续调研。

