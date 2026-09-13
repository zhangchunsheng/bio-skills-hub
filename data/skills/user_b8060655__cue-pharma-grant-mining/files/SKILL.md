---
name: cue-pharma-grant-mining
slug: cue-pharma-grant-mining
version: 1.0.0
displayName: 创新药政务资助项目挖掘
description: >
  逆向反查药企的政府资助与科技奖项公告，将模糊项目名与管线代号/靶点做语义对齐，同步扫描出口管制与数据出境合规风险，输出含 BD 切入点的红圈作战底稿。搭配药企跨境出海战略提案底稿形成"资助发现→BD提案"闭环。
  Reverse-mining pharma government grant & award announcements: map vague project names to pipeline codes/targets, scan export-control & data-transfer compliance risks, deliver a red-circle battle card with BD entry points.
  触发 Triggers: 药企资助、政府补助、管线挖掘、合规扫描、BD 切入点 / pharma grant mining, pipeline mapping, compliance scan
license: MIT
metadata:
  source: cuecue.cn/playbook
  scene: "律所BD"
  generated_from: /api/playbook
---

# Cue「创新药政务资助项目挖掘」研究 skill

[Cue](https://cuecue.cn) 是一个深度调研 Agent，接入交易所公告、政府公示、专利数据库、临床登记等 300+ 公开数据源，多源交叉验证，每条结论带来源链接。

加载本 skill 后，你可以用 Cue 跑创新药政务资助项目的定向挖掘与合规风险扫描。

## 能做什么

- **逆向挖掘资助公告**：检索巨潮资讯、港交所披露易等官方信源，用"重大专项""政府补助""科学技术奖""小巨人"等关键词锁定药企资助公告，自动剔除纯金额、无项目名的无效公告，只保留能关联到具体研发项目的记录。
- **管线代号语义对齐**：公告里写的"一类新药产业化项目"到底对应哪个管线？Cue 二次检索企业 Pipeline 图谱、招股书和投资者问答，把模糊项目名映射到具体商业化代号和靶点，标不出来就标记"[待核实]"而不是硬编。
- **合规红线预扫描**：映射出管线后，自动对《禁止出口限制出口技术目录》《人类遗传资源管理条例》等法规做匹配——涉及基因编辑、CAR-T、细胞治疗的管线直接标红，数据出境风险项单独列出。
- **输出 BD 切入点**：不是交一份资助清单就完了——每条记录附 BD 切入建议：这家企业拿了什么资助 → 对应什么技术壁垒 → 涉及什么合规风险 → 律所可以从哪个口子切入。

## 搭配使用

- **药企跨境出海战略提案底稿**（`cue-pharma-bd-strategy`）：挖到有重大资助、高技术壁垒的药企 → 直接进入 BD 战略提案流程，做架构设计和条款对标。

## 怎么跑（搭子是动态的，运行时查 live）
1. **拉本场景当前搭子**：`GET https://cuecue.cn/api/playbook`，找对应 scene，读 `buddies[]`（每个有 `template_id`/`title`/`goal`）。若该场景当前不在返回里 → 告知用户暂不可用。
2. **选一个搭子**：**委托 cue-research 的匹配逻辑**（其 `+match`/Stage-2：对 `goal` 做语义匹配、把用户的具体主体从匹配中剥离、弱命中先列 ≤2 候选确认）。取选中搭子的 `template_id`。
3. **确认 credits（强制）**：跑深度研究消耗 credits。运行前显式问用户「将用搭子 X 跑【主体】，耗 credits，是否继续？」并等确认。
4. **跑**：`python3 ~/.cue/cue-skills/cue-research/scripts/research_run.py --query "<目标赛道/靶点>" --template-id <template_id>`。深度研究 3–15 分钟。读 runner 末行 `RESULT ok|empty`：`empty` → 告知用户本次未取到内容、可换主体/搭子重试，**不要编造**。
5. **回报**：把带来源链接的报告交给用户，不去掉来源、不杜撰。

## 前置
- Cue 账号 API key（cue CLI 登录后在 `~/.cue/config.json`，runner 自动读）；新账号送免费积分（注册 50 + 每天 10），可先免费试。
- `git` + `python3`（自举 runner 用；runner 仅标准库）。
- 跑深度研究**消耗 credits**；只覆盖公开数据，不替代尽调/法律/核保。

## 联系与反馈

- **微信服务号**：搜索「**感易Cue**」关注，领免费积分、看最新搭子、提交需求
- **客服电话**：13770767226
- **邮箱**：cue@sensedeal.ai
