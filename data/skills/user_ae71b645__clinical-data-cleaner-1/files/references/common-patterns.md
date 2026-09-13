## 常见模式

### 模式 1：监管申报准备

**场景**：为 FDA 申报准备 SDTM 数据集。

```json
{
  "submission_type": "FDA NDA",
  "domains": ["DM", "LB", "VS", "AE", "MH"],
  "cleaning_approach": "Conservative - flag rather than remove",
  "validation": "CDISC SDTM IG v3.2",
  "audit_requirements": "Complete traceability of all changes",
  "deliverables": [
    "Cleaned datasets",
    "Cleaning reports",
    "Programming specifications"
  ]
}
```

**工作流程：**
1. 从 EDC 系统加载原始数据
2. 根据 SDTM 领域规范进行验证
3. 使用保守设置进行清洗（标记异常值）
4. 生成全面的审计轨迹
5. 使用 Pinnacle 21 验证最终数据集
6. 记录所有清洗决策
7. 打包用于监管申报

**输出示例：**
```
FDA Submission Package:
  
Datasets:
  ✓ dm.xpt (1,247 subjects)
  ✓ lb.xpt (45,678 records)
  ✓ vs.xpt (12,470 records)
  
Cleaning Statistics:
  - Missing values imputed: 234
  - Outliers flagged: 89
  - Date formats standardized: 1,247
  
Audit Trail:
  - Cleaning reports: 3 files
  - All actions documented
  - 21 CFR Part 11 compliant
  
Validation:
  ✓ Pinnacle 21: 0 errors, 3 warnings
  ✓ CDISC SDTM IG v3.2 compliant
```

### 模式 2：中期分析数据准备

**场景**：为正在进行的试验的中期分析清洗数据。

```json
{
  "analysis_type": "Interim efficacy",
  "data_cutoff": "2023-12-31",
  "cleaning_priority": "Speed with quality",
  "domains_needed": ["DM", "LB", "VS"],
  "outlier_handling": "Flag for statistician review",
  "timeline": "3 days"
}
```

**工作流程：**
1. 按截止日期提取数据
2. 快速验证关键字段
3. 使用中位数填补缺失值
4. 标记异常值（不删除）
5. 统一日期格式
6. 交付给统计团队
7. 记录已知问题

**输出示例：**
```
Interim Analysis Dataset:
  Data cutoff: 2023-12-31
  Subjects: 456/500 enrolled
  
Cleaning Summary:
  - Processing time: 2 hours
  - Missing values: 45 (imputed)
  - Outliers flagged: 12
  - Ready for analysis: Yes
  
Notes for Statistician:
  - 3 subjects with incomplete follow-up
  - 1 site with delayed data entry
  - All outliers reviewed and plausible
```

### 模式 3：数据库迁移清理

**场景**：在不同数据管理系统之间迁移时清洗数据。

```json
{
  "migration_type": "EDC system upgrade",
  "source_system": "Legacy EDC",
  "target_system": "New Veeva",
  "challenges": [
    "Different date formats",
    "Field name changes",
    "Encoding issues"
  ],
  "validation": "Compare before/after counts"
}
```

**工作流程：**
1. 从旧系统导出所有数据
2. 将旧字段名映射到 SDTM
3. 统一格式（日期、分类）
4. 清洗缺失值/异常值
5. 验证记录数一致
6. 测试导入新系统
7. 记录所有转换过程

**输出示例：**
```
Database Migration Results:
  Legacy records: 15,678
  Migrated records: 15,678
  Match: ✓ 100%
  
Transformations Applied:
  - Date format: 23,456 fields
  - Field names: 156 mappings
  - Missing values: 234 imputed
  - Outliers: 45 flagged
  
Validation:
  ✓ Subject counts match
  ✓ Record counts match
  ✓ Critical values preserved
  ✓ Import to new system successful
```

### 模式 4：外部数据整合

**场景**：将外部实验室数据整合到临床数据库中。

```json
{
  "data_source": "Central lab",
  "integration_type": "LB domain augmentation",
  "challenges": [
    "Different units",
    "Varying reference ranges",
    "Date/time zone issues"
  ],
  "cleaning_focus": "Standardization and validation"
}
```

**工作流程：**
1. 加载中心实验室数据导出文件
2. 将本地实验室代码映射到 LBTESTCD
3. 统一单位（如需要则转换）
4. 根据参考范围进行验证
5. 处理日期/时区问题
6. 与现有 LB 数据合并
7. 验证无重复记录

