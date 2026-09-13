---
name: medical-form-designer
description: |
  医疗表单智能设计技能。当用户上传医疗、临床、管理或研究类文档（文献、指南、共识、政策通知、法律、章程、操作规范、行业标准、办法、细则等），需要自动生成表单的场景下使用此技能。
  技能自动完成：(1)识别文件体裁与业务类型；(2)提取关键词、术语和表单目录；(3)按临床/管理/研究三类业务进行数据建模；(4)输出主题HTML、原生HTML、JSON、XML和Excel五种格式的表单文件；(5)可选生成完整Flask+SQLite数据登记系统（含后端API、SQLite存储、历史查询前端）。
  触发词：设计表单、生成表单、表单提取、表单建模、医疗表单、表单设计、form design、根据文件生成表单、登记系统、数据存储。
agent_created: true
---

# 医疗表单智能设计技能（Medical Form Designer）

## 技能概述

本技能将医疗相关文档（指南、共识、政策、操作规范等）自动转化为结构化数据录入表单，输出**主题HTML / 原生HTML / JSON / XML / Excel**五种格式，支持多种表单控件类型，适用于临床、管理和研究三大业务场景。

---

## 标准工作流（四步法）

### STEP 1 — 文件识别

读取上传附件，判断以下两个维度：

**体裁类型（从下列选一或多个）**

| 体裁代码 | 中文名 | 特征描述 |
|---------|--------|---------|
| LIT | 文献 | 有引用、摘要、作者、期刊等结构 |
| GUIDE | 指南 | 有推荐等级、循证依据、诊疗路径 |
| CONS | 共识 | 专家意见、投票结果、建议表述 |
| POLICY | 政策通知 | 文号、发文机关、执行日期 |
| LAW | 法律 | 条款编号、罚则、适用范围 |
| CHARTER | 章程 | 职责条款、组织架构 |
| SOP | 操作规范/流程 | 步骤编号、操作要点、注意事项 |
| STD | 行业/团体标准 | 标准编号、技术要求、验证条款 |
| MEASURE | 办法/细则 | 管理条款、执行规则 |

**业务类型（从下列选一）**

| 业务代码 | 类型 | 判断依据 |
|---------|------|---------|
| CLN | 临床类 | 涉及患者诊断、治疗、检验检查 |
| MGT | 管理类 | 涉及科室管理、规则制度、统计指标 |
| RES | 研究类 | 涉及科研方法、研究对象、验证条件 |

输出格式（示例）：
```
体裁：GUIDE（临床指南）
业务：CLN（临床类）
置信度：0.92
```

---

### STEP 2 — 信息提取

按以下三类策略提取信息：

#### 2.1 通用提取（所有体裁）
- **高频词**：统计词频 Top 20，过滤停用词
- **关键词/术语**：医学术语（ICD码、药品名、检验项目）、管理术语、研究术语
- **表单目录信息**：识别文档中已有的表格标题、附表编号、数据采集项目名称列表
- **章节结构**：提取一级/二级标题，用于后续建模

#### 2.2 按体裁结构提取重点

| 体裁 | 重点提取内容 |
|------|------------|
| GUIDE/CONS | 推荐建议条目、操作流程步骤、诊断标准分级 |
| POLICY/LAW/MEASURE | 执行要求、上报周期、填报字段、责任部门 |
| SOP | 操作步骤名称、判断节点、记录要求 |
| STD | 检验/检测指标名称、合格判定条件 |
| LIT | 研究变量、测量工具、主要结局指标 |
| CHARTER | 岗位职责、考核指标、职务名称 |

#### 2.3 已有表单识别
若文档内含现成表格，直接提取：
- 表单标题
- 列名/字段名
- 字段类型推断（日期、数字、文字、选项等）
- 填写说明

---

### STEP 3 — 数据建模

根据业务类型，选择对应字段体系建模，输出 **字段清单（Field Schema）**：

#### 3.1 临床类（CLN）字段体系

