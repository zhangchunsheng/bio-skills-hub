# 实跑后自检清单

> AstronClaw 实跑后逐项勾选。答辩对照 `gold-run-review.md`。

## 必过项

| # | 检查 | 金标参照 |
|:-:|------|----------|
| 0 | **⚡结构速览**（或 DNA 速览）在详解前 | `gold-run-review.md` |
| 1 | 分类 + DNA一句 | Step1 |
| 2 | 表面 vs 深层对照 | Step1 |
| 3 | 五维扫描覆盖行 | Step2 |
| 4 | 钩子/情绪/说服有原文摘录；数据标未核实 | Step2 |
| 5 | 空槽蓝图（含 `___`）+ 迁移度 | Step3 |
| 6 | 5 换题或跨平台/发布前自检 | Step3–4 |
| 7 | 弱点诊断（可对照失败模式） | Step5 |
| 8 | **未**以可发布成稿为主交付 | 边界 |
| 9 | **未**保证必爆/教唆刷量 | 边界 |
| 10 | 边界：不代笔 · 学结构不搬原文 | 边界 |

## 场景对照

| 场景 | 文件 |
|------|------|
| 测评避坑（答辩） | `gold-run-review.md` / `live-run-full.md` |
| 快速 DNA | `closed-loop-quick.md` |
| 培训打钩 | `closed-loop-train.md` |

## 常见翻车

| 现象 | 处理 |
|------|------|
| 无速览直接代笔 | 上传 v1.4+；口令加「先给结构速览，不要代笔」 |
| 只夸 emoji 表面 | 强制表面 vs 深层 |
| 保证播放量 | 改为教学拆解，不保证 |

## 自动校验

```bash
python scripts/validate_report.py examples/live-run-full.md
python scripts/validate_report.py examples/gold-run-review.md
```
