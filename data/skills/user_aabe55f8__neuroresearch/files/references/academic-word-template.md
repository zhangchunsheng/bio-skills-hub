# 学术 Word 文档交付规范

本技能在产出正式文稿（文献综述、开题报告、基金标书、论文草稿、审稿回复等）时，默认交付为 **.docx Word 文档**，并符合以下学术排版规范。轻量对话、代码片段、临时结果不强制转 Word；但若用户要求"出文档/出报告"，一律走 Word。

## 一、生成流程
1. 先按对应模块（literature-review / experiment-design / manuscript-and-submission 等）完成内容创作，得到结构化大纲或 Markdown。
2. 生成 .docx（**两种通道，环境无 tencent-docx 时用兜底，绝不阻塞交付**）：
   - **首选**：调用 `tencent-docx` skill（或从 HTML 中转走 `html-to-docx`），生成时即套用下方排版规范（标题用 Word 样式、字体字号、页边距等）。
   - **兜底（无 tencent-docx 时）**：用 Python `python-docx` 直接生成——脚本开头按 `references/python-runtime.md` 自检安装 `python-docx`；按下方规范设置页面/字体/段落/标题样式（Heading 1–3 用内置样式）、三线表（`table.style = 'Table Grid'` + 手绘边框）、参考文献条目，保存 `.docx`。python-docx 是纯 Python 库，任何环境可装。
3. 生成后按第七节"交付前自检清单"逐项核对，再交付用户。

### 1.1 python-docx 兜底骨架（关键 API）
```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)      # A4
sec.top_margin = sec.bottom_margin = Cm(2.54)
sec.left_margin = sec.right_margin = Cm(3.18)

# 中文字体需同时设 ascii（西文）与 eastAsia（中文）
def set_font(run, cn="宋体", en="Times New Roman", size=12, bold=False):
    run.font.name = en
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)
    run.font.size = Pt(size)
    run.font.bold = bold

p = doc.add_paragraph()
r = p.add_run("正文内容")
set_font(r)
p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
p.paragraph_format.first_line_indent = Pt(24)             # 2 字符（小四 12pt）
doc.save("output.docx")
```
> 三线表用 `table.style = 'Table Grid'` 后，手动删除竖线与内部横线、仅保留顶线/栏目线/底线（见第六节）。

## 二、页面设置
- 纸张：A4（210 × 297 mm）。
- 页边距：上/下 2.54 cm，左/右 3.18 cm（可按目标期刊或学校模板调整）。
- 页眉页脚：页脚居中页码（建议从正文起编）；奇数页页眉可放短标题。中文综述/学位论文常要求「摘要、目录用罗马数字（Ⅰ Ⅱ Ⅲ）编页，正文起用阿拉伯数字（1 2 3）重编」。

## 三、字体与字号
- 正文中文：宋体（SimSun）/ 仿宋，英文：Times New Roman，小四（12 pt）。
- 一级标题：黑体（SimHei）三号（16 pt）加粗；二级标题：黑体四号（14 pt）加粗；三级标题：黑体小四（12 pt）加粗；四级标题：宋体小四加粗。
- 图表题注、参考文献条目：宋体小五（9 pt）或五号（10.5 pt）。
- 中英文混排：**中文用宋体、西文/数字用 Times New Roman**（python-docx 中分设 ascii / eastAsia 字体，见 1.1）。

## 四、段落与行距
- 正文：1.5 倍行距（或固定值 20–22 pt），段后间距 0–6 pt。
- 首行缩进：2 字符（标题、图表题注、参考文献不缩进）。
- 对齐：正文两端对齐；标题居中或左对齐（依规范）。

## 五、标题层级
- 采用"一、/（一）/ 1. /（1）"或"1 / 1.1 / 1.1.1"层级，与期刊/学校模板一致。
- 必须用 Word 内置样式（标题 1 / 标题 2 / 标题 3）而非手动加粗，便于自动生成目录。

### 5.1 封面与前置部分（综述 / 学位论文 / 标书）
- **标题**：居中、二号（22 pt）黑体加粗；副标题另起行、三号。
- **作者/单位/日期**：标题下方居中，宋体四号；单位与通讯作者用脚注或下角标注。
- **摘要**：标题"摘要"黑体小四居中；正文宋体小四、首行缩进；中文摘要后接英文 Abstract（Times New Roman）。
- **关键词**：`关键词：` 加粗，3–5 个，分号分隔，与摘要同字号。
- **目录**：插入域代码 `TOC \o "1-3" \h \z \u` 自动生成，标题层级正确即可一键更新。

