# CHANGELOG · 文哥漫画-手绘

> 本 skill 的版本变更记录。从 v1.0 起步。

---

## v1.0 · 2026-07-13 · 拆分首发

### 起源
- 拆分自 上一代 v3.0 漫画 skill
- 解决 3 个问题：
  1. **5 老 IP 角色捆死跨界内容** —— v3.0 降级为彩蛋库仍不够，要彻底废弃
  2. **三 SKU 架构太重** —— 漫画四格 + 长文配图 + PPT 演讲页混在一起，风格决策复杂
  3. **缺调性适配** —— 不同内容调性不同（商业 vs 娱乐），不分容易"严肃内容画成贱萌"或"娱乐内容画成商务"

### 核心变更
1. **极简手绘风独立成 skill** —— 与 `文哥漫画-贱萌` 并列
2. **5 老 IP 彻底废弃** —— 主 IP 100% 固定文哥 v6，无 wenge/xiaoneng/chuzi/banzhang/xiaoq/caitan 角色档案
3. **调性适配评估 · 5 维评分** —— 每个新任务必走 + shot list 必填 tone_match 字段
4. **图片数量弹性指南** —— 5 档推荐（1/3-5/6-10/10-20/20-30+ 张），不写死张数
5. **配色两套锁定** —— IP1 三色（长文配图）+ IP2 5 色（PPT 演讲页），B+ 套 6 色（贱萌）拆分到 `文哥漫画-贱萌`
6. **shot list 14 字段** —— v3.0 的 13 字段 + tone_match 字段
7. **角色架构简化** —— 文哥 v6 + 按需角色 + 火柴人 Agent，3 层结构

### 3 个核心开关
| 开关 | 名称 | 改法 | 效果 |
|---|---|---|---|
| **A** | 调性适配评估 | 5 维评分 + tone_match 字段 | 不匹配时主动建议 |
| **B** | 角色架构简化 | 删 5 老 IP，只留文哥 v6 + 按需 + Agent | 主 IP 永远 1 个 |
| **C** | 图片数量弹性 | 5 档推荐（1/3-5/6-10/10-20/20-30+）+ 按文章 KB | 不写死张数 |

### 文件结构
```
文哥漫画-手绘/
├── SKILL.md                            # v1.0 主文件
├── CHANGELOG.md                        # 本文件
├── references/
│   ├── palette.md                      # v1.0 IP1 三色 + IP2 5 色
│   ├── character-architecture.md       # v1.0 文哥 v6 + 按需 + Agent
│   ├── comedy-techniques.md            # v1.0 脱口秀 14 手法字典
│   ├── copywriting-style.md            # v1.0 脱口秀化文案
│   ├── shot-list.md                    # v1.0 14 字段 shot list（含 tone_match）
│   ├── longform-illustration.md        # v1.0 长文配图 SKU
│   ├── tone-matching.md                # v1.0 5 维调性评估（核心）
│   ├── episode-count-formula.md        # v1.0 图数算法 + 弹性指南
│   ├── brand-constraints.md            # 品牌硬约束
│   └── input-formats.md                # 7 种输入处理
└── assets/
    ├── main_anchor.png                 # 文哥 v6 主锚图（必传）
    ├── 规范说明图.png                  # 文哥 v6 规范
    ├── 动作扩展图.png                  # 文哥 v6 动作扩展
    ├── main_anchor_v2.png              # 文哥 IP2 商务版主锚图
    └── 规范说明图_v2.png               # 文哥 IP2 商务版规范
```

### 验证数据
- 2026-07-12 华为经营分析会 5 张长文配图：4 A+ / 1 A 评级
- 2026-07-12 YouTube AI 概念大串联 13 张长文配图：5 A+ / 7 A / 1 A- 评级
- 验证了 shot list 14 字段（含 tone_match）的实操可行性
- 验证了 IP1 三色配色 + 文哥 v6 主 IP image-to-image 锁形

### 已知问题
- 无（v1.0 新建，等待实际项目验证）

### 下个版本计划（v1.1）
- 自动化脚本（read 文章 → 自动列 shot list → 批量 matrix）
- 与 `文哥漫画-贱萌` skill 的"同主题双风格"混排模板
- IP2 商务版"PPT 一键生成"工作流
- 集成到 ip-diagram-creator skill（v2.0 升级）

---

## 历史版本（来自 上一代 v3.0 漫画 skill）

### v3.0 · 2026-07-12 · 上一代漫画 skill 三 SKU 架构
- 三 SKU 架构（漫画四格 + 长文配图 + PPT 演讲页）
- 角色架构升级（主 IP 改文哥 v6 + 5 老 IP 彩蛋库 + 按需角色 + 火柴人 Agent）
- 文案脱口秀化（13 手法字典 + Setup/Punchline 节奏 + 自嘲词典）
- 配色三套锁定（IP1 三色 + B+ 套 6 色 + IP2 5 色）
- shot list 13 字段

### v2.5 · 减法版
- primary_block 0-1 选 1
- 文哥说降级 14px 灰字 1 行兜底
- 封面钩子句 3 选 1
- 删底部副字"装完就能撩人"

### v2.4.1 · 还原 v1.0 架构 + 幽默手法字典
- HTML 不叠气泡，气泡画在图里
- 9 套 layout + 脱口秀 13 幽默手法融合

### v2.3.1 · 角色圣经 5 角色 + 4 锁
- 5 角色（wenge/xiaoneng/chuzi/banzhang/xiaoq/caitan）
- 4 锁规则（必带小眼睛 / 禁尖耳 / 禁光头 / 跨图同角）
- 圆耳硬约束（v2.4.5 全文档统一）
- 谐音梗字典

### v2.4 · 内容驱动布局
- layout_hint 9 套

### v2.2 · 真人图 chibi 化
- 文哥 = 真人图 chibi 化 + 薄荷青 bomber jacket
- 解决 v2.1 bug（白色技术宅卫衣）

### v1.0 · 漫画四格 SKU
- 贱萌 Q 版 + B 套 5 色 + 8-30 集连载
