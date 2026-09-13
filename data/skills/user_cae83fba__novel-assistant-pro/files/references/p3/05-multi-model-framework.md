# P3-05 多模型协作框架

> v3.x 路线图。不同任务用不同模型，让创作更稳定、更高效。

## 目标

不同创作任务调用不同模型：

| 任务 | 推荐模型特性 |
|---|---|
| 灵感发散 | 温度高（0.8-1.0）、多样性优先 |
| 大纲规划 | 温度中（0.5-0.7）、逻辑性强 |
| 正文产出 | 温度中（0.6-0.7）、稳定性高 |
| 对白生成 | 温度中（0.7）、角色化 |
| 校对润色 | 温度低（0.2-0.4）、准确性高 |
| 风格一致性检查 | 温度低（0.1-0.3）、客观性 |
| 冲突检测 | 温度低（0.1-0.2）、逻辑严密 |
| 风格漂移分析 | 温度低（0.1-0.3）、统计性 |

## 模型路由

```text
任务输入
  ↓
任务分类器（自动）
  ↓
模型路由器
  ├─ 灵感发散 → 模型 A（高温度）
  ├─ 正文产出 → 模型 B（中温度）
  ├─ 校对润色 → 模型 C（低温度）
  └─ 检测分析 → 模型 D（极低温度）
  ↓
结果整合
```

## 配置示例

```yaml
# references/p3/claude-3-opusonfig.yaml
models:
  inspiration:
    provider: openai
    model: gpt-4
    temperature: 0.9
    top_p: 0.95
    use_for:
      - 灵感发散
      - 大纲初稿
      - 故事设定

  drafting:
    provider: openai
    model: gpt-4
    temperature: 0.65
    top_p: 0.9
    use_for:
      - 章节正文
      - 对白生成
      - 场景描写

  polishing:
    provider: anthropic
    model: claude-3-opus
    temperature: 0.3
    top_p: 0.85
    use_for:
      - 校对润色
      - 去 AI 腔
      - 文笔优化

  analysis:
    provider: anthropic
    model: claude-3-sonnet
    temperature: 0.1
    top_p: 0.8
    use_for:
      - 冲突检测
      - 一致性检查
      - 风格漂移分析
```

## 任务路由脚本

```python
# scripts/route-task.py
"""
根据任务类型路由到不同模型。

使用：
    python3 scripts/route-task.py --task inspiration --prompt "..."
"""

import argparse
import json
import sys
from pathlib import Path


TASK_MODEL_MAPPING = {
    'inspiration': {'temperature': 0.9, 'top_p': 0.95},
    'drafting': {'temperature': 0.65, 'top_p': 0.9},
    'polishing': {'temperature': 0.3, 'top_p': 0.85},
    'analysis': {'temperature': 0.1, 'top_p': 0.8},
}


def route_task(task: str, prompt: str, model_config_path: Path = None):
    """路由任务到对应模型配置。"""
    if task not in TASK_MODEL_MAPPING:
        return {'error': f'未知任务类型：{task}'}

    config = TASK_MODEL_MAPPING[task]

    if model_config_path and model_config_path.exists():
        full_config = json.loads(model_config_path.read_text(encoding='utf-8'))
        if task in full_config.get('models', {}):
            config.update(full_config['models'][task])

    return {
        'task': task,
        'prompt': prompt,
        'model_config': config,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='novel-assistant-pro · 任务路由（v3.x）')
    parser.add_argument('--task', required=True, choices=list(TASK_MODEL_MAPPING.keys()))
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--config', type=Path, help='模型配置文件')

    args = parser.parse_args()
    result = route_task(args.task, args.prompt, args.config)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 集成方式

```text
novel-assistant-pro 的每个能力调用前：
  1. 任务分类（自动）
  2. 模型路由（按配置）
  3. 调用对应模型
  4. 结果整合
```

## 与 P3-03 的结合

读者反馈分析需要"低温度"模型（保证客观）；风格调整建议需要"中温度"模型（保证多样性）。

## 实现阶段

| 阶段 | 内容 |
|---|---|
| 1 | 任务分类器 + 模型路由脚本 |
| 2 | 多模型并行调用（草稿 + 校对） |
| 3 | 模型投票机制（多模型结果对比） |
| 4 | 自适应模型选择（基于历史效果） |

## 状态

**Roadmap（v3.4+）** - 当前版本使用单一模型。

## 相关链接

- 风格 DNA：`references/style-dna.md`
- 多模型集成：见各模型官方文档
