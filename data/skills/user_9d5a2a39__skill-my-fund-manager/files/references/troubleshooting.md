# 故障排查

## 常见错误速查

| 症状 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: requests` | requests 未安装 | 脚本会自动安装；若失败手动 `pip install requests` |
| `ModuleNotFoundError: openpyxl` | Excel 导出依赖缺失 | 脚本会自动安装；或用 CSV 格式（`export_table.py csv`） |
| 东方财富返回 403 | 反爬检测 | 检查 User-Agent/Referer；增加延迟；稍后重试 |
| 经理搜索无结果 | 姓名不准确或索引过期 | 用基金代码/产品名搜索；或重建索引 `manager_search.py` 中 `force_refresh=True` |
| 重仓数据为空 | 基金无股票持仓（债券型/货币型） | 正常现象；检查基金类型 |
| 业绩数据缺失 | pingzhongdata 不可达或基金代码错误 | 检查网络；确认基金代码正确 |
| 蒸馏质量低 | 使用规则引擎 | 建议在对话中让 LLM 直接蒸馏（`distill_manager.py task <id>`） |
| 名单已满 | 超过50人上限 | 先删除一些经理 `roster_manager.py remove <id>` |
| SKILL.md 版本未更新 | bump_skill_version 未找到版本号 | 确认 SKILL.md frontmatter 含 `version:` 字段 |

## 环境适配

### Windows + Git Bash
- 路径用正斜杠 `/` 或双反斜杠 `\\`
- Python 命令为 `python`（不是 `python3`）
- 脚本内路径用 `os.path.join` 自动处理

### Linux / Mac
- Python 命令可能为 `python3`
- 路径用正斜杠 `/`

### 无网络环境
- 只能用已缓存的经理索引和已蒸馏的档案
- 蒸馏只能用规则引擎
- 无法获取最新重仓和业绩

## 数据质量提示

- 规则引擎蒸馏（`engine=rules`）质量有限，只生成风格标签和基础简介
- 对话 LLM 蒸馏（`engine=llm`）质量最高，能生成完整思维 DNA
- 建议：首次添加经理后，在对话中让 LLM 蒸馏一次，后续更新用规则引擎即可