## 六、图表与公式
- 图：居中，图序图题置于图下（如"图 1. TBI 后小胶质细胞活化"），宋体小五。
- 表：优先三线表，表序表题置于表上（如"表 1. 各组样本量与时间点"）。
- **三线表画法**：顶线、底线 1.5 pt 实线；栏目线（表头下）0.75 pt；**无竖线、无内部横线**。表内文字宋体五号，数字右对齐、单位统一。
- 图表编号连续，正文引用用"如图 1 / 表 1 所示"。
- **图片分辨率与格式**：投稿位图 ≥300 dpi、TIFF 或 PNG；矢量 PDF/EPS。正文插图单栏 90 mm、双栏 180 mm（详见 `prism-style-plot.md`）。
- 公式用公式编辑器录入，居中、右编号（1）。

## 七、参考文献（序号制，详见 manuscript-and-submission.md §4）
- 文末"参考文献"标题用黑体；条目宋体小五、悬挂缩进，按 [1][2]… 顺序排列。
- 条目格式（期刊）：`[n] 作者. 题名[J]. 刊名, 年, 卷(期): 起止页. DOI.`
- 正文引用用方括号序号 `[1]`，与文末一一对应，不出现作者-年混排。
- 具体著录规则（含预印本/数据集/软件/书章等）见 `citation-formatting.md`。

## 八、单位、数字与缩写
- 单位用 SI（如 mg/kg、μM、mm³），数字与单位间加空格（`10 μM`）；范围用 `–`（en dash）。
- 统计：精确 p 值 + 效应量 + n，格式见 `statistical-analysis.md`；p < 0.001 用科学计数法，不写 `p=0.000`。
- 缩写首次出现给全称 + 括号缩写，如"创伤性脑损伤（traumatic brain injury, TBI）"，此后统一用缩写。
- 中英文标点不混用：中文稿用全角标点，英文稿用半角。

## 九、交付前自检清单
- [ ] 为 .docx 格式，可用 Word 正常打开
- [ ] 页面 A4、页边距正确
- [ ] 字体/字号/行距符合第三节、第四节
- [ ] 标题使用了 Word 样式（可自动生成目录）
- [ ] 封面/摘要/关键词齐全（若适用）
- [ ] 图表题注完整、编号连续、三线表规范、图片 ≥300 dpi
- [ ] 参考文献为序号制，与正文一一对应，DOI 齐全
- [ ] 无未定义缩写、无错别字、中英文标点不混用
- [ ] 中英文混排时英文用 Times New Roman、中文用宋体
- [ ] 单位 SI、数字/统计格式规范

## 十、文件命名规范
所有交付物统一写入工作区 `deliverables/<项目名>/`（中间产物入 `deliverables/_tmp/`），详见 SKILL.md 核心原则第 9 条。在该目录下，输出文件（尤其是 .docx 交付物）命名必须具体、可检索，禁止笼统命名。
- **模板**：`{项目名}_{具体产出内容}_{YYYY-MM-DD}.ext`
  - 项目名：用户给定的项目简称，或课题标题缩写（如 `<课题简称>`）。
  - 具体产出内容：点明研究对象与方法，不要只写"实验设计/综述/分析"，而应写"某损伤模型实验设计""某细胞类型 RNA-seq 差异分析""某分子通路文献综述"。
  - 时间戳：文件创建当天的 `YYYY-MM-DD`（如 `2026-08-10`）。
- **反面示例（禁止）**：`实验设计.docx`、`综述.docx`、`分析.docx`、`report.docx`。
- **正面示例**：
  - `<课题简称>_某损伤模型实验设计_2026-08-10.docx`
  - `<课题简称>_某细胞类型条件培养基RNA-seq差异分析_2026-08-10.docx`
  - `<课题简称>_某分子调控细胞死亡文献综述_2026-08-10.docx`
- 若用户未提供项目名，主动询问或用本课题默认简称；多版本时再加 `_v2` 等后缀。
