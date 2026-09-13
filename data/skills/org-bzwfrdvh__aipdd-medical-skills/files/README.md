# Medical Skills（医学分析推理·聚合技能包）

遵循 WorkBuddy / Agent Skills 规格的医疗 AI 技能集合。根目录 `SKILL.md` 是唯一技能入口（frontmatter `name: 医学分析推理`），索引并调度各子技能；子技能指令文件以 `MODULE.md` 命名（非 SKILL.md），避免被 WorkBuddy 重复识别为独立技能。

## 结构

```
医学分析推理/
├── SKILL.md                        ← 唯一入口，索引子技能
├── README.md                       ← 本文件
└── medgemma-medical-analysis/      ← 子技能：MedGemma 1.5 4B 医疗分析
    ├── MODULE.md                   ← 子技能指令（单独安装时重命名为 SKILL.md）
    ├── scripts/
    ├── references/
    └── assets/
```

## 子技能列表

| 子技能 | 模块文件 | 能力 |
| --- | --- | --- |
| medgemma-medical-analysis | medgemma-medical-analysis/MODULE.md | 通过 NewAPI 调用 Google MedGemma 1.5 4B：胸片/CT/MRI/病理/皮肤/眼底影像分析、解剖定位、化验单结构化提取、EHR 解读、临床推理、医学报告生成 |

## 安装

```bash
cp -r 医学分析推理 ~/.workbuddy/skills/
```

安装目录名必须与 SKILL.md frontmatter 的 `name` 一致（当前为 `医学分析推理`）。发送 `/reload-skills` 或重启客户端生效。

> 注意：本项目仓库目录名为 `medgemma-skills`，安装时请将目录重命名为 `医学分析推理`（或同步修改 SKILL.md frontmatter 的 `name` 为英文标识后再安装，避免部分工具链对中文路径兼容性问题），否则技能可能无法被识别。

## 配置

首次使用前运行子技能配置脚本（详见 medgemma-medical-analysis/MODULE.md）：

```bash
# 基本配置（baseUrl + apiKey 必填）
echo '{"baseUrl": "https://your-newapi.example.com", "apiKey": "sk-xxx"}' | node medgemma-medical-analysis/scripts/configure.js

# 可选：同时指定模型名（中转站上模型名与默认值不同时）
echo '{"baseUrl": "https://your-newapi.example.com", "apiKey": "sk-xxx", "model": "medgemma-1.5-4b-it"}' | node medgemma-medical-analysis/scripts/configure.js
```

配置读取优先级：`config.json` > 环境变量 `NEWAPI_BASE_URL` / `NEWAPI_API_KEY`；可用 `NEWAPI_CONFIG` 指定配置文件路径。模型名优先级：`--model` > `config.json` 的 `model` > 环境变量 `MEDGEMMA_MODEL` > 默认 `medgemma-1.5-4b-it`。

## 验证连接

配置后先用 `--ping` 确认服务可达并列出中转站上可用模型（用于确认实际模型名）：

```bash
node medgemma-medical-analysis/scripts/medgemma.js --ping
```

返回 `{"success":true,...,"models":{...}}` 即连通；`models.data` 中即为可用的模型 ID 列表。

## 快速开始

```bash
# 胸片解读
node medgemma-medical-analysis/scripts/medgemma.js --task cxr \
  --image /path/to/chest-xray.png --question "描述这张胸片的主要发现"

# 化验单结构化提取（图像）
node medgemma-medical-analysis/scripts/medgemma.js --task lab-report \
  --image /path/to/lab-report.png

# 临床推理问答（文本）
node medgemma-medical-analysis/scripts/medgemma.js --task clinical-reasoning \
  --text "58岁男性，胸痛3小时，心电图示ST段抬高..." --question "鉴别诊断有哪些？"
```

支持的图像格式：PNG/JPEG/WebP/GIF/BMP/TIFF。**DICOM 需先转换为 PNG/JPEG**（可用 `scripts/prepare-image.js` 一键转换并缩放到 896x896）：

```bash
node medgemma-medical-analysis/scripts/prepare-image.js /path/to/scan.dcm
node medgemma-medical-analysis/scripts/medgemma.js --task radiology-2d --image /path/to/scan.png
```

3D CT/MRI 体数据、视频需预处理为切片图像。

## 故障排查

- 脚本报 `missing base URL` / `missing API key`：未配置服务地址，运行配置脚本或设置环境变量。
- 脚本报 `HTTP error 404`：模型名不对或不可用，先运行 `--ping` 查看中转站可用模型，再通过 `--model` 或配置 `model` 指定正确模型名。
- 脚本报 `request timed out`：请求超过 120 秒，检查网络与中转站负载。
- 多图场景结果异常：确认传图顺序（纵向对比第一张为当前/最新）与图像尺寸（建议 896x896）。
- DICOM 文件报 `cannot read image file`：先用 `scripts/prepare-image.js` 转换（需安装 ffmpeg 或 dcmtk）。

## 合规提醒

所有分析结果仅供医学研究、教学与辅助参考，不可作为临床诊断依据；最终诊断请以执业医师意见为准。患者数据发送前请脱敏。
