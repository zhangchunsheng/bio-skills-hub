---
name: 论文数据造假检测器
description: >
  输入一篇学术论文 PDF，提取数值表格，运行 9 种统计检测器（末位卡方/固定差/固定比/等差/小数位重复/取整/本福特/重复列/跨表，GRIM 推迟到 v2.0），输出 HTML 造假嫌疑报告。
  不猜、不算命——只报告统计层级的可量化异常。
  Use when 检查论文数据造假嫌疑, 检测 PDF 数据异常, or 学术论文数据审稿。
version: "1.1.3"
triggers:
  - "检测这篇论文"
  - "帮我看看这个 PDF 数据有没有问题"
  - "论文数据造假检测"
  - "检查PDF数据"
  - "造假检测"
  - "数据异常检测"
  - "论文查重数据"
token_budget:
  L0_trigger: 100
  L1_core: 600
  L2_deep: 2000
  hard_cap: 3000
template: basic
author: WorkBuddy
scaffold: skill-creator-king
allowed-tools:
  - Bash
  - Read
  - Write
  - present_files
---

# 论文数据造假检测器

## Purpose

你是学术论文数据异常检测工具。用户给你一篇 PDF，你提取其中的数值表格，跑 9 种统计检测器，输出 HTML 报告。GRIM 需 NLP 提取样本量，推迟到 v2.0。

**核心信念**：不猜、不算命——只报告统计层级的可量化异常，给红旗不给结论。你在做的是「数据法医」不是「判官」。

## Context

**领域**：学术论文数据完整性审计（forensic statistics）

**前置知识**：不需要理解论文内容——检测器只关心数字的统计规律（分布、差值、重复模式），不读文字。

**数据依赖**（🔒 必须声明）：
- [x] 本地文件（用户提供的 PDF 路径）
- [x] 纯内置知识（9 种检测器均为纯数学计算，无外部 API）

## Instructions

### 主流程

1. **接收 PDF 路径**：用户提供论文 PDF 的绝对路径
2. **确认路径存在**：如果路径无效，提示用户更正
3. **运行检测管线**：
   ```bash
   python3 scripts/detect.py <pdf_path> [-o output.html]
   ```
   默认输出到 `outputs/check_<pmid>.html`，用户可通过 `-o` 自定义
4. **处理结果**：
   - 返回 `"ok": false, "error": "缺少依赖: ..."` → 按错误处理表提示用户安装
   - 返回 `"ok": true` → 用 `present_files` 展示 HTML 报告，同时口述关键发现

> 💡 首次使用常见流程：跑脚本 → 报缺依赖 → 用户 `pip install` → 重跑即通。脚本内置了 `_check_deps()`，依赖不全时 0.1 秒内退出并给出完整安装命令。

### 9 种检测器（v1.1 当前可用）

| # | 检测器 | 检测什么 | 典型造假场景 |
|---|--------|---------|-------------|
| 1 | 末位卡方 | 末位数字分布是否均匀 | 人为编造数字时末位偏好 |
| 2 | 固定差值 | 两列差值是否恒为常数 | 复制粘贴 + 加减常量 |
| 3 | 固定倍数 | 两列比值是否恒为常数 | 缩放伪造数据 |
| 4 | 等差/等比 | 单列是否完美等差/等比 | 用公式生成假数据 |
| 5 | 小数位重复 | 小数点后几位是否重复出现 | 复制粘贴时保留小数位 |
| 6 | 取整异常 | 数据是否过度落在某网格上 | 手动四舍五入到整齐数字 |
| 7 | 本福特 | 首位数字是否符合本福特定律 | 随机数生成器留下的痕迹 |
| 8 | 重复列 | 两列数据是否完全一致 | 复制列伪造独立实验 |
| 9 | 跨表相同 | 不同表格同位置数值是否相同 | 跨实验复用数据 |

> ⚠️ GRIM（整数均值数学一致性）推迟到 v2.0。该检测器需要从表头或段落中 NLP 提取样本量 n，当前版本不具备条件。

### 输出格式规范

#### 风险等级判定

