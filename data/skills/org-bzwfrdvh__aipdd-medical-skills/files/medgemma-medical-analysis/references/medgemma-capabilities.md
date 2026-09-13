# MedGemma 1.5 4B 模型能力说明

## 模型概况

- 模型：Google MedGemma 1.5 4B（多模态，2026-01-13 发布，v1.5.0），基于 Gemma 3 架构，decoder-only Transformer（GQA 注意力）。
- 参数规模：4B（bfloat16 推理），计算高效，适合本地/私有化部署；官方定位为"计算高效的起点模型"。
- 输入：文本 + 图像（SigLIP 图像编码器，经去标识化医学数据预训练：胸片、皮肤、眼底、病理等）。
- 输出：纯文本。
- 上下文：至少 128K tokens；输出上限 8192 tokens。
- 图像编码：归一化至 896x896，每张图编码为 256 tokens，单次最多 4 张。
- 常用模型标识（以部署为准）：`medgemma-1.5-4b-it`（Hugging Face: google/medgemma-1.5-4b-it）。
- 许可：Health AI Developer Foundations terms of use（免费用于研究与商业用途，需遵守其条款）。

## 支持的分析任务

| 任务 | 说明 | 输入建议 |
| --- | --- | --- |
| 高维医学影像（CT/MRI 3D） | 三维体数据解读，如病灶检测（官方内部基准：CT 分类 Macro accuracy 61.1，MRI 64.7） | 按部署方要求预处理为切片图像后传入（建议 2-4 张代表性切片） |
| 全切片病理影像（WSI） | 多 patch 同时解读（官方内部基准 WSI-Path ROUGE 49.4，较前代 2.2 大幅提升） | 最多 4 张 patch 图，按空间位置组织 |
| 纵向医学影像 | 胸片当前 vs 历史对比（进展/改善/新发；MS-CXR-T Macro accuracy 65.7） | 第一张为当前/最新，后续为历史，按此顺序传图 |
| 解剖定位 | 胸片解剖结构与病灶 bounding box 定位（Chest ImaGenome IoU 38.0） | 单张胸片，坐标归一化 0-1000 |
| 医学文档理解 | 化验单/检验报告中提取值、单位等结构化数据（PDF/图像转 JSON Macro F1 71-91） | 文本或图像 |
| EHR 理解 | 电子病历文本解读（EHRQA 89.6、EHRNoteQA 80.4） | 文本 |
| 医学文本推理 | 医学问答、临床推理（MedQA 4-op 69.1、MedMCQA 59.8） | 文本 |
| 2D 影像解读 | 胸片、皮肤、眼底、病理切片的 2D 分类与描述 | 单张图像 |
| 医学报告生成 | 胸片报告生成（MIMIC-CXR RadGraph F1 27.2） | 图像 + 临床背景文本 |

## 已知表现（官方 model card 评测摘要，MedGemma 1.5 4B）

### 影像

- 胸片分类：MIMIC-CXR 5 项 Macro F1 ≈ 89.5；CheXpert 5 项 ≈ 48.2；CXR14 3 项 ≈ 48.4。
- 3D 影像：CT 分类 Macro accuracy ≈ 61.1；MRI 分类 Macro accuracy ≈ 64.7（较前代 51.3 提升显著）。
- 眼底（EyePACS）分类准确率 ≈ 76.8；皮肤（US-DermMCQA）≈ 73.5；病理（PathMCQA）≈ 70.0。
- 全切片病理（WSI-Path）ROUGE ≈ 49.4；纵向疾病进展（MS-CXR-T）Macro accuracy ≈ 65.7。
- 解剖定位（Chest ImaGenome）IoU ≈ 38.0（较前代 3.1 提升 35 个百分点）。
- 医学 VQA：VQA-RAD 闭集准确率 ≈ 70.2；SLAKE 闭集 ≈ 82.8（但 SLAKE 问答格式优化弱于前代，官方标注需微调）。

### 文本

- MedQA（4-op）≈ 69.1；MedMCQA ≈ 59.8；PubMedQA ≈ 68.2；MMLU Med ≈ 69.6；AfriMed-QA ≈ 56.0。
- EHR：EHRQA ≈ 89.6（较前代 67.6 大幅提升）；EHRNoteQA ≈ 80.4。

### 文档理解（化验单）

- PDF→JSON 化验数据提取 Macro F1 ≈ 91.0（内部 EHR 数据集 2）/ 71.0（数据集 3）；PNG 图像化验单 Macro F1 ≈ 85.0。

## 使用限制（官方声明）

- 官方评测以单图任务为主；多图理解（纵向对比、WSI 多 patch）为 1.5 新增能力，未经全面评测，结果需谨慎解读。
- 模型未针对多轮对话优化；对 prompt 较敏感（比 Gemma 3 更敏感），建议使用固定任务模板。
- 训练与评测以英文数据为主；用于其他语言时需验证表现。
- 具体下游任务建议微调（官方定位为"起点模型"，需开发者验证与适配）。
- 输出不用于直接临床诊断、患者管理决策或治疗建议。

## 合规与隐私

- 供医学研究、教学与辅助参考，不构成临床诊断。
- 最终诊断以执业医师意见为准；不提供治疗处方建议。
- 图像会以 base64 或 URL 形式发送至用户配置的 NewAPI 服务，注意患者数据脱敏与隐私合规。
