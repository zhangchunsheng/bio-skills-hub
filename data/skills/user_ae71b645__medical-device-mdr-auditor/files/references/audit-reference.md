# 审计参考

## 适用范围

- 技能目录：`medical-device-mdr-auditor`
- 核心用途：依据欧盟 MDR 2017/745 法规审计医疗器械技术文件。
- 仅在 `SKILL.md` 中已文档化的工作流与分类边界内使用。

## 支持的审计路径

- `python -m py_compile scripts/main.py`
- `python scripts/main.py --help`
- `python scripts/main.py -h`

## 应急处理边界

若必需输入不完整，本技能仍应返回：

- 缺失的必需输入
- 仍可安全完成的步骤
- 执行前需要确认的假设
- 接受最终可交付物之前的下一步核查
