# cell-therapy-tracker

追踪全球细胞 / 基因治疗产品上市动态，自动搜索最新获批产品并追加到 Excel 汇总表，新增行黄色高亮。

## 目录结构

```
cell-therapy-tracker/
├── SKILL.md                       # 技能主文档（触发示例 / 完整 runbook / 示例 / FAQ）
├── README.md                      # 本文件（v2 改动记录与结构说明）
├── scripts/
│   ├── update_excel.py            # 追加新行 + 黄色高亮（含容错/自动定位/安全模式）
│   └── gen_search_queries.py      # 搜索查询生成器（解析最新日期 → 输出三梯队关键词）
├── references/
│   ├── classification.md          # 产品分类规则（免疫细胞/干细胞/基因疗法/其他）
│   └── watchlist.md               # 在审/已获批产品监控表
└── _user_meta.json
```

## v2 改动记录（2026-07-18）

针对 skillhub 测评反馈的 4 项问题做了系统性改进：

### ① 健壮性（scripts/update_excel.py 重写）
- 输入校验：文件不存在 / 非合法 xlsx / 缺核心部件 → 人话报错 + 排查建议，不抛堆栈、安全退出（退出码非 0）
- 自动定位：不传路径时递归搜索工作区，**仅**在命中关键词（细胞/治疗/上市/CGT…）的文件中挑最新的，避免误选随机 xlsx
- XML 容错：缺失 `styles.xml` / `sharedStrings.xml` / `fills` / `cellXfs` 自动补建；复用已有黄色样式
- 命名空间修复：原集中式 `ns_prefix` 假设整包一致，实测该文件 workbook 用 `ns0:` 而 sharedStrings 不用 → 改回**每个部件各自检测前缀**，解决"无法找到 sst 元素"报错
- 写后 zip 完整性校验；**永不覆盖原文件**（始终 `_updated_YYYYMMDD.xlsx`）
- 新增 `--check`（预览不写）、`--info`（打印结构与各表最新日期）

### ② 触发方式（SKILL.md 新增「你可以这样问我」）
6 句可直接说的话（"更新细胞治疗追踪表""最近有没有新细胞疗法获批？""跑一次 cell-therapy-tracker" 等），用户不用猜触发词。

### ③ 示例 / FAQ（SKILL.md 新增）
- 三个前后对比使用示例（常规更新 / 无新增 / 补录遗漏）
- 8 条常见问题 FAQ
- 合并原先分散在脚本注释 / 多处文档里的说明

### ④ 保留优点 + 搜索闭环
- 黄色高亮新增行、三梯队搜索策略（FDA/EMA/NMPA/PMDA + watchlist 在审产品）保留并显式点名
- 新增 `scripts/gen_search_queries.py`：解析最新上市日期 → 输出三梯队 + watchlist 精确查询清单，让搜索从"人工照清单搜"变成"脚本出清单、Agent 照单搜"的完整闭环

## 快速使用

让 Agent 一句话启动（推荐）：
> 「更新细胞治疗追踪表」

或 CLI：
```bash
# 生成本轮搜索查询清单
python scripts/gen_search_queries.py <追踪表.xlsx>

# 追加新产品（--check 预览，--info 看结构）
python scripts/update_excel.py <追踪表.xlsx> --products-json products.json --output <新文件.xlsx>
```

## 回落历史记录
- 2026-07-03：初始追踪表基础
- 2026-07-18：v2 改造；同日补录 Amtagvi（美国 FDA 2024.02.16，TIL）与 Rimqarto（韩国 MFDS 2026.04.29，CD19 CAR-T）两项历史遗漏，watchlist 同步更新
