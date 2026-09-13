# 🚀 RUNBOOK — 我的基金经理 Skill v2.0 一页纸速查

> 看完这一页即可上手。详情见 [SKILL.md](SKILL.md)。

---

## ⚠️ 重要声明

**本工具仅供参考，不构成投资建议！**
- 基金经理数据基于公开来源抓取，**可能有 1-2 周延迟**
- 业绩数据**不预示未来表现**，投资有风险
- 工具不存储你的实时聊天内容，但生成的报告**你自己保管**

---

## 🆕 v2.0 新功能一览

| 新功能 | 怎么用 |
|-------|--------|
| ✨ **基金经理对比** — 多经理并排对照 | `python scripts/manager_compare.py 30189741 30189744` |
| ✨ **数据备份与恢复** — 安全迁移/防误删 | `python scripts/data_backup.py backup` |
| ✨ **完整测试套件** — 36 个回归测试 | `python -m pytest tests/ -v` |
| 🛠️ **.gitignore** — 防止数据被 git 跟踪 | 自动生成 |

---

## 1. 一句话用（3 种路径）

```bash
# A. 智能导入（最常用）
"导入2025-2026知名基金经理种子库"

# B. 交互菜单
python scripts/roster_manager.py

# C. 单步调试
python scripts/famous_manager_importer.py import_all   # 一键导入80位知名经理
python scripts/monthly_updater.py smart_update        # 智能增量更新（首次=全量）
python scripts/export_table.py                        # 导出表格
```

---

## 2. 完整命令速查（11 个脚本）

### 📰 数据采集（5 个）

```bash
python scripts/search_news.py "你们新基金"  # 新闻（公开市场）
python scripts/fetch_fund_info.py 30189741  # 抓基金详情
python scripts/fetch_performance.py --id 1  # 业绩数据
python scripts/fetch_reports.py --id 1      # 季报
python scripts/fetch_holdings.py --id 1     # 重仓股
```

### 🌱 种子库 + 名单管理

```bash
# 导入 2025-2026 知名经理（80 位，4 分类）
python scripts/famous_manager_importer.py import_all
python scripts/famous_manager_importer.py import_category 公募明星

# 名单 CRUD
python scripts/roster_manager.py add 张坤 易方达基金
python scripts/roster_manager.py list
python scripts/roster_manager.py remove 30189741
```

### 🔄 三种更新模式

```bash
# 智能增量（推荐）：只更新变化的经理
python scripts/monthly_updater.py smart_update

# 全量：刷新全部（耗时）
python scripts/monthly_updater.py update_all

# 仅过期：超过 N 天才更新
python scripts/monthly_updater.py update_stale --days 30
```

### 📤 导出 / 对比 / 备份（v2.0 新）

```bash
python scripts/export_table.py                          # 导出名单/风格/重仓/业绩
python scripts/manager_compare.py 30189741 30189744      # 🆕 多经理对比
python scripts/data_backup.py backup                     # 🆕 备份
python scripts/data_backup.py list                       # 查看历史备份
python scripts/data_backup.py restore backups/skill_backup_XXX.zip  # 恢复
```

### 🧪 测试

```bash
python tests/test_common.py            # 23 个 _common 测试
python tests/test_roster.py            # 13 个 roster_manager 测试
python tests/test_new_features.py      # 11 个新功能测试
python -m pytest tests/ -v             # 一键全跑
```

---

## 3. 快速决定表

| 你想做什么 | 推荐命令 |
|----------|---------|
| **首次使用** | `python scripts/famous_manager_importer.py import_all` 然后 `smart_update` |
| **日常维护** | 每周一跑 `smart_update` 一次 |
| **查询经理** | 直接对加载了本 Skill 的 AI 助手说"张坤怎么样" |
| **多经理对比** | `python scripts/manager_compare.py <id1> <id2> <id3>` |
| **导出数据** | `python scripts/export_table.py`（输出 `data/exports/` 目录） |
| **防丢失** | 跑 `data_backup.py backup`，zip 存 U 盘/网盘 |
| **出错了** | 跑 `python scripts/monthly_updater.py doctor`（如支持），或看 [references/troubleshooting.md](references/troubleshooting.md) |

---

## 4. 数据存储说明

```
data/
├── roster.json              # 名单（最多 100 个经理的清单）
├── manager_index.json       # 经理索引（搜索加速用）
├── famous_managers_2025_2026.json  # 80 位知名经理种子库
├── managers/                # 每个经理一份 JSON 档案
│   ├── 30189741.json        # 个人档案（含风格、重仓、业绩）
│   └── ...
├── exports/                 # 导出表格（CSV/Excel）
├── change_log/              # 每次更新记录（用于查"上次改了啥"）
├── progress/                # 进度（断点续传）
└── backups/                 # 🆕 备份文件
```

---

## 5. 常见问题（5 大坑）

### 🔴 Q1：跑 `import_all` 后什么都没变？

**答**：可能的原因：
1. 网络问题 → 检查能否访问 `fundf10.eastmoney.com`
2. 已经在名单里 → 看 `roster.json` 已有 ID
3. 路径错误 → 在 skill **根目录**运行，不在 scripts/

### 🟡 Q2：`smart_update` 提示"无变化，跳过"

**答**：正常！这说明这两天没有基金公告/持仓变化。可手动 `update_all` 强制刷新。

### 🟠 Q3：`is_in_roster` 找不到我刚加的经理

**答**：ID 必须严格匹配字符串。区分大小写、区分零宽字符。`is_in_roster(30189741)` 与 `is_in_roster("30189741")` **等价**（都转 str）。

### 🟡 Q4：导出表格打不开？

**答**：
- CSV：Excel/Numbers 直接双击
- xlsx：需要 `openpyxl`（pip install openpyxl）

### 🔴 Q5：如何迁移到新电脑？

**答**：
```bash
# 旧电脑
python scripts/data_backup.py backup
# → 得到 skill_backup_20260728_XXX.zip

# 拷贝到新电脑的同一目录
python scripts/data_backup.py restore skill_backup_20260728_XXX.zip
```

---

## 6. 风险控制（v2.0 强化）

| 风险 | 防护 |
|------|------|
| 误删经理 | v2.0 `update_status` 校验状态值（不再静默写入） |
| 数据丢失 | v2.0 `data_backup.py` 30 秒一键备份 |
| 路径冲突 | v2.0 `_common.ROSTER_PATH` 走模块属性，不在 import 时固化 |
| 测试污染 | v2.0 测试通过修改模块属性 + finally 恢复 |
| 反爬 | v2.0 `http_get` 非 200 也延迟，避免被快速封 IP |

详见 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 7. 一行命令速记（贴桌面）

```bash
# 每日维护
python scripts/monthly_updater.py smart_update

# 智能备份
python scripts/data_backup.py backup

# 导出 + 对比 + 审计
python scripts/export_table.py && python scripts/data_backup.py backup
```

---

## 8. 文档交叉引用

- 📘 [SKILL.md](SKILL.md) — 完整规范（500+ 行）
- 📗 [README.md](README.md) — 项目说明
- 📚 [references/](references/) — 4 篇方法论文档（共 493 行）
  - `data-sources.md` 数据来源
  - `distill-prompts.md` 蒸馏提示词
  - `roster-schema.md` 名单数据结构
  - `troubleshooting.md` 故障排查
- 🆕 **scripts/manager_compare.py** — 多经理对比工具
- 🆕 **scripts/data_backup.py** — 备份恢复工具
- 🆕 **tests/test_common.py / test_roster.py / test_new_features.py** — 完整测试套件

---

*最后更新：v2.0（2026-07-28）*