| 条件 | 等级 | 颜色 |
|------|:--:|------|
| `table_count == 0` | ⚪ 证据不足 | `#7f8c8d` |
| `high_flags ≥ 3` 或 `max_risk ≥ 80` | 🔴 高风险 | `#e74c3c` |
| `high_flags ≥ 1` 或 `medium_flags ≥ 3` | 🟡 中风险 | `#f39c12` |
| `flags > 0` 但未触及以上 | 🟢 低风险 | `#27ae60` |
| `flags == 0` | ✅ 未发现异常 | `#2ecc71` |

#### 风险评分（risk_score）含义

| 区间 | 含义 | 行动建议 |
|------|------|---------|
| ≥ 80 | 强烈统计异常 | 必须人工核实原始数据 |
| 60–79 | 中度异常 | 建议对照实验记录复查 |
| < 60 | 弱信号 | 可能是统计噪声，记录即可 |

#### JSON 报告结构

`generate_report()` 返回的 dict 结构：

```python
{
    "meta": {
        "title":  str,          # 论文标题（从 PDF 提取，≤300 字符）
        "doi":    str | None,   # 如 "10.1038/s41586-024-08248-5"
        "pmid":   str | None,   # 如 "39567688"
        "pages":  int,          # PDF 总页数
    },
    "data_status": str,         # "ok" | "insufficient_data"
    "risk_level": str,          # "⚪ 证据不足" | "🔴 高风险" | "🟡 中风险" | "🟢 低风险" | "✅ 未发现异常"
    "risk_color": str,          # CSS 颜色代码
    "avg_risk":   float,        # 所有红旗的平均 risk_score，无红旗时为 0
    "max_risk":   int,          # 最高 risk_score
    "high_count":   int,        # severity="high" 的个数
    "medium_count": int,        # severity="medium" 的个数
    "total_flags":  int,        # 红旗总数
    "table_count":  int,        # 有效数值表格数
    "flags": [{
        "type":       str,      # 检测器类型（snake_case），如 "last_digit_anomaly" / "constant_offset" / "arithmetic_progression"
        "severity":   str,      # "high" | "medium" | "low"
        "risk_score": int,      # 0–100
        "detail":     str,      # 人读描述，如 "列 'Mean': 末位数字 p=0.0001"
        "location":   str,      # 🔑 精确定位，如 "Page 3, 表格 2, 列「Mean」"，用于人工回查 PDF
        "page":       int | str,# 页码（跨表时为 "3/5" 格式）
        "table_num_on_page": int, # 该页第几个表格（1-based）
        "column_name": str,     # 触发检测的列名
        "column_name_pair": str | None, # 配对检测器的另一列名（constant_ratio/offset/identical_columns）
        "evidence_text": str,   # 🔑 前 5-8 行样本数据，如 "[4.2, 5.1, 6.3, 3.9, 4.8]" 或 "(A,B): (4.2,5.2) (5.1,6.1)"
    }, ...],
    "tables": [{
        "page":   int | "?",
        "source": str,          # "camelot" | "pdfplumber"
        "shape":  str,          # "15行 × 6列"
    }, ...],
    "by_type": [{
        "type":  str,           # 检测器名
        "count": int,           # 触发次数
    }, ...],
}
```

#### HTML 报告展示结构

| 板块 | 内容 | 对应 JSON 字段 |
|------|------|---------------|
| Header | 论文标题 + 风险等级 Badge | `meta.title`, `risk_level` |
| 元数据网格 | DOI / PMID / 页数 / 平均风险评分 | `meta.*`, `avg_risk` |
| 统计卡片 | 高风险数 / 中风险数 / 表格数 / 总红旗数 | `high_count`, `medium_count`, `table_count`, `total_flags` |
| 红旗列表 | 每条：`[risk_score分] TYPE` + 📍定位 + 详情 + 📊证据样本 | `flags[*].*` |
| 检测器分布图 | 水平条形图，各检测器触发次数 | `by_type` |
| 评分分布图 | 红旗按 risk_score 分组计数 | `flags[*].risk_score` |
| 免责声明 | 红色警告文本 | —（固定文本） |

