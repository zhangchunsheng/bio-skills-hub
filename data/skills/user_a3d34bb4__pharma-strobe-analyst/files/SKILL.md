---
name: 药学数据分析助手
description: 药学真实世界研究（RWS）STROBE规范完整数据分析工作流。当用户提供Excel数据（含多sheet的患者基本信息、用药记录、随访记录、实验室检查、结局事件），要求做数据分析、STROBE报告、基线特征三线表、PSM匹配、KM生存曲线、森林图、中介效应分析、箱线图/热力图、生成Word数据分析报告时触发。覆盖数据体检、清洗、Table 1、主要/次要结局、PSM、4张标准图表、中介效应Bootstrap、docx-js Word报告全流程。药学专用：血肌酐单位换算（mg/dL→µmol/L×88.4）、MoCA认知量表、HOMA-IR、hs-CRP。
agent_created: true
---

# 药学数据分析助手 · STROBE规范完整工作流

## 定位（AI 必读）

本 skill 是 **AI 执行药学真实世界研究数据分析的操作手册**，覆盖从"多sheet Excel数据"到"STROBE规范Word报告"的完整流程。

- **用户**：提供多sheet Excel数据文件（≥5个sheet：患者基本信息、用药记录、随访记录、实验室检查、结局事件，可选变量字典），提出分析要求
- **AI**：读本 skill → Step 1~8 依次执行 → 交付 Word 报告 + 4张图表
- **目标**：一次交付药学期刊风格的 STROBE 规范分析报告

---

## Overview

核心8步流程：

```
Step 1 数据读取 → Step 2 数据体检 → Step 3 数据清洗
→ Step 4 Table 1 三线表 → Step 5 主要结局分析 + PSM
→ Step 6 4张标准图表 → Step 7 中介效应 Bootstrap
→ Step 8 Word 报告生成
```

---

## Step 1：读取多Sheet Excel数据

### 1.1 标准数据表结构

真实世界研究数据通常按以下结构组织：

| Sheet名 | 典型行数 | 关键字段 |
|:---|:---|:---|
| `01_患者基本信息` | ~1200 | 患者ID、年龄、性别、BMI、受教育年限、病程、HbA1c、合并用药种数、基线评分、分组 |
| `02_用药记录` | ~15000 | 患者ID、处方日期、药品名称、单次剂量、每日次数、开药天数 |
| `03_随访记录` | ~6000 | 患者ID、随访日期、随访次序、距基线年数、评分 |
| `04_实验室检查` | ~4000 | 患者ID、检验日期、血肌酐、HbA1c、HOMA-IR、hs-CRP |
| `05_结局事件` | ~1200 | 患者ID、随访终点日期、随访时长、是否发生事件、事件类型、失访原因 |
| 变量字典(可选) | ~40 | 所在表、字段名、类型、说明(⚠️标记) |

### 1.2 读取代码

```python
import pandas as pd, numpy as np

f = r'数据文件路径.xlsx'
xls = pd.ExcelFile(f)
print('Sheets:', xls.sheet_names)  # 先看有哪些sheet

df_basic   = pd.read_excel(f, sheet_name='01_患者基本信息')
df_med     = pd.read_excel(f, sheet_name='02_用药记录')
df_fu      = pd.read_excel(f, sheet_name='03_随访记录')
df_lab     = pd.read_excel(f, sheet_name='04_实验室检查')
df_outcome = pd.read_excel(f, sheet_name='05_结局事件')
```

### 1.3 必须先读变量字典

变量字典标注了各字段的坑（"⚠️ 个人标识"、"⚠️ 日期格式不同"、"⚠️ 单位不统一"），**分析前不读变量字典 = 必然出错**。

---

## Step 2：数据体检

### 2.1 缺失值分析

逐Sheet逐列计算缺失数 + 缺失率：

```python
for s in sheet_names:
    df = pd.read_excel(f, sheet_name=s)
    miss = df.isnull().sum()
    miss_pct = (miss / len(df) * 100).round(2)
    for col in miss[miss > 0].index:
        print(f'{s}.{col}: {miss[col]} ({miss_pct[col]:.1f}%)')
```

