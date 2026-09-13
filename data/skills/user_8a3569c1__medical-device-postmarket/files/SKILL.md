---
name: medical-device-postmarket
slug: medical-device-postmarket
display_name: 医械上市后监管
displayName: 医械上市后监管
title: 医械上市后监管
version: 1.0.0
category: 通用技能
platforms:
  - windows
  - macos
  - linux
  - web
author: 注册老炮
license: MIT
description: 医疗器械上市后监管（Post-Market Surveillance, PMS）实操手册——中美欧日四市场上市后义务对照（不良事件报告、PSUR 定期安全报告、FSCA/召回现场安全纠正、PMCF 上市后临床跟踪）、各市场报告时限与流程清单（美国 21 CFR 803 致死 30 天/严重 90 天、欧盟 MDCG 2022-21 PSUR 频率、中国 2018 年 1 号令报告时限、日本 PMDA）、PMS 计划与 PSUR 撰写框架、监测-报告-纠正闭环落地，附零依赖本地工具一键查询义务对照、报告时限与生成 PMS/PSUR 框架。面向医械法规、质量与临床负责人，拿证后的持续合规一站理清。
description_en: A hands-on playbook for medical device post-market surveillance (PMS) — four-market obligation comparison (US/EU/CN/JP) covering adverse event reporting, PSUR, FSCA/recall field safety corrective actions and PMCF post-market clinical follow-up, with report timelines and process checklists per market (US 21 CFR 803 30-day death/90-day serious injury, EU MDCG 2022-21 PSUR frequency, China 2018 Order No.1 timelines, Japan PMDA), PMS plan and PSUR writing frameworks, and the monitor-report-correct closed loop. Includes a zero-dependency local toolkit for obligation comparison, timeline queries and PMS/PSUR framework generation. Built for regulatory, quality and clinical leaders — one-stop continuous compliance after certification.
tags:
  - 医疗器械
  - 上市后监管
  - PMS
  - 不良事件
  - PSUR
  - FSCA
  - 召回
  - PMCF
  - MDR
  - Post-market
  - 21 CFR 803
  - MDCG 2022-21
---

# 医械上市后监管

医疗器械上市后监管（PMS）工作台：**对得上四市场义务、报得了不良事件、写得出 PSUR、纠得了 FSCA/召回、闭环不踩雷**。拿证之后，「监测—报告—纠正」闭环做不好，注册证都可能被收回。

## 什么时候用这个技能

- **义务对照**：「产品在中美欧日上市，各有哪些 PMS 义务？」
- **不良事件**：「美国收到严重伤害事件，多久报告？中国呢？」
- **定期文件**：「IIb 器械 PSUR 怎么写？多久更新一次？」
- **纠正措施**：「什么时候触发 FSCA/召回？流程是什么？」
- **PMCF**：「上市后临床跟踪计划怎么写？」
- **闭环落地**：「PMS 计划怎么建？监测-报告-纠正怎么转起来？」

## 怎么用（两种模式）

### 模式一：直接问（推荐）

> 「我们在美国收到一起严重伤害不良事件，要报告吗？多久？」
> 「出口欧盟的 IIb 器械 PSUR 怎么写？」
> 「中国的不良事件报告时限是多少？」

### 模式二：本地工具（要结构化结果）

```bash
# ① 义务对照（按市场）
python tools/pms_toolkit.py obligations --region us      # us=美国 / eu=欧盟 / cn=中国 / jp=日本

# ② 不良事件报告时限速查
python tools/pms_toolkit.py report --region us

# ③ PMS 计划框架（生成 Markdown 骨架）
python tools/pms_toolkit.py plan

# ④ PSUR 撰写框架（按风险等级）
python tools/pms_toolkit.py psur --class IIb

# ⑤ FSCA/召回流程
python tools/pms_toolkit.py recall

# 查看全部命令
python tools/pms_toolkit.py --help
```

## 知识库导航（references/）

| 模块 | 文件 | 解决什么问题 |
|---|---|---|
| ① 四市场义务对照 | `references/上市后监管知识库.md` 第一章 | 中美欧日 PMS 义务总览 |
| ② 美国报告（21 CFR 803） | `references/上市后监管知识库.md` 第二章 | eMDR/MAUDE、30/90 天时限 |
| ③ 欧盟警戒/FSCA/PSUR | `references/上市后监管知识库.md` 第三章 | MDCG 指南、PSUR 频率 |
| ④ PMCF 计划与报告 | `references/上市后监管知识库.md` 第四章 | MDCG 2020-7/8 框架 |
| ⑤ 中国监测与再评价 | `references/上市后监管知识库.md` 第五章 | 2018 年 1 号令、报告时限 |
| ⑥ 日本 PMDA 报告 | `references/上市后监管知识库.md` 第六章 | 日本报告义务 |
| ⑦ PMS 计划/PSUR 框架 | `references/上市后监管知识库.md` 第七章 | 撰写结构 |

## 快速上手（三步）

1. **对义务**：`obligations` 命令查产品所在市场义务，对照知识库第一章；
2. **建闭环**：`report` 查报告时限，建不良事件接收→评估→报告流程；
3. **写文件**：`plan`/`psur` 生成框架，按知识库第七章程式组织。

## 能力边界（如实说明）

- **本技能提供框架与要点，不替代各国监管机构个案裁定**：具体事件报告时限与格式，以产品所在市场最新法规和监管机构最新通知为准；
- **法规持续更新**（FDA 指南改版频繁、EU 协调标准滚动更新），引用前复核官方原文；
- **工具不联网**：本地规则匹配，不采集数据、不调用外部服务。

## 常见问题（FAQ）

- **Q：所有上市产品都要做 PMS 吗？** 是——PMS 是拿证后的持续义务，四市场都有要求（中国/欧盟明确强制，美国通过不良事件报告体现）。
- **Q：PSUR 多久写一次？** 欧盟按风险等级：IIb 至少每 2 年、III 类至少每年（MDCG 2022-21），可并入技术文档更新。
- **Q：FSCA 和召回什么区别？** FSCA 是现场安全纠正措施（含召回）——欧盟触发 FSCA 须报告主管当局；召回是纠正方式之一（见知识库第三章）。
- **Q：工具脚本要装依赖吗？** 不需要，仅 Python 标准库。

## 版权与许可

**版权与许可**：© 2026 注册老炮。本作品（含方法论、模板、法规整理与原创表达）依 MIT License 提供，详见 `LICENSE.md`。

**知识版权声明**：本作品汇集的上市后监管方法论、义务整理、流程框架与原创表达，归 注册老炮 所有。未经许可，不得复制、转载、转售本作品全部或实质部分，不得用于任何模型训练或二次分发牟利。

**免责声明**：本作品按「现状」(AS IS) 提供，不作任何明示或暗示的担保，包括但不限于适销性、特定用途适用性与监管准确性保证。使用者应自行核实并承担使用后果，作者不对因使用本作品产生的任何直接或间接损失负责。
