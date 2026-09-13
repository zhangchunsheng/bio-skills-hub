#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-clinic-inquiry skill 自检器

五项检查：
  1. 真相源唯一性 —— references/ 与 SKILL.md 是否出现内容重复（重复 = 分叉风险）
  2. SKILL.md 自包含性 —— 追问阶段必需的规则是否都内联在 SKILL.md 里
  3. 移植性 —— 是否混入机器专属的绝对路径（换机器/换用户即失效）
  4. 数值一致性 —— references 是否另立字数/轮数标准（与 SKILL.md 冲突）
  5. Token 预算 —— 各文件体积与按需加载策略下的每轮开销

改完 skill 任何文件后跑一次：
    python3 scripts/lint_skill.py
退出码 0 = 通过，1 = 有问题。
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 追问阶段必须内联在 SKILL.md 的规则（缺任何一条 → 追问轮就得读 references，破坏预算）
SELF_CONTAINED = {
    "轮数硬门禁": "追问上限 3 轮",
    "一轮一题违规": "一轮一题是最严重的违规",
    "红线清单完整": "报告危急值",
    "自评不抵消红线": "自评程度轻不得抵消红线",
    "头痛专项": "头痛专项",
    "L2 高频漏判": "狂犬暴露",
    "L1/L2 一致性锚点": "L1 时首选科室必须是",
    "一题一维度": "一题只问一个维度",
    "兜底自解释": "不确定检查结果",
    "选项数上限": "压到 4 个选项内",
    "禁伪选项": "占位型伪选项",
    "删组合冗余": "多选删组合冗余",
    "性别硬过滤": "性别硬过滤",
    "年龄过滤": "年龄未知一律按成人",
    "隐式否认": "隐式否认",
    "病程≠年龄": "病程 ≠ 年龄",
    "首轮字数上限": "硬上限 300 字",
    "首轮职责边界": "首轮只写这四项",
    "首轮末句轮换": "首轮末句在下列范式间轮换",
    "禁预告题目": "禁止预告题目内容",
    "禁问号": "禁在过渡话术里出现问号",
    "禁读脚本源码": "不要读它的源码",
    "按需加载禁令": "禁止在追问阶段读",
    "摘要字数": "100-200 字",
    "原因两栏": "to_exclude",
    "行动计划分组": "action_plan",
    "质检门禁": "质检门禁",
    "L编号不外露": "绝不会渲染给用户",
    "答问字段": "`answers`",
    "行动模块": "可选行动模块", 
}

# 允许出现在 references 里的"指针式"提及：这些是引用 SKILL.md 而非重复定义
POINTER_MARKERS = ("真相源", "唯一定义位置", "见 `SKILL.md", "见 SKILL.md",
                   "只改 `SKILL.md`", "lint_skill.py", "唯一真相源")

# 固定常量：这些字面文本本就要在模板/声明/代码里各出现一次，不算规则分叉
ALLOWED_DUP_CONSTANTS = (
    "以上仅供参考，不替代线下就诊。如症状加重或出现危险信号，请及时就医。",
    "健康问问 AI诊室",
    "就诊贴士",
)


def norm(s: str) -> str:
    return re.sub(r'[*`#>|\-—\s。，、：；！？（）()「」【】""\u3000]+', "", s)


def est_tokens(s: str) -> int:
    zh = sum(1 for c in s if "\u4e00" <= c <= "\u9fff")
    return int(zh * 1.3 + (len(s) - zh) / 3.2)


def check_self_contained(skill: str):
    missing = [k for k, v in SELF_CONTAINED.items() if v not in skill]
    return missing


