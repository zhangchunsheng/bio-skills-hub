# P3 长期演进路线图

> v2.0.0 当前未实现，预留给 v3.x。详见各模块设计文档。

## 模块列表

| 模块 | 状态 | 文档 | 优先级 |
|---|---|---|---|
| P3-01 智能伏笔推荐 | Roadmap（v3.1+） | [01-intelligent-foreshadowing.md](./01-intelligent-foreshadowing.md) | 高 |
| P3-02 跨作品知识迁移 | Roadmap（v3.1+） | [02-cross-work-migration.md](./02-cross-work-migration.md) | 中 |
| P3-03 读者数据反馈接入 | Roadmap（v3.2+） | [03-reader-data-feedback.md](./03-reader-data-feedback.md) | 中 |
| P3-04 与 publishing-assistant 协同 | Roadmap（v3.3+） | [04-publishing-collaboration.md](./04-publishing-collaboration.md) | 低 |
| P3-05 多模型协作框架 | Roadmap（v3.4+） | [05-multi-model-framework.md](./05-multi-model-framework.md) | 低 |

## 设计原则

| 原则 | 说明 |
|---|---|
| 用户价值优先 | 每个模块都解决明确痛点 |
| 数据驱动决策 | 基于真实使用数据决定优先级 |
| 渐进式实现 | 每个模块分 4 个阶段逐步上线 |
| 向后兼容 | 不破坏 v2.0.0 已建立的接口 |

## 实现节奏

```text
v3.0（基础升级）
  ├─ 性能优化
  ├─ 新流派模板
  └─ 新平台调性卡

v3.1（智能辅助）
  ├─ P3-01 智能伏笔推荐
  └─ P3-02 跨作品知识迁移

v3.2（数据闭环）
  └─ P3-03 读者数据反馈接入

v3.3（生态集成）
  └─ P3-04 与 publishing-assistant 协同

v3.4（多模型协作）
  └─ P3-05 多模型协作框架
```

## 反馈与建议

如对 P3 路线图有建议，请：

- 在 问题追踪系统 中提交 feature request
- 或在 `references/p3/` 下追加 `XX-new-feature.md` 设计草稿

## 状态

**All Roadmap** - 当前 v2.0.0 版本未实现 P3 任何模块。
