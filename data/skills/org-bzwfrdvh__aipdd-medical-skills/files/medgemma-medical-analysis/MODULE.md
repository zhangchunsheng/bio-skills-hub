---
name: medgemma-medical-analysis
description: Analyzes medical images and clinical text using Google MedGemma 1.5 4B through the user's NewAPI relay. Use when the user asks to interpret chest X-rays, CT, MRI, pathology slides, dermatology or fundus images, extract structured data from lab reports, interpret EHR or medical records, generate medical reports, or answer clinical reasoning questions, and a NewAPI endpoint serving medgemma-1.5-4b-it is available.
license: MIT
allowed-tools: Bash,Read,Write
metadata:
  runtime: node >= 18
  model: medgemma-1.5-4b-it
---

> 本文件是「医学分析推理（Medical Skills）」聚合技能包的子技能指令模块，非独立 SKILL.md 入口。
> 如需将本子技能单独安装为独立技能，请将本文件重命名为 SKILL.md 后放入 `~/.workbuddy/skills/medgemma-medical-analysis/`。

# MedGemma Medical Analysis

通过用户自建 NewAPI 服务调用 Google MedGemma 1.5 4B 多模态模型进行医疗分析的技能。只调用用户配置的服务地址，不猜测地址、模型或参数。

## 配置流程

1. 首次使用前要求用户提供 NewAPI 中转站服务地址（baseUrl）和 API Key，并确认中转站已提供 `medgemma-1.5-4b-it` 模型（模型名以中转站实际为准，可用 `--ping` 查看可用模型列表）。
2. 运行 `node scripts/configure.js`，通过标准输入传入 JSON：`{"baseUrl": "https://your-newapi.example.com", "apiKey": "sk-xxx"}`；可选 `"model"` 字段一并指定模型名（中转站模型名与默认值不同时）。
3. 不要把 API Key 回显到对话、日志或最终报告中；建议配置文件设置权限：`chmod 600 config.json`。
4. 配置读取优先级：`config.json` > 环境变量 `NEWAPI_BASE_URL` / `NEWAPI_API_KEY`。配置文件默认路径为 `~/.workbuddy/skills/medgemma-medical-analysis/config.json`；可用环境变量 `NEWAPI_CONFIG` 指定配置文件路径，`WORKBUDDY_HOME` / `OPENCLAW_HOME` / `OPENCLAW_STATE_DIR` 可覆盖默认目录（configure.js 与 medgemma.js 行为一致）。模型名优先级：`--model` > `config.json` 的 `model` > 环境变量 `MEDGEMMA_MODEL` > 默认 `medgemma-1.5-4b-it`。
5. 配置完成后先运行 `node scripts/medgemma.js --ping` 验证连通性并确认模型名，再进入正式调用。

## 调用规则

- 模型名优先级：`--model` > `config.json` 的 `model` > 环境变量 `MEDGEMMA_MODEL` > 默认 `medgemma-1.5-4b-it`。
- 用户没有指定模型且默认模型不可用时（404），运行 `--ping` 查看中转站可用模型，再与用户确认正确的模型名，不要静默更换模型。
- 本地图像自动转为 base64 data URI 上传；远程图像必须使用 HTTPS URL。
- 图像建议 896x896 归一化后发送（脚本不做图像预处理，需调用方提前准备或依赖服务端自动处理），单次最多传 4 张（纵向对比、病理多 patch 场景），超出部分先裁剪或拼接再发送。
- 支持的图像格式：PNG/JPEG/WebP/GIF/BMP/TIFF。**DICOM（.dcm）不在支持范围**，需先用工具（如 dcm2png / dcmj2pnm / 医学影像查看器）转换为 PNG/JPEG 后再传入。
- 视频、3D CT/MRI 体数据需按后端部署要求预处理（如抽取切片）后再以图像形式传入，脚本不处理体积数据格式。
- 纵向胸片对比（`cxr-longitudinal`）传图顺序固定：**第一张为当前/最新影像，后续为历史影像**，请按此顺序组织 `--image`。
- 请求超时 120 秒；上游服务失败（网络错误、HTTP 错误、超时）时保留原始错误信息输出，不要自动换模型重试。
- 结果必须报告使用的模型、任务类型和关键发现；脚本只输出 JSON，将其转换为简洁的中文回复。

