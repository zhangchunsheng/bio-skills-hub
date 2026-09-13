#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quality_check.py —— 18 项质量自查

任 3 项以上不通过 -> 退回润色（status=reject）。

部分项（13 人设一致 / 14 核心冲突贯穿 / 18 符合情绪曲线）依赖跨章上下文，
通过可选参数提供时做启发式检测，否则标记为 manual（不计入 fail_count）。

用法：
  python quality_check.py <chapter.md>
      [--min 2200] [--max 2800]
      [--prev-hook TYPE]
      [--profile "弃妇;隐藏大佬"]        # 主角人设关键词，用于一致性启发式
      [--core-conflict "复仇"]            # 核心冲突关键词
      [--emotion-position 压|小扬|爆]
      [--json]
"""
import argparse
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import validate_chapter as V  # 复用检测函数

ADJ_WORDS = ["美丽", "漂亮", "愤怒", "悲伤", "高兴", "巨大", "微小", "安静", "冰冷", "炽热",
             "温柔", "残忍", "邪恶", "善良", "绝望", "璀璨", "绚丽", "漆黑", "雪白", "红润",
             "阴冷", "狰狞", "明媚", "凄美", "诡异", "呆滞", "空洞", "炽烈"]
FOUR_CHAR = ["总而言之", "毫无疑问", "不可思议", "目瞪口呆", "心如刀绞", "怒火中烧",
             "泪流满面", "不寒而栗", "毛骨悚然", "心灰意冷", "恍然大悟", "意料之中",
             "显而易见", "不言而喻", "总而言之", "理所当然", "顺理成章", "水到渠成"]
EMO_SAY = re.compile(r"(愤怒|悲伤|温柔|高兴|冷漠|激动|平静|无奈|失望|紧张|害怕|兴奋|悲伤)地(说|想|问|看|道|笑)")
WEAK_OPEN = ["那是一个", "这是一个", "清晨", "傍晚", "他揉了揉", "她揉了揉", "我叫", "我叫", "我叫"]
TRANSFER_WORDS = ["却", "但", "原来", "竟", "才是", "不过", "从来", "终于", "活该", "偏偏", "反倒", "殊不知"]
TURN_WORDS = ["看到", "终于", "出现", "希望", "转机", "亮了", "成了", "答应", "答应了"]
CLIMAX_WORDS = ["爆发", "反转", "打脸", "揭晓", "崩溃", "复仇", "雪恨", "逆袭", "碾压", "兑现", "翻盘"]


def check(chapter_path, args):
    with open(chapter_path, encoding="utf-8") as f:
        text = f.read()
    total = V.count_cjk(text)
    results = []

    def add(num, name, passed, note):
        results.append({"no": num, "name": name, "pass": passed, "note": note})

    # 1 字数
    wc = total
    add(1, "字数达标", args.min <= wc <= args.max, f"{wc} 字")

    # 2 前50字
    ot, _ = V.detect_open_type(V.first_n_chars(text, 50))
    add(2, "前50字合规", ot is not None, f"类型={ot or 'none'}")

    # 3 前20%冲突
    add(3, "前20%即时冲突", V.has_early_conflict(text), "")

    # 4 对话占比
    _, _, ratio = V.dialog_ratio(text)
    add(4, "对话占比达标", args.dmin <= ratio <= args.dmax, f"{ratio:.0%}")

    # 5 结尾钩子
    ht, _ = V.detect_hook(text)
    add(5, "结尾有钩子", ht is not None, f"类型={ht or 'none'}")

    # 6 钩子非重复
    if args.prev_hook is None:
        add(6, "钩子非连续重复", True, "首章")
    else:
        add(6, "钩子非连续重复", ht != args.prev_hook, f"上章={args.prev_hook}")

    # 7 无低效开头
    head200 = V.first_n_chars(text, 200)
    weak = any(w in head200 for w in WEAK_OPEN)
    add(7, "无低效开头", not weak, "命中低效开头" if weak else "")

    # 8 形容词密度
    adj_cnt = sum(text.count(w) for w in ADJ_WORDS)
    adj_density = adj_cnt / total if total else 0
    add(8, "形容词密度不过高", adj_density < 0.015, f"{adj_density:.1%}")

    # 9 四字词密度（连续3+）
    hits = [w for w in FOUR_CHAR if w in text]
    # 简单窗口检测：任意两 idiom 距离 < 200 字视为密集
    positions = [text.find(w) for w in hits if text.find(w) >= 0]
    dense = False
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            if 0 < abs(positions[i] - positions[j]) < 200:
                dense = True
    add(9, "四字词密度不过高", not dense, f"命中{len(hits)}个四字词")

    # 10 角色说话方式差异化
    speakers = set(re.findall(r"([一-龥]{1,4})说", text))
    # 去除"有人说"等泛称
    speakers = {s for s in speakers if s not in ("有人", "有人", "大家", "众人")}
    if len(speakers) >= 2:
        add(10, "角色说话方式差异化", True, f"检测到说话人:{','.join(list(speakers)[:5])}")
    else:
        add(10, "角色说话方式差异化", None, "单一说话人/需人物档案核对(manual)")

    # 11 无情绪直述堆砌
    emo_cnt = len(EMO_SAY.findall(text))
    add(11, "无情绪直述堆砌", emo_cnt < 3, f"'XX地说'出现{emo_cnt}次")

    # 12 含金句
    sentences = re.split(r"[。！？!?]", text)
    has_gold = any(8 <= len(V.CJK.findall(s)) <= 22 and any(w in s for w in TRANSFER_WORDS) for s in sentences)
    add(12, "含金句", has_gold, "" if has_gold else "未检测到可摘录短句")

    # 13 主角人设一致
    if args.profile:
        kws = [k.strip() for k in args.profile.split(";") if k.strip()]
        # 启发式：若同时出现对立关键词则疑似打架
        contra = [("怕水", "游泳"), ("普通人", "玄学"), ("弃妇", "大佬")]
        clash = any(a in text and b in text for a, b in contra)
        add(13, "主角人设一致", not clash, "检测到潜在人设冲突" if clash else "未检出冲突(启发式)")
    else:
        add(13, None, "需人物档案核对(manual)", "")

    # 14 核心冲突贯穿
    if args.core_conflict:
        add(14, "核心冲突贯穿", args.core_conflict in text, f"关键词'{args.core_conflict}'未出现" if args.core_conflict not in text else "")
    else:
        add(14, None, "需核心冲突关键词(manual)", "")

    # 15 有情绪推进
    has_neg = any(w in text for w in ["压", "辱", "困", "难", "敌", "战"])
    has_pos = any(w in text for w in TURN_WORDS) or ht is not None
    add(15, "有情绪推进", has_neg and has_pos, "")

    # 16 信息密度
    filler = text.count("（") + text.count("简单来说") + text.count("换句话说")
    add(16, "信息密度够", filler < 3, f"说明性括号/解释{filler}处")

    # 17 钩子类型轮换（同6）
    if args.prev_hook is None:
        add(17, "钩子类型轮换", True, "首章")
    else:
        add(17, "钩子类型轮换", ht != args.prev_hook, f"上章={args.prev_hook}")

    # 18 符合情绪曲线
    if args.emotion_position:
        if args.emotion_position == "爆":
            ok = any(w in text for w in CLIMAX_WORDS)
            add(18, "符合情绪曲线", ok, "爆点章缺高潮词" if not ok else "")
        elif args.emotion_position == "压":
            ok = V.has_early_conflict(text)
            add(18, "符合情绪曲线", ok, "压章缺冲突" if not ok else "")
        else:  # 小扬
            ok = any(w in text for w in TURN_WORDS)
            add(18, "符合情绪曲线", ok, "扬章缺转机词" if not ok else "")
    else:
        add(18, None, "需情绪定位(manual)", "")

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter")
    ap.add_argument("--min", type=int, default=2200)
    ap.add_argument("--max", type=int, default=2800)
    ap.add_argument("--dmin", type=float, default=0.35)
    ap.add_argument("--dmax", type=float, default=0.45)
    ap.add_argument("--prev-hook", default=None)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--core-conflict", default=None)
    ap.add_argument("--emotion-position", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = check(args.chapter, args)
    fails = [r for r in results if r["pass"] is False]
    manuals = [r for r in results if r["pass"] is None]
    passed = [r for r in results if r["pass"] is True]
    status = "reject" if len(fails) >= 3 else "deliver"

    out = {
        "file": args.chapter,
        "passed": len(passed),
        "failed": len(fails),
        "manual": len(manuals),
        "fail_count": len(fails),
        "status": status,
        "message": "退回润色：列出不通过项" if status == "reject" else "可交付（manual项建议人审）",
        "items": results,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"=== 18 项质量自查：{args.chapter} ===")
        for r in results:
            tag = "✅" if r["pass"] is True else ("❌" if r["pass"] is False else "⚠️")
            print(f"[{r['no']:>2}] {tag} {r['name']}  {r['note']}")
        print(f"\n通过 {len(passed)} / 不通过 {len(fails)} / 需人审 {len(manuals)}")
        print(f"结论：{'退回润色 ❌' if status == 'reject' else '可交付 ✅'}")


if __name__ == "__main__":
    main()
