# MedDRA 编码指引

MedDRA（监管活动医学词典，Medical Dictionary for Regulatory Activities）是药品不良反应个例报告（ICSR）与定期报告的国际标准医学术语集，由 ICH 维护、WHO UMC 分发。正确编码是把临床描述转化为可上报、可统计术语的关键一步。

> ⚠️ MedDRA 为受版权保护的授权术语库，本 skill **无法离线访问完整字典**。以下提供层级结构与编码方法，AI 给出的 PT/LLT 名称仅供初拟，**最终编码须由药师用机构授权的 MedDRA 工具确认**。

## 一、五级层级结构（自上而下）

| 层级 | 英文 | 含义 | 上报用途 |
|------|------|------|----------|
| SOC | System Organ Class | 系统器官分类 | 主要分组维度 |
| HLGT | High Level Group Term | 高级别组术语 | 中间归类 |
| HLT | High Level Term | 高级术语 | 中间归类 |
| PT | Preferred Term | 首选术语 | **个例报告主要编码对象** |
| LLT | Lowest Level Term | 最低级别术语 | 最贴近原始描述 |

## 二、编码步骤

1. 提取原始描述中的每一处「体征 / 症状 / 疾病诊断 / 检查异常」。
2. 为每条映射到最合适的 **PT**（首选术语）。
3. 确定该 PT 所属的 **SOC**（注意：一个 PT 可能归属多个 SOC，ICSR 中需选「主要 SO C」——通常指最严重或最相关的系统）。
4. 记录 PT 与 SOC；如能判断则一并给出 LLT。
5. 严重标准（按 ICH E2A / 国内《办法》）单独判定，不依赖编码：死亡、危及生命、住院或住院延长、永久或显著残疾、先天性异常、其他重要医学事件。

## 三、常见 ADR 的 SOC 映射示例（仅作提示，须用授权字典核对）

| 临床表现 | 常见 SOC | 可能 PT（示例，待核实） |
|----------|----------|--------------------------|
| 皮疹、瘙痒、荨麻疹 | 皮肤及皮下组织类疾病 | Rash, Pruritus, Urticaria |
| 恶心、呕吐、腹泻、转氨酶升高 | 胃肠系统疾病 / 肝胆系统疾病 | Nausea, Vomiting, Diarrhoea, Hepatic enzyme increased |
| 头痛、头晕、失眠 | 各类神经系统疾病 | Headache, Dizziness, Insomnia |
| 白细胞减少、血小板减少 | 血液及淋巴系统疾病 | Leukopenia, Thrombocytopenia |
| 心动过速、QT 延长 | 心脏器官疾病 | Tachycardia, QT prolonged |
| 过敏性休克 | 免疫系统疾病 / 全身性疾病 | Anaphylactic shock, Anaphylactic reaction |

## 四、注意事项

- 同一临床表现在不同时期版本 MedDRA 中 PT 名称可能变化，编码须注明所用 MedDRA 版本。
- 「不良反应名称」原始文字与编码 PT 都应在报告中并列保留，便于追溯。
- 若无法用 MedDRA 准确表达（如罕见中医证候），在报告中说明并建议药师人工裁定。