**输出示例：**
```
Central Lab Integration:
  External records: 8,234
  Successfully integrated: 8,234 (100%)
  
Standardization:
  - Unit conversions: 234 records
  - Date adjustments: 8,234 records
  - Code mappings: 45 tests
  
Validation:
  ✓ No duplicate records
  ✓ All USUBJID matched
  ✓ Units standardized
  ✓ Reference ranges aligned
  
Data Quality:
  - Outliers flagged: 23
  - Missing values: 0
  - Ready for analysis: Yes
```

---

## 质量检查清单

**清洗前：**
- [ ] **关键**：确认输入数据来自经过验证的来源（EDC，而非草稿）
- [ ] 确认数据导出日期和截止时间
- [ ] 检查文件格式（CSV/Excel）和编码
- [ ] 核实领域规范（DM、LB、VS）
- [ ] 查阅研究方案以了解预期数据结构
- [ ] 检查数据锁定状态
- [ ] 确认访问权限和数据安全性
- [ ] 记录原始数据文件位置（用于审计）

**清洗配置：**
- [ ] **关键**：为数据类型选择合适的缺失值处理策略
- [ ] 选择适合该领域的异常值检测方法（LB/VS 建议使用 'domain'）
- [ ] 根据监管要求设置异常值处理方式（建议使用 'flag'）
- [ ] 如提供了自定义配置,检查是否合理
- [ ] 与统计师确认清洗参数
- [ ] 记录所有参数选择的理由
- [ ] 检查是否需要分层（按中心、治疗组）
- [ ] 在统计分析计划中验证清洗方法

**清洗过程中：**
- [ ] **关键**：检查验证警告（缺失字段）
- [ ] 检查缺失值填补数量
- [ ] 检查异常值检测结果
- [ ] 核实标记的异常值是否合理
- [ ] 检查日期统一化的成功率
- [ ] 监控是否有意外的数据丢失
- [ ] 检查清洗日志中的异常情况
- [ ] 比较清洗前后的行数

**清洗后：**
- [ ] **关键**：根据 CDISC SDTM IG 验证清洗后的数据
- [ ] 检查 Pinnacle 21（或类似工具）的验证结果
- [ ] 查阅审计轨迹中的所有清洗操作
- [ ] 核实 SDTM 领域结构是否正确
- [ ] 测试导入分析软件（SAS、R）
- [ ] 生成关键变量的汇总统计信息
- [ ] 与预期范围进行比较
- [ ] 记录与方案的任何偏差

**监管合规：**
- [ ] **关键**：所有清洗操作均记录理由
- [ ] 审计轨迹完整并已归档
- [ ] 清洗程序纳入版本控制
- [ ] 验证文档完整
- [ ] 经过独立质控审查（如需要）
- [ ] 经统计师/医学监查员批准
- [ ] 与统计分析计划保持一致
- [ ] 已准备好进行监管申报

---

## 常见陷阱

**数据质量问题：**
- ❌ **清洗原始/草稿数据** → 最终数据与清洗后数据不一致
  - ✅ 仅清洗已锁定/已验证的数据
  
- ❌ **未经调查就删除异常值** → 丢失合理的极端值
  - ✅ 标记异常值；删除前先审查
  
- ❌ **不恰当的填补方式** → 使统计分析产生偏差
  - ✅ 根据缺失机制选择策略
  
- ❌ **忽视缺失模式** → 将 MNAR 数据误当作 MCAR 处理
  - ✅ 分析缺失模式；咨询统计师

**监管问题：**
- ❌ **审计轨迹不完整** → 监管驳回
  - ✅ 记录每一项更改及其理由
  
- ❌ **未经记录就更改数据** → 违反合规要求
  - ✅ 切勿修改原始数据；创建新的清洗数据集
  
- ❌ **未根据 SDTM IG 进行验证** → 申报出现问题
  - ✅ 始终运行 CDISC 验证工具
  
- ❌ **数据库锁定后进行清洗** → 违反方案
  - ✅ 锁定前完成清洗；锁定后的任何更改都需要有记录的批准

**技术问题：**
- ❌ **日期解析错误** → 时间关系不正确
  - ✅ 验证日期格式；与 CRF 核对
  
- ❌ **单位转换错误** → 临床数值无效
  - ✅ 仔细核对所有单位转换
  
- ❌ **受试者 ID 不匹配** → 数据关联失败
  - ✅ 核实各领域间 USUBJID 的一致性
  
- ❌ **覆盖原始文件** → 数据丢失
  - ✅ 始终保存为新文件；保留原始数据

---
