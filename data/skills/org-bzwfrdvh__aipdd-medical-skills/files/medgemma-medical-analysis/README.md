# medgemma-medical-analysis（WorkBuddy 子技能）

通过用户自建 NewAPI 服务调用 Google MedGemma 1.5 4B 多模态模型进行医疗分析的技能，遵循 WorkBuddy / Agent Skills 规格。

本技能是「医学分析推理（Medical Skills）」聚合技能包的子技能，指令文件为 `MODULE.md`（非 SKILL.md，避免被重复识别）。

## 功能

- 医学影像分析：胸片（含纵向对比）、CT/MRI 切片、病理切片、皮肤影像、眼底影像。
- 解剖定位：胸片结构与病灶 bounding box。
- 医学文档理解：化验单/检验报告结构化提取（文本或图像）。
- EHR / 病历解读、临床推理问答、医学报告生成。
- 本地图像自动 base64 编码，远程图像需 HTTPS URL，最多 4 张多图输入。

## 安装

推荐整体安装聚合技能包（入口为根目录 SKILL.md）：

```bash
cp -r 医学分析推理 ~/.workbuddy/skills/
```

如需单独安装本子技能：将本目录复制到 `~/.workbuddy/skills/medgemma-medical-analysis/`，并把 `MODULE.md` 重命名为 `SKILL.md`。

发送 `/reload-skills` 或重启客户端生效。目录名必须与 frontmatter 中的 `name` 一致。

## 配置

```bash
# 基本配置（baseUrl + apiKey 必填）
echo '{"baseUrl": "https://your-newapi.example.com", "apiKey": "sk-xxx"}' | node scripts/configure.js

# 可选：同时指定模型名（中转站模型名与默认值不同时）
echo '{"baseUrl": "https://your-newapi.example.com", "apiKey": "sk-xxx", "model": "medgemma-1.5-4b-it"}' | node scripts/configure.js
```

配置读取优先级：`~/.workbuddy/skills/medgemma-medical-analysis/config.json` > 环境变量 `NEWAPI_BASE_URL` / `NEWAPI_API_KEY`；可用 `NEWAPI_CONFIG` 指定配置文件路径。模型名优先级：`--model` > `config.json` 的 `model` > 环境变量 `MEDGEMMA_MODEL` > 默认 `medgemma-1.5-4b-it`。

配置后先验证连接并查看中转站可用模型：

```bash
node scripts/medgemma.js --ping
```

## 使用

```bash
node scripts/medgemma.js --task cxr --image /path/to/chest-xray.png --question "描述主要发现"
node scripts/medgemma.js --task lab-report --text "Hb 13.2 g/dL; WBC 8.1 x10^9/L"
node scripts/medgemma.js --task report-generation --image /path/to/ct-slice.png --output ./report.md
```

图像格式支持 PNG/JPEG/WebP/GIF/BMP/TIFF；DICOM 等格式先用 `node scripts/prepare-image.js <file>` 转换为 PNG 并缩放到 896x896。

## 结构

- `MODULE.md`：子技能指令（单独安装时重命名为 SKILL.md）。
- `scripts/medgemma.js`：调用与任务模板（含 `--ping` 连接验证）；`scripts/configure.js`：配置写入；`scripts/prepare-image.js`：图像格式转换与缩放。
- `references/`：模型能力说明、prompt 模板。
- `assets/`：医学报告输出模板。

## 合规提醒

结果仅供医学研究、教学与辅助参考，不可作为临床诊断依据；最终诊断请以执业医师意见为准。患者数据发送前请脱敏。
