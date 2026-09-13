#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selfcheck.py — neuroresearch 一致性 + 引擎自检脚本
==========================================================

用途：每次改动技能后跑一遍，自动抓「版本号漂移」「文档与磁盘不同步」「引用集合
不一致」等元数据问题，并对绘图引擎做冒烟回归，替代人工逐项对账。

运行方式（二选一）：
  1) 直接跑（一致性检查永远可用；引擎测试在依赖齐全时自动跑）：
        python scripts/selfcheck.py
  2) 推荐（完整自检，含引擎回归）：
        PY=$(python scripts/ensure_env.py) && $PY scripts/selfcheck.py

两部分：
  A. 一致性检查 —— 纯 Python 标准库，零第三方依赖，任何环境可跑。
  B. 引擎冒烟测试 —— 需要 numpy / matplotlib / scipy；缺失则 SKIP（不判失败）。

退出码：0 = 全绿；1 = 存在 FAIL（A 类失败必须修；B 类只出现 PASS / SKIP）。

约定：本脚本本身不装任何包（保持秒退、只读），依赖缺失时提示用 ensure_env.py。
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:  # Windows 控制台 / 管道下强制 UTF-8，避免中文输出 UnicodeEncodeError
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR = os.path.join(SKILL_DIR, "references")
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")

_npass = _nfail = _nskip = _nwarn = 0


def check(label, ok, detail=""):
    """记录一条 PASS/FAIL 并打印。"""
    global _npass, _nfail
    if ok:
        _npass += 1
        print(f"  [PASS] {label}")
    else:
        _nfail += 1
        print(f"  [FAIL] {label}  {detail}")


def skip(label, detail=""):
    """记录一条 SKIP（依赖缺失等，不判失败）。"""
    global _nskip
    _nskip += 1
    print(f"  [SKIP] {label}  {detail}")


def warn(label, detail=""):
    """记录一条 WARN（非阻断：提示性漂移，不判失败、不阻止提交）。"""
    global _nwarn
    _nwarn += 1
    print(f"  [WARN] {label}  {detail}")


def _read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def _skill_version():
    m = re.search(r"^version:\s*([0-9]+\.[0-9]+\.[0-9]+)",
                  _read(os.path.join(SKILL_DIR, "SKILL.md")), re.M)
    return m.group(1) if m else None


def _changelog_versions():
    return re.findall(r"^##\s+v?([0-9]+\.[0-9]+\.[0-9]+)",
                      _read(os.path.join(SKILL_DIR, "CHANGELOG.md")), re.M)


def _refs_in(path):
    """提取某文档中所有带前缀的 references/<name>.md 引用（导航表/速查表）。"""
    return set(re.findall(r"references/([a-z0-9\-]+\.md)", _read(path)))


def _tree_refs_in(path):
    """提取目录树形式（`├── xxx.md` / `└── xxx.md`）列出的 references 条目。"""
    return set(re.findall(r"[├└]──\s*([a-z0-9\-]+\.md)", _read(path)))


def _ver_tuple(v):
    return tuple(int(x) for x in v.split("."))


# ---------------------------------------------------------------------------
# 辅助：从 prism_theme.py 提取 __all__ 名称集合（纯正则，无需 import / 依赖）
# ---------------------------------------------------------------------------
def _all_names():
    src = _read(os.path.join(SCRIPTS_DIR, "prism_theme.py"))
    m = re.search(r"__all__\s*=\s*\[(.*?)\]", src, re.S)
    if not m:
        return set(), src
    names = set(re.findall(r'"(\w+)"', m.group(1)))
    return names, src


