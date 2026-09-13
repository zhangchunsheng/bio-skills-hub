# 审计参考文档

## 范围

- 技能目录：`unstructured-medical-text-miner`
- 核心目的：从MIMIC-IV非结构化临床文本中挖掘诊断逻辑。
- 仅在 `SKILL.md` 中已记录的工作流和类别边界内使用。

## 支持的审计路径

- `python -m py_compile scripts/main.py`
- `python scripts/main.py --help`
- `python scripts/main.py -h`

## 备用边界

若必要输入不完整，本技能仍应返回：

- 缺失的必要输入项
- 仍可安全完成的步骤
- 执行前需确认的假设
- 接受最终可交付物前的后续检查项
