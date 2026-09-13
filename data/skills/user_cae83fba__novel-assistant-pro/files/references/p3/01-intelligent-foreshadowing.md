# P3-01 智能伏笔推荐

> v3.x 路线图。基于章节节奏与历史伏笔埋设点，预测 P1 伏笔的最佳回收窗口。

## 目标

减少"伏笔被遗忘"的常见痛点。系统主动建议"现在是不是该回收 F001？"。

## 算法思路

```text
输入：
  - 记忆文件（含未解决伏笔表 + 章节概要）
  - 当前章节号
  - 历史埋设点

输出：
  - P1 伏笔的"建议回收优先级"列表
  - 每条伏笔的"建议回收章节窗口"
  - 推荐的回收方式（揭示 / 反转 / 部分揭示）
```

## 推荐算法

```python
# 伪代码
def recommend_foreshadowing(memory_file, current_chapter):
    unresolved_p1 = parse_unresolved_p1(memory_file)
    recommendations = []

    for fs in unresolved_p1:
        buried_chapter = fs['buried_chapter']
        stale_chapters = current_chapter - buried_chapter
        target_chapter = fs.get('target_chapter')

        # 推荐优先级 = 1 - 与目标章节的距离 / 阈值
        if target_chapter:
            distance = abs(current_chapter - target_chapter)
            priority = max(0, 1 - distance / 5)  # 5 章窗口
        else:
            # 没有目标章节：基于节奏自动推荐
            if stale_chapters > 10:
                priority = 0.9  # 强烈建议
            elif stale_chapters > 5:
                priority = 0.6
            else:
                priority = 0.3

        recommendations.append({
            'id': fs['id'],
            'priority': priority,
            'stale_chapters': stale_chapters,
            'suggested_chapter_window': (current_chapter, current_chapter + 3),
            'suggested_method': '反转揭示',  # or '部分揭示'
        })

    return sorted(recommendations, key=lambda r: r['priority'], reverse=True)
```

## 集成方式

```text
用户："续写第 8 章"

技能：
  1. 调用智能伏笔推荐
  2. 输出："建议本章回收 F001（埋设于第 3 章，已 5 章未推进）"
  3. 在续写流程中融入推荐
```

## 输出格式

```markdown
=== 智能伏笔推荐 ===

当前章节：第 8 章
未解决 P1：3 个

强烈建议本章回收（优先级 ≥ 0.8）：
  - F001（埋设于第 3 章，已 5 章未推进）
    建议回收窗口：第 8-10 章
    建议方式：反转揭示
    与当前章节的契合度：高（本章涉及顾闻对质）

中度建议（优先级 0.5-0.8）：
  - F002（埋设于第 1 章，已 7 章未推进）
    建议回收窗口：第 10-12 章

轻度建议（优先级 < 0.5）：
  - F005（埋设于第 5 章，已 3 章未推进）
```

## 数据要求

- 至少 30 章以上的章节概要（用于训练节奏模型）
- 每条伏笔的"埋设章节"和"目标回收章节"（可选）
- 章节字数与节拍卡（用于判断节奏）

## 实现阶段

| 阶段 | 内容 |
|---|---|
| 1 | 基于规则的推荐（阈值 + 距离） |
| 2 | 基于历史数据的统计推荐 |
| 3 | 基于 LLM 的语义推荐（结合情节上下文） |
| 4 | 多目标优化（同时考虑伏笔、节奏、人物弧） |

## 参考资源

- 伏笔追踪：`references/foreshadowing.md`
- 章节节拍：`references/pacing/chapter-pacing.md`
- 脚本：`scripts/validate-novel-memory.py --check-p1-stale`

## 状态

**Roadmap（v3.1+）** - 当前版本未实现，已预留接口。