正常缺失模式（不是数据错误）：
- 结局事件表"事件类型"缺失 = 未发生事件的患者
- 失访原因缺失 = 未失访患者
- 随访MoCA缺失 = 电话随访无法做量表

### 2.2 异常值识别

必须逐列检查 min/max/mean，关注以下典型异常：

| 变量 | 合理范围 | 异常信号 | 处理 |
|:---|:---|:---|:---|
| 年龄 | 0–120 | >120 或 999(占位符) | 设为缺失 |
| BMI | 10–50 | <10 或 >50 | 设为缺失 |
| MoCA | 0–30 | >30(非标准量表) | 标记注释 |
| 血肌酐 | — | **<10 = 疑似mg/dL单位** | 换算×88.4 |

### 2.3 日期格式检查（必做！）

```python
for s in ['02_用药记录','03_随访记录','04_实验室检查','05_结局事件']:
    df = pd.read_excel(f, sheet_name=s)
    for c in [c for c in df.columns if '日期' in c]:
        print(f'{s}.{c}:', df[c].dropna().head(8).tolist())
```

典型混用：`YYYY-MM-DD` / `DD-MM-YYYY` / `YYYYMMDD`

### 2.4 分类变量编码检查

性别编码常见混用：中文(男/女)、英文(M/F)、数字(1/2)。分组变量可能有空格/全角字符。

---

## Step 3：数据清洗

### 3.1 日期统一解析

```python
def parse_mixed_date(series):
    parsed = []
    for v in series:
        if pd.isna(v): parsed.append(pd.NaT); continue
        v = str(v).strip()
        try:
            if len(v) == 8 and v.isdigit():
                parsed.append(pd.to_datetime(v, format='%Y%m%d'))
            elif '-' in v:
                parts = v.split('-')
                parsed.append(pd.to_datetime(v, format='%Y-%m-%d' if len(parts[0])==4 else '%d-%m-%Y'))
            else:
                parsed.append(pd.to_datetime(v))
        except:
            parsed.append(pd.NaT)
    return pd.Series(parsed, index=series.index)
```

### 3.2 性别编码统一

```python
sex_map = {'男':'M','女':'F','M':'M','F':'F','1':'M','2':'F',1:'M',2:'F'}
df_basic['性别_std'] = df_basic['性别'].map(sex_map)
```

### 3.3 血肌酐单位换算（药学专属）

数值<10的确认为mg/dL，换算公式：**µmol/L = mg/dL × 88.4**

```python
mgdl_mask = df_lab['血肌酐'] < 10
df_lab.loc[mgdl_mask, '血肌酐'] *= 88.4
print(f'血肌酐单位换算: {mgdl_mask.sum()}条 (mg/dL→µmol/L×88.4)')
```

### 3.4 删除隐私字段

```python
df_basic = df_basic.drop(columns=['患者姓名','身份证号','联系电话'])
```

### 3.5 清洗建议清单格式

完成后必须输出结构化清单，格式：
```
1. 统一日期为YYYY-MM-DD (已完成)
2. 血肌酐单位统一为µmol/L (已完成，共XXX条转换)
3. 性别编码统一为M/F (已完成)
4. 年龄>120视为录入错误，建议回查 (本次设为缺失)
...
```

---

## Step 4：Table 1 基线特征三线表

### 4.1 统计方法

| 变量类型 | 描述方式 | 检验方法 |
|:---|:---|:---|
| 连续变量(非正态) | 中位数(IQR) | Mann-Whitney U |
| 连续变量(正态) | 均值±标准差 | 独立样本t检验 |
| 分类变量 | n(%) | χ²检验 |

正态性判断：`scipy.stats.normaltest`，P<0.05 或 n<30 用非参数方法。

### 4.2 P值格式（严格规范）

| 条件 | 格式 | 示例 |
|:---|:---|:---|
| P < 0.001 | `P<0.001` | P<0.001 |
| 0.001 ≤ P < 0.01 | `P=0.00X` | P=0.004 |
| P ≥ 0.01 | `P=0.XXX` | P=0.032 |
| P ≥ 0.05 | `P=0.XXX` | P=0.182 |

### 4.3 三线表格式

**只有3条横线：顶线、表头下线、底线。没有任何竖线。**