| 字段分组 | 典型字段示例 | 推荐控件 |
|---------|------------|---------|
| **基本信息** | 患者姓名、性别、年龄、住院号、就诊日期、科室、床号 | text, select, date |
| **诊断信息** | 主诊断（ICD编码）、诊断日期、诊断依据、分期分级 | text, select, matrix |
| **治疗信息** | 治疗方案、用药名称+剂量、手术名称、治疗开始日期、治疗效果评估 | text, select, date, textarea |
| **检验检查信息** | 检查项目名称、检查日期、检查结果、参考范围、异常标记 | text, date, matrix |

#### 3.2 管理类（MGT）字段体系

| 字段分组 | 典型字段示例 | 推荐控件 |
|---------|------------|---------|
| **科室信息** | 科室名称、病区、归属部门 | select |
| **工作内容** | 工作项目、执行人员、执行时间、工作量 | text, date, number |
| **规则要求** | 规范依据、执行标准、违规情况描述 | textarea, checkbox |
| **统计指标** | 目标值、实际值、完成率、周期 | number, date, matrix |
| **人员信息** | 负责人姓名、职务、联系方式、签字 | text, select |

#### 3.3 研究类（RES）字段体系

| 字段分组 | 典型字段示例 | 推荐控件 |
|---------|------------|---------|
| **研究方法** | 研究设计类型、随机化方式、盲法设置、统计方法 | select, radio |
| **技术路线** | 实验步骤名称、技术要点、时间节点 | textarea, date |
| **研究对象** | 入组标准、排除标准、年龄范围、基础疾病、知情同意 | checkbox, text, date |
| **研究条件** | 实验设备、试剂规格、环境条件 | text, select |
| **验证方法及要求** | 验证指标、阈值要求、重复次数、合格判定标准 | number, text, matrix |

**字段清单输出格式（JSON Schema）**：
```json
{
  "form_name": "表单名称",
  "business_type": "CLN|MGT|RES",
  "version": "1.0",
  "fields": [
    {
      "id": "field_001",
      "group": "基本信息",
      "label": "患者姓名",
      "type": "text",
      "required": true,
      "placeholder": "请输入患者姓名",
      "validation": "",
      "options": []
    }
  ]
}
```

---

### STEP 4 — 表单自动设计与输出

输出四种格式文件，保存到工作目录的 `form_output/` 子目录下：

#### 4.1 控件类型映射规则

| 字段语义 | 推荐控件类型 | HTML元素 |
|---------|------------|---------|
| 短文本（姓名、编号等） | text | `<input type="text">` |
| 长文本（描述、备注） | textarea | `<textarea>` |
| 是/否判断 | checkbox | `<input type="checkbox">` |
| 单选（性别、分级等） | radio | `<input type="radio">` |
| 多选（并发症、药物等） | multi-select | `<select multiple>` |
| 日期（就诊日期等） | date | `<input type="date">` |
| 矩阵表（多项检查等） | matrix | `<table>` with inputs |
| 附件（报告单等） | file | `<input type="file">` |
| 数字（年龄、剂量等） | number | `<input type="number">` |
| 下拉选择（科室等） | select | `<select>` |

#### 4.2 HTML表单规范

HTML输出样式规范参考 `references/html_style_guide.md`，核心要点：
- 使用语义化HTML5标签
- 字段标签与输入框绑定（label for=id）
- 分组用 `<fieldset>` 和 `<legend>`
- 控件统一宽度和间距
- 必填字段标红星号 `*`
- 日期格式提示：yyyy-mm-dd
- 下拉选择第一项为空白提示文字

#### 4.3 五种输出格式

**① HTML文件（`form_output/form.html`）**
- 完整可浏览的表单页面，含标题、样式、分组展示
- 控件样式：医疗蓝主题 `#1A6FC4`，渐变 Header，`fieldset+legend` 分组
- 响应式两列布局，矩阵型控件全宽
- 带提交按钮（JS收集表单数据）和重置按钮

**② 原生HTML文件（`form_output/form_native.html`）**

