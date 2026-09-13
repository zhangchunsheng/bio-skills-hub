# Skill 元数据 (metadata)

> 本文件为 Skill 的结构化元数据，方便其他系统或脚本读取 Skill 的关键信息。

## 基本信息

| 字段 | 值 |
|------|-----|
| Skill ID | `clinical-pharmacist` |
| 中文名 | 临床药师「小药」用药教育助手 |
| 版本 | 1.0.0 |
| 作者 | CodeBuddy AI |
| 创建日期 | 2026-08-09 |
| 最近更新 | 2026-08-09 |
| 分类 | 医疗健康 / 用药教育 |
| 许可 | 仅作助手教育用途，不构成医疗建议 |

## 触发条件

详见 SKILL.md 中的 "When to Use" / "When NOT to Use" 章节。

## 依赖

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | ≥3.10 | 运行查询脚本 |
| 网络 | - | 访问药品说明书数据源 |
| 数据源 | https://www.gzpykj.com/zssyall | 中山大学附属第三医院药学部 |

## 文件清单

```
clinical-pharmacist/
├── SKILL.md                         # Skill 主定义
├── references/                      # 参考资料
│   ├── metadata.md                  # 本文件
│   ├── drug-categories.md           # 药品分类参考
│   ├── safety-checklist.md          # 用药安全检查清单
│   └── conversation-examples.md     # 对话示例集
├── assets/                          # 静态资源
│   └── icons/                       # 表情符号与图标速查
│       └── README.md
└── scripts/                         # 执行脚本
    └── drug_lookup.py               # 药品说明书查询
```

## 变更日志

### 1.0.0 (2026-08-09)
- 初版发布
- 支持中山三院药品说明书库全站搜索与详情查询
- 6 步标准用药教育流程
- 安全警示与边界处理