```python
# 三线表关键代码
border = {style: BorderStyle.SINGLE, size: 1}
noB = {style: BorderStyle.NONE, size: 0}
borders_none = {top: noB, bottom: noB, left: noB, right: noB}

# 表头行：顶线+底线
# 数据行：无线
# 末行：底线
```

表题在表上方。表头灰底(F2F2F2)便于阅读。脚注标注检验方法。

### 4.4 代码参考

详见 `references/full_analysis.py` 中 `table1_row_continuous()` 和 `table1_row_categorical()`。

---

## Step 5：主要结局分析

### 5.1 变化率计算

对于重复测量设计（如MoCA评分随访），计算每位患者的年均变化率：

```python
first_moca  = df_fu.dropna(subset=['评分']).groupby('ID').first()['评分']
last_moca   = df_fu.dropna(subset=['评分']).groupby('ID').last()['评分']
first_time  = df_fu.dropna(subset=['评分']).groupby('ID').first()['距基线_年']
last_time   = df_fu.dropna(subset=['评分']).groupby('ID').last()['距基线_年']

time_diff = last_time - first_time
annual_change = (last_moca - first_moca) / time_diff  # 仅保留time_diff>0.1的
```

### 5.2 效应量

- **Cohen's d**：(mean1 - mean2) / pooled SD
- **95%CI**：差值 ± 1.96 × SE_diff

### 5.3 次要结局（MCI转化率）

- 列联表 → χ²检验
- OR + 95%CI (Woolf法)

### 5.4 倾向性评分匹配（PSM）

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Step 1: 逻辑回归估计倾向性评分
X = df_psm[协变量列表]  # 含年龄/性别/BMI/病程/HbA1c/用药种数/基线评分
y = (df_psm['分组'] == '治疗组').astype(int)

scaler = StandardScaler()
logreg = LogisticRegression(max_iter=1000)
logreg.fit(scaler.fit_transform(X), y)
df_psm['ps'] = logreg.predict_proba(scaler.transform(X))[:, 1]

# Step 2: 1:1贪婪匹配，caliper = 0.2 × SD(ps)
# Step 3: 匹配后SMD报告，所有SMD<0.1视为平衡
```

PSM后必须输出平衡性报告：每个协变量的匹配前后SMD及变化量。

---

## Step 6：4张标准图表

### 图1：KM生存曲线

```python
from lifelines import KaplanMeierFitter, logrank_test

kmf = KaplanMeierFitter()
for grp in groups:
    kmf.fit(group_df['随访时长'], group_df['是否发生事件'], label=grp_name)
    kmf.plot_survival_function(ax=ax, ci_show=True)
# + logrank_test
```

**格式要求**：图题在图下方（"图1 两组XXX累积发生率比较(Kaplan-Meier曲线)"），标注Log-rank P值。

### 图2：亚组分析森林图

按年龄分层/性别/教育水平/HbA1c分层，计算各亚组Risk Ratio + 95%CI，绘制森林图。x=1.0处画红色虚线。

### 图3：随访变化箱线图/轨迹图

两组分面板，按随访次序展示评分分布。使用`matplotlib.pyplot.boxplot`，patch_artist=True。

### 图4：相关性热力图

```python
import seaborn as sns
corr = df[变量列表].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0, mask=上三角)
```

包含：人口学、病程、化验指标、合并用药、结局事件的相关矩阵。

**所有图表**：dpi=300, bbox_inches='tight', 字体Arial, 中文用英文标签。

---

## Step 7：中介效应分析（Bootstrap 5000次）

### 7.1 检验路径

X(分组) → M(中介变量如HOMA-IR/hs-CRP) → Y(结局如MoCA变化)

### 7.2 Bootstrap实现

```python
def mediation_bootstrap(X, M, Y, n_bootstrap=5000):
    results = {'a':[], 'b':[], 'c':[], 'cp':[], 'ab':[]}
    n = len(X)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        Xb, Mb, Yb = X[idx], M[idx], Y[idx]
        a_coef = np.polyfit(Xb, Mb, 1)[0]           # X→M
        X2 = np.column_stack([np.ones(n), Xb, Mb])
        beta = np.linalg.lstsq(X2, Yb, rcond=None)[0]
        b_coef, cp_coef = beta[2], beta[1]           # M→Y, X→Y(直接)
        c_coef = np.polyfit(Xb, Yb, 1)[0]            # 总效应
        results['a'].append(a_coef); results['b'].append(b_coef)
        results['c'].append(c_coef); results['cp'].append(cp_coef)
        results['ab'].append(a_coef * b_coef)

    ab_est = np.mean(results['ab'])
    ab_ci  = np.percentile(results['ab'], [2.5, 97.5])
    # P值：间接效应分布中≥0或≤0的比例 × 2
    return ab_est, ab_ci, p_value
