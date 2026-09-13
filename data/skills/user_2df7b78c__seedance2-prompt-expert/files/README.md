# 🎬 Seedance 2.0 电影级提示词生成器 · 专业版 V2.1.7

> **可执行代码技能** — 真实 Python 脚本，不是规则文档

---

## 📌 一句话介绍

真实可运行的 Seedance 2.0 提示词工程工具。基于**女娲四层建筑方法论**，集成八大行业模板、反模式过滤器、问题诊断引擎、多模态绑定组装器，一键产出高成功率电影级视频提示词。

---

## 🎯 核心能力

- 🏗️ **参数化提示词生成器**（L1→L4 四层结构自动组装）
- 🎨 **八大行业模板一键调用**（T1 电商 / T2 治愈 / T3 科幻 / T4 美食 / T5 运动 / T6 MV / T7 微电影 / T8 国风）
- 🔍 **反模式过滤器**（抽象词/冲突指令/多动叠加/违背物理自动检测）
- 🩺 **问题诊断引擎**（12+ 症状 → 修复方案）
- 🔗 **多模态绑定组装器**（@图片/@视频/@音频 语法）
- ⚠️ **能力边界校验**（时长/口型/文字/流体自动预警）
- 🐍 **零第三方依赖**（仅需 Python 3.8+）

---

## 🚀 快速开始

### 模板生成（最简单）

```bash
python3 seedance.py --template T1 --subject "白色运动鞋"
python3 seedance.py --template T3 --subject "宇航员" --duration 15
```

### 自定义生成

```bash
python3 seedance.py --custom \
    --subject "古装女子" \
    --scene "沙漠戈壁" \
    --style "西部电影" \
    --emotion "苍凉孤寂"
```

### 问题诊断

```bash
python3 seedance.py --diagnose "人物变脸"
```

### 反模式检查

```bash
python3 seedance.py --check "很科幻的画面，静止且冲刺"
```

### Python API

```python
from seedance import generate_from_template

output = generate_from_template("T3", subject="宇航员", duration=15)
print(output.prompt)
print(output.risk.is_safe)
```

---

## 🎨 八大模板速查

| ID | 名称 | 画幅 | 时长 |
|----|------|------|------|
| T1 | 电商产品展示 | 16:9 | 5s |
| T2 | 治愈生活 | 9:16 | 5s |
| T3 | 科幻史诗 | 2.35:1 | 10s |
| T4 | 美食特写 | 16:9 | 5s |
| T5 | 运动潮流 | 9:16 | 5s |
| T6 | 音乐舞蹈MV | 16:9 | 8s |
| T7 | 情感微电影 | 2.35:1 | 10s |
| T8 | 国风古风 | 16:9 | 5s |

---

## 📊 Seedance 2.0 能力边界

| 能力项 | 上限 |
|--------|------|
| 时长 | 60 秒 2K |
| 唇形同步 | 92.4% |
| 成片可用率 | 90% |
| 音画同步 | 原生支持 |
| 多镜头叙事 | 支持 |

---

## 📝 版本信息

- **版本号**：V2.1.7（代码版）
- **发布日期**：2026-07-03
- **作者**：团子 🦐 | 知灵技舍
- **许可**：MIT
- **依赖**：Python 3.8+（无第三方依赖）

---

_Seedance Prompt Expert — 真实代码，电影级 AI 视频，工业级提示词_ 🎬✨
