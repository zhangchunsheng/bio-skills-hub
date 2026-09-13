---
name: wellness-routine-planner
description: 当用户想要建立个人养生/健康习惯时间表与自动化提醒系统时，使用此技能。它将想养成的习惯挂在用户既有动作上（锚点制，不靠死钟数），用定时弹窗+对话主动提醒（双层提醒）防遗忘，并生成手机友好的时间表（Markdown+HTML）、配置定时自动化（每日/每周/每月/每半年/每年）、部署到线上 URL 便于手机查看。Use when a user wants to build a personalized wellness routine, habit tracker, or automated health reminders (water, stretch, exercise, skincare, meds, check-ups) without manually setting many alerts.
agent_created: true
---

# 🌿 养生时间表管家 (Wellness Routine Planner)

> 🖼️ Skill 封面图标见 `assets/icon.svg`（绿叶 + 太阳 + 时钟，呼应"自然作息 + 日程提醒"）。

## 概述
本技能帮助用户把"想养成的健康/生活习惯"变成一套**真正执行得到**的系统。核心不是列一张清单，而是：
- 🪝 用**锚点制**把习惯挂在用户本来就做的动作上（起身、吃饭、洗面、冲凉、睡），不靠死钟数；
- 🔔 用**双层提醒**防"一埋头就忘"——定时自动化弹窗 + 在对话里主动口头提醒；
- 📱 产出**手机友好**的时间表（Markdown + 移动端 HTML），并部署到线上 URL，让用户早上不开电脑也能看；
- ⚙️ 把提醒落成**定时自动化**（每日/每周/每月/每半年/每年），系统自动跑，不靠人力记。

> 💬 用用户偏好的语言沟通与输出（如粤语用户用粤语，简中用户用简中）。示例与模板默认简体中文。

## 何时使用
- 用户说"帮我做个每日养生安排 / 作息表 / 健康提醒"
- 用户想系统管理喝水、拉伸、运动、护肤、服药/保健品、冥想、复诊等习惯
- 用户抱怨"总是忘记 XX""作息乱""没条理"
- 用户已有习惯清单，想变成可执行的提醒系统

## 💡 示例触发语句（中英对照）
用户可能会这样开口（也可作为市场上架的示例 prompt）：
- 「帮我做个每日养生安排，我成日唔记得饮水」/ "Help me build a daily wellness routine — I always forget to drink water"
- 「我想系统啲管理食保健品同做运动嘅时间」/ "I want to systematically manage my supplements and workout schedule"
- 「帮我设啲提醒：瞓觉前做护肤、每周做面膜」/ "Set up reminders: skincare before bed, face mask every week"
- 「我有甲亢，唔可以剧烈运动，帮手排个温和啲嘅作息」/ "I have hyperthyroidism, no intense workouts — plan a gentle routine for me"
- 「将我嘅习惯清单变成会自动弹嘅提醒系统」/ "Turn my habit list into an automated reminder system"

## 工作流（6 步）

### 🧭 第 1 步：采集用户画像（对话式，控制提问量）
通过简短提问了解关键项，**先问最重要的一项，逐步细化**，避免一次抛太多问题：
- **现有固定动作（锚点）**：起身、吃饭、洗面、冲凉、睡等——习惯要挂在这些上面
- **想养成的习惯**：运动、喝水、拉伸、护肤、服药/保健品、冥想、复诊等
- **频率**：每日 / 每周（哪几天）/ 每月 / 每半年·每年
- **体力与禁忌**：是否需温和方案（如甲亢忌剧烈出汗）、每段可用时长
- **手机查看需求**：是否早上不开电脑、需 deploy 到 URL

### 🪝 第 2 步：设计锚点制时间表
- 把每个习惯"挂"到最近的锚点动作，写"做完 A 就做 B"，不写死钟点
- 区分**死守项**（晨起 startup、睡前课等必须做）与**弹性项**（可减、可替、不补）
- 给每个时段标注**总时长**（"做几多 + 用几多时间"），降低执行门槛
- 输出结构：每日（晨起链 / 吃饭节奏 / 夜晚 / 睡前链）→ 每周 → 每月 → 每半年·每年

