---
name: cue-pharma-regulatory-monitor
slug: cue-pharma-regulatory-monitor
version: 1.0.0
displayName: 医药跨境合规全球监管动向与营销
description: >
  定向监测中国（商务部/网信办/科技部/药监局）及海外（BIS/FDA/欧盟委员会/EDPB）的医药跨境合规监管异动，自动过滤无约束力的媒体猜测，将法规增量翻译为药企 CEO 能读懂的商业后果，并生成合伙人可直接分发的 Client Alert + 朋友圈话术。搭配 BD 战略提案或政务资助挖掘形成获客闭环。
  Monitor pharma cross-border regulatory changes (China & global), filter binding actions from noise, translate legal updates into business-impact analysis, auto-generate Client Alert drafts and partner-ready social copy.
  触发 Triggers: 医药合规、监管动向、跨境合规、Client Alert / pharma regulatory monitor, cross-border compliance, thought leadership
license: MIT
metadata:
  source: cuecue.cn/playbook
  scene: "涉外法律"
  generated_from: /api/playbook
---

# Cue「医药跨境合规全球监管动向与营销」研究 skill

[Cue](https://cuecue.cn) 是一个深度调研 Agent，接入 Congress.gov、Federal Register、商务部/网信办/药监局公告、SEC EDGAR 等 300+ 公开数据源，多源交叉验证，每条结论悬挂原始法案编号或公告链接。

加载本 skill 后，你可以用 Cue 跑医药跨境合规监管动向的持续监测与营销内容生产。

## 能做什么

- **识别真正有约束力的增量信息**：在海量信息中筛掉纯学术讨论和无证据的媒体猜测，只保留有法律约束力的变动——新法案修订、制裁名单更新、行业指导原则、重大行政处罚、征求意见稿。自动区分"正式文本（Act/Regulation）"和"草案（Bill/Draft）"，避免把讨论当结论发给客户。
- **把法条翻译成商业后果**：不堆砌法律术语。每条法规变动映射到具体商业场景——CXO 供应链是否受影响？License-out 里程碑付款会不会中断？NewCo 架构需不需要调整？用药企 CEO/CBO 关心的语言写，不是写给法务看的 memo。
- **自动生成可分发的营销物料**：产出包括——微信公众号 Client Alert 初稿（含 3 个爆款标题 + 三段式专业解析 + 文末业务引导）、合伙人朋友圈/私信话术（150 字口语化小钩子）、一页纸作战地图框架（适合直接发客户法务总监）。一次跑完，审核就能发。
- **专家共识代理验证**：官方文本模糊时，自动检索全球 Top 10 律所（Sidley Austin、Covington、汉坤、方达等）的深度解读，及受影响头部药企（药明康德、恒瑞、信达等）的官方公告，提炼行业共识观点，不孤证。

## 搭配使用

- **药企跨境出海战略提案底稿**（`cue-pharma-bd-strategy`）：战略提案中的合规风险章节 → 用本搭子持续跟踪最新法规变化，提案不过时。
- **创新药政务资助项目挖掘**（`cue-pharma-grant-mining`）：资助挖掘中标红的合规风险项 → 用本搭子追踪相关法规的最新执法动态和处罚案例。

## 怎么跑（搭子是动态的，运行时查 live）
1. **拉本场景当前搭子**：`GET https://cuecue.cn/api/playbook`，找对应 scene，读 `buddies[]`（每个有 `template_id`/`title`/`goal`）。
2. **选一个搭子**：**委托 cue-research 的匹配逻辑**（其 `+match`/Stage-2：对 `goal` 做语义匹配、弱命中先列 ≤2 候选确认）。取选中搭子的 `template_id`。
3. **确认 credits（强制）**：跑深度研究消耗 credits。运行前显式问用户确认。
4. **跑**：`python3 ~/.cue/cue-skills/cue-research/scripts/research_run.py --query "<时间窗口> 医药跨境合规" --template-id <template_id>`。深度研究 3–15 分钟。
5. **回报**：把带来源链接的报告交给用户，不去掉来源、不杜撰。

## 前置
- Cue 账号 API key（cue CLI 登录后在 `~/.cue/config.json`，runner 自动读）；新账号送免费积分（注册 50 + 每天 10）。
- `git` + `python3`（自举 runner 用；runner 仅标准库）。
- 跑深度研究**消耗 credits**；只覆盖公开数据，不替代尽调/法律/核保。

## 联系与反馈

- **微信服务号**：搜索「**感易Cue**」关注，领免费积分、看最新搭子、提交需求
- **客服电话**：13770767226
- **邮箱**：cue@sensedeal.ai
