#!/usr/bin/env python3
"""
报告合规校验工具（check_report.py）

用途：对生成的 HTML 报告做机器可检的合规校验，覆盖「七条硬性要求」
      与结构、命名、表格一致性。生成报告后应跑一遍再交付。

为什么需要：
  有些错误肉眼看不出来但会破坏阅读 —— 典型是表格加列后漏改某一行，
  渲染时整行错位；还有目录锚点失效、章节断号、CDN 残留。
  这些用正则一扫即知，不该靠人眼。

用法：
  python3 check_report.py <报告.html>
  python3 check_report.py <报告.html> --quiet     # 只输出失败项

退出码：
  0 = 全部通过    1 = 存在不合规项

参考完整示例：examples/sample_report.html
"""

import argparse
import os
import re
import sys

EXPECTED_TITLES = [
    "报告总结", "处理优先级", "异常指标详细解读", "关联性分析",
    "干扰因素排查", "风险预测", "趋势变化", "下一步",
    "生活指导", "参考指南", "重要提醒",
]

# 不该出现在成品报告里的词
DEV_TRACES = ["示例", "模板", "TODO", "占位", "待评审", "方案 v2", "demo", "FIXME"]

# 身份信息字段
PRIVACY_FIELDS = ["身份证", "手机号", "姓名：", "门诊号", "住院号", "病案号"]

# 已废弃的口语化/内部术语标题
BAD_TITLES = [
    "先看这里", "哪些要紧", "每项指标什么意思", "几项异常放在一起",
    "虚惊一场", "风险算给你看", "和以前比", "接下来该做什么",
    "吃动睡", "交叉模式发现", "异常指标综合分析", "定量风险评估",
]

# 不该暴露给用户的内部档位代号
LEVEL_CODES = r"L[1-4]\s*档|按\s*L[1-4]|档位[：:]\s*L[1-4]|>L[1-4]<"