```

### 7.3 报告格式

| 中介变量 | 总效应c | 直接效应c' | 间接效应a×b(95%CI) | P值 |
|:---|:---|:---|:---|:---|
| HOMA-IR | 0.XXX | 0.XXX | 0.XXX(−0.XXX, 0.XXX) | P=0.XXX |
| hs-CRP  | 0.XXX | 0.XXX | 0.XXX(−0.XXX, 0.XXX) | P=0.XXX |

95%CI包含0 → 中介效应不显著 → 需讨论其他可能机制通路。

---

## Step 8：Word报告生成（docx-js）

### 8.1 依赖与环境

```bash
cd 项目目录 && npm install docx
```

使用 Node.js 22+，`docx` npm 包。详见`references/gen_report.js`。

### 8.2 报告结构

按 STROBE 规范组织章节：
```
封面(标题+数据来源+样本量+日期)
一、数据体检报告(缺失/异常/日期/编码/清洗建议)
二、基线特征 Table 1(三线表)
三、主要结局分析(组间比较+PSM平衡性报告)
四、次要结局分析(MCI转化率+生化指标)
五、图表(4张，每张配解读段落)
六、中介效应分析(Bootstrap 5000次)
七、结论要点(3–5条)
八、图表清单(表1/表2/图1–4)
```

### 8.3 格式规范

- A4纸 (11906 × 16838 DXA)
- 页边距 1英寸
- 标题：一级#1F4E79 16pt加粗，二级#2E75B6 14pt加粗
- 正文：Arial 12pt
- 三线表：只有顶线+表头下线+底线，表头灰底
- 表题在表上方居中加粗，图题在图下方居中斜体
- 页眉：报告标题，页脚：页码

### 8.4 严格禁用词

报告中**绝对不能**出现这些措辞：
- "根据数据显示"
- "由此可见"
- "结果表明具有一定"
- "差异较为明显"
- "呈现出一定趋势"

替代方案：直接陈述数据结论（"XX组年均下降 X.XX分/年，YY组下降 X.XX分/年，组间差值X.XX"）。

### 8.5 图表插入

```javascript
new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: "png",
    data: fs.readFileSync("fig1.png"),
    transformation: { width: 500, height: 380 },
    altText: { title: "图1", description: "图1", name: "图1" }
  })]
})
```

---

## 环境依赖

运行前确保已安装：

```bash
pip install pandas openpyxl matplotlib seaborn scipy statsmodels lifelines scikit-learn
npm install docx
```

Python 3.10+，Node.js 20+。

---

## 参考代码

完整可执行的分析脚本和Word生成脚本位于 `references/` 目录：

- `references/full_analysis.py` — 数据分析全流程（数据体检→Table 1→PSM→图表→中介效应）
- `references/gen_report.js` — docx-js Word报告生成（三线表+图片插入+完整章节）

---

## 执行顺序（AI必读）

当用户触发本 skill 后，按以下顺序执行（不可跳步）：

1. **Read** 数据文件的变量字典sheet（如有），了解数据结构与注意事项
2. **Bash** 运行 `references/full_analysis.py`（先改 INPUT_FILE 路径为实际文件）→ 生成图表PNG + 报告数据JSON
3. **Bash** 运行 `references/gen_report.js`（先修改 report data 路径）→ 生成 .docx
4. **present_files** 交付 .docx 报告 + 4张图表

如果用户数据表结构与标准不同，先读数据理解结构，再按本 skill 流程适配；核心步骤和格式规范不变。