def check_duplication(skill: str):
    """检测 references 中是否有段落与 SKILL.md 实质重复。"""
    skill_n = norm(skill)
    const_n = [norm(c) for c in ALLOWED_DUP_CONSTANTS]
    findings = []
    for p in sorted((ROOT / "references").glob("*.md")):
        txt = p.read_text(encoding="utf-8")
        for para in re.split(r"\n\s*\n", txt):
            n = norm(para)
            if len(n) < 40:
                continue
            # 指针式引用不算重复
            if any(m in para for m in POINTER_MARKERS):
                continue
            # 剔除固定常量后再比对，避免免责声明等字面量误报
            probe = n
            for c in const_n:
                probe = probe.replace(c, "")
            if len(probe) < 40:
                continue
            # 连续 24 字命中即判为实质重复
            hit = next((probe[i:i + 24] for i in range(0, len(probe) - 24, 8)
                        if probe[i:i + 24] in skill_n), None)
            if hit:
                first = para.strip().split("\n")[0][:56]
                findings.append((p.name, first, hit[:24]))
    return findings


def check_portability():
    """检测机器专属的绝对路径——这类路径换机器/换用户就失效。"""
    # 机器专属路径模式（会随用户名、发行版、Python 版本变化）
    bad = [
        (r"/Users/[A-Za-z0-9._-]+", "macOS 用户家目录绝对路径"),
        (r"/home/[A-Za-z0-9._-]+", "Linux 用户家目录绝对路径"),
        (r"[A-Za-z]:\\\\Users", "Windows 用户家目录绝对路径"),
        (r"~/\.workbuddy/skills/", "写死的 skill 安装位置"),
        (r"binaries/python/versions/\d", "写死的 Python 版本路径"),
    ]
    # 反例/禁令语境：这些行是在教"不要这样写"，不算违规
    NEGATIVE_CTX = ("不要", "严禁", "禁止", "不许", "换一台机器", "即失效",
                    "就会失效", "跑不了", "这类路径", "反例", "❌")
    findings = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in (".md", ".py", ".json", ".sh"):
            continue
        rel = p.relative_to(ROOT)
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            # 本检测器自身的正则定义与白名单行不算
            if p.name == "lint_skill.py":
                continue
            # 教学性反例不算
            if any(k in line for k in NEGATIVE_CTX):
                continue
            for pat, why in bad:
                if re.search(pat, line):
                    findings.append((str(rel), i, why, line.strip()[:64]))
                    break
    return findings


def check_conflicts(skill: str):
    """检测跨文件的数值矛盾——references 里另立字数/轮数标准会与 SKILL.md 分叉。

    典型历史事故：SKILL.md 写「首轮 200-300 字」，composer-voice.md 写「约 400-600 字」，
    导致同一 skill 两次问诊行为不一致。lint 的重复检测抓不到这种「不同数值」的冲突。
    """
    # 这些量纲的唯一定义位置是 SKILL.md，references 里出现具体数值即为分叉
    NUMERIC_CLAIMS = [
        (r"首轮[^\n]{0,12}?(\d{2,4})\s*[-–~至]\s*(\d{2,4})\s*字", "首轮字数区间"),
        (r"不低于\s*(\d{2,4})\s*字", "首轮字数下限"),
        (r"追问[^\n]{0,8}?上限\s*(\d+)\s*轮", "追问轮数上限"),
        (r"每轮[^\n]{0,8}?(\d)\s*[-–]\s*(\d)\s*题", "每轮题数"),
        (r"每题[^\n]{0,10}?(\d)\s*[-–]\s*(\d)\s*个?选项", "每题选项数"),
    ]
    findings = []
    for p in sorted((ROOT / "references").glob("*.md")):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            # 指针式引用（明确写了以 SKILL.md 为准）不算分叉
            if any(m in line for m in POINTER_MARKERS):
                continue
            for pat, why in NUMERIC_CLAIMS:
                m = re.search(pat, line)
                if m:
                    findings.append((p.name, i, why, line.strip()[:64]))
                    break
    return findings


def check_budget(skill: str):
    sizes = {p.name: est_tokens(p.read_text(encoding="utf-8"))
             for p in sorted((ROOT / "references").glob("*.md"))}
    skill_t = est_tokens(skill)
    ask = skill_t
    report = skill_t + sizes.get("summary-report.md", 0) + sizes.get("evidence-search.md", 0)
    return skill_t, sizes, ask, report