class Checker:
    def __init__(self, path, quiet=False):
        self.path = path
        self.quiet = quiet
        self.raw = open(path, encoding="utf-8").read()
        # 去掉 HTML 注释后的可见内容 —— 注释里的示例文本不算违规
        self.body = re.sub(r"<!--.*?-->", "", self.raw, flags=re.S)
        self.failed = []
        self.passed = []

    def ok(self, name, detail=""):
        self.passed.append((name, detail))

    def bad(self, name, detail):
        self.failed.append((name, detail))

    # ── 七条硬性要求 ──────────────────────────────────────
    def check_no_external(self):
        urls = [
            u for u in re.findall(r'(?:src|href)=["\'](https?://[^"\']+)', self.raw)
            if "w3.org" not in u
        ]
        if urls:
            self.bad("零外部依赖", f"发现 {len(urls)} 个外链：{urls[:3]}")
        else:
            self.ok("零外部依赖")

    def check_no_script(self):
        n = len(re.findall(r"<script", self.body, re.I))
        if n:
            self.bad("零 script", f"发现 {n} 个 script 标签")
        else:
            self.ok("零 script")

    def check_inline_svg(self):
        has_trend = "趋势变化" in self.body
        if not has_trend:
            self.ok("内联 SVG 趋势图", "单份报告，无趋势段（跳过）")
            return
        if re.search(r"<polyline", self.body):
            self.ok("内联 SVG 趋势图")
        else:
            self.bad("内联 SVG 趋势图", "有趋势段但未找到 polyline，图表可能缺失")

    def check_color_scheme(self):
        if re.search(r'name=["\']color-scheme["\'][^>]*light', self.raw):
            self.ok("锁定浅色模式")
        else:
            self.bad("锁定浅色模式",
                     '缺 <meta name="color-scheme" content="light">，'
                     "手机深色模式会反色")

    def check_table_wrap(self):
        tables = len(re.findall(r"<table[^>]*>", self.body))
        wraps = len(re.findall(r'class="tw"', self.body))
        if tables == 0:
            self.ok("表格可横滑", "无表格")
        elif tables == wraps:
            self.ok("表格可横滑", f"{tables} 个表格全部包裹")
        else:
            self.bad("表格可横滑", f"{tables} 个表格但只有 {wraps} 个 .tw 容器")

    def check_no_dev_traces(self):
        found = [w for w in DEV_TRACES if w.lower() in self.body.lower()]
        if found:
            self.bad("无开发痕迹", f"发现：{found}")
        else:
            self.ok("无开发痕迹")

    def check_no_privacy(self):
        found = [w for w in PRIVACY_FIELDS if w in self.body]
        if found:
            self.bad("无身份信息", f"发现：{found}")
        else:
            self.ok("无身份信息")

    # ── 结构与命名 ────────────────────────────────────────
    def check_sections(self):
        secs = re.findall(
            r'<span class="no">(\d+)</span><span class="ttl">(.*?)</span>', self.body
        )
        disc = re.search(
            r'<div class="dh"><span class="no">(\d+)</span><span>(.*?)</span>', self.body
        )
        found = [(int(n), t) for n, t in secs]
        if disc:
            found.append((int(disc.group(1)), disc.group(2)))

        nums = [n for n, _ in found]
        titles = [t for _, t in found]

        # 允许单份报告缺 07（趋势），此时序号应为 1-6,8-11
        full = list(range(1, 12))
        no_trend = [n for n in full if n != 7]
        if nums == full:
            self.ok("章节序号", "01~11 完整")
        elif nums == no_trend:
            self.ok("章节序号", "01~11（单份报告，无 07 趋势段）")
        else:
            self.bad("章节序号", f"序号异常：{nums}")

        expected = {i + 1: t for i, t in enumerate(EXPECTED_TITLES)}
        wrong = [(n, t, expected.get(n)) for n, t in found if expected.get(n) != t]
        if wrong:
            self.bad("章节标题", f"与规范不符：{wrong}")
        else:
            self.ok("章节标题", f"{len(titles)} 段全部符合规范")

    def check_toc(self):
        links = re.findall(r'<a href="#(s\d+)"><b>(\d+)</b>(.*?)</a>', self.body)
        ids = set(re.findall(r'id="(s\d+)"', self.body))
        if not links:
            self.bad("目录导航", "未找到目录，长报告缺目录只能一路下滑")
            return
        broken = [l[0] for l in links if l[0] not in ids]
        if broken:
            self.bad("目录锚点", f"失效链接：{broken}")
        else:
            self.ok("目录锚点", f"{len(links)} 项全部可跳转")

        # 目录文字须与章节标题一致
        sec_map = {}
        for n, t in re.findall(
            r'<span class="no">(\d+)</span><span class="ttl">(.*?)</span>', self.body
        ):
            sec_map[f"s{n}"] = t
        d = re.search(
            r'<div class="dh"><span class="no">(\d+)</span><span>(.*?)</span>', self.body
        )
        if d:
            sec_map[f"s{d.group(1)}"] = d.group(2)
        mismatch = [
            (l[0], l[2], sec_map.get(l[0]))
            for l in links
            if l[0] in sec_map and sec_map[l[0]] != l[2]
        ]
        if mismatch:
            self.bad("目录文字", f"与章节标题不一致：{mismatch}")
        else:
            self.ok("目录文字", "与章节标题一致")

    def check_no_emoji(self):
        emo = [
            c for c in self.body
            if 0x1F300 <= ord(c) <= 0x1FAFF
            or 0x2600 <= ord(c) <= 0x27BF
            or ord(c) == 0xFE0F
        ]
        if emo:
            self.bad("无 emoji", f"发现：{sorted(set(emo))}")
        else:
            self.ok("无 emoji")

    def check_bad_titles(self):
        # 只在标题元素内检测 —— 正文里出现「把几项异常放在一起看」是正常表述，
        # 不能因为字面包含旧标题词就误判
        titles = re.findall(
            r'<span class="ttl">(.*?)</span>'
            r'|<h3 class="sub[^"]*">(.*?)</h3>'
            r'|<h4 class="sub2">(.*?)</h4>',
            self.body, re.S,
        )
        flat = " ".join(t for grp in titles for t in grp if t)
        flat = re.sub(r"<.*?>", "", flat)
        found = [w for w in BAD_TITLES if w in flat]
        if found:
            self.bad("标题调性", f"标题中发现已废弃的口语化/内部术语：{found}")
        else:
            self.ok("标题调性", f"已检查 {len(titles)} 个标题")

    def check_no_level_codes(self):
        found = re.findall(LEVEL_CODES, self.body)
        if found:
            self.bad("档位代号", f"向用户暴露了 L1~L4 内部代号：{sorted(set(found))}")
        else:
            self.ok("档位代号", "未暴露 L1~L4")

    def check_sub_numbering(self):
        n2 = len(re.findall(r'class="n2"', self.body))
        n3 = len(re.findall(r'class="n3"', self.body))
        h3 = len(re.findall(r'<h3 class="sub', self.body))
        h4 = len(re.findall(r'<h4 class="sub2"', self.body))
        if h3 and n2 != h3:
            self.bad("二级标题序号", f"{h3} 个二级标题但只有 {n2} 个序号")
        elif h4 and n3 != h4:
            self.bad("三级标题序号", f"{h4} 个三级标题但只有 {n3} 个序号")
        else:
            self.ok("标题序号", f"二级 {n2} 个、三级 {n3} 个，全部带序号")

    def check_table_columns(self):
        bad = []
        # <table 可能带属性，不能只匹配 <table>
        for i, t in enumerate(
            re.findall(r"<table[^>]*>.*?</table>", self.body, re.S), 1
        ):
            cols = [
                len(re.findall(r"<t[hd]", r))
                for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)
            ]
            if len(set(cols)) > 1:
                bad.append((i, cols))
        if bad:
            self.bad("表格列数一致性",
                     f"{len(bad)} 个表格列数不齐（会导致渲染错位）：{bad[:3]}")
        else:
            n = len(re.findall(r"<table[^>]*>", self.body))
            self.ok("表格列数一致性", f"{n} 个表格全部一致")

    def check_note_budget(self):
        n = len(re.findall(r'<div class="note"', self.body))
        if n > 5:
            self.bad("色块预算", f"{n} 处底色块，超出 ≤5 的限制，会让重点失效")
        else:
            self.ok("色块预算", f"{n} 处（限 ≤5）")

    def check_guidelines_section(self):
        m = re.search(r'id="s10".*?(?=id="s11")', self.body, re.S)
        if not m:
            self.bad("参考指南段", "未找到第 10 段")
            return
        blk = m.group()
        rows = len(re.findall(r"<tr[^>]*>", blk))
        if rows < 4:
            self.bad("参考指南段", f"内容过少（仅 {rows} 行），应含指南表与数值出处表")
        elif rows > 60:
            self.bad("参考指南段",
                     f"{rows} 行，疑似照搬 guidelines.md 全表 —— "
                     "只应列本次实际用到的指南")
        else:
            self.ok("参考指南段", f"{rows} 行，规模合理")

    def check_print_style(self):
        missing = []
        if "print-color-adjust" not in self.raw:
            missing.append("print-color-adjust（打印会丢失风险色块）")
        if "break-inside" not in self.raw:
            missing.append("break-inside（卡片可能被分页截断）")
        if missing:
            self.bad("打印样式", "缺少：" + "；".join(missing))
        else:
            self.ok("打印样式")

    def check_mobile(self):
        if "max-width:640px" in self.raw or "max-width: 640px" in self.raw:
            self.ok("移动端适配")
        else:
            self.bad("移动端适配", "缺少窄屏断点")

    def run(self):
        for fn in [
            self.check_no_external, self.check_no_script, self.check_inline_svg,
            self.check_color_scheme, self.check_table_wrap,
            self.check_no_dev_traces, self.check_no_privacy,
            self.check_sections, self.check_toc, self.check_no_emoji,
            self.check_bad_titles, self.check_no_level_codes,
            self.check_sub_numbering, self.check_table_columns,
            self.check_note_budget, self.check_guidelines_section,
            self.check_print_style, self.check_mobile,
        ]:
            try:
                fn()
            except Exception as e:
                self.bad(fn.__name__, f"校验器异常：{e}")

        size = os.path.getsize(self.path) / 1024
        print(f"校验对象：{self.path}（{size:.1f} KB）\n")

        if not self.quiet:
            for name, detail in self.passed:
                print(f"  通过  {name}" + (f" —— {detail}" if detail else ""))
            if self.passed and self.failed:
                print()

        for name, detail in self.failed:
            print(f"  失败  {name} —— {detail}")

        print(f"\n合计 {len(self.passed)} 项通过，{len(self.failed)} 项失败")
        return 0 if not self.failed else 1


def main():
    ap = argparse.ArgumentParser(description="报告合规校验")
    ap.add_argument("report", help="HTML 报告路径")
    ap.add_argument("--quiet", action="store_true", help="只输出失败项")
    args = ap.parse_args()

    if not os.path.exists(args.report):
        print(f"错误：文件不存在 {args.report}", file=sys.stderr)
        sys.exit(2)

    sys.exit(Checker(args.report, args.quiet).run())


if __name__ == "__main__":
    main()