# ---------------------------------------------------------------------------
# 辅助：提取某 markdown 中所有标题行首的「小节编号标记」
#   例：## 四-B、常见检验 → "四-B"；### 4.B.1 → "4.B.1"；## 五、→ "五"；
#        ## Phase 0：识别 → "Phase 0"；### §1 摘要 → "§1"
#   用于 P1-3 跨文件 §N 引用可达性校验。
# ---------------------------------------------------------------------------
def _heading_tokens(src):
    # 中文数字 ↔ 阿拉伯数字互转，避免「## 四、」与跨文件引用「§4」因写法不同而误报
    cn2ar = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
             '六': '6', '七': '7', '八': '8', '九': '9'}
    toks = set()
    for line in src.splitlines():
        m = re.match(r"^#{2,3}\s+(.*)$", line)
        if not m:
            continue
        head = m.group(1).strip()
        # 取标题开头到第一个空白 / 、/ ：/ ． 之前的部分作为小节号
        m2 = re.match(r"^(?:§\s*)?([0-9]+(?:\.[0-9A-Z]+)*|[一二三四五六七八九十]+(?:-[A-Za-z0-9]+)?|Phase\s*[0-9]+|[A-Za-z]+[-\s]*[0-9]+)", head)
        if m2:
            tok = m2.group(1).strip()
            toks.add(tok)
            if tok and tok[0] in cn2ar:          # 「四」→「4」、「四-B」→「4-B」
                toks.add(cn2ar[tok[0]] + tok[1:])
        # 也保留中文数字「X、」形式（同步加阿拉伯形式）
        m3 = re.match(r"^([一二三四五六七八九十]+)[、。]", head)
        if m3:
            c = m3.group(1)
            toks.add(c)
            if c in cn2ar:
                toks.add(cn2ar[c])
    return toks


# ---------------------------------------------------------------------------
# P1-3：跨文件 `xxx.md §N` 引用可达性校验（WARN 不阻断）
#   仅校验「带文件前缀」的跨文件引用（如 `experiment-report.md §8.1`）；
#   同文件裸引用（如 `见 §二`）不在本检查范围。
#   目标文件存在但 §N 未在标题中出现 → WARN（提示小节已重排/失效）。
# ---------------------------------------------------------------------------
def _check_section_anchors():
    print("\n== A+. 跨文件 §N 引用可达性（WARN） ==")
    # 目标文件集合
    ref_files = {f[:-3]: _read(os.path.join(REF_DIR, f))
                 for f in os.listdir(REF_DIR) if f.endswith(".md")}
    heading_cache = {name: _heading_tokens(src) for name, src in ref_files.items()}

    # 收集所有 `references/xxx.md §N` 或 `xxx.md §N` 引用
    pat = re.compile(r"`?([a-z0-9\-]+)\.md`?\s*§\s*([0-9A-Za-z一-鿿]+(?:[\.\-][0-9A-Za-z]+)*)")
    seen = set()
    for name, src in ref_files.items():
        for m in pat.finditer(src):
            tgt, sec = m.group(1), m.group(2)
            key = (tgt, sec, name)
            if key in seen:
                continue
            seen.add(key)
            if tgt not in ref_files:
                warn(f"{name} → {tgt}.md §{sec}", "目标文件不存在")
                continue
            toks = heading_cache[tgt]
            if sec not in toks:
                warn(f"{name} → {tgt}.md §{sec}", "目标文件未找到对应标题（可能已重排）")


# ---------------------------------------------------------------------------
# P1-4：绘图核心规则「单一权威源」校验
#   规则（p 值铁律 / 0.75pt 线宽 / 0.26 顶部留白 / 均衡抖动）的权威定义位于
#   `prism-style-plot.md`；其余文件（statistical-analysis / plotting-protocol /
#   scatter-layout）应仅作引用，不重复定义。校验：① 权威源标记存在；
#   ② 三个引用文件均含指向权威源的指针短语。
# ---------------------------------------------------------------------------
def _check_authoritative_source():
    print("\n== A++. 绘图规则单一权威源 ==")
    auth = _read(os.path.join(REF_DIR, "prism-style-plot.md"))
    check("prism-style-plot.md 含「核心规则权威源」标记",
          "核心规则（权威源）" in auth or "权威源" in auth)
    marker = "prism-style-plot.md"
    for f in ("statistical-analysis.md", "plotting-protocol.md",
              "scatter-layout.md"):
        src = _read(os.path.join(REF_DIR, f))
        check(f"{f} 含指向权威源的指针",
              marker in src and ("权威" in src or "见 `prism-style-plot.md`" in src
                                 or "见prism-style-plot.md" in src or "prism-style-plot.md §" in src))


