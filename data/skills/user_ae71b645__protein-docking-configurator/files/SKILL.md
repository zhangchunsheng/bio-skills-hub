---
slug: protein-docking-configurator
displayName: 蛋白质分子对接配置生成器
description: 为分子对接软件准备输入文件，基于活性位点残基或参考配体自动计算 Grid Box 的中心坐标与尺寸，生成 AutoDock Vina 配置文件或 AutoDock4
  Grid Parameter File（GPF）。以下场景也会触发本技能："帮我算一下这个蛋白的 docking box""根据这几个活性位点残基生成 Vina 配置文件""帮我用参考配体确定对接盒子范围""生成 AutoDock4 的 GPF 文件"。
version: 1.1.0
category: Bioinfo
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# 蛋白质分子对接配置生成器

## 功能特性

- 解析蛋白质 PDB 文件，识别配体结合口袋
- 自动计算 Grid Box 中心坐标和尺寸
- 生成 AutoDock Vina 配置文件
- 生成 AutoDock4 Grid Parameter File（GPF）
- 支持基于活性位点残基或参考配体两种方式确定 Box 位置

## 用法

### 作为命令行工具

```bash
# 基于活性位点残基计算 Grid Box
python scripts/main.py --receptor protein.pdb --active-site-residues "A:120,A:145,A:189" --software vina

# 基于参考配体计算 Grid Box
python scripts/main.py --receptor protein.pdb --reference-ligand ligand.pdb --software vina

# 手动指定 Box 参数
python scripts/main.py --receptor protein.pdb --center-x 10.5 --center-y -5.2 --center-z 20.1 --size-x 20 --size-y 20 --size-z 20 --software vina
```

### 作为 Python 模块

```python
from scripts.main import DockingConfigurator

config = DockingConfigurator()

# 基于受体和活性位点计算 box
config.from_active_site("protein.pdb", ["A:120", "A:145", "A:189"])
config.write_vina_config("config.txt", exhaustiveness=32)

# 基于受体和参考配体计算 box
config.from_reference_ligand("protein.pdb", "ligand.pdb", padding=5.0)
config.write_autodock4_gpf("protein.gpf", spacing=0.375)
```

## 参数说明

### 命令行参数

| 参数 | 说明 | 是否必需 |
|------|------|------|
| `--receptor` | 受体蛋白 PDB 文件路径 | 是 |
| `--software` | 对接软件类型（vina/autodock4） | 是 |
| `--active-site-residues` | 活性位点残基列表，格式："链:残基序号" | 否 |
| `--reference-ligand` | 参考配体 PDB/MOL 文件 | 否 |
| `--center-x/y/z` | Grid Box 中心坐标 | 否 |
| `--size-x/y/z` | Grid Box 尺寸（Å） | 否 |
| `--spacing` | 网格间距（仅 AutoDock4） | 否（默认 0.375） |
| `--exhaustiveness` | 搜索详尽度（仅 Vina） | 否（默认 32） |
| `--output` | 输出文件路径 | 否 |

> **说明**：`--active-site-residues` 和 `--reference-ligand` 是互斥参数（`argparse` 的 `mutually_exclusive_group`），二者只能选择其一；若两者都未提供，则需要同时提供 `--center-x`/`--center-y`/`--center-z` 手动指定中心坐标，否则脚本会报错退出。此外，脚本实际还支持 `--num-modes`（Vina 输出构象数量，默认 9）、`--padding`（配体周围留白，默认 5.0Å）、`--quiet`/`-q`（静默模式，不打印摘要信息）等参数，源文档未列出，此处补充。

## 输出

- **AutoDock Vina**：生成 config.txt 配置文件
- **AutoDock4**：生成 .gpf（Grid Parameter File）文件；文件内部的字段名、注释（如 `receptor_types`、`ligand_types`、`gridcenter` 等）遵循 AutoDock4 官方文件格式规范，是 AutoDock4 程序直接读取解析的内容，因此保留英文原文，未做翻译

## 依赖环境

- Python 3.8+
- 无需额外第三方包（脚本仅使用标准库：`argparse`、`sys`、`re`、`pathlib`、`typing`）

> **文档修正说明**：源文档"依赖"部分写的是 `numpy`，但实际脚本未导入 `numpy`，全部坐标与包围盒计算都是用标准库手写的（见 `PDBParser.calculate_center`/`calculate_bounding_box`），因此本次已修正为"无需额外第三方包"。

## 示例

```bash
# 示例 1：使用活性位点残基
python scripts/main.py --receptor 1abc_receptor.pdb --active-site-residues "A:45,A:92,A:156" --software vina --output vina_config.txt

# 示例 2：使用参考配体并自定义 Box 尺寸
python scripts/main.py --receptor kinase.pdb --reference-ligand ATP.pdb --software vina --size-x 25 --size-y 25 --size-z 25

# 示例 3：AutoDock4 配置
python scripts/main.py --receptor protein.pdb --active-site-residues "A:100" --software autodock4 --spacing 0.375 --output protein.gpf
```

## 注意事项

1. 输入的 PDB 文件应先去除水分子和不需要的异质原子（heteroatom），除非确实需要保留
2. 建议先对受体进行加氢质子化和电荷计算（可使用 AutoDock Tools 等工具）后再用于后续对接
3. Grid Box 尺寸应足够覆盖配体的构象空间，通常建议 20–30Å
4. 活性位点残基应包含催化残基和关键结合残基

## 局限性

- 脚本仅解析标准 PDB 格式（固定列宽的 `ATOM`/`HETATM` 记录行），不支持 PDBx/mmCIF 格式
- 基于活性位点残基计算 Box 时，若某个残基规格在受体文件中找不到匹配原子，会直接抛出异常终止；请确认链 ID 和残基序号与 PDB 文件中的记录一致
- `--active-site-residues` 与 `--reference-ligand` 互斥，不能同时使用；脚本本身不会自动判断该用哪种方式，需要调用者根据实际场景选择

## 风险评估

| 风险指标 | 评估 | 级别 |
|----------------|------------|-------|
| 代码执行 | 本地执行 Python 脚本 | 中 |
| 网络访问 | 无外部 API 调用 | 低 |
| 文件系统访问 | 读取输入文件、写入输出文件 | 中 |
| 指令篡改 | 标准提示词规范 | 低 |
| 数据暴露 | 输出文件保存至工作目录 | 低 |

## 安全检查清单

- [ ] 无硬编码凭据或 API 密钥
- [ ] 无未授权的文件系统访问（../）
- [ ] 输出不暴露敏感信息
- [ ] 具备提示词注入防护
- [ ] 输入文件路径经过校验（无 ../ 路径穿越）
- [ ] 输出目录限制在工作区内
- [ ] 脚本在沙箱环境中执行
- [ ] 错误信息经过清理（不暴露堆栈跟踪）
- [ ] 依赖项已审计

## 前置条件

无需安装额外的 Python 包。

## 评估标准

### 成功指标
- [ ] 能成功执行主要功能
- [ ] 输出符合质量标准
- [ ] 能妥善处理边界情况
- [ ] 性能可接受

### 测试用例
1. **基础功能**：标准输入 → 预期输出
2. **边界情况**：无效输入 → 妥善的错误处理
3. **性能**：大型数据集 → 可接受的处理时间

## 生命周期状态

- **当前阶段**：草案
- **下次评审日期**：2026-03-06
- **已知问题**：无
- **计划改进**：
  - 性能优化
  - 支持更多功能
