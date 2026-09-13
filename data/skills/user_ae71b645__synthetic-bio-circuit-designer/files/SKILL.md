---
slug: synthetic-bio-circuit-designer
displayName: 合成生物回路设计器
description: 设计合成生物学基因回路，支持拨动开关和振荡器电路设计与模拟。触发短语：基因回路设计、合成生物回路、拨动开关电路、repressilator振荡器
version: 1.1.0
category: Bioinfo
tags: []
author: AIPOCH
license: MIT
status: Draft
risk_level: Medium
skill_type: Tool/Script
owner: AIPOCH
reviewer: ''
last_updated: '2026-02-06'
---

# 合成生物回路设计器

设计和模拟合成生物学基因回路。

## 使用方法

```bash
python scripts/main.py --type toggle --p1 P1 --p2 P2
python scripts/main.py --type oscillator
```

## 回路类型

- 拨动开关（Toggle switch）：双稳态基因开关
- 振荡器（Oscillator）：Repressilator 回路

## 输出

- 回路设计方案
- 元件列表
- 预期行为描述

## 风险评估

| 风险指标 | 评估 | 等级 |
|----------|------|------|
| 代码执行 | 本地执行 Python/R 脚本 | 中 |
| 网络访问 | 无外部 API 调用 | 低 |
| 文件系统访问 | 读取输入文件，写入输出文件 | 中 |
| 指令篡改 | 标准提示词规范 | 低 |
| 数据暴露 | 输出文件保存至工作区 | 低 |

## 安全检查清单

- [ ] 无硬编码凭据或 API 密钥
- [ ] 无未授权文件系统访问（../）
- [ ] 输出不暴露敏感信息
- [ ] 已设置提示词注入防护
- [ ] 已验证输入文件路径（无 ../ 穿越）
- [ ] 输出目录限制在工作区内
- [ ] 脚本在沙箱环境中执行
- [ ] 错误信息已脱敏（不暴露堆栈跟踪）
- [ ] 依赖项已审计

## 前提条件

无需额外 Python 包。

## 评估标准

### 成功指标
- [ ] 成功执行主要功能
- [ ] 输出满足质量标准
- [ ] 优雅处理边界情况
- [ ] 性能可接受

### 测试用例
1. **基础功能**：标准输入 → 预期输出
2. **边界情况**：无效输入 → 优雅错误处理
3. **性能测试**：大数据集 → 可接受的处理时间

## 生命周期状态

- **当前阶段**：草稿
- **下次审查日期**：2026-03-06
- **已知问题**：无
- **计划改进**：
  - 性能优化
  - 支持更多功能