def main():
    skill_path = ROOT / "SKILL.md"
    if not skill_path.is_file():
        print(f"[错误] 找不到 {skill_path}", file=sys.stderr)
        return 1
    skill = skill_path.read_text(encoding="utf-8")
    ok = True

    print("=" * 66)
    print("1) 真相源唯一性")
    print("=" * 66)
    dups = check_duplication(skill)
    if dups:
        ok = False
        print(f"✗ 发现 {len(dups)} 处与 SKILL.md 实质重复（分叉风险）:\n")
        for fn, head, frag in dups:
            print(f"   {fn}")
            print(f"     段落: {head}")
            print(f"     重复片段: …{frag}…")
        print("\n   处理：把重复内容从 reference 里删掉，只留一行指向 SKILL.md 的指针。")
        print("   安全规则（红线/分级）尤其不能有两份——分叉会导致判定不一致。")
    else:
        print("✓ references 中无与 SKILL.md 重复的实质内容")

    print("\n" + "=" * 66)
    print("2) SKILL.md 自包含性（追问阶段无需读 references）")
    print("=" * 66)
    missing = check_self_contained(skill)
    if missing:
        ok = False
        print(f"✗ 缺失 {len(missing)} 条必须内联的规则:")
        for m in missing:
            print(f"   - {m}（关键字 “{SELF_CONTAINED[m]}”）")
        print("\n   缺失会导致追问轮不得不去读 references，每轮多背上万 token。")
    else:
        print(f"✓ {len(SELF_CONTAINED)} 条追问阶段规则全部内联")

    print("\n" + "=" * 66)
    print("3) 移植性（换机器/换用户是否还能跑）")
    print("=" * 66)
    ports = check_portability()
    if ports:
        ok = False
        print(f"✗ 发现 {len(ports)} 处机器专属绝对路径:\n")
        for rel, ln, why, txt in ports:
            print(f"   {rel}:{ln}  [{why}]")
            print(f"     {txt}")
        print("\n   处理：改用「SKILL.md 所在目录 + 相对路径」，解释器写 `python3`。")
    else:
        print("✓ 无机器专属绝对路径，换机器可直接用")

    print("\n" + "=" * 66)
    print("4) 数值一致性（references 是否另立字数/轮数标准）")
    print("=" * 66)
    confs = check_conflicts(skill)
    if confs:
        ok = False
        print(f"✗ 发现 {len(confs)} 处与 SKILL.md 可能冲突的数值规定:\n")
        for rel, ln, why, txt in confs:
            print(f"   references/{rel}:{ln}  [{why}]")
            print(f"     {txt}")
        print("\n   处理：删掉该数值，改为一行指向 SKILL.md 的指针。")
        print("   量纲（字数/轮数/题数/选项数）的唯一真相源必须是 SKILL.md。")
    else:
        print("✓ references 未另立数值标准，量纲口径唯一")

    print("\n" + "=" * 66)
    print("5) Token 预算")
    print("=" * 66)
    skill_t, sizes, ask, report = check_budget(skill)
    print(f"   SKILL.md{'':<22}{skill_t:>7,}")
    for k, v in sorted(sizes.items(), key=lambda x: -x[1]):
        print(f"   references/{k:<19}{v:>7,}")
    print(f"\n   追问轮开销（只读 SKILL.md）      {ask:>7,}")
    print(f"   报告轮开销（+2 个 reference）    {report:>7,}")
    total = ask * 3 + report
    print(f"   3 轮追问 + 1 报告轮 skill 侧合计 {total:>7,}")
    if ask > 8000:
        ok = False
        print(f"\n✗ 追问轮开销 {ask:,} 超过 8,000 预算——SKILL.md 该瘦身了")
    else:
        print(f"\n✓ 追问轮开销在 8,000 预算内")

    print("\n" + "=" * 66)
    print("通过 ✓" if ok else "存在问题 ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
