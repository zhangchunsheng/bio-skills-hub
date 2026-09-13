#!/usr/bin/env python3
"""
bionic-brain 快速入门示例
"""

import sys
import os

# 添加脚本目录到路径
scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
sys.path.insert(0, scripts_dir)

from bionic_brain import BionicBrain, analyze, get_brain

def example_basic():
    """基础用法"""
    print("\n" + "=" * 60)
    print("示例1: 基础分析")
    print("=" * 60)

    # 简单分析
    result = analyze("帮我写一个PPT演示文稿")

    print(f"复杂度: {result['complexity']}")
    print(f"意图: {result['intent']['intent']}")
    print(f"风险: {result['risk']['level']} - {result['risk']['desc']}")
    print(f"置信度: {result['confidence']['score']:.0%}")
    print(f"建议: {result['summary']}")


def example_danger():
    """危险操作检测"""
    print("\n" + "=" * 60)
    print("示例2: 危险操作检测")
    print("=" * 60)

    # 带命令的分析
    result = analyze(
        "清理一下桌面",
        command="rm -rf ~/Desktop/*"
    )

    if result['blocked']:
        print(f"操作被拦截: {result['risk']['desc']}")
        print(f"原因: {result['risk']['warnings']}")
    else:
        print("操作安全")


def example_complex():
    """复杂任务分析"""
    print("\n" + "=" * 60)
    print("示例3: 复杂任务分析")
    print("=" * 60)

    result = analyze("设计一个高并发的分布式系统架构")

    print(f"复杂度: {result['complexity']} (需要深度: {result['required_depth']})")
    print(f"假设方案:")
    for h in result['hypotheses']:
        print(f"  {h['id']}: {h['desc']} (先验: {h.get('prior', 0):.0%})")

    if result['ambiguities']:
        print(f"歧义检测:")
        for q in result['ambiguities']:
            print(f"  - {q}")

    if result['info_theory']['should_ask']:
        print(f"{result['info_theory']['question']}")


def example_learning():
    """学习与进化"""
    print("\n" + "=" * 60)
    print("示例4: 学习与进化")
    print("=" * 60)

    brain = get_brain()

    # 模拟任务完成
    brain.post_task("写PPT", success=True, score=0.9)
    brain.post_task("写代码", success=True, score=0.8)
    brain.post_task("写PPT", success=True, score=0.95)

    # 查看状态
    status = brain.get_status()
    print(f"当前习惯数: {status['habits_count']}")
    print(f"进化代数: {status['evolution_generations']}")
    print(f"最佳适应度: {status['best_fitness']:.2f}")


def example_workflow():
    """完整工作流"""
    print("\n" + "=" * 60)
    print("示例5: 完整工作流")
    print("=" * 60)

    brain = get_brain()

    # 1. 接收任务
    task = "帮我优化一下这个SQL查询"
    print(f"任务: {task}")

    # 2. 分析
    result = brain.analyze(task)
    print(f"\n分析结果:")
    print(f"  复杂度: {result['complexity']}")
    print(f"  意图: {result['intent']['intent']}")
    print(f"  风险: {result['risk']['level']}")

    if result['blocked']:
        print("\n任务被拦截，终止执行")
        return

    # 3. 记录决策
    brain.record_decision(
        action="开始分析SQL",
        reason="复杂度C3，需要深度分析",
        outcome="进行中"
    )

    # 4. 记录产物
    brain.add_artifact("analysis", "/tmp/sql-analysis.md")

    # 5. 完成任务
    brain.post_task(task, success=True, score=0.85)
    print("\n任务完成")


if __name__ == "__main__":
    print("\nbionic-brain 快速入门")
    print("=" * 60)

    example_basic()
    example_danger()
    example_complex()
    example_learning()
    example_workflow()

    print("\n" + "=" * 60)
    print("示例结束")
    print("=" * 60)