# ---------------------------------------------------------------------------
# A. 一致性检查（纯标准库）
# ---------------------------------------------------------------------------
def check_consistency():
    print("\n== A. 一致性检查 ==")

    # 1) SKILL.md version == CHANGELOG 最新版本（最易漂移的一处）
    skill_ver = _skill_version()
    changelog_vers = _changelog_versions()
    check("SKILL.md 有 version 字段", skill_ver is not None)
    check("CHANGELOG 能解析出版本号", bool(changelog_vers))
    if skill_ver and changelog_vers:
        check(f"SKILL.md version({skill_ver}) == CHANGELOG 最新({changelog_vers[0]})",
              skill_ver == changelog_vers[0],
              f"漂移：SKILL.md={skill_ver}, CHANGELOG={changelog_vers[0]}")

    # 2) CHANGELOG 版本号严格倒序（最新在最上）
    if len(changelog_vers) >= 2:
        ordered = all(_ver_tuple(a) > _ver_tuple(b)
                      for a, b in zip(changelog_vers, changelog_vers[1:]))
        check("CHANGELOG 版本号严格倒序", ordered,
              f"顺序异常：{changelog_vers[:5]}")

    # 3) 磁盘 references vs 文档引用
    on_disk = set(f for f in os.listdir(REF_DIR) if f.endswith(".md"))
    skill_refs = _refs_in(os.path.join(SKILL_DIR, "SKILL.md"))
    doc_refs = _refs_in(os.path.join(SKILL_DIR, "使用文档.md"))
    check("SKILL.md 导航表引用的 references 全部存在",
          skill_refs.issubset(on_disk), f"缺失 {skill_refs - on_disk}")
    check("使用文档.md 引用的 references 全部存在",
          doc_refs.issubset(on_disk), f"缺失 {doc_refs - on_disk}")

    # 4) 两文档引用的 reference 集合一致（无此有彼遗漏）
    check("SKILL.md 与 使用文档.md 引用集合一致", skill_refs == doc_refs,
          f"差异 {skill_refs ^ doc_refs}")

    # 5) 无孤儿 reference（磁盘有、但没被任何文档引用）
    orphans = on_disk - (skill_refs | doc_refs)
    check("无孤儿 reference 文件", not orphans, f"未被引用 {orphans}")

    # 5.5) 使用文档「文件结构图」列出的 references 完整（目录树形式单独校验，
    #      避免结构图漏列而速查表/导航表却完整时成为盲区）
    doc_tree_refs = _tree_refs_in(os.path.join(SKILL_DIR, "使用文档.md"))
    check("使用文档文件结构图列出的 references 完整",
          doc_tree_refs == on_disk, f"差异 {doc_tree_refs ^ on_disk}")

    # 6) 使用文档「N 个模块」数字 == 磁盘 references 数量
    m = re.search(r"(\d+)\s*个模块", _read(os.path.join(SKILL_DIR, "使用文档.md")))
    if m:
        declared = int(m.group(1))
        check(f"使用文档声明模块数({declared}) == 磁盘 references 数({len(on_disk)})",
              declared == len(on_disk),
              f"漂移：文档写 {declared}，磁盘 {len(on_disk)} 个")

    # 7) scripts：文档引用的脚本存在 + 无孤儿脚本
    #     两种形式都要识别：带前缀 `scripts/xxx.py`（正文/description 里），
    #     以及目录树形式 `├── xxx.py`（使用文档文件结构图里）。
    on_disk_scripts = set(f for f in os.listdir(SCRIPTS_DIR)
                          if f.endswith((".py", ".R")))
    doc_text = (_read(os.path.join(SKILL_DIR, "使用文档.md"))
                + "\n" + _read(os.path.join(SKILL_DIR, "SKILL.md")))
    doc_scripts = set(re.findall(r"scripts/([a-z0-9_\-]+\.(?:py|R))", doc_text))
    doc_scripts |= set(re.findall(r"[├└]──\s*([a-z0-9_\-]+\.(?:py|R))", doc_text))
    check("文档引用的 scripts 全部存在", doc_scripts.issubset(on_disk_scripts),
          f"缺失 {doc_scripts - on_disk_scripts}")
    check("无孤儿脚本（磁盘脚本均被文档引用）",
          on_disk_scripts.issubset(doc_scripts),
          f"未被引用 {on_disk_scripts - doc_scripts}")

    # 8) 所有 references 引用的 scripts/xxx 均存在（防 build_pathway 类断链：
    #    文档正文/衔接表里写了 scripts/xxx 但磁盘没有）
    ref_scripts = set()
    for f in on_disk:
        ref_scripts |= set(re.findall(r"scripts/([a-z0-9_\-]+\.(?:py|R))",
                                      _read(os.path.join(REF_DIR, f))))
    check("references 引用的 scripts 全部存在",
          ref_scripts.issubset(on_disk_scripts),
          f"缺失 {ref_scripts - on_disk_scripts}")

    # 9) prism-style-plot.md API 速查表函数名 vs prism_theme.py 实际 def
    #    （内容级防漂移：文档声称的 API 实现缺失会立即报 FAIL）
    theme_src = _read(os.path.join(SCRIPTS_DIR, "prism_theme.py"))
    real_funcs = set(re.findall(r"^def (\w+)\(", theme_src, re.M))
    api_md = _read(os.path.join(REF_DIR, "prism-style-plot.md"))
    doc_funcs = set(re.findall(r"`(prism_\w+)\(", api_md))
    missing = doc_funcs - real_funcs
    check("prism-style-plot.md API 表函数均存在于 prism_theme.py",
          not missing, f"文档声称但实现缺失 {missing}")

    # 10) P1-5：文档声明的「公开 API 数量」与 __all__ 实际数量双向校验
    all_names, _ = _all_names()
    declared = set()
    for doc in ("SKILL.md", "使用文档.md", "references/prism-style-plot.md"):
        doc_src = _read(os.path.join(SKILL_DIR, doc)) if doc in ("SKILL.md", "使用文档.md") \
            else _read(os.path.join(REF_DIR, "prism-style-plot.md"))
        for m in re.finditer(r"公开\s*API\s*(\d+)\s*项|(\d+)\s*项\s*公开\s*API|(\d+)\s*个\s*公开\s*API", doc_src):
            declared.add(int(m.group(1) or m.group(2) or m.group(3)))
    if declared:
        check(f"文档声明公开 API 数({sorted(declared)}) == __all__ 实际数({len(all_names)})",
              len(all_names) in declared and all(d == len(all_names) for d in declared),
              f"漂移：文档 {sorted(declared)}，实际 {len(all_names)}")
    else:
        skip("文档公开 API 数声明校验", "未在文档中找到『公开 API N 项』表述")

    # 11) P2-10a：templates/*.py 导入名全部在 __all__ 中（静态解析，无需 import）
    tmpl_dir = os.path.join(SKILL_DIR, "templates")
    if os.path.isdir(tmpl_dir):
        bad_imports = {}
        for f in sorted(os.listdir(tmpl_dir)):
            if not f.endswith(".py"):
                continue
            t = _read(os.path.join(tmpl_dir, f))
            for chunk in re.findall(r"from\s+scripts\.prism_theme\s+import\s*\((.*?)\)", t, re.S):
                body = re.sub(r"#.*", "", chunk)          # 去行内注释
                for nm in re.findall(r"(\w+)", body):
                    if nm not in all_names:
                        bad_imports.setdefault(f, []).append(nm)
        check("templates/*.py 导入名均在 __all__ 中",
              not bad_imports, f"越界导入 {bad_imports}")

    # 12) P2-10b：references/recipes/*.md 调用的 prism_* 函数均在 __all__ 中
    rec_dir = os.path.join(REF_DIR, "recipes")
    if os.path.isdir(rec_dir):
        bad_calls = {}
        for f in sorted(os.listdir(rec_dir)):
            if not f.endswith(".md"):
                continue
            t = _read(os.path.join(rec_dir, f))
            for fn in re.findall(r"\b(prism_\w+)\(", t):
                if fn not in all_names:
                    bad_calls.setdefault(f, []).append(fn)
        check("recipes/*.md 调用的 prism_* 函数均在 __all__ 中",
              not bad_calls, f"越界调用 {bad_calls}")

    # 13) P1-3 / P1-4：跨文件 §N 引用可达性 + 绘图规则单一权威源（详见上方函数）
    _check_section_anchors()
    _check_authoritative_source()

    # 14) P2-4a：templates/*.py 不得含硬编码本机路径 / 指向外部技能（可移植性红线）
    #     历史问题：v2.4.x 曾 8 个模板全部硬编码 C:\Users\DELL\...\prism-style-plot，
    #     换机器即坏且破坏自包含承诺；本检查防止回归。
    if os.path.isdir(tmpl_dir):
        bad_tmpl = {}
        for f in sorted(os.listdir(tmpl_dir)):
            if not f.endswith(".py"):
                continue
            t = _read(os.path.join(tmpl_dir, f))
            if re.search(r"C:\\Users\\", t) or re.search(r"C:/Users/", t):
                bad_tmpl.setdefault(f, []).append("含 C:\\Users\\ 硬编码路径")
            if "skills\\prism-style-plot" in t or "skills/prism-style-plot" in t:
                bad_tmpl.setdefault(f, []).append("引用外部 prism-style-plot 技能路径")
        check("templates/*.py 无硬编码路径/外部技能引用",
              not bad_tmpl, f"违规 {bad_tmpl}")

    # 15) P2-4b：references/ 与 verify/README.md 中引用的 verify*.py 均须存在于磁盘
    #     历史问题：recipes 曾引用 verify4_grouped_bar.py / verify8_multivar.py 等
    #     不存在的文件；README 表格停留在早期 6 个脚本。
    verify_dir = os.path.join(SCRIPTS_DIR, "verify")
    disk_verify = set()
    if os.path.isdir(verify_dir):
        disk_verify = set(f for f in os.listdir(verify_dir)
                          if re.match(r"verify.*\.py$", f))
    ref_verify = set()
    for f in on_disk:
        ref_verify |= set(re.findall(r"\b(verify\d+[a-z0-9_]*\.py)",
                                     _read(os.path.join(REF_DIR, f))))
    readme_p = os.path.join(verify_dir, "README.md")
    if os.path.isfile(readme_p):
        ref_verify |= set(re.findall(r"\b(verify\d+[a-z0-9_]*\.py)", _read(readme_p)))
    missing_verify = ref_verify - disk_verify
    check("references / verify-README 引用的 verify*.py 均存在",
          not missing_verify, f"断链 {missing_verify}")

    # 16) P2-4c：prism-style-plot.md「最新同步至 vX.Y.Z」== prism_theme.py UPSTREAM_VERSION
    #     历史问题：标题曾写 v2.6.x 而引擎已同步 v2.7.4，自检未抓到。
    theme_up = re.search(r"UPSTREAM_VERSION\s*=\s*[\"']v?([^\"']+)[\"']", theme_src)
    m_sync = re.search(r"最新同步至\s*v?([0-9.]+)", api_md)
    if theme_up and m_sync:
        check("prism-style-plot.md「最新同步至」== UPSTREAM_VERSION",
              theme_up.group(1).lstrip("v") == m_sync.group(1),
              f"漂移：文档写 v{m_sync.group(1)}，引擎 {theme_up.group(1)}")
    else:
        skip("prism-style-plot.md 版本号一致性",
             "未找到「最新同步至 vX.Y.Z」或 UPSTREAM_VERSION 标记")


