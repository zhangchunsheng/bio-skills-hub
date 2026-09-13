# 解读字段规范（interpretation schema）

每条入库条目（论文或产品）的 `interpretation` 采用固定嵌套结构，保证看板渲染、Markdown 导出、知识图谱节点抽取一致。

## 顶层 entry 字段
```json
{
  "id": "YYYY-MM-DD-<slug>",      // 唯一 id；论文用 pmid，产品用发布日期+缩写
  "date": "YYYY-MM-DD",           // 入库日期
  "type": "paper | product",      // 论文 or 官方AI产品
  "title": "英文标题",
  "titleZh": "中文标题",
  "source": "PubMed | FDA/官网 | ...",
  "pmid": "42632516",             // 论文填，产品留空串
  "doi": "...",
  "journal": "期刊/厂商",
  "year": 2026,
  "if": 13.8,                     // 影响因子（PubMed 不返回，用期刊映射近似；产品填 null）
  "citations": 0,                 // 引用数（Europe PMC 取；新文多为 0）
  "aiTags": ["医学影像", "深度学习", "..."],
  "url": "原文/官网链接",
  "interpretation": { ... },      // 见下
  "status": "draft",              // draft / published
  "publishedUrl": ""              // 发布后回填
}
```

## interpretation 嵌套结构（重点）
- `background`（字符串）：背景与未满足的临床需求。
- `method`（**对象，非字符串**），含 5 子项，渲染顺序固定：
  - `algorithm`：具体算法 / 模型
  - `datasets`：采用的数据集
  - `dataVolume`：数据量（例数 / 图像数）
  - `pipeline`：技术流程
  - `evaluation`：**测试/验证**（敏感度、特异度、AUC 等）；注意它放在 method 内，不是顶层字段
- `clinicalStatus`（**对象**），含 3 子项：
  - `stage`：所处阶段（研究中 / 已上市 / 规模化部署…）
  - `approval`：审批阶段（FDA De Novo / NMPA 三类证 / CE / 未获批…）
  - `commercial`：**商业化阶段**；若已进入商业化，必须给出**公司 / 融资 / 销售部署 / 营收医保**等可查证信息；未商业化则写商业化机会或潜在障碍
- `similar`（字符串）：相似研究 / 产品及差异点
- `advantages`（字符串）：优势 / 特点（3–4 条，基于事实）
- `limitations`（字符串）：局限 / 风险（不得回避缺陷）

## 渲染顺序约定
看板与 Markdown 导出统一顺序：`background → method(算法/数据集/数据量/流程/测试验证) → clinicalStatus(阶段/审批/商业化) → advantages → limitations → similar`。
**禁止**在 `similar` 之后重复渲染 `advantages`/`limitations`。

## 知识图谱节点类型
- `entry`：条目本身（前缀 e_）
- `method`：方法/算法（m_）
- `scene`：临床场景（s_）
- `org`：机构/公司（o_）
- `dataset`：数据集（d_）
- `metric`：指标（met_）
- `approval`：审批/监管（reg_）

边 `relation` 用「采用 / 场景 / 公司 / 数据 / 指标 / 获批 / 相似」。两条目共享同一 `method` 或 `org` 节点时自动形成「相似」边。
