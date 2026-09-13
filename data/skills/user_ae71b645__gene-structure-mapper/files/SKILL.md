---
name: gene-structure-mapper
description: 通过外显子-内含子示意图、结构域注释和突变位置标记来可视化基因结构。根据基因符号输入，生成适合发表的 SVG、PNG 或 PDF 图像。
license: MIT
skill-author: AIPOCH
status: beta
displayName: "基因结构映射"
version: "1.0.1"
slug: gene-structure-mapper
---
# 基因结构映射

使用 Ensembl REST API 为任意基因符号生成外显子-内含子结构示意图。可选择叠加蛋白质结构域注释（UniProt）并标记突变热点位置。输出适合发表的 SVG、PNG 或 PDF 图像。

> ✅ **已实现** — `scripts/main.py` 功能完整。Ensembl REST API、缓存、matplotlib 可视化以及 `--domains`、`--mutations` 和 `--demo` 均已实现。

## 快速检查

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py --demo --output demo.png
```

## 适用场景

- 为论文或演示创建基因结构图
- 可视化剪接变体和亚型差异
- 在基因图上标记突变位置以进行功能注释
- 在外显子-内含子图谱上叠加结构域边界

## 工作流程

1. 在进行详细工作之前，确认用户目标、所需输入和不可变更的约束条件。
2. 验证请求是否符合文档描述的范围，如果任务需要不支持的假设则提前终止。
3. 使用打包的脚本路径或记录的推理路径，仅使用实际可用的输入。
4. 返回结构化结果，将假设、可交付成果、风险和未解决事项分别列出。
5. 如果执行失败或输入不完整，切换到备用路径并明确说明阻止完成的原因。

**备用模板：** 如果 `scripts/main.py` 失败或基因符号无法识别，请报告：(a) 失败点，(b) 是否可以通过手动 Ensembl/UCSC 查询替代，(c) 哪些输出格式仍可生成。

## 参数

| 参数 | 类型 | 是否必需 | 说明 |
|-----------|------|----------|-------------|
| `--gene`, `-g` | string | 是* | 基因符号或 Ensembl ID（例如 `TP53`、`BRCA1`、`ENSG00000141510`） |
| `--species` | string | 否 | Ensembl 查询的物种名称（默认：`homo_sapiens`） |
| `--format` | string | 否 | 输出格式：`png`、`svg`、`pdf`（默认：`png`） |
| `--output`, `-o` | string | 否 | 输出文件路径（默认：`<gene>_structure.<format>`） |
| `--domains` | flag | 否 | 获取并叠加 UniProt 蛋白质结构域注释 |
| `--mutations` | string | 否 | 要标记的逗号分隔的密码子位置（例如 `248,273`） |
| `--demo` | flag | 否 | 使用硬编码的 TP53 GRCh38 数据——无需联网 |

*除非使用 `--demo`，否则为必填项。

## 用法

```text
python scripts/main.py --gene TP53 --format png
python scripts/main.py --gene BRCA1 --format png --domains --output brca1_structure.png
python scripts/main.py --gene KRAS --mutations 12,13,61 --format pdf
python scripts/main.py --demo
python scripts/main.py --demo --output demo.png --format svg
```

## 实现说明（供脚本开发人员参考）

脚本必须实现：

1. **基因查询** — `GET https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene}?expand=1` 以获取外显子坐标。将响应缓存到 `.cache/{gene}_ensembl.json` 以避免重复 API 调用。批量查询时添加 0.1 秒延迟。未认证的速率限制为每秒 15 次请求。
2. **未知基因处理** — 捕获来自 Ensembl 的 HTTP 400/404 错误，并以代码 1 退出：`Error: Gene not found: {gene_name}. Check the gene symbol and try again.`
3. **SVG/PNG/PDF 输出** — 使用 `matplotlib` 或 `svgwrite` 绘制外显子块（填充矩形）和按基因组坐标缩放的内含子线条。
4. **`--domains` 标志** — 获取 UniProt 结构域注释并在基因结构上叠加彩色结构域块。
5. **`--mutations` 标志** — 接受逗号分隔的密码子位置；映射到外显子坐标并绘制垂直标记。
6. **`--demo` 标志** — 使用硬编码的 TP53 GRCh38 外显子坐标（无需联网）生成演示可视化图。

## 已知限制

- 对于具有多种亚型的基因，脚本使用规范转录本（Ensembl `is_canonical` 标志）。不可视化其他亚型。
- 结构域叠加（`--domains`）使用 CDS 长度将 UniProt 氨基酸位置映射到基因组坐标；对于具有复杂剪接的基因，准确性可能存在差异。
- Ensembl API 响应缓存到 `.cache/{gene}_ensembl.json`。删除缓存文件可强制重新查询。
- 未认证的 Ensembl REST API 速率限制为每秒 15 次请求；批量请求之间应用 0.1 秒延迟。

## 功能特性

- 按基因组坐标缩放的外显子-内含子可视化
- 通过 UniProt 叠加蛋白质结构域注释（可选，`--domains`）
- 带可配置标签的突变位置标记（`--mutations`）
- SVG、PNG 或 PDF 格式的出版就绪输出
- 用于离线测试的演示模式（`--demo`）
- Ensembl API 响应缓存以避免速率限制问题

## 输出要求

每次响应必须明确说明以下内容：

- 目标和可交付成果
- 使用的输入和引入的假设（例如，基因组版本、选择的转录本亚型）
- 采用的工作流程或决策路径
- 核心结果：基因结构图文件路径
- 约束条件、风险、注意事项（例如，多亚型基因、注释版本）
- 未解决事项和后续检查步骤

## 输入验证

本技能接受：用于结构可视化的基因符号输入，以及可选的结构域和突变叠加。

如果请求不涉及基因结构可视化——例如，要求执行序列比对、预测蛋白质结构或分析表达数据——则不要继续执行。而是回复：

> "`gene-structure-mapper` 旨在可视化基因外显子-内含子结构。您的请求似乎超出了此范围。请提供基因符号和所需的输出格式，或为您的任务使用更合适的工具。"

## 错误处理

- 如果缺少 `--gene`，说明基因符号为必填项并提供示例。
- 如果在 Ensembl 中找不到基因符号（HTTP 400/404），则打印：`Error: Gene not found: {gene_name}. Check the gene symbol and try again.` 并以代码 1 退出。
- 如果 `--mutations` 包含非数字值，则拒绝并显示：`Error: --mutations must be comma-separated integers (codon positions).`
- 如果任务超出文档描述的范围，应停止而不是猜测或默默地扩大任务范围。
- 如果 `scripts/main.py` 失败，报告失败点，概述仍可安全完成的内容，并提供手动备用方案。
- 不得伪造文件、引用、数据、搜索结果或执行结果。

## 响应模板

1. 目标
2. 收到的输入
3. 假设
4. 工作流程
5. 可交付成果
6. 风险与限制
7. 后续检查