## 模型限制（来自官方 model card）

- 官方评测以单图任务为主，多图理解（纵向对比、WSI 多 patch）为 1.5 新增能力但未经全面评测，对多图结果需谨慎解读。
- 模型未针对多轮对话优化；每次调用为独立单轮请求。
- 模型对 prompt 较敏感，建议使用内置任务模板，不要随意改写系统提示词。
- 训练与评测以英文数据为主；中文提问时建议在 `--question` 中补充关键医学词汇的英文对照。

## 医疗合规规则

- 所有分析结果仅供医学研究、教学与辅助参考，不可作为临床诊断依据。
- 在回复中附免责声明：最终诊断请以执业医师意见为准。
- 不提供治疗建议；涉及用药、手术等决策时建议用户咨询执业医师。

## 使用脚本

```bash
# 验证服务连通并列出可用模型（配置后先执行一次）
node scripts/medgemma.js --ping

# 胸片解读
node scripts/medgemma.js --task cxr --image /path/to/chest-xray.png --question "描述这张胸片的主要发现"

# 纵向胸片对比（当前 vs 历史，按顺序传图）
node scripts/medgemma.js --task cxr-longitudinal --image /path/to/current.png,/path/to/prior.png

# 皮肤影像分析（远程 URL）
node scripts/medgemma.js --task derm --image https://example.com/lesion.jpg

# 化验单结构化提取（图像）
node scripts/medgemma.js --task lab-report --image /path/to/lab-report.png

# 化验单结构化提取（文本）
node scripts/medgemma.js --task lab-report --text "Hb 13.2 g/dL; WBC 8.1 x10^9/L; ..."

# EHR / 病历解读
node scripts/medgemma.js --task ehr --text-file /path/to/record.txt --question "总结关键异常"

# 临床推理问答
node scripts/medgemma.js --task clinical-reasoning --text "58岁男性，胸痛3小时，心电图示ST段抬高..." --question "鉴别诊断有哪些？"

# 生成医学报告并写入文件
node scripts/medgemma.js --task report-generation --image /path/to/ct-slice.png --output ./report.md --context "患者女，45岁，咳嗽两周"
```

可选参数：`--task`、`--question`、`--text`、`--text-file`、`--image`（逗号分隔多图，第一张为当前/最新）、`--context`、`--model`、`--max-tokens`（默认 2048，上限 8192）、`--temperature`（默认 0.1）、`--output`、`--ping`（仅验证连接）。

## 图像准备

`medgemma.js` 只接受 PNG/JPEG/WebP/GIF/BMP/TIFF；DICOM（.dcm）及非常见格式先用 `scripts/prepare-image.js` 转换并缩放到 896x896：

```bash
# DICOM → PNG（需安装 ffmpeg 或 dcmtk）
node scripts/prepare-image.js /path/to/scan.dcm

# 其他格式（HEIC/TIFF 等），macOS 使用自带 sips
node scripts/prepare-image.js /path/to/photo.heic --size 896

# 指定输出文件
node scripts/prepare-image.js /path/to/scan.dcm --output /tmp/scan.png
```

## 任务类型

`--task` 支持：`cxr`（胸片）、`cxr-longitudinal`（纵向胸片对比）、`radiology-2d`（通用 2D 影像）、`pathology`（病理切片）、`derm`（皮肤影像）、`eyefundus`（眼底影像）、`anatomy-loc`（解剖定位）、`lab-report`（化验单提取）、`ehr`（病历解读）、`clinical-reasoning`（临床推理）、`report-generation`（报告生成）。

For model capabilities, refer to references/medgemma-capabilities.md
For prompt templates per task type, refer to references/prompt-templates.md
Fill assets/medical-report-template.md when writing reports via --output.