### 🔔 第 3 步：设计双层提醒
- **第一层（定时自动化）**：用 `automation_update` 工具设置，近似钟点弹（如每日 11:15 食保健品、22:00 睡前链）
- **第二层（主动口头提醒）**：对"已内化但仍易忘"的习惯（如工作期间喝水/拉伸），不设这个定时弹，改为**在对话中主动口头提醒**——用户说"得闲"或工作一段后，主动提一句
- 在时间表的"自动提醒一览"列出全部提醒，让用户一目了然

### 📄 第 4 步：生成交付物
- **Markdown 时间表**（如 `养生时间表.md`）：核心原则 + 每日/每周/每月/每半年·每年习惯 + 自动提醒一览
- **移动端 HTML**（如 `养生时间表.html`）：响应式、大字号、分类卡片，便于手机看。基于 `assets/mobile-routine.html` 模板填充内容
- 两份内容保持一致，HTML 是 MD 的手机友好版

### ⚙️ 第 5 步：设置自动化（automation_update）
- 每日类：`scheduleType=recurring` + `rrule=FREQ=DAILY;BYHOUR=11;BYMINUTE=15`
- 每周类：`FREQ=WEEKLY;BYDAY=TU`（指定星期几）
- 每月 / 每两月：`FREQ=MONTHLY;INTERVAL=1 或 2;BYMONTHDAY=1`
- 每半年 / 每年：用 `validFrom/validUntil` 周期，或一次性 + 提前 N 周提醒
- **提前提醒模式**：复诊/剪发/洗牙等，设"提前 2–3 周"的提醒自动化
- 一次性预约：用 `scheduleType=once` + `scheduledAt`（ISO 8601）

### 🌐 第 6 步：部署到线上（如用户手机看）
- 凡用户要"随时手机看"的交付物，优先 deploy 到线上 URL（静态托管），不要只留 local file
- 告知用户 URL 并验证可访问

## 🌟 更多用例示例

### 用例 A · 上班族（易忘喝水 / 拉伸）
**用户**：朝九晚六、一埋头就忘饮水同起身拉伸。
**做法**：锚点挂到"起身""午饭""落班"；双层提醒——午饭弹饮水、落班弹拉伸；HTML 手机版朝早搭车睇。

### 用例 B · 需温和方案者（甲亢 / 孕娠 / 慢病）
**用户**：有健康禁忌，唔可以剧烈运动。
**做法**：默认温和（微汗即收的轻柔运动）；文档注明"以专业意见为准"；复诊/服药用提前提醒。

### 用例 C · 长辈 / 退休（复诊 / 服药提醒）
**用户**：要准时食药、定期覆诊，但唔熟科技。
**做法**：简单时间表 + 大字手机版；每日服药弹、每半年覆诊提前 2–3 周提；由家人协助 deploy。

## 设计原则（必读）
详见 `references/design-principles.md`：锚点制、双层提醒、温和原则、清晰画面的具体做法。

## 示例成品
详见 `references/sample-routine.md`：一份真实时间表长什么样（已脱敏），供参考输出风格与粒度。

## 健康免责声明
本技能仅协助用户**组织作息与习惯提醒**，不构成任何医疗、诊断或治疗建议。涉及用药、疾病管理、运动禁忌等，应咨询专业医生/医师。用户有特殊健康状况时，默认采用温和方案并在文档注明"以专业意见为准"。

## 📦 资源
- `references/design-principles.md` — 锚点制 + 双层提醒方法论
- `references/sample-routine.md` — 脱敏示例时间表
- `references/marketplace-listing.md` — **上架市场用双语描述**（中英文标题/简介/功能/示例/标签），直接 copy 提交
- `assets/mobile-routine.html` — 手机版 HTML 模板（响应式、大字号，填充即用）
- `assets/icon.svg` — Skill 封面图标