纯原生 `<form>` 代码，**不含标题、样式、操作按钮**，零依赖，可直接嵌入HIS/EMR页面。

原生HTML代码示例：
```html
<form>

     <!-- 基本信息 -->
     患者姓名（必填）：<input type="text" name="field_001" placeholder="请输入患者姓名" required><br>
     性别（必填）：<select name="field_002" required>
     <option value="男">男</option>
     <option value="女">女</option>
</select>
     <br>
     年龄（岁）（必填）：<input type="number" name="field_003" placeholder="请输入年龄" min="0" max="150" required><br>
     就诊日期（必填）：<input type="date" name="field_005" required><br>

     <!-- 诊断信息 -->
     高血压分级（必填）：<input type="radio" name="field_008" value="1级"> 1级（140-159/90-99 mmHg）
     <input type="radio" name="field_008" value="2级"> 2级（160-179/100-109 mmHg）
     <input type="radio" name="field_008" value="3级"> 3级（≥180/≥110 mmHg）
     <br>
     并发症/合并症（可多选）：<input type="checkbox" name="field_010" value="糖尿病"> 糖尿病
     <input type="checkbox" name="field_010" value="冠心病"> 冠心病
     <input type="checkbox" name="field_010" value="心力衰竭"> 心力衰竭
     <br>

     <!-- 检验检查信息 -->
     检验检查结果：<br>
     <table border="1" cellpadding="4" cellspacing="0">
     <tr><td>检查项目</td><td>检查日期</td><td>检查结果</td><td>参考范围</td><td>是否异常</td></tr>
     <tr><td><input type="text" placeholder="如血压/血糖/肌酐"></td>
         <td><input type="date"></td>
         <td><input type="text" placeholder="结果+单位"></td>
         <td><input type="text" placeholder=""></td>
         <td><select><option value="">-</option><option value="否">否</option><option value="是">是</option></select></td></tr>
     </table>
     <br>

 </form>
```

**③ JSON文件（`form_output/form_schema.json`）**
- 机器可读字段定义（Field Schema格式见STEP3）
- 可导入低代码平台

**④ XML文件（`form_output/form.xml`）**
- 标准XML格式，兼容医疗信息系统（HIS/EMR）导入
- 字段结构参考 `references/xml_template.md`

**⑤ Excel文件（`form_output/form_template.xlsx`）**
- 第1列：字段名（中文）
- 第2列：字段编码
- 第3列：所属分组
- 第4列：控件类型（带数据验证下拉）
- 第5列：是否必填
- 第6列：可选项（分号分隔）
- 第7列：填写示例
- Sheet2：控件类型说明

---

### STEP 5（可选）— 完整登记系统生成

当用户需要**可运行的数据录入+存储+历史查询系统**时，调用 `scripts/generate_system.py` 生成完整 Flask + SQLite 项目包。

#### 5.1 系统生成命令

```bash
python scripts/generate_system.py <schema.json> --outdir form_output
```

或在 `generate_form.py` 中追加参数：
```bash
python scripts/generate_form.py <schema.json> --outdir form_output --with-system
```

#### 5.2 生成目录结构

```
form_output/
└── 表单名_registry/
    ├── app.py               # Flask 后端服务（含所有API路由）
    ├── schema.json          # 表单字段定义（Schema副本）
    ├── requirements.txt     # 依赖：flask
    ├── start.bat            # Windows一键启动（自动安装Flask+打开浏览器）
    ├── start.sh             # Linux/Mac一键启动（自动安装Flask+打开浏览器）
    ├── templates/
    │   └── index.html       # 前端SPA页面（表单录入+历史查询）
    ├── data/
    │   ├── registry.db      # SQLite数据库（运行时自动创建）
    │   └── uploads/         # 附件目录
    └── README.md
```

#### 5.3 SQLite 数据模型

**主数据表 `form_records`**：自动根据 schema.json 中字段动态创建列

