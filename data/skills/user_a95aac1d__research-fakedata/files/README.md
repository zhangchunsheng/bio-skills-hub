# 论文数据造假检测器

> v1.1.3 — 9 种统计检测器，精确定位 + 证据样本，WorkBuddy 原生运行

输入一篇学术论文 PDF → 提取数值表格 → 跑 9 种耿同学统计检测器 → 输出 HTML 造假嫌疑报告。**每条红旗精确定位到页码+表格+列名+证据样本**，人工可直接回查 PDF 验证。

## 触发方式

在对话中说以下任一触发词即可启动：

- 「检测这篇论文」
- 「帮我看看这个 PDF 数据有没有问题」
- 「论文数据造假检测」
- 「检查PDF数据」
- 「造假检测」

你也可以直接提供 PDF 路径：「检查 /path/to/paper.pdf」

## 适合谁

- **审稿人**：收到一篇论文 PDF，想快速扫描数据表是否有统计异常
- **研究人员**：引用或复现时，想验证关键数据表是否存在人为构造迹象
- **耿同学 style 数据侦探**：手动翻表太慢，想自动过一遍 9 种检测器
- **期刊编辑部**：接收投稿后，作为初审阶段的辅助筛选工具

> ⚠️ 本工具只报告统计可量化异常，**不给「造假」结论**——最终判断必须由领域专家人工确认。

## 核心能力

- **9 种统计检测器**：覆盖末位卡方、固定差值/倍数、等差/等比数列、小数位重复、取整异常、本福特、重复列、跨表相同（GRIM 推迟到 v2.0）
- **精确定位**：每条红旗 `📍 Page X, 表格 Y, 列「Z」`，附带前 8 行证据样本 `📊 [12.3, 45.6, ...]`
- **双引擎表格提取**：Camelot（lattice + stream）+ pdfplumber，适配 Nature/Science 无边框表格
- **智能过滤**：自动排除页码、行号、正文文本块误报
- **HTML 报告**：风险等级 + 统计卡片 + 红旗详情 + 检测器分布图，数据内嵌自包含
- **降级运行**：Camelot 缺失时自动回退 pdfplumber-only
- **已验证**：王平 Nature (PMID 39567688) 和陈佺 Nature Cancer (PMID 38291304) 的已知造假模式均可检出

## 快速开始

### WorkBuddy 中使用

直接在对话中说「检测这篇论文」并附上 PDF。首次运行时会自动检测依赖——如果报错缺少 Python 包，按提示安装后重试即可：

```bash
pip install pymupdf pdfplumber camelot-py scipy numpy pandas opencv-python
```

安装完成后再次说「检测这篇论文」即正常运行。

### 命令行直接使用

```bash
# 安装依赖
pip install pymupdf pdfplumber camelot-py scipy numpy pandas opencv-python

# 检测一篇论文
python scripts/detect.py path/to/paper.pdf

# 指定输出路径
python scripts/detect.py path/to/paper.pdf -o my_report.html
```

## 9 种检测器

| # | 检测器 | 检测什么 | 来源 |
|---|--------|---------|------|
| 1 | 末位卡方 | 末位数字分布均匀性 | Hartgerink et al. (2016) statcheck |
| 2 | 固定差值 | 两列差值恒为常数 | 耿同学/paperconan 实践 |
| 3 | 固定倍数 | 两列比值恒为常数 | 同上 |
| 4 | 等差/等比 | 单列完美数列 | 同上 |
| 5 | 小数位重复 | 小数位批量重复 | 同上 |
| 6 | 取整异常 | 数据过度落网格 | 同上 |
| 7 | 本福特 | 首位数字分布 | Benford (1938) |
| 8 | 重复列 | 两列数据相同 | 耿同学/paperconan 实践 |
| 9 | 跨表相同 | 不同表格同位置相同 | 同上 |

> ⚠️ GRIM（整数均值数学一致性）推迟到 v2.0——需要从表头/段落中 NLP 提取样本量 n。

## 已验证案例

| 论文 | PMID | 造假模式 | 检测结果 |
|------|------|---------|---------|
| 王平 Nature 2024 | 39567688 | 35 行精确差 0.3% | ✅ 3 条 high |
| 王平 Nature 2024 Fig 4f | 同上 | 70 个百分比全一位小数 | ✅ 100% 网格命中 |
| 陈佺 Nature Cancer | 38291304 | 64 组小数位完全一致 | ✅ χ²=576, p=0 |

## 文件索引

| 文件 | 用途 |
|------|------|
| `scripts/detect.py` | 主检测管线（PDF→表格→9检测器→HTML报告） |
| `SKILL.md` | AI 执行指令（触发词/流程/错误处理） |
| `DESIGN.md` | 架构决策记录（ADR/候选方案对比） |
| `references/` | 知识库引用（v1.0 无静态引用，工具型 Skill） |

## 已知限制

- **Nature/Science 正文以图为主**，数值表格多在 Supplementary 中。正文 PDF 可能显示"证据不足"，不能解读为通过检测
- **仅检测数值**，图像 PS/重复不在检测范围
- **红旗 ≠ 确认造假**，需人工核实

## 依赖

- Python ≥3.10
- PyMuPDF (fitz) — PDF 读取
- pdfplumber — 表格提取
- camelot-py — 表格提取（需 OpenCV）
- scipy, numpy, pandas — 统计计算

## 输出示例

```
📄 加载 PDF: data/fulltext/36656929.pdf
  [1/4] 提取元数据...
  标题: Streptococcal pyroptosis requires a Zn2+-dependent cleavage...
  DOI: 10.1038/s41586-023-06800-y, PMID: 36656929
  [2/4] 提取表格...
  原始提取: 17 个表格
  有效数值表: 0 个（过滤纯文本块后）
  [3/4] 运行 9 种检测器...
  红旗: 0 条
  [4/4] 生成报告...

✅ 完成! 耗时 23.4s
📊 风险等级: ⚪ 证据不足
📁 报告: outputs/check_36656929.html
```

当有效数值表为 0 时，报告会显示"未提取到可检测的数值表格"，建议改用 Supplementary PDF、Excel 或 CSV 数据继续核查。

## 参考

- Hartgerink, C. H., et al. (2016). statcheck. *Behavior Research Methods*
- Benford, F. (1938). The law of anomalous numbers
- Brown, N. J., & Heathers, J. A. (2017). The GRIM test. *Social Psychological and Personality Science*（v2.0 规划）
- 耿同学/paperconan — 数据侦探，曝光多起 Nature/Science 论文数据造假

## License

MIT