# ---------------------------------------------------------------------------
# B. 引擎冒烟测试（需 numpy/matplotlib/scipy）
# ---------------------------------------------------------------------------
def check_engine():
    print("\n== B. 引擎冒烟测试 ==")
    deps = ["numpy", "matplotlib", "scipy"]
    missing = [d for d in deps if importlib.util.find_spec(d) is None]
    if missing:
        skip("引擎测试", f"缺依赖 {missing}，用 ensure_env.py 引导后重跑")
        return

    import matplotlib
    matplotlib.use("Agg")  # 无显示环境必须
    import matplotlib.pyplot as plt
    import numpy as np

    sys.path.insert(0, SCRIPTS_DIR)  # 命中 bundled 引擎
    import prism_theme as P

    # ---- 纯函数（p 值/统计格式铁律）----
    stars = [P.p_to_stars(p)[0]
             for p in (0.9, 0.04, 0.009, 0.0009, 0.00009)]
    check("p_to_stars 五档分级正确", stars == ["ns", "*", "**", "***", "****"],
          f"实际 {stars}")
    check("p_to_stars 非有限值返回空串", P.p_to_stars(np.nan) == ("", False))
    check("format_p 精确值（≥0.001 三位小数）",
          P.format_p(0.134) == "p=0.134" and P.format_p(0.5) == "p=0.500",
          f"实际 {P.format_p(0.134)}, {P.format_p(0.5)}")
    check("format_p 下溢与 NaN",
          P.format_p(0.0) == "p=<1e-300" and P.format_p(np.nan) == "NA",
          f"实际 {P.format_p(0.0)}, {P.format_p(np.nan)}")
    check("mean_sem 均值正确", P.mean_sem([1.0, 2.0, 3.0, 4.0])[0] == 2.5)
    check("mean_sem 空数组返回 (nan, nan)", all(np.isnan(P.mean_sem([]))))
    check("mean_sd 使用 ddof=1",
          abs(P.mean_sd([1.0, 2.0, 3.0, 4.0])[1] - 1.2909944487358056) < 1e-12)

    # ---- 统计封装 ----
    rng = np.random.default_rng(42)
    g1 = rng.normal(5.0, 1.0, 10)
    g2 = rng.normal(6.8, 1.2, 10)
    g3 = rng.normal(8.5, 1.4, 10)
    res = P.oneway_anova_tukey([g1, g2, g3], ["A", "B", "C"])
    check("oneway_anova_tukey 结构完整",
          set(res) >= {"method", "anova_p", "pairwise"}
          and len(res["pairwise"]) == 3)
    t = P.ttest_two_groups(g1, g2)
    check("ttest_two_groups 返回 (stat, p, 方法名)",
          len(t) == 3 and isinstance(t[1], float))

    # ---- 5 类图端到端（保存到临时目录，跑完即删，不污染技能目录）----
    P.apply_prism_theme()
    tmp = tempfile.mkdtemp(prefix="prism_selfcheck_")

    def _smoke(name, fn):
        try:
            fig, ax = plt.subplots(figsize=P.get_figsize("tall"))
            fn(ax)
            out = P.save_figure(fig, name, out_dir=tmp)  # 默认 PNG+PDF
            check(f"端到端出图：{name}", len(out) == 2)
        except Exception as e:  # noqa: BLE001 —— 冒烟测试要捕获一切异常并报 FAIL
            check(f"端到端出图：{name}", False, repr(e))

    _smoke("box", lambda ax: (
        P.prism_boxplot(ax, [g1, g2, g3], ["A", "B", "C"]),
        P.add_pairwise_brackets(ax, res["pairwise"], labels=["A", "B", "C"])))
    _smoke("bars", lambda ax: P.prism_bars(ax, [g1, g2, g3], ["A", "B", "C"],
                                           error_type="sem"))
    _smoke("violin", lambda ax: P.prism_violin(ax, [g1, g2, g3], ["A", "B", "C"]))

    def _km(n, med, seed):
        r = np.random.default_rng(seed)
        return r.exponential(med, n), (r.uniform(0, 1, n) > 0.1).astype(int)

    t1, e1 = _km(40, 6, 1)
    t2, e2 = _km(40, 9, 2)
    t3, e3 = _km(40, 18, 3)

    def _surv(ax):
        return P.prism_survival(
            ax,
            np.concatenate([t1, t2, t3]),
            np.concatenate([e1, e2, e3]),
            np.repeat(["A", "B", "C"], 40))

    _smoke("survival", _surv)

    x = np.array([0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000.])
    y = 10 + 90 / (1 + 10 ** ((np.log10(30) - np.log10(x)) * 1.0))
    _smoke("xy_fit", lambda ax: P.prism_xy_fit(ax, x, y, model="4pl"))

    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# C. 引擎双源同步校验（vendored ↔ 外部 prism-style-plot 技能，WARN 不阻断）
