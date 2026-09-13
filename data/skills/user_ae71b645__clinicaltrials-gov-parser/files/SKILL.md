---
name: clinicaltrials-gov-parser
description: '从 ClinicalTrials.gov 监测并汇总竞争对手临床试验状态变化。

  触发条件：当用户要求跟踪临床试验、监测试验状态变化、

  获取特定试验的更新，或分析竞争对手试验活动时。

  使用场景：制药行业竞争情报、试验监测、状态跟踪、

  招募更新、完成提醒。

  '
version: "1.0.1"
category: Pharma
tags:
- pharma
- clinical-trials
- monitoring
- api
- competitive-intelligence
author: AIPOCH
license: MIT
status: Draft
risk_level: High
skill_type: Hybrid (Tool/Script + Network/API)
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
displayName: "ClinicalTrials.gov 解析器"
slug: clinicaltrials-gov-parser
---

# ClinicalTrials.gov 解析器

从 ClinicalTrials.gov 监测并汇总竞争对手临床试验状态变化。

## 使用场景

- **试验监测**：跟踪特定临床试验的状态变化
- **竞争情报**：监测竞争对手的试验活动和里程碑
- **招募跟踪**：获取入组状态的最新信息
- **完成提醒**：监测试验完成情况和结果发布

## 参数说明

| 参数 | 类型 | 默认值 | 必填 | 描述 |
|-----------|------|---------|----------|-------------|
| `--sponsor` | string | - | No | 试验申办方名称 |
| `--condition` | string | - | No | 适应症/疾病 |
| `--status` | string | - | No | 试验状态（Recruiting、Completed 等） |
| `--trials` | string | - | No | 逗号分隔的试验 ID（NCT 编号） |
| `--output` | string | json | No | 输出格式（json、csv） |
| `--days` | int | 30 | No | 监测的天数 |

## 使用方法

```python
from scripts.main import ClinicalTrialsMonitor

# Initialize monitor
monitor = ClinicalTrialsMonitor()

# Search for trials
trials = monitor.search_trials(
    sponsor="Pfizer",
    condition="Diabetes",
    status="Recruiting"
)

# Get trial details
trial = monitor.get_trial("NCT05108922")

# Check for status changes
changes = monitor.check_status_changes(trial_ids=["NCT05108922"])
```

## 命令行使用

```bash
# Search trials
python scripts/main.py search --sponsor "Pfizer" --condition "Diabetes"

# Get trial details
python scripts/main.py get NCT05108922

# Monitor status changes
python scripts/main.py monitor --trials NCT05108922,NCT05108923 --output json

# Generate summary report
python scripts/main.py report --sponsor "Pfizer" --days 30
```

## API 方法

| 方法 | 描述 |
|--------|-------------|
| `search_trials()` | 按条件搜索试验 |
| `get_trial(nct_id)` | 获取详细试验信息 |
| `check_status_changes()` | 检查状态更新 |
| `get_recruitment_status()` | 获取入组更新 |
| `generate_summary()` | 生成竞争对手摘要 |

## 技术详情

- **API**: ClinicalTrials.gov API v2
- **速率限制**: 每秒 10 次请求
- **数据格式**: JSON
- **难度**: 中等

## 参考资料

- API 文档请参见 `references/api-docs.md`
- 试验状态定义请参见 `references/status-codes.md`
- 使用示例请参见 `references/examples.md`

## 风险评估

| 风险指标 | 评估 | 级别 |
|----------------|------------|-------|
| 代码执行 | 使用工具的 Python 脚本 | 高 |
| 网络访问 | 外部 API 调用 | 高 |
| 文件系统访问 | 读写数据 | 中 |
| 指令篡改 | 标准提示词指南 | 低 |
| 数据暴露 | 数据安全处理 | 中 |

## 安全检查清单

- [ ] 无硬编码凭据或 API 密钥
- [ ] 无未授权文件系统访问（../）
- [ ] 输出不暴露敏感信息
- [ ] 已实施提示注入防护
- [ ] API 请求仅使用 HTTPS
- [ ] 输入已按允许模式验证
- [ ] 已实现 API 超时与重试机制
- [ ] 输出目录限制在工作区内
- [ ] 脚本在沙盒环境中执行
- [ ] 错误信息已净化（不暴露内部路径）
- [ ] 依赖项已审计
- [ ] 不暴露内部服务架构
## 前置条件

```bash
# Python dependencies
pip install -r requirements.txt
```

## 评估标准

### 成功指标
- [ ] 成功执行主要功能
- [ ] 输出符合质量标准
- [ ] 优雅处理边缘情况
- [ ] 性能可接受

### 测试用例
1. **基本功能**：标准输入 → 预期输出
2. **边缘情况**：无效输入 → 优雅错误处理
3. **性能**：大数据集 → 可接受的处理时间

## 生命周期状态

- **当前阶段**：草稿
- **下次审查日期**：2026-03-06
- **已知问题**：无
- **计划改进**：
  - 性能优化
  - 额外功能支持
