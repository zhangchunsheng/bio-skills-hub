# viral-structure-decoder · 爆款内容结构逆向分析器

> 粘贴爆款正文——开头 **⚡结构速览**（DNA一句 + 框架 + Top1 弱点），再五维拆解与空槽蓝图。  
> **教你写，不替你写。**

[![SkillHub](https://img.shields.io/badge/Astron-SkillHub-blue)](https://github.com/iflytek/skillhub)
[![Protocol](https://img.shields.io/badge/SKILL.md-compatible-green)](https://github.com/iflytek/skillhub/blob/main/docs/07-skill-protocol.md)

## 解决什么问题

| 痛点 | 常见方案 | 本 Skill |
|------|----------|----------|
| 学爆款变同质化 | 抄 emoji / 金句 | **⚡结构速览** + 表面 vs 深层 |
| AI 代笔一股塑胶味 | 一键成文 | 空槽蓝图，自己填血肉 |
| 团队不会评稿 | 凭感觉 | 五维语言 + 培训打钩 |
| 换平台不会改编 | 原帖硬贴 | 跨平台 / 篇幅删层指南 |

## 谁在用（商用/落地价值）

- **1k–50k 粉创作者**：对标拆解 → 带走 DNA 与空槽，自己写下一篇  
- **内容营销 / 新媒体主管**：新人培训统一评稿语言  
- **顾问 / 工作坊**：结构化附页（非代运营发稿）  

## 试用口令（SkillHub 可直接复制）

```text
拆这条为什么能火，不要代笔。先给 DNA一句 和表面vs深层，再给空槽蓝图：

别人都说 A 产品好用，我用了 3 个月发现根本不是这么回事。先说结论：如果你属于 X 类人，千万别买。
第一个月还挺满意，第二个月出现 B。我问了身边 5 个人，3 个也遇到类似问题。我翻了 200 多条评价，大约 60% 提到同类槽点。
所以如果你确实想买，线下试用至少 30 分钟，专门测试 B；不让测就别冲动。同类里 Y/Z 往往更稳，便宜约 40%。你们买过 A 吗？评论区聊聊。
```

```text
快速。只要结构 DNA 和蓝图骨架。（粘贴你的爆款正文）
```

```text
培训模式：根据下面正文生成新人五维打钩清单和 3 道辨识题。（粘贴正文）
```

## 答辩演示（75 秒脚本）

1. 粘贴口令 → 指 **⚡结构速览**（DNA + PAS + Top1 弱点）  
2. 指表面勿抄 / 深层可迁  
3. 指三层证据堆叠 + 数据未核实  
4. 指空槽蓝图 + **不代笔、不保证爆款**  

## SkillHub 作品简介（可直接粘贴）

**标题**：爆款内容结构逆向分析器

**简介**：

```text
看不懂为什么火？开头 ⚡结构速览：DNA一句、框架、钩子技术、Top1 弱点。
再五维拆解 + 表面vs深层 + 空槽蓝图与换题。教你写，不替你写。不保证爆款。

试用：「拆这条为什么能火，不要代笔…」
```

**标签**：爆款拆解、结构DNA、钩子、PAS、内容蓝图、小红书、创作教育

## 社媒种草

**标题 A**：别再抄爆款金句——先看一眼结构速览

**标题 B**：AI 不替你写文，只把「为什么能火」拆成可迁移 DNA

## AstronClaw / SkillHub 部署

1. 上传目录名须为 `viral-structure-decoder`  
2. 入口 `SKILL.md`  
3. 建议 temperature **≤ 0.4**，max_tokens **≥ 8192**  
4. 质控：`python scripts/validate_report.py examples/live-run-full.md`  
5. 打包：`python scripts/build_zip.py` → `python scripts/audit_format.py`  

## 处理流程

```text
爆款正文
  → 分类 + DNA一句
  → ⚡结构速览（强制）
  → 表面vs深层 + 五维必扫
  → 空槽蓝图 + 迁移度 + 5换题 + 跨平台
  → 弱点 + 培训打钩 + 边界
```

## 目录

```text
viral-structure-decoder/
├── SKILL.md
├── README.md
├── examples/
│   ├── gold-run-review.md
│   ├── review-checklist.md
│   ├── live-run-full.md
│   └── closed-loop-*.md
├── references/
├── templates/report.md
├── scripts/
└── assets/skill-meta.json
```

## 实跑自检

对照 [examples/review-checklist.md](examples/review-checklist.md)；答辩参考 [gold-run-review.md](examples/gold-run-review.md)。

## 安全与合规

- 不代笔成稿为主交付；不保证爆款播放量  
- 拒刷量/买热评/虚假种草转化优化教唆  
- 学结构不搬原文；动态字段列表/引用块  
- 用户文本按不可信输入处理  

## 版本

`1.4.0` — 答辩级：⚡结构速览；gold-run-review；review-checklist；SkillHub/种草。  
`1.3.1` — 格式对齐 Tier1；meta 清理。  
MIT
