# 文献数据提取表规范

> 基于用户提供的SPS病例报告文献汇总表抽象出的通用规范，适用于任何麻醉学病例报告的文献对照分析。

## 标准列结构（11列，4大分组）

| 列号 | 分组 | 列名 | 提取内容 | 数据类型 |
|:---|:---|:---|:---|:---|
| 1 | A. 文献信息 | 年份 | 发表年份 | 整数 |
| 2 | | 参考文档标题 | 论文标题（过长时可缩写至60字符内） | 文本 |
| 3 | | 作者 | 第一作者 et al. | 文本 |
| 4 | | 期刊 | 期刊名标准缩写 | 文本 |
| 5 | B. 患者 | 病例数/基本资料 | 例数，年龄，性别，身高/体重（如有BMI） | 文本 |
| 6 | | 合并症 | 相关合并症 + 术前用药详情 | 文本 |
| 7 | C. 麻醉方案 | 手术 | 术式名称 | 文本 |
| 8 | | 麻醉方式 | 麻醉技术分类（TIVA/GA+Inhalation/Regional/CSE等） | 分类 |
| 9 | | 吸入药 | 药物名 + 浓度/剂量 | 文本 |
| 10 | | 静脉药 | 诱导药物+剂量；维持药物+输注速率 | 文本 |
| 11 | | 阿片类/区域麻醉药 | 阿片类药物+剂量；区域麻醉药物+浓度+容量 | 文本 |
| 12 | | 肌松药及拮抗 | NMBA种类+剂量；拮抗剂种类+剂量；"未使用" | 文本 |
| 13 | D. 结局 | 并发症/结局 | 并发症类型 + 处理措施 + 转归 | 文本 |

## 提取规则

### 通用规则

1. **本病例独占首行**：用 `**本病例**` 加粗标注，与文献病例明确区分
2. **文献病例按年份降序排列**：同一年份按第一作者字母序
3. **缺失值标注**：文献未提及的信息标注 `—`（em dash），区别于临床决策"未使用"
4. **"未使用"标注**：文献明确说明不使用某类药物时，标注"未使用"
5. **剂量保留原文献单位**：不进行跨单位换算（mg不转µg，避免换算误差）
6. **同一文献多次麻醉**：分拆为独立行，标注"病例X-第1次"、"病例X-第2次"
7. **非手术病例**：若病例不涉及手术（如丙泊酚治疗性用药），仍纳入表格但标注"非手术"

### 麻醉方式分类标准

| 分类 | 涵盖 | 缩写 |
|:---|:---|:---|
| 全凭静脉麻醉 | 仅使用静脉麻醉药，无吸入药 | TIVA |
| 吸入麻醉（全麻） | 使用挥发性麻醉药维持 | GA + Inhalation |
| 静吸复合麻醉 | TIVA + 吸入药联用 | Balanced GA |
| 区域麻醉 | 椎管内/神经阻滞（可能联合镇静） | RA |
| 腰硬联合麻醉 | 脊麻 + 硬膜外 | CSE |
| 监测下麻醉管理 | 镇静 + 局麻 | MAC |
| 全身麻醉联合区域麻醉 | GA + 椎管内/神经阻滞 | GA + RA |

### 并发症编码参考

| 类别 | 具体并发症 |
|:---|:---|
| 肌松相关 | 术后肌张力减退(prolonged hypotonia)、拔管延迟(delayed extubation)、残余肌松(residual neuromuscular blockade) |
| 血流动力学 | 低血压(hypotension)、高血压(hypertension)、心律失常(arrhythmia) |
| 呼吸系统 | 低氧血症(hypoxemia)、支气管痉挛(bronchospasm)、术后机械通气>24h |
| 神经系统 | 术后痉挛加重(worsened spasms)、意识恢复延迟(delayed emergence)、术后认知功能障碍(POCD) |
| 其他 | PONV、过敏反应、手术部位感染 |

## 表格模板

```markdown
**Table 1. Summary of Published Case Reports of Anesthetic Management in Patients with [Disease]**

| Year | Title | Author | Journal | Patient(s) | Comorbidities | Surgery | Anesthetic Technique | Inhalational Agents | IV Agents | Opioids/Regional | NMBA & Reversal | Complications/Outcome |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **本病例** | — | — | — | [age]y, [M/F] | [comorbidities + preop meds] | [procedure] | [technique] | [agents] | [agents + doses] | [agents + doses] | [agents + doses] | [outcome] |
| [YYYY] | [Title] | [Author] | [Journal] | [demographics] | [comorbidities] | [surgery] | [technique] | [agents] | [agents] | [agents] | [NMBA + reversal] | [outcome] |
```

## 定性分析维度（基于表格数据的自动化分析）

表格生成后，按以下维度系统分析：

1. **麻醉方式选择**：统计各类麻醉方式的病例数 → 识别主流方案 → 定位本病例
2. **肌松药安全性**：NMBA使用例数 / 未使用例数 / 使用后并发症率
3. **吸入药 vs TIVA**：制作2×2表（吸入药± × 并发症±），描述趋势
4. **拮抗策略比较**：Sugammadex vs Neostigmine使用频率和成功率
5. **并发症因果链**：归纳并发症类型 → 发生条件 → 处理 → 转归

## 定量分析建议模板

```
基于Table 1的N例报告，以下统计方法可供未来汇总分析参考：
- 二分类结局（并发症有/无）：Fisher精确检验（N<30）
- 连续变量（住院天数）：Mann-Whitney U检验
- 多变量分析（若N≥30）：逻辑回归识别独立预测因子
- 样本量需求：[基于当前效应量趋势的估算]
⚠️ 当前N值不足以支持统计推断，以上仅为方向性建议。
```