#   本技能的 scripts/prism_theme.py 是从独立 prism-style-plot 技能同步的拷贝。
#   若该技能在本环境存在，比对两者 __all__ 数量与 UPSTREAM_VERSION，
#   不一致则 WARN「需重新同步」，不阻断提交（避免误报阻断）。
# ---------------------------------------------------------------------------
def check_external_sync():
    print("\n== C. 引擎双源同步（vendored ↔ prism-style-plot，WARN） ==")
    local_src = _read(os.path.join(SCRIPTS_DIR, "prism_theme.py"))
    m = re.search(r"UPSTREAM_VERSION\s*=\s*[\"']([^\"']+)[\"']", local_src)
    local_ver = m.group(1) if m else None
    local_n = len(_all_names()[0])

    ext = os.path.expanduser("~/.workbuddy/skills/prism-style-plot/scripts/prism_theme.py")
    if not os.path.isfile(ext):
        skip("双源同步比对", "本环境未安装独立 prism-style-plot 技能，跳过")
        return
    ext_src = _read(ext)
    me = re.search(r"UPSTREAM_VERSION\s*=\s*[\"']([^\"']+)[\"']", ext_src)
    ext_ver = me.group(1) if me else None
    em = re.search(r"__all__\s*=\s*\[(.*?)\]", ext_src, re.S)
    ext_n = len(set(re.findall(r'"(\w+)"', em.group(1)))) if em else None
    if local_n != ext_n:
        warn(f"vendored __all__({local_n}) ≠ prism-style-plot __all__({ext_n})",
             "需重新从 prism-style-plot 同步")
    elif local_ver and ext_ver and local_ver != ext_ver:
        warn(f"UPSTREAM_VERSION 不一致（vendored={local_ver}, prism-style-plot={ext_ver}）",
             "版本标记需对齐")
    else:
        # 数量与版本标记一致时，再比对内容哈希——防「数量巧合一致但内容已漂移」漏报。
        # 比对前排除：① 整行 # 注释（本技能与上游刻意保持"仅注释差异"）；
        # ② UPSTREAM_VERSION / UPSTREAM_SYNCED 两行本技能特有标记（上游无）。
        import hashlib

        def _code_hash(s):
            body = re.sub(r"(?m)^\s*#.*$", "", s)
            body = re.sub(r"(?m)^\s*UPSTREAM_(VERSION|SYNCED)\s*=.*$", "", body)
            body = re.sub(r"\s+", "", body)
            return hashlib.sha256(body.encode("utf-8")).hexdigest()

        h_local, h_ext = _code_hash(local_src), _code_hash(ext_src)
        if h_local != h_ext:
            warn("vendored 与 prism-style-plot 内容不一致（API 数量/版本标记巧合一致）",
                 "建议核对差异后重新同步")
        else:
            print(f"  [PASS] vendored({local_n}, {local_ver}) ↔ prism-style-plot({ext_n}, {ext_ver}) 内容一致")