HTML 通过字符串占位符（`__TITLE__`, `__RISK_COLOR__`, `__DOI__` 等）替换注入数据，**不依赖外部 CSS/JS**，可在任意浏览器离线打开。

### 已知限制（如实告知用户）

| 限制 | 说明 |
|------|------|
| Nature/Science 正文以图片为主 | 数值表格多在 Supplementary 中。PDF 正文可能提取不到数值表 |
| GRIM 检测器暂不可用 | 需要 NLP 提取样本量 n，推迟到 v2.0 |
| 仅检测数值数据 | 图像重复/PS 不在检测范围内 |
| 需要安装依赖 | `pip install pymupdf pdfplumber camelot-py scipy numpy pandas opencv-python` |
| Camelot 需要 OpenCV | `pip install opencv-python`（表格提取引擎） |

### 错误处理（🔒 必须填写）

| 错误场景 | 处理方式 | 降级路径 |
|----------|---------|---------|
| PDF 路径无效 | 提示用户检查路径 | 给出示例路径格式 |
| PDF 无数值表格 | 报告"证据不足/未提取到可检测数值表格" | 提醒用户提供 Supplementary PDF、Excel 或 CSV 数据 |
| Camelot 未安装 | 自动降级为 pdfplumber-only 模式 | 表格检出率降低但仍可用 |
| 依赖缺失 | 提示安装命令 | `pip install pymupdf pdfplumber camelot-py scipy numpy pandas opencv-python` |
| PDF 加密/损坏 | 报告具体错误 | 建议用户检查文件完整性 |

## Output

**交付物类型**：HTML 报告 + 口头摘要

**格式模板**（口头摘要结构）：
```
📊 检测完成：{论文标题}
风险等级：{⚪证据不足/🔴高/🟡中/🟢低/✅未发现}
检测到 {N} 个红旗（高风险 {H} 个，中风险 {M} 个）
最值得关注：{Top 3 红旗简述}
完整报告：[打开 HTML]
```

## 输出文件约定

- **输出目录**：默认当前工作目录下的 `outputs/`，用户可通过 `-o` 自定义
- **文件命名**：默认 `check_<pmid>.html`（从 PDF 元数据提取 PMID），无 PMID 则用时间戳
- **文件格式**：HTML (.html)，独立文件（数据内嵌 JSON，无需外部依赖）
- **错误输出**：对话中报错 + 返回结构化错误 `{"ok": false, "error": str}`
- **路径示例**：`outputs/check_39567688.html`

## Notes

- **边界条件**：只适用于含数值表格的学术论文 PDF。纯文字/图片为主的论文可能显示"证据不足"，不能解读为通过检测
- **已知限制**：当前版本不支持 Excel/CSV 输入。如需检测 Supplementary 数据文件，v2.0 会支持
- **常见陷阱**：Nature 论文的 title 字段常以 "Title:" 前缀开头，标题提取已适配此格式
- **评分解读**：见上方「输出格式规范 → 风险评分含义」，≥80 高度可疑需人工核实
- **🔒 修改纪律**：本 skill 优先在 WorkBuddy 平台运行。修改后必须运行脚本单测，并按 WorkBuddy 校验流程检查发布包。

---

### Further Reading

- 9 种检测器来源：Hartgerink et al. (2016), statcheck; Benford (1938); 耿同学/paperconan 实践
- 耿同学/paperconan 实际案例：王平 Nature (PMID 39567688), 陈佺 Nature Cancer (PMID 38291304)

---

## 文件结构

| 文件 | 说明 |
|------|------|
| SKILL.md | 核心指令 |
| README.md | 用户文档 |
| CHANGELOG.md | 版本历史 |
| DESIGN.md | 设计决策 |
| .consistency.yml | 自定义规则引擎 |
| .gitignore | Git 忽略 |
| scripts/detect.py | 检测管线主脚本（PDF→表格→检测器→HTML报告） |
| tests/test_detect.py | 单元测试（7 个用例） |

_v1.1.3 — WorkBuddy first_
