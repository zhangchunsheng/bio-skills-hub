# 病案去标识工具

把病案首页数据里的病案号替换为不可逆的研究ID（HMAC-SHA256），同一患者跨文件、跨批次 ID 一致，纵向研究（再入院、重复住院）可直接拼接。全程本机离线运行，无网络请求。

## 快速开始

```bash
# 依赖体检（需要 Python 3.10+ 与 openpyxl）
python scripts/deid_cli.py --doctor

# 干跑统计：不产生任何文件，看纵向研究可行性
python scripts/deid_cli.py scan "数据目录" --id-col 病案号

# 批量转换（key.bin 与全部产物在导出目录）
python scripts/deid_cli.py convert "数据目录" --out-dir "去标识导出"

# 增量转换：同一导出目录再跑一次新数据，默认沿用密钥，老患者ID不变
python scripts/deid_cli.py convert "2026新数据" --out-dir "去标识导出"

# 28 项核心逻辑自检
python scripts/deid_cli.py selftest
```

## 输出规则

| 输入 | 研究者版（给分析者） | 对照表（病案科留存） |
|------|--------------------|--------------------|
| xxx.csv | xxx.csv（病案号→研究ID，无姓名列） | xxx对照表.csv |
| xxx.xlsx | xxx.xlsx | xxx对照表.xlsx |

另生成：`key.bin`（密钥）、`总对照表.csv`（累计历次批次）、`批量转换报告.txt`。

## 安全须知

1. **对照表、总对照表、key.bin 只留在病案科**，严禁随数据外发。
2. **key.bin 丢失不可恢复**（HMAC 单向），请多处备份。
3. 研究者版自动删除姓名列；`--keep-name` 仅对对照表生效。
4. 无密钥模式已被移除：病案号可枚举，公开盐值的无密钥哈希可被字典攻击还原，
   不构成真正的去标识化。

## 许可

MIT（详见 SKILL.md frontmatter 与合规底线）。