# ---------------------------------------------------------------------------
# D. R 脚本端到端自检（缺 R / 缺 Bioconductor 包则 SKIP，与引擎测试同策略）
#   用 bioinfo_rna_seq.R 内置 demo=TRUE 合成数据跑通全流程，验证生信交付物不因
#   R / 包环境变动而静默失效。
# ---------------------------------------------------------------------------
def check_r_script():
    print("\n== D. R 脚本端到端（bioinfo_rna_seq.R demo） ==")
    rs = shutil.which("Rscript") or shutil.which("R")
    if not rs:
        skip("R 脚本自检", "未检测到 Rscript/R，跳过（不影响 Python 路径）")
        return
    rfile = os.path.join(SCRIPTS_DIR, "bioinfo_rna_seq.R")
    if not os.path.isfile(rfile):
        skip("R 脚本自检", "scripts/bioinfo_rna_seq.R 不存在")
        return
    tmp = tempfile.mkdtemp(prefix="neuro_r_selfcheck_")
    try:
        r = subprocess.run([rs, rfile], cwd=tmp, capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            check("bioinfo_rna_seq.R demo 端到端跑通", True)
        elif ("there is no package called" in r.stderr
              or "依赖缺失" in (r.stderr + r.stdout)
              or "已中止" in (r.stderr + r.stdout)):
            skip("R 脚本自检", "缺 Bioconductor 包（DESeq2 / org.Hs.eg.db 等），装齐后重跑")
        else:
            check("bioinfo_rna_seq.R demo 端到端跑通", False, r.stderr[-500:])
    except subprocess.TimeoutExpired:
        check("bioinfo_rna_seq.R demo 端到端跑通", False, "超时（>300s）")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    print(f"neuroresearch 自检 @ {SKILL_DIR}")
    check_consistency()
    check_engine()
    check_external_sync()
    check_r_script()
    print("\n" + "=" * 56)
    print(f"结果：PASS {_npass} | FAIL {_nfail} | SKIP {_nskip} | WARN {_nwarn}")
    if _nfail:
        print("存在 FAIL，请先修复（版本 / 文档漂移）再提交。")
    elif _nwarn:
        print("无 FAIL；有 WARN（提示性漂移，不阻断，建议择机处理）。")
    else:
        print("自检通过。")
    return 1 if _nfail else 0


if __name__ == "__main__":
    sys.exit(main())
