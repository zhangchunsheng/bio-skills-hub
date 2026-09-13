# 临床试验状态代码

## 总体状态值

| 状态 | 描述 |
|--------|-------------|
| `RECRUITING` | 正在积极招募受试者 |
| `ACTIVE_NOT_RECRUITING` | 进行中但未招募 |
| `NOT_YET_RECRUITING` | 尚未开放招募 |
| `COMPLETED` | 研究正常完成 |
| `SUSPENDED` | 暂时暂停 |
| `TERMINATED` | 提前终止 |
| `WITHDRAWN` | 在入组前撤回 |
| `WITHHELD` | 对公众隐藏 |
| `UNKNOWN` | 状态未知 |

## 阶段值

| 阶段 | 描述 |
|-------|-------------|
| `EARLY_PHASE1` | 早期 I 期（探索性） |
| `PHASE1` | I 期（安全性/剂量） |
| `PHASE2` | II 期（有效性） |
| `PHASE3` | III 期（有效性/监测） |
| `PHASE4` | IV 期（上市后） |

## 状态变更的原因

### 常见状态转换

1. `NOT_YET_RECRUITING` → `RECRUITING`
   - 研究开放入组

2. `RECRUITING` → `ACTIVE_NOT_RECRUITING`
   - 已达到入组目标

3. `RECRUITING` → `SUSPENDED`
   - 临时搁置（安全性、行政原因）

4. `RECRUITING`/`ACTIVE_NOT_RECRUITING` → `COMPLETED`
   - 研究成功完成

5. `RECRUITING` → `TERMINATED`
   - 提前终止（无效、安全性、商业原因）

## 监测优先级

### 高优先级变更
- RECRUITING → SUSPENDED（安全问题）
- RECRUITING → TERMINATED（竞争影响）
- ACTIVE_NOT_RECRUITING → COMPLETED（结果即将发布）

### 中优先级变更
- NOT_YET_RECRUITING → RECRUITING（新竞争）
- 阶段推进（PHASE1 → PHASE2）

### 低优先级变更
- WITHDRAWN（无竞争影响）
- 日期更新但无状态变更
