#!/usr/bin/env python3
"""事件链闭合检验模板（概念级）

本脚本是 UEC-CBL-ERC214-KW 体系中事件链闭合检验的概念级实现。
不包含具体数值——所有参数需用户根据实际数据填充。

用法：
  python verify_chain.py --target "曹雪芹卒于1763" --events events.json
  python verify_chain.py --demo
"""

import argparse
import json
import sys
from dataclasses import dataclass, field


@dataclass
class ChainEvent:
    """事件链中的一个节点"""
    date: str
    description: str
    evidence_type: str = ""  # 物质/文献/制度/行为
    confidence: str = "待实证"


@dataclass
class ChainReport:
    target: str
    events: list = field(default_factory=list)
    fractures: list = field(default_factory=list)
    dimensions_closed: int = 0
    verdict: str = "待判定"

    @property
    def is_closed(self) -> bool:
        return len(self.fractures) == 0

    def summary(self) -> str:
        lines = [
            f"验证目标: {self.target}",
            f"事件链节点: {len(self.events)} 个",
            f"断裂点: {len(self.fractures)} 个",
            f"闭合维度: {self.dimensions_closed}/4",
            f"判定: {self.verdict}",
        ]
        if self.fractures:
            lines.append("断裂点清单:")
            for f in self.fractures:
                lines.append(f"  - {f}")
        return "\n".join(lines)


def demo():
    """内置示例：曹雪芹卒年反证（概念级）"""
    events = [
        ChainEvent("1763-02-12", "传统说认定的卒日（壬午除夕）", "文献"),
        ChainEvent("1765", "同仁堂病历记录（结核杆菌）", "物质", "待实证"),
        ChainEvent("1766", "药房购药记录", "制度", "待实证"),
        ChainEvent("1770", "盐引交易记录", "制度", "待实证"),
        ChainEvent("1775-03-05", "行政文书提及", "制度", "待实证"),
        ChainEvent("1775-11-22", "张阶封箱", "制度", "待实证"),
        ChainEvent("1775-12-22", "官方死亡确认", "制度", "待实证"),
    ]

    report = ChainReport(
        target="曹雪芹卒于1763-02-12",
        events=events,
        fractures=[
            "1763年后存在连续行为记录（至少4条）",
            "事件链跨越12年无法闭合于1763节点",
            "官方死亡确认日期1775-12-22与X节点矛盾",
        ],
        dimensions_closed=3,
        verdict="X节点（1763卒）不成立——事件链无法闭合，CBL压力分析指向1775年",
    )

    print("=" * 60)
    print("事件链闭合检验 · 演示")
    print("=" * 60)
    print(report.summary())
    print()
    print("注意：以上为概念级示例，具体证据需真实数据填充。")


def main():
    ap = argparse.ArgumentParser(description="事件链闭合检验")
    ap.add_argument("--target", help="验证目标节点描述")
    ap.add_argument("--events", help="事件链 JSON 文件路径")
    ap.add_argument("--demo", action="store_true", help="运行内置示例")
    args = ap.parse_args()

    if args.demo or not args.target:
        demo()
        return

    if args.events:
        with open(args.events, encoding="utf-8") as f:
            data = json.load(f)
        events = [ChainEvent(**e) for e in data.get("events", [])]
        report = ChainReport(
            target=args.target,
            events=events,
        )
        print(report.summary())


if __name__ == "__main__":
    main()