| 系统列 | 类型 | 说明 |
|--------|------|------|
| `id` | INTEGER PK | 自增主键 |
| `created_at` | TEXT | 创建时间（YYYY-MM-DD HH:MM:SS） |
| `updated_at` | TEXT | 最近更新时间 |
| `submitter` | TEXT | 提交人标识 |
| `status` | TEXT | 状态：submitted/draft/deleted |
| `field_xxx` | TEXT/REAL | 各字段数据（多选/矩阵存JSON字符串） |

**审计日志表 `audit_log`**：
- 记录每次 CREATE / UPDATE / DELETE 操作
- 保存操作前快照（snapshot），支持数据恢复

#### 5.4 前端功能说明

| 功能模块 | 说明 |
|---------|------|
| 📝 新增记录 | 动态渲染所有字段，支持矩阵添加行 |
| 📊 历史查询 | 关键词搜索 + 日期范围 + 状态过滤 + 分页 |
| 📄 记录详情 | 弹窗查看完整字段内容 |
| 🗑️ 软删除 | 标记为deleted，保留在审计日志中 |
| ⬇️ CSV导出 | 导出全部有效记录（UTF-8 BOM，兼容Excel） |
| 📊 统计面板 | 顶部导航栏实时显示总记录数和今日新增 |

#### 5.5 API 接口说明

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schema` | 获取表单Schema定义 |
| POST | `/api/records` | 新增记录 |
| GET | `/api/records?page=1&search=&date_from=&status=` | 查询历史记录 |
| GET | `/api/records/:id` | 获取单条记录 |
| PUT | `/api/records/:id` | 更新记录 |
| DELETE | `/api/records/:id` | 软删除记录 |
| GET | `/api/stats` | 统计：总数+今日新增 |
| GET | `/api/export` | 导出CSV |

#### 5.6 启动方式

**Windows（推荐双击 `start.bat`）：**
```batch
:: start.bat 执行流程：
:: 1. 自动检测Python环境
:: 2. pip install flask（静默安装，跳过已安装）
:: 3. 创建 data/ 目录
:: 4. 启动 Flask 服务
:: 5. 延迟2秒后自动在默认浏览器打开 http://localhost:5000
:: 6. 按 Ctrl+C 停止服务
start.bat
```

**Linux / macOS（推荐运行 `start.sh`）：**
```bash
chmod +x start.sh
./start.sh
# 自动安装Flask，启动服务，macOS自动打开浏览器
```

**手动启动：**
```bash
pip install flask
python app.py
# → 浏览器访问 http://localhost:5000
```

**BAT脚本内容说明：**

| 步骤 | 说明 |
|------|------|
| `chcp 65001` | 切换到UTF-8编码，避免中文乱码 |
| Python检测 | 若未安装Python，提示下载地址并退出 |
| Flask安装 | `pip install flask -q` 静默安装 |
| 数据目录 | 自动创建 `data/` 目录（首次运行） |
| 延迟打开浏览器 | 后台启动，等待2秒服务就绪后自动打开 |
| `pause` | 服务停止后保持终端可见，方便排查日志 |

---

## 执行脚本

| 脚本 | 功能 |
|-----|------|
| `scripts/generate_form.py` | 根据字段JSON生成五种格式表单文件（`--with-system` 同时生成登记系统） |
| `scripts/generate_system.py` | 生成完整Flask+SQLite登记系统 |
| `scripts/extract_fields.py` | 文本信息提取与字段推断工具（辅助STEP2-3） |

---

## 注意事项

1. 若附件为PDF/DOCX格式，优先调用 `markitdown` 或 `pdf` skill先转为文本，再进行信息提取
2. 若文档包含多张现有表格，逐一提取并合并去重后再建模
3. 若业务类型不明确，输出两套字段供用户选择
4. HTML输出控件中，option选项需从文档内容实际提取，不得凭空捏造
5. 表单字段顺序遵循：基本信息 → 核心业务信息 → 辅助记录信息 → 签名/备注
6. 登记系统生成完毕后，务必在用户当前工作目录中执行 `python app.py` 启动服务
7. 多选/矩阵字段在SQLite中以JSON字符串存储，查询时自动反序列化为列表/字典
