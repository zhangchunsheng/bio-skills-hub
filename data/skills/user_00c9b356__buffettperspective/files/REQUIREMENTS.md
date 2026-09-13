# 需求看板 · buffett-perspective

> 三件套之一（SKILL.md + REQUIREMENTS.md + SOLUTIONS.md）。
> 需求三源：Stream A(用户提) / Stream B(评测+GitHub) / Stream C(miner 隐性)。
> 状态：✅ 已实现 / 🔲 未做 / 🔜 进行中。版本号随发版全局替换。

---

## Stream A · 用户提（need-to-skill-flow 跑通）

| ID | 来源 | 需求 | 状态 | 版本 |
|----|------|------|------|------|
| R-001 | 用户 | 用 need-to-skill-flow 跑通"巴菲特之秤"，以本地 v1.2.0 为真相源精修并发布对齐 SkillHub | ✅ | v1.2.1 |
| R-002 | 用户 | 不推荐具体股票、不预测短期市场（巴菲特本人禁忌，写进 skill） | ✅ | v1.2.0 |
| R-003 | 用户 | 保持"思维顾问 + 角色扮演"定位，不退化成语录拼贴 | ✅ | v1.2.0 |

---

## Stream B · 评测反馈 + GitHub 借鉴

| ID | 来源 | 需求 | 状态 | 版本 |
|----|------|------|------|------|
| R-004 | GitHub(nuwa-skill) | 借鉴"遇事实先研究"Agentic Protocol，防凭训练记忆编造 | ✅ | v1.2.1 |
| R-005 | GitHub(ai-hedge-fund) | 结构化"巴菲特式投资体检卡"（护城河/ROE>15%/低负债/定价权/安全边际） | 🔲 | —（选项3，本版未做，见 SOLUTIONS ADR-002） |
| R-006 | 评测(SkillHub TRACE) | 发布审核通过后取回五维评测，扣分点回填本表 | 🔲 | —（待发布后做，Phase C） |

---

## Stream C · 隐性需求（conversation-miner）

| ID | 来源 | 需求 | 状态 | 版本 |
|----|------|------|------|------|
| R-007 | miner | （待 Phase C 跑 conversation-miner 产出 _RECURRING.json 后回填） | 🔲 | — |

---

## 变更日志

- v1.2.1 (2026-07-12)：need-to-skill-flow 解码+构建；补 Agentic Protocol（R-004）；种双看板。
- v1.2.0 (2026-06-30)：四心智模型+置信度+诚实边界5条+自进化 Loop。
- v1.1.0：认知放大器验证后修正模型、降级2个、新增诚实边界。
