#!/usr/bin/env python3
"""
generate_mindmap.py — Mind Map Generator v6 (v1.1.0)
Layout : Balanced left-right tree (XMind style)
         - branches split evenly left / right
         - each side laid out as a vertical tree
         - elbow connectors (horizontal → vertical)
         - smooth Bezier from root to first-level branches
Features:
  - Click −/+ badge to collapse / expand; double-click node to edit label
  - Enter = add sibling, Tab = add child, F2 = edit; drag root node = pan whole map
  - Drag a node onto another node to re-parent it (detach + attach as child)
  - Drag a node to empty space to reorder it among siblings; the map always
    re-flows to a clean layout on drop (dragging never leaves the map messy)
  - Labels over 20 characters are ellipsized (…); double-click a node to view/edit the full text
  - Save HTML: bind the file once (File System Access API) → every edit auto-saves;
    falls back to download on browsers without the API
  - Pan, zoom toward cursor, reset view
  - In-browser export: HTML (edited) / SVG / PNG / JPG / PDF / XMind
  - Python-side export: --format html|svg|png|jpg|pdf|xmind

Usage:
    python3 generate_mindmap.py --title "Topic" --output /tmp/map.html \\
        --data '{"central":"...","branches":[...]}' [--format html]
"""

import argparse, json, math, re, sys, zipfile, io, uuid, os, platform, subprocess
from datetime import datetime
from pathlib import Path


def _ensure_pillow(auto_install=True):
    """Import Pillow; optionally auto-install into the current environment.

    Safety: tries `pip install pillow`, then `pip install --user pillow`.
    Never uses --break-system-packages — on externally-managed Pythons
    (PEP 668) it prints instructions instead of forcing the install.
    Disable entirely with --no-auto-install.
    """
    try:
        from PIL import Image  # noqa: F401
        return True
    except ImportError:
        pass
    if not auto_install:
        print("[mindmap] Pillow is required for this format. Install it with:",
              file=sys.stderr)
        print("    pip install pillow", file=sys.stderr)
        return False
    for extra in ([], ["--user"]):
        cmd = [sys.executable, "-m", "pip", "install", "pillow",
               "--quiet", "--disable-pip-version-check"] + extra
        print(f"[mindmap] Pillow not found — running: {' '.join(cmd)}", file=sys.stderr)
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    try:
        from PIL import Image  # noqa: F401
        print("[mindmap] ✅ Pillow installed.", file=sys.stderr)
        return True
    except ImportError:
        print("[mindmap] ⚠ Auto-install did not succeed (possibly an "
              "externally-managed Python). Install manually, e.g.:", file=sys.stderr)
        print("    pip install pillow            # or inside a venv", file=sys.stderr)
        print("    pip install --user pillow", file=sys.stderr)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Cross-platform path helpers
# ─────────────────────────────────────────────────────────────────────────────
def _workspace_dir() -> Path:
    """Pick the default output directory, adapting to the environment.

    Priority:
      1. $MINDMAP_OUTPUT_DIR            (explicit override)
      2. /mnt/user-data/outputs         (claude.ai / Claude Desktop sandbox)
      3. ~/.openclaw/workspace          (OpenClaw, if ~/.openclaw exists)
      4. current working directory
    """
    env = os.environ.get("MINDMAP_OUTPUT_DIR")
    if env:
        p = Path(os.path.expandvars(os.path.expanduser(env)))
        p.mkdir(parents=True, exist_ok=True)
        return p
    sandbox = Path("/mnt/user-data/outputs")
    if sandbox.is_dir():
        return sandbox
    if (Path.home() / ".openclaw").is_dir():
        p = Path.home() / ".openclaw" / "workspace"
        p.mkdir(parents=True, exist_ok=True)
        return p
    return Path.cwd()


def resolve_output(raw_path: str, fmt: str) -> str:
    """Expand ~, $HOME, %USERPROFILE%, create parent dirs, fix extension.

    If the path is just a filename without directory (e.g. 'mindmap.png'),
    it is placed under ~/.openclaw/workspace/ instead of the current dir.
    """
    p = Path(os.path.expandvars(os.path.expanduser(raw_path)))
    ext_map = {"html":".html","svg":".svg","png":".png",
               "jpg":".jpg","pdf":".pdf","xmind":".xmind"}
    expected = ext_map.get(fmt, "")
    if expected and p.suffix.lower() != expected:
        p = p.with_suffix(expected)

    # If only a bare filename was given (no directory), use default workspace
    if p.parent == Path(".") or str(p.parent) == ".":
        p = _workspace_dir() / p.name

    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)


def default_output(fmt: str) -> str:
    """Return a sensible default output path for the current OS.

    Default: ~/.openclaw/workspace/  (cross-platform, auto-adapts to username)
      - Windows:  C:\\Users\\<username>\\.openclaw\\workspace\\
      - macOS:    /Users/<username>/.openclaw/workspace/
      - Linux:    /home/<username>/.openclaw/workspace/
    """
    ext_map = {"html":".html","svg":".svg","png":".png",
               "jpg":".jpg","pdf":".pdf","xmind":".xmind"}
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = ext_map.get(fmt, ".html")
    name = f"mindmap_{ts}{ext}"
    return str(_workspace_dir() / name)


DEFAULT_COLORS = [
    "#4A90D9","#E86C3A","#27AE60","#9B59B6",
    "#E74C3C","#F39C12","#1ABC9C","#E91E63",
    "#00BCD4","#8BC34A",
]

# ── Themes ────────────────────────────────────────────────────────────────
# "midnight" — 深空（深色，默认）; "paper" — 纸墨（浅色，适合打印/文档嵌入）
# Node text colors are indexed by depth: [root, branch, child, leaf].
THEMES = {
    "midnight": {
        "bg": "#0d0f1a",
        "bg_rgb": (13, 15, 26),
        "node_text": ["#ffffff", "#ffffff", "#e0e4f0", "#a8b0c8"],
    },
    "paper": {
        "bg": "#f7f5ef",
        "bg_rgb": (247, 245, 239),
        "node_text": ["#ffffff", "#26304a", "#39435e", "#5b6580"],
    },
}

# ── Visual config per depth ────────────────────────────────────────────────────
# depth 0 = central, 1 = branch, 2 = leaf, 3 = sub-leaf
CFG = [
    dict(h=48, fs=16, fw="bold",   rx=12, px=32, min_w=180, max_w=420),
    dict(h=38, fs=13, fw="bold",   rx= 8, px=24, min_w=110, max_w=340),
    dict(h=30, fs=12, fw="normal", rx= 6, px=18, min_w= 80, max_w=300),
    dict(h=26, fs=11, fw="normal", rx= 5, px=16, min_w= 72, max_w=280),
]

# Horizontal gap between node right-edge and children column
H_GAP  = [0, 64, 48, 40]
# Vertical gap between sibling nodes
V_GAP  = [0, 20, 12, 8]

FONT_STACK = "PingFang SC,Hiragino Sans GB,Microsoft YaHei,Segoe UI,Arial,sans-serif"


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="OpenClaw Mind Map Generator — cross-platform (macOS / Linux / Windows)"
    )
    p.add_argument("--title",   required=True,  help="Mind map title")
    p.add_argument("--output",  default=None,
                   help="Output file path (default: auto-detected workspace). "
                        "With multiple formats, the extension is swapped per format.")
    p.add_argument("--data",    default=None,
                   help="Inline mind-map data: JSON, or a Markdown outline "
                        "(auto-detected). Prefer --data-file for anything non-trivial.")
    p.add_argument("--data-file", default=None,
                   help="Read data (JSON or Markdown outline) from a file; "
                        "'-' reads from stdin. Avoids shell-quoting pitfalls.")
    p.add_argument("--format",  default="html",
                   help="Output format(s), comma-separated: html,svg,png,jpg,pdf,xmind "
                        "(default: html). E.g. --format html,png,xmind")
    p.add_argument("--theme",   default="midnight", choices=sorted(THEMES),
                   help="Color theme: midnight (dark, default) or paper (light). "
                        "HTML output includes an in-page theme toggle.")
    p.add_argument("--scale",   type=float, default=2.0,
                   help="Pixel density for PNG/JPG/PDF (default: 2.0)")
    p.add_argument("--quality", type=int,   default=92,
                   help="JPEG quality 1-100 (default: 92)")
    p.add_argument("--no-auto-install", action="store_true",
                   help="Never pip-install Pillow automatically; print instructions instead.")
    p.add_argument("--no-lint", action="store_true",
                   help="Skip the structure quality report.")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Tree helpers
# ─────────────────────────────────────────────────────────────────────────────
def normalize_node(node):
    if isinstance(node, str):
        return {"label": node, "children": []}
    if isinstance(node, dict):
        node.setdefault("children", [])
        node["children"] = [normalize_node(c) for c in node["children"]]
        return node
    return {"label": str(node), "children": []}


# ─────────────────────────────────────────────────────────────────────────────
# Markdown outline input
# ─────────────────────────────────────────────────────────────────────────────
def parse_markdown_outline(text, fallback_title=None):
    """Convert a Markdown outline into mind-map JSON.

    Supported syntax (both may be mixed):
        # 中心主题            ← level-1 heading = central node
        ## 分支               ← level-2 heading = main branch
        - 子节点              ← bullets nest by indentation (2 spaces or tab)
          - 叶节点
    A branch heading may carry a color:  ## 分支 [#4A90D9]
    If no level-1 heading exists, --title (fallback_title) becomes the central node.
    """
    items = []          # list of (depth, label)
    heading_depth = -1  # depth of last seen heading
    in_fence = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip():
            continue
        s = line.strip()
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            depth = len(m.group(1)) - 1
            items.append((depth, m.group(2).strip()))
            heading_depth = depth
            continue
        m = re.match(r"^([ \t]*)(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if m:
            indent = m.group(1).replace("\t", "  ")
            level = len(indent) // 2
            base = heading_depth + 1 if heading_depth >= 0 else 1
            items.append((base + level, m.group(2).strip()))
            continue
        # plain line: treat as a node one level under the last item
        items.append((items[-1][0] + 1 if items else 0, s))

    if not items:
        raise ValueError("Markdown outline is empty.")

    # Normalize so exactly one depth-0 central node exists
    if sum(1 for d, _ in items if d == 0) != 1 or items[0][0] != 0:
        central_label = fallback_title or items[0][1]
        items = [(0, central_label)] + [(d + 1, t) for d, t in items]

    def take_color(label):
        m = re.search(r"\s*\[(#[0-9a-fA-F]{6})\]\s*$", label)
        if m:
            return label[:m.start()].strip(), m.group(1)
        return label, None

    root = {"central": items[0][1], "branches": []}
    stack = [(0, root)]  # (depth, node)
    for depth, label in items[1:]:
        label, color = take_color(label)
        node = {"label": label, "children": []}
        if color:
            node["color"] = color
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if not stack:
            stack = [(0, root)]
        parent = stack[-1][1]
        key = "branches" if parent is root else "children"
        parent.setdefault(key, []).append(node)
        stack.append((depth, node))
    return root


def load_data(args):
    """Read data from --data / --data-file / stdin; auto-detect JSON vs Markdown."""
    if args.data_file:
        if args.data_file == "-":
            text = sys.stdin.read()
        else:
            fp = Path(os.path.expandvars(os.path.expanduser(args.data_file)))
            if not fp.is_file():
                raise ValueError(f"--data-file not found: {fp}")
            text = fp.read_text(encoding="utf-8")
    elif args.data is not None:
        text = args.data
    else:
        raise ValueError("Provide --data or --data-file (use '-' for stdin).")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON — {e}")
    return parse_markdown_outline(text, fallback_title=args.title)


# ─────────────────────────────────────────────────────────────────────────────
# Structure quality report (认知科学质检)
# ─────────────────────────────────────────────────────────────────────────────
def _visible_len(text):
    """Approximate label length in 字: CJK counts 1, Latin/digits 0.5;
    whitespace, emoji, variation selectors, and ZWJ are excluded."""
    n = 0.0
    for ch in text:
        cp = ord(ch)
        if ch.isspace() or cp >= 0x1F000 or cp in (0xFE0F, 0x200D, 0x20E3) \
           or 0x2600 <= cp <= 0x27BF:
            continue
        n += 1.0 if cp > 0x2E7F else 0.5
    return n


def lint_tree(tree):
    """Check the tree against the cognitive-science guidelines and report.

    Prints a one-line summary plus warnings to stderr. Non-blocking:
    the map is still generated — warnings tell the caller how to improve it.

    Covers: 米勒定律/认知负荷 (Miller/Sweller), 双重编码 (Paivio),
    渐进分化 (Ausubel progressive differentiation),
    完全穷尽 (MECE), 概念图关系识别 (Novak concept maps).
    """
    stats = {"total": 1, "max_depth": 0, "labels": []}
    warnings = []
    # 渐进分化：记录每个节点相对父节点的“概括度”是否递减（用可见长度做代理指标：
    # 越具体的标签通常越长；若子节点明显比父节点更短更宽泛，可能是概括度倒挂）
    reversed_pairs = []
    # 概念图关系词：出现这些词，说明该处的核心是“关系”而非“从属”，
    # 纯树形从属会丢失信息，建议用关系标签/连线颜色表达因果·对比·时序·条件
    RELATION_HINTS = {
        "因果": ["导致", "因为", "所以", "引发", "造成", "促使", "因此", "使得", "带来"],
        "对比": ["vs", "对比", "相比", "而非", "不同于", "区别", "优于", "劣于"],
        "时序": ["然后", "接着", "之后", "首先", "最后", "第一步", "第二步", "阶段"],
        "条件": ["如果", "只要", "除非", "当且仅当", "取决于", "前提"],
    }
    relation_found = {}

    def walk(node, depth, parent_len):
        stats["max_depth"] = max(stats["max_depth"], depth)
        label = node.get("label") or node.get("central", "")
        stats["labels"].append(label)
        vlen = _visible_len(label)
        # 概念图关系词检测
        low = label.lower()
        for rtype, words in RELATION_HINTS.items():
            if any(w in low for w in words):
                relation_found.setdefault(rtype, label)
        kids = node.get("branches", []) + node.get("children", [])
        stats["total"] += len(kids)
        if depth >= 1 and len(kids) == 1:
            warnings.append(f'分支 “{label}” 只有 1 个子节点 — 建议合并进父节点或补充第二条证据')
        # 渐进分化：子节点应当比父节点更具体（不应更宽泛）。用长度代理，留足容差（>4字）以降误报。
        if depth >= 2 and parent_len and vlen + 4 < parent_len and vlen <= 4:
            reversed_pairs.append(label)
        for k in kids:
            walk(k, depth + 1, vlen)

    walk(tree, 0, None)
    branches = tree.get("branches", [])
    nb = len(branches)

    # ── 容量与认知负荷（Miller / Sweller）───────────────────────────────
    if nb > 6:
        warnings.append(f"主分支 {nb} 个，超过米勒定律上限（3–6 个）— 建议合并同类维度")
    elif nb == 1:
        warnings.append("只有 1 个主分支 — 放射结构至少需要 2 个维度")
    if stats["total"] > 40:
        warnings.append(f"总节点 {stats['total']} 个（> 40）— 内在认知负荷偏高，"
                        "建议按内在关联度拆分为多张图，或合并叶节点")
    if stats["max_depth"] > 3:
        warnings.append(f"层级深度 {stats['max_depth'] + 1} 层（> 4）— 建议压平最深一层")

    # ── 双重编码（Paivio）──────────────────────────────────────────────
    long_labels = [l for l in stats["labels"] if _visible_len(l) > 15]
    if long_labels:
        sample = "、".join(f"“{l}”" for l in long_labels[:2])
        warnings.append(f"{len(long_labels)} 个节点超过 15 字（如 {sample}）— 提炼为 4–12 字关键词组")
    emojis = [b.get("label", "")[:2].strip() for b in branches]
    dup = {e for e in emojis if e and emojis.count(e) > 1}
    if dup:
        warnings.append(f"主分支 emoji 重复（{'、'.join(sorted(dup))}）— 每个分支用不同的图像锚点")

    # ── 渐进分化 / Ausubel（概括度自上而下递减）─────────────────────────
    if reversed_pairs:
        s = "、".join(f"“{l}”" for l in reversed_pairs[:2])
        warnings.append(f"{len(reversed_pairs)} 处深层节点比其父节点更宽泛（如 {s}）— "
                        "渐进分化要求越往下越具体，检查是否概括度倒挂")

    # ── MECE：完全穷尽（麦肯锡 / 集合论）────────────────────────────────
    if 2 <= nb <= 6:
        warnings.append("【MECE 自检】请确认这 " + str(nb) +
                        " 个主分支是否【完全穷尽】了中心主题：有无明显遗漏的维度？"
                        "（总结类任务尤其要避免漏项）")

    # ── 概念图关系（Novak）：识别到关系型内容 ───────────────────────────
    if relation_found:
        types = "、".join(relation_found.keys())
        warnings.append(f"检测到{types}等关系型表述 — 思维导图默认只表达从属关系，"
                        "这类因果/对比/时序/条件关系建议用关系标签或连线颜色标注，"
                        "或选用鱼骨图(因果)/时间线(时序)布局以免丢失信息")

    avg = (sum(_visible_len(l) for l in stats["labels"]) / max(1, len(stats["labels"])))
    print(f"[mindmap] 📋 结构质检 · 节点 {stats['total']} · 主分支 {nb} · "
          f"深度 {stats['max_depth'] + 1} 层 · 平均标签 {avg:.0f} 字", file=sys.stderr)
    for w in warnings:
        print(f"[mindmap] ⚠ {w}", file=sys.stderr)
    if not warnings:
        print("[mindmap] ✓ 结构符合认知负荷·双重编码·渐进分化·MECE 原则", file=sys.stderr)
    return warnings


def build_tree(data):
    if "central" not in data:
        raise ValueError("JSON must contain a 'central' key.")
    branches = []
    for i, b in enumerate(data.get("branches", [])):
        nb = normalize_node(b)
        nb.setdefault("color", DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
        # ── Auto-inject emoji if branch label doesn't start with one ──
        _auto_inject_emoji(nb, i)
        branches.append(nb)
    return {"central": data["central"], "branches": branches}


# ── Emoji auto-injection (Dual-Coding Theory) ────────────────────────────
# If the AI didn't add emoji to branch labels, the script selects an emoji
# by matching the label text against a semantic keyword dictionary.
# This ensures the emoji visually represents the *meaning* of the branch,
# not just its color.

# Semantic keyword → emoji mapping (Chinese + English, ordered by specificity)
# More specific keywords must come before general ones.
_SEMANTIC_EMOJI = [
    # ── 人物/角色 ──
    (["人物", "角色", "团队", "成员", "员工", "用户", "画像", "character", "people", "team", "user", "member", "staff", "player", "persona"], "👥"),
    (["作者", "作家", "创始人", "author", "writer", "founder", "creator"], "✍️"),
    (["领导", "管理层", "CEO", "leader", "management", "executive"], "👔"),
    (["客户", "顾客", "消费者", "受众", "customer", "client", "consumer", "audience"], "🧑‍💼"),
    (["合作", "伙伴", "联盟", "协作", "partner", "collaborat", "alliance", "cooperat"], "🤝"),
    # ── 时间/历史 ──
    (["历史", "背景", "起源", "演变", "发展史", "history", "background", "origin", "evolution", "heritage"], "🏛️"),
    (["时间", "阶段", "时期", "年代", "时间线", "timeline", "period", "phase", "era", "date", "schedule"], "📅"),
    (["未来", "趋势", "展望", "预测", "前景", "future", "trend", "forecast", "outlook", "vision"], "🔮"),
    # ── 技术/科学 ──
    (["技术", "科技", "研发", "算法", "tech", "technology", "algorithm", "engineering", "R&D"], "🔬"),
    (["AI", "人工智能", "机器学习", "深度学习", "模型", "artificial intelligence", "machine learning", "neural", "GPT", "LLM"], "🤖"),
    (["代码", "编程", "开发", "软件", "code", "programming", "software", "develop", "API", "debug"], "💻"),
    (["数据", "数据库", "统计", "指标", "data", "database", "analytics", "statistics", "metric", "KPI"], "📊"),
    (["网络", "互联网", "通信", "社交媒体", "社交", "social media", "network", "internet", "communication", "web", "online"], "🌐"),
    (["安全", "加密", "隐私", "防护", "security", "encryption", "privacy", "cyber", "protect"], "🔒"),
    # ── 商业/金融 ──
    (["商业", "盈利", "收入", "营收", "利润", "变现", "business", "revenue", "profit", "income", "monetiz"], "💰"),
    (["市场", "营销", "推广", "品牌", "口碑", "传播", "market", "marketing", "brand", "promotion", "advertis", "PR"], "📈"),
    (["销售", "卖点", "转化", "获客", "增长", "拉新", "sale", "conver", "acquisition", "growth", "retain", "funnel"], "📊"),
    (["竞争", "对手", "竞品", "壁垒", "competi", "rival", "barrier"], "⚔️"),
    (["成本", "费用", "预算", "投资", "融资", "cost", "budget", "invest", "expense", "funding", "capital"], "💵"),
    (["价格", "定价", "收费", "报价", "price", "pricing", "fee", "charge", "quota"], "🏷️"),
    (["战略", "策略", "规划", "布局", "strategy", "strategic", "planning", "roadmap"], "🎯"),
    (["产品", "功能", "特性", "需求", "product", "feature", "function", "requirement", "spec"], "📦"),
    (["渠道", "分发", "分销", "平台", "channel", "distribut", "platform"], "🔗"),
    (["供应链", "供应", "采购", "库存", "procurement", "supply", "inventory", "sourcing", "vendor"], "🏭"),
    (["运营", "运维", "运作", "operation", "ops", "maintain"], "⚙️"),
    # ── 客户服务 ──
    (["服务", "客服", "售后", "保障", "支持", "service", "support", "after-sale", "warranty", "helpdesk"], "🎧"),
    (["体验", "满意度", "反馈", "口碑", "评价", "experience", "satisfaction", "feedback", "review", "NPS", "UX"], "⭐"),
    (["留存", "复购", "忠诚", "黏性", "retention", "loyalty", "repeat", "churn", "stickiness"], "🔁"),
    # ── 教育/学习 ──
    (["学习", "教育", "课程", "培训", "教学", "learn", "education", "course", "training", "teach", "study"], "🎓"),
    (["知识", "概念", "理论", "原理", "knowledge", "concept", "theory", "principle"], "📚"),
    (["考试", "测试", "评估", "评价", "评分", "exam", "test", "assessment", "evaluation", "grading"], "📝"),
    (["启蒙", "早教", "入门", "基础", "beginner", "fundamental", "basic", "introduct", "primer"], "🌟"),
    # ── 职业/求职 ──
    (["职业", "求职", "面试", "简历", "career", "job", "interview", "resume", "CV", "hiring", "recruit"], "💼"),
    (["薪资", "工资", "薪酬", "待遇", "salary", "wage", "compensation", "pay", "bonus"], "💳"),
    (["晋升", "升职", "成长", "发展", "职级", "promotion", "advancement", "career path", "growth"], "📶"),
    (["技能", "能力", "技巧", "skill", "ability", "competenc", "expertise", "proficienc"], "🎯"),
    # ── 文学/艺术 ──
    (["作品", "文学", "小说", "著作", "文章", "writing", "literature", "novel", "book", "article"], "📖"),
    (["艺术", "风格", "美学", "art", "style", "aesthetic"], "🎨"),
    (["音乐", "歌曲", "music", "song", "melody", "album"], "🎵"),
    (["电影", "视频", "影视", "film", "movie", "video", "cinema"], "🎬"),
    (["文化", "传统", "文明", "民俗", "culture", "tradition", "civilization", "folk"], "🌍"),
    (["摄影", "拍摄", "相机", "镜头", "photo", "camera", "lens", "shoot", "image"], "📷"),
    (["设计", "UI", "UX", "排版", "视觉", "design", "layout", "visual", "graphic", "typograph"], "🎨"),
    # ── 结构/组织 ──
    (["结构", "组织", "架构", "框架", "structure", "organization", "framework", "architect"], "🏗️"),
    (["流程", "步骤", "过程", "方法", "工艺", "process", "step", "procedure", "method", "workflow", "SOP"], "🔄"),
    (["分类", "类型", "类别", "种类", "category", "type", "classification", "kind", "taxonomy"], "🗂️"),
    (["情节", "故事", "叙事", "剧情", "plot", "story", "narrative", "chapter"], "📜"),
    (["标准", "规范", "验收", "准则", "质检", "standard", "specification", "criteria", "QA", "QC", "inspect", "quality"], "✅"),
    # ── 问题/风险 ──
    (["问题", "挑战", "困难", "障碍", "痛点", "problem", "challenge", "difficult", "obstacle", "issue", "pain point"], "⚠️"),
    (["风险", "危险", "威胁", "risk", "danger", "threat", "hazard"], "🚨"),
    (["限制", "缺点", "不足", "局限", "短板", "limitation", "disadvantage", "weakness", "restrict", "drawback"], "🚧"),
    (["监管", "法规", "合规", "政策", "法律", "regulat", "compliance", "policy", "law", "legal", "govern"], "⚖️"),
    # ── 成果/价值 ──
    (["成果", "成就", "成功", "价值", "优势", "亮点", "achievement", "success", "value", "advantage", "benefit", "highlight"], "🏆"),
    (["目标", "愿景", "使命", "goal", "objective", "mission", "OKR", "KR"], "🎯"),
    (["创新", "突破", "改进", "优化", "innovati", "breakthrough", "improve", "optimiz"], "💡"),
    (["影响", "效果", "作用", "成效", "impact", "effect", "influence", "outcome", "result"], "💫"),
    (["应用", "实践", "案例", "场景", "用途", "application", "practice", "case", "scenario", "use case", "usage"], "🛠️"),
    # ── 资源/工具 ──
    (["资源", "工具", "设备", "器材", "装备", "resource", "tool", "equipment", "instrument", "gear", "device"], "🔧"),
    (["材料", "原料", "物料", "素材", "material", "ingredient", "raw material", "substance", "fabric"], "📦"),
    (["环境", "生态", "自然", "绿色", "environment", "ecology", "nature", "climate", "green", "sustain"], "🌱"),
    # ── 健康/医疗 ──
    (["健康", "医疗", "疾病", "治疗", "症状", "health", "medical", "disease", "treatment", "clinical", "symptom", "diagnosis"], "🏥"),
    (["营养", "饮食", "膳食", "维生素", "nutrition", "diet", "vitamin", "supplement", "calorie"], "🥗"),
    (["疫苗", "免疫", "防疫", "vaccine", "immuniz", "prevention"], "💉"),
    (["健身", "运动", "锻炼", "体能", "fitness", "workout", "exercise", "gym", "training"], "💪"),
    (["减肥", "瘦身", "体重", "weight loss", "slim", "body fat"], "⚖️"),
    (["睡眠", "休息", "作息", "sleep", "rest", "insomnia", "nap"], "😴"),
    (["压力", "焦虑", "减压", "放松", "stress", "anxiety", "relax", "mindful", "meditation"], "🧘"),
    # ── 地理/旅游 ──
    (["地理", "地点", "位置", "区域", "国家", "geography", "location", "region", "country", "city"], "🗺️"),
    (["旅游", "旅行", "攻略", "出行", "度假", "travel", "trip", "tour", "vacation", "journey", "itinerary"], "✈️"),
    (["住宿", "酒店", "民宿", "hotel", "accommodation", "hostel", "lodging", "Airbnb"], "🏨"),
    (["景点", "景区", "名胜", "观光", "sight", "attraction", "landmark", "scenic", "destination"], "🏞️"),
    (["交通", "物流", "运输", "出行", "transport", "logistics", "shipping", "commut", "transit"], "🚚"),
    # ── 食物/烹饪 ──
    (["食物", "美食", "菜肴", "菜谱", "烹饪", "做菜", "food", "cuisine", "cooking", "recipe", "meal", "dish", "chef"], "🍽️"),
    # ── 家庭/育儿 ──
    (["育儿", "孩子", "儿童", "宝宝", "亲子", "parent", "child", "baby", "kid", "toddler", "nurtur"], "👶"),
    (["家庭", "家居", "家装", "居家", "family", "home", "household", "domestic"], "🏠"),
    (["装修", "装饰", "翻新", "改造", "renovati", "decorat", "interior", "remodel", "furnish"], "🏠"),
    # ── 宠物 ──
    (["宠物", "猫", "狗", "喂养", "兽医", "pet", "cat", "dog", "vet", "animal", "breed", "groom"], "🐾"),
    # ── 体育/运动 ──
    (["体育", "赛事", "联赛", "比赛", "竞技", "sport", "league", "competition", "athletic", "tournament", "championship"], "⚽"),
    # ── 法律/制度 ──
    (["制度", "规则", "条例", "法案", "条款", "system", "rule", "regulation", "act", "institution", "clause"], "📜"),
    # ── 情感/心理 ──
    (["情感", "心理", "性格", "认知", "行为", "personality", "emotion", "psychology", "mental", "character", "cognitive", "behavior"], "🧠"),
    # ── 建筑/空间 ──
    (["建筑", "空间", "场所", "场地", "building", "space", "place", "architecture", "venue", "facility"], "🏗️"),
    # ── 财务/理财 ──
    (["理财", "投资", "基金", "股票", "债券", "保险", "finance", "invest", "fund", "stock", "bond", "insurance", "portfolio"], "💹"),
    (["税", "税务", "纳税", "报税", "tax", "taxation", "fiscal"], "🧾"),
    (["退休", "养老", "pension", "retire", "annuity"], "🏖️"),
    (["资产", "财富", "净值", "asset", "wealth", "net worth", "estate", "property"], "🏦"),
    # ── 制造/生产 ──
    (["制造", "生产", "工厂", "产线", "manufactur", "production", "factory", "assembly", "fabricat"], "🏭"),
    (["包装", "封装", "标签", "packaging", "labeling", "wrapping", "container"], "📦"),
    (["检测", "测量", "检验", "校准", "detect", "measure", "inspect", "calibrat", "monitor"], "🔎"),
    (["配方", "研发", "recipe", "formul", "R&D", "develop"], "🧪"),
    # ── 概述/介绍/总结 ──
    (["概述", "简介", "总结", "综述", "overview", "introduction", "summary", "abstract", "brief", "recap"], "📋"),
    # ── 军事/战争 ──
    (["战役", "战争", "军事", "战斗", "作战", "攻防", "battle", "war", "military", "combat", "warfare", "campaign"], "⚔️"),
    # ── 思想/哲学 ──
    (["思想", "哲学", "主题", "观点", "理念", "意识形态", "thought", "philosophy", "theme", "ideology", "idea", "viewpoint"], "💭"),
    # ── 研究/学术 ──
    (["研究", "学术", "流派", "论文", "学科", "实验", "research", "academic", "paper", "discipline", "experiment", "scholar"], "🔍"),
    # ── 版本/变更 ──
    (["版本", "变更", "更新", "迭代", "修订", "version", "update", "revision", "iteration", "changelog"], "📄"),
    # ── 护理/日常 ──
    (["护理", "保养", "维护", "保健", "日常", "care", "maintenance", "routine", "daily", "upkeep", "hygiene"], "🧴"),
    # ── 沟通/表达 ──
    (["沟通", "表达", "演讲", "谈判", "对话", "communicat", "express", "speech", "negotiat", "dialog", "present"], "🗣️"),
    # ── 选择/推荐/对比 ──
    (["选择", "推荐", "对比", "评测", "排名", "选型", "choose", "recommend", "compare", "review", "rank", "select", "pick", "best"], "🔖"),
    # ── 指南/攻略/技巧 ──
    (["指南", "攻略", "技巧", "诀窍", "要点", "秘诀", "guide", "tip", "trick", "hack", "how-to", "tutorial", "cheat sheet"], "📌"),
    # ── 构图/光线 (摄影/视觉) ──
    (["构图", "光线", "色彩", "曝光", "composit", "lighting", "exposure", "color", "tone", "contrast"], "🖼️"),
    # ── 后期/编辑 ──
    (["后期", "编辑", "修图", "剪辑", "渲染", "edit", "post-process", "retouch", "render", "montage"], "✂️"),
]

_FALLBACK_EMOJIS = ["📌", "📎", "🔹", "🔸", "▪️", "🔻", "🔺", "💠", "🔘", "📍"]


def _has_emoji_prefix(text):
    """Check if text starts with an emoji (Unicode emoji range)."""
    if not text:
        return False
    cp = ord(text[0])
    if cp >= 0x1F300:  return True
    if 0x2600 <= cp <= 0x27BF: return True
    if 0x2300 <= cp <= 0x23FF: return True
    if 0xFE00 <= cp <= 0xFEFF: return True
    if 0x200D <= cp <= 0x200D: return True
    if len(text) > 1:
        cp2 = ord(text[1])
        if cp2 >= 0x1F300 or cp2 == 0xFE0F or cp2 == 0x20E3:
            return True
    return False


def _match_emoji_by_semantic(label):
    """Match an emoji by scanning the label against the keyword dictionary."""
    text = label.lower()
    for keywords, emoji in _SEMANTIC_EMOJI:
        for kw in keywords:
            if kw.lower() in text:
                return emoji
    return None


def _auto_inject_emoji(branch, index):
    """Add semantically matched emoji prefix to branch label if missing."""
    label = branch.get("label", "")
    if _has_emoji_prefix(label):
        return  # already has emoji

    # 1. Try semantic keyword matching
    emoji = _match_emoji_by_semantic(label)

    # 2. Fallback: use index-based neutral emoji
    if not emoji:
        emoji = _FALLBACK_EMOJIS[index % len(_FALLBACK_EMOJIS)]

    branch["label"] = f"{emoji} {label}"


def _char_w(ch, fs):
    return fs * (0.92 if ord(ch) > 127 else 0.58)


MAX_LABEL_CHARS = 20   # 与前端 MAX_LABEL_CHARS 对齐：超过即省略显示


def trunc_label(full):
    """按字符数截断：超过 MAX_LABEL_CHARS 截断加省略号。返回 (text, truncated)。"""
    s = str(full)
    if len(s) <= MAX_LABEL_CHARS:
        return s, False
    return s[:MAX_LABEL_CHARS] + "…", True


def measure_w(text, depth):
    c = CFG[min(depth, len(CFG)-1)]
    shown = trunc_label(text)[0]                 # 按截断后文字算宽
    w = sum(_char_w(ch, c["fs"]) for ch in shown)
    return max(c["min_w"], min(c["max_w"], w + c["px"] * 2))


def display_label(node):
    """节点显示文字：超过 20 字符省略（与前端 displayLabel 对齐）。"""
    full = node.get("label") or node.get("central", "")
    return trunc_label(full)[0]


_nid = [0]

def annotate(node, depth):
    node["_id"]    = "n" + str(_nid[0]); _nid[0] += 1
    node["_depth"] = depth
    node["_w"]     = measure_w(node.get("label") or node.get("central", ""), depth)
    node["_h"]     = CFG[min(depth, len(CFG)-1)]["h"]
    for ch in node.get("children", []): annotate(ch, depth + 1)
    for b  in node.get("branches",  []): annotate(b, 1)


def flatten_tree(tree):
    result, q = [], [tree]
    while q:
        n = q.pop(0); result.append(n)
        for c in n.get("children", []) + n.get("branches", []): q.append(c)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT  —  Balanced left-right tree
#
#  Right side:  branch node → children stacked vertically to its right
#  Left  side:  branch node → children stacked vertically to its left
#               (node x = -(branch_x + branch_w/2 + gap + child_w/2))
#
#  Positions are stored as node centres.
# ─────────────────────────────────────────────────────────────────────────────

def subtree_height(node):
    """Total vertical space this subtree needs (including V_GAP between siblings)."""
    d    = node["_depth"]
    kids = node.get("children", [])
    vg   = V_GAP[min(d, len(V_GAP)-1)]
    if not kids:
        return node["_h"]
    ch_total = sum(subtree_height(k) for k in kids) + vg * (len(kids) - 1)
    return max(node["_h"], ch_total)


def layout_subtree(node, cx, cy, side, positions):
    """
    Place `node` centred at (cx, cy).
    Then place its children on `side` (+1 = right, -1 = left).
    """
    positions[node["_id"]] = {"x": cx, "y": cy, "parent_id":
                               positions.get(node["_id"], {}).get("parent_id")}

    kids = node.get("children", [])
    if not kids:
        return

    d    = node["_depth"]
    vg   = V_GAP[min(d+1, len(V_GAP)-1)]
    hg   = H_GAP[min(d+1, len(H_GAP)-1)]

    # x-centre of children column
    child_w  = max(k["_w"] for k in kids)
    child_cx = cx + side * (node["_w"] / 2 + hg + child_w / 2)

    # total height block of children
    heights  = [subtree_height(k) for k in kids]
    total_h  = sum(heights) + vg * (len(kids) - 1)

    # start y so the block is centred on cy
    cur_y = cy - total_h / 2

    for kid, h in zip(kids, heights):
        kid_cy = cur_y + h / 2
        positions[kid["_id"]] = {"x": child_cx, "y": kid_cy,
                                  "parent_id": node["_id"]}
        layout_subtree(kid, child_cx, kid_cy, side, positions)
        cur_y += h + vg


def compute_layout(tree):
    positions = {}
    positions[tree["_id"]] = {"x": 0, "y": 0, "parent_id": None}

    branches = tree.get("branches", [])
    if not branches:
        return positions

    n      = len(branches)
    n_right = math.ceil(n / 2)   # right side gets ceiling
    n_left  = n - n_right

    right_branches = branches[:n_right]
    left_branches  = branches[n_right:]

    root_h = CFG[0]["h"]
    root_w = tree["_w"]

    def place_side(side_branches, side):
        """Stack branches vertically, centred on root y=0."""
        vg = V_GAP[1]
        heights = [subtree_height(b) for b in side_branches]
        total_h = sum(heights) + vg * (len(heights) - 1)
        hg      = H_GAP[1]
        # branch column x-centre
        branch_cx = side * (root_w / 2 + hg + (max(b["_w"] for b in side_branches) / 2 if side_branches else 0))
        cur_y = -total_h / 2
        for branch, h in zip(side_branches, heights):
            bcy = cur_y + h / 2
            positions[branch["_id"]] = {"x": branch_cx, "y": bcy,
                                         "parent_id": tree["_id"]}
            layout_subtree(branch, branch_cx, bcy, side, positions)
            cur_y += h + vg

    place_side(right_branches,  1)
    place_side(left_branches,  -1)

    return positions


def bounding_box(positions, nodes, pad=60):
    xs, ys = [], []
    for n in nodes:
        p = positions.get(n["_id"])
        if not p: continue
        xs += [p["x"] - n["_w"]/2, p["x"] + n["_w"]/2]
        ys += [p["y"] - n["_h"]/2, p["y"] + n["_h"]/2]
    if not xs:
        return -pad, -pad, pad, pad
    return min(xs)-pad, min(ys)-pad, max(xs)+pad, max(ys)+pad


def build_color_map(tree):
    cmap = {tree["_id"]: "#7c8cf8"}
    def fill(node, color):
        cmap[node["_id"]] = color
        for ch in node.get("children", []): fill(ch, color)
    for b in tree.get("branches", []): fill(b, b.get("color", "#888"))
    return cmap


# ─────────────────────────────────────────────────────────────────────────────
# Edge path helpers
# ─────────────────────────────────────────────────────────────────────────────
def edge_path(px, py, pw, cx, cy, cw, depth, ph=30):
    """
    Smooth cubic Bezier from parent side-edge to child side-edge. All children
    of a node leave from the SAME point (the parent's vertical center) and then
    curve out to each child — matching the HTML edgePath0.
    """
    s = 1 if cx >= px else -1
    x1 = px + s * pw/2
    x2 = cx - s * cw/2
    y1 = py                              # single shared exit point (parent center)

    if abs(cy - y1) < 2:
        return f"M{x1:.1f},{y1:.1f} L{x2:.1f},{cy:.1f}"

    span = abs(x2 - x1) or 1
    t = 0.55 if depth == 1 else 0.48
    cp1x = x1 + s * span * t
    cp2x = x2 - s * span * t
    return f"M{x1:.1f},{y1:.1f} C{cp1x:.1f},{y1:.1f} {cp2x:.1f},{cy:.1f} {x2:.1f},{cy:.1f}"


# ─────────────────────────────────────────────────────────────────────────────
# Static SVG  (Python-side export)
# ─────────────────────────────────────────────────────────────────────────────
def _xml(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")


def render_svg_static(tree, positions, include_xml_header=True, theme="midnight"):
    th    = THEMES.get(theme, THEMES["midnight"])
    nodes = flatten_tree(tree)
    minx, miny, maxx, maxy = bounding_box(positions, nodes)
    W, H  = maxx - minx, maxy - miny
    cmap  = build_color_map(tree)
    L     = []

    if include_xml_header:
        L.append('<?xml version="1.0" encoding="UTF-8"?>')
    L.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'viewBox="{minx:.1f} {miny:.1f} {W:.1f} {H:.1f}" '
             f'width="{W:.0f}" height="{H:.0f}">')

    # defs: glow + gradient for root
    L.append('''<defs>
  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <linearGradient id="root-grad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#4c5fdb"/>
    <stop offset="100%" stop-color="#7c8cf8"/>
  </linearGradient>
</defs>''')

    # background
    L.append(f'<rect x="{minx:.1f}" y="{miny:.1f}" width="{W:.1f}" height="{H:.1f}" fill="{th["bg"]}"/>')

    # ── edges ──
    for node in nodes:
        p = positions.get(node["_id"])
        if not p or p["parent_id"] is None: continue
        pp    = positions.get(p["parent_id"])
        if not pp: continue
        pnode = next((n for n in nodes if n["_id"] == p["parent_id"]), None)
        if not pnode: continue

        color = cmap.get(node["_id"], "#888")
        depth = node["_depth"]
        sw    = 2.5 if depth == 1 else (1.8 if depth == 2 else 1.3)
        op    = 0.85 if depth == 1 else (0.6 if depth == 2 else 0.4)
        d_path = edge_path(pp["x"], pp["y"], pnode["_w"],
                           p["x"],  p["y"],  node["_w"], depth, pnode["_h"])
        L.append(f'<path d="{d_path}" fill="none" stroke="{color}" '
                 f'stroke-width="{sw}" stroke-opacity="{op}" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')

    # ── nodes ──
    for node in nodes:
        p = positions.get(node["_id"])
        if not p: continue
        depth = node["_depth"]
        c     = CFG[min(depth, len(CFG)-1)]
        w, h  = node["_w"], node["_h"]
        nx, ny = p["x"] - w/2, p["y"] - h/2
        color  = cmap.get(node["_id"], "#888")
        label  = display_label(node)

        # rect
        if depth == 0:
            L.append(f'<rect x="{nx:.1f}" y="{ny:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'rx="{c["rx"]}" fill="url(#root-grad)" filter="url(#glow)"/>')
            tc = th["node_text"][0]
        elif depth == 1:
            L.append(f'<rect x="{nx:.1f}" y="{ny:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'rx="{c["rx"]}" fill="{color}30" stroke="{color}" stroke-width="2"/>')
            tc = th["node_text"][1]
        elif depth == 2:
            L.append(f'<rect x="{nx:.1f}" y="{ny:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'rx="{c["rx"]}" fill="{color}18" stroke="{color}bb" stroke-width="1.5"/>')
            tc = th["node_text"][2]
        else:
            L.append(f'<rect x="{nx:.1f}" y="{ny:.1f}" width="{w:.1f}" height="{h:.1f}" '
                     f'rx="{c["rx"]}" fill="{color}0e" stroke="{color}77" stroke-width="1"/>')
            tc = th["node_text"][3]

        # text
        L.append(f'<text x="{p["x"]:.1f}" y="{p["y"]:.1f}" '
                 f'dominant-baseline="central" text-anchor="middle" '
                 f'font-family="{FONT_STACK}" font-size="{c["fs"]}" font-weight="{c["fw"]}" '
                 f'fill="{tc}">{_xml(label)}</text>')

    L.append('</svg>')
    return "\n".join(L)


# ─────────────────────────────────────────────────────────────────────────────
# XMind export
# ─────────────────────────────────────────────────────────────────────────────
def build_xmind(tree, title):
    """
    Generate an .xmind file compatible with both XMind 8 and XMind 2020+.
    Includes content.xml (XMind 8 format) AND content.json (XMind 2020 format).
    """
    def uid(): return uuid.uuid4().hex[:26]

    # ── content.json (XMind 2020+) ─────────────────────────────────────────
    def xnode_json(node):
        children = node.get("branches", []) + node.get("children", [])
        obj = {"id": uid(), "class": "topic",
               "title": node.get("label") or node.get("central", "")}
        if children:
            obj["children"] = {"attached": [xnode_json(c) for c in children]}
        if node.get("color"):
            obj["style"] = {"id": uid(), "properties": {
                "line-color":        node["color"],
                "line-width":        "2pt",
                "background-color":  node["color"] + "33",
                "border-line-color": node["color"],
                "shape-class":       "org.xmind.topicShape.roundedRect",
            }}
        return obj

    root_json = xnode_json(tree)
    root_json["structureClass"] = "org.xmind.ui.map.unbalanced"
    sheet_id  = uid()
    content_json = [{
        "id": sheet_id, "class": "sheet", "title": title,
        "rootTopic": root_json, "theme": {}, "extensions": [],
    }]

    # ── content.xml (XMind 8) ──────────────────────────────────────────────
    def _xe(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;")
                      .replace(">", "&gt;").replace('"', "&quot;"))

    def xnode_xml(node, depth=0):
        children = node.get("branches", []) + node.get("children", [])
        label = node.get("label") or node.get("central", "")
        color = node.get("color", "")
        ind = "  " * depth
        lines = [f'{ind}<topic id="{uid()}"']
        if depth == 0:
            lines[0] += ' structure-class="org.xmind.ui.map.unbalanced"'
        if color:
            style_id = uid()
            lines[0] += f' style-id="{style_id}"'
        lines[0] += ">"
        lines.append(f'{ind}  <title>{_xe(label)}</title>')
        if color:
            lines.append(f'{ind}  <style-ref id="{style_id}"/>')
        if children:
            lines.append(f'{ind}  <children>')
            lines.append(f'{ind}    <topics type="attached">')
            for child in children:
                lines.extend(xnode_xml(child, depth + 3).split("\n"))
            lines.append(f'{ind}    </topics>')
            lines.append(f'{ind}  </children>')
        lines.append(f'{ind}</topic>')
        return "\n".join(lines)

    def build_styles(node, styles=None):
        if styles is None: styles = []
        color = node.get("color", "")
        if color:
            styles.append(
                f'  <style id="{uid()}" type="topic">\n'
                f'    <topic-properties border-line-color="{color}" '
                f'fill-color="{color}33" line-color="{color}" line-width="2pt"/>\n'
                f'  </style>'
            )
        for c in node.get("branches", []) + node.get("children", []):
            build_styles(c, styles)
        return styles

    xml_sheet_id = uid()
    xml_root = xnode_xml(tree, 0)
    styles   = build_styles(tree)

    content_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"
  xmlns:fo="http://www.w3.org/1999/XSL/Format"
  xmlns:svg="http://www.w3.org/2000/svg"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  version="2.0">
  <sheet id="{xml_sheet_id}">
{xml_root}
    <title>{_xe(title)}</title>
  </sheet>
</xmap-content>"""

    styles_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                  '<xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0" version="2.0">\n'
                  + "\n".join(styles) + "\n</xmap-styles>")

    # ── metadata ───────────────────────────────────────────────────────────
    metadata = {
        "modifier": "",
        "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
        "creator": {"name": "OpenClaw MindMap", "version": "5.0", "platform": ""},
    }

    manifest = {"file-entries": {
        "content.json":  {"media-type": "application/json"},
        "content.xml":   {"media-type": "text/xml"},
        "styles.xml":    {"media-type": "text/xml"},
        "metadata.json": {"media-type": "application/json"},
        "manifest.json": {"media-type": "application/json"},
    }}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest,      ensure_ascii=False))
        zf.writestr("content.json",  json.dumps(content_json,  ensure_ascii=False, indent=2))
        zf.writestr("content.xml",   content_xml.encode("utf-8"))
        zf.writestr("styles.xml",    styles_xml.encode("utf-8"))
        zf.writestr("metadata.json", json.dumps(metadata,      ensure_ascii=False, indent=2))
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# HTML template  (raw string — no f-string, JS braces are literal)
# ─────────────────────────────────────────────────────────────────────────────
_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>__TITLE__</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --bg:#0d0f1a;--fg:#e8eaf0;--fg-strong:#fff;--btn-fg:#c0c4dc;
  --dim-fg:rgba(255,255,255,.45);--muted:rgba(255,255,255,.26);
  --panel:rgba(255,255,255,.04);--border-soft:rgba(255,255,255,.08);
  --border:rgba(255,255,255,.13);--hover-bg:rgba(255,255,255,.1);
  --active-bg:rgba(255,255,255,.16);--menu-bg:rgba(18,22,38,.98);
  --exp-fg:rgba(180,200,255,.75);--exp-bg:rgba(55,85,200,.14);
  --exp-border:rgba(90,130,255,.22);--exp-hover-bg:rgba(75,110,230,.3);
  --exp-hover-fg:#ccd8ff;--accent-fg:#b4bcff;--accent-bg:rgba(124,140,248,.28);
  --accent-border:rgba(124,140,248,.55);
}
body[data-theme="paper"]{
  --bg:#f7f5ef;--fg:#2a3040;--fg-strong:#14181f;--btn-fg:#4a5266;
  --dim-fg:rgba(20,25,40,.55);--muted:rgba(20,25,40,.4);
  --panel:rgba(20,25,40,.045);--border-soft:rgba(20,25,40,.1);
  --border:rgba(20,25,40,.16);--hover-bg:rgba(20,25,40,.08);
  --active-bg:rgba(20,25,40,.14);--menu-bg:rgba(255,255,254,.99);
  --exp-fg:#3b56c4;--exp-bg:rgba(76,95,219,.1);
  --exp-border:rgba(76,95,219,.3);--exp-hover-bg:rgba(76,95,219,.2);
  --exp-hover-fg:#2a41a8;--accent-fg:#4c5fdb;--accent-bg:rgba(124,140,248,.18);
  --accent-border:rgba(124,140,248,.5);
}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
              "Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--fg);
  height:100vh;overflow:hidden;display:flex;flex-direction:column;
}
header{
  padding:8px 16px;background:var(--panel);
  border-bottom:1px solid var(--border-soft);
  display:flex;flex-direction:column;gap:6px;
  flex-shrink:0;user-select:none;
}
.header-row{display:flex;align-items:center;gap:5px;flex-wrap:wrap;}
.header-row.top{justify-content:space-between;}
header h1{font-size:14px;font-weight:600;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;flex:1;min-width:0;}
.btn-group{
  display:flex;align-items:center;gap:2px;
  background:var(--panel);border:1px solid var(--border-soft);
  border-radius:8px;padding:2px;
}
.btn-group-label{
  font-size:10px;color:var(--muted);padding:0 5px 0 7px;
  white-space:nowrap;letter-spacing:.04em;text-transform:uppercase;
}
.btn{
  background:transparent;border:1px solid transparent;
  color:var(--btn-fg);padding:4px 9px;border-radius:6px;font-size:12px;
  cursor:pointer;transition:background .12s,color .12s,border-color .12s;
  white-space:nowrap;
}
.btn:hover{background:var(--hover-bg);color:var(--fg-strong);border-color:var(--border);}
.btn:active{background:var(--active-bg);}
.btn.exp{
  font-size:11px;padding:4px 10px;
  color:var(--exp-fg);
  background:var(--exp-bg);
  border-color:var(--exp-border);
}
.btn.exp:hover{background:var(--exp-hover-bg);border-color:var(--exp-border);color:var(--exp-hover-fg);}
.sep{width:1px;height:16px;background:var(--hover-bg);margin:0 2px;}
.btn.layout-btn{padding:3px 8px;font-size:11px;color:var(--dim-fg);}
.btn.layout-btn:hover{color:var(--fg);}
.btn.layout-btn.active{background:var(--accent-bg);border-color:var(--accent-border);color:var(--accent-fg);font-weight:500;}
.btn.undo-btn{font-size:14px;padding:3px 7px;color:var(--dim-fg);}
.btn.undo-btn:not([disabled]):hover{color:var(--fg);}
.btn.undo-btn[disabled]{opacity:.28;cursor:default;}
.btn.undo-btn[disabled]:hover{background:transparent;border-color:transparent;}
.btn.undo-btn{padding:4px 8px;font-size:12px;}
.btn.undo-btn:disabled{opacity:.3;cursor:default;}
.meta{font-size:10px;color:var(--muted);white-space:nowrap;margin-left:auto;}
#wrap{flex:1;overflow:hidden;position:relative;}
svg{width:100%;height:100%;display:block;}
.nd{cursor:pointer;}
.nd .bg{transition:filter .12s;}
.nd:hover .bg{filter:brightness(1.3);}
.nd.drop-target .bg{filter:brightness(1.5);stroke:#7c8cf8;stroke-width:3;}
.nd.drop-target{filter:drop-shadow(0 0 6px rgba(124,140,248,.9));}
.nd.selected .sel-ring{display:block;}
.sel-ring{display:none;pointer-events:none;}
.tog circle{transition:fill .12s;}
.tog:hover circle{opacity:.9;}
.edge{fill:none;}

/* context menu */
#ctx-menu{
  position:fixed;display:none;z-index:300;
  background:var(--menu-bg);border:1px solid var(--border);
  border-radius:9px;padding:5px 0;min-width:165px;
  box-shadow:0 8px 32px rgba(0,0,0,.5);font-size:13px;
}
#ctx-menu.open{display:block;}
.ctx-item{padding:7px 16px;cursor:pointer;display:flex;align-items:center;gap:9px;color:var(--fg);transition:background .1s;user-select:none;}
.ctx-item:hover{background:var(--hover-bg);}
.ctx-item.danger{color:#f87171;}
.ctx-item.danger:hover{background:rgba(248,113,113,.1);}
.ctx-sep{height:1px;background:var(--border-soft);margin:4px 0;}
.ctx-icon{width:16px;text-align:center;font-size:14px;}
.ctx-colors{padding:6px 12px;display:flex;gap:6px;flex-wrap:wrap;}
.color-dot{width:18px;height:18px;border-radius:50%;cursor:pointer;border:2px solid transparent;transition:transform .1s,border-color .1s;}
.color-dot.active{border-color:var(--fg-strong);transform:scale(1.25);box-shadow:0 0 0 2px var(--border);}
.color-dot:hover{transform:scale(1.2);border-color:var(--dim-fg);}
/* inline label editor */
#label-editor{
  position:absolute;display:none;z-index:200;
  border:2px solid #7c8cf8;border-radius:6px;outline:none;
  background:var(--menu-bg);color:var(--fg);
  font-family:inherit;text-align:center;
  box-shadow:0 4px 16px rgba(0,0,0,.35);
  padding:0 8px;box-sizing:border-box;
}
/* 详情浮层：显示被省略节点的完整内容 */
#detail-pop{
  position:absolute;display:none;z-index:180;max-width:340px;
  background:var(--menu-bg);color:var(--fg);
  border:1px solid var(--accent-border);border-radius:8px;
  padding:9px 13px;font-size:13px;line-height:1.5;
  box-shadow:0 6px 22px rgba(0,0,0,.4);
  white-space:pre-wrap;word-break:break-word;pointer-events:none;
}
#detail-pop .dp-hint{
  display:block;margin-top:6px;font-size:11px;color:var(--dim-fg);
}
/* 截断节点标记：文字末尾已有省略号，这里给个细微下标提示可点开 */
.nd.truncated .bg{ stroke-dasharray:none; }
/* toast */
#toast{
  position:fixed;bottom:20px;left:50%;transform:translateX(-50%);
  background:var(--menu-bg);border:1px solid var(--border);
  border-radius:8px;padding:7px 18px;font-size:13px;
  pointer-events:none;opacity:0;transition:opacity .2s;z-index:99;
}
#toast.show{opacity:1;}
</style>
</head>
<body data-theme="__THEME__">
<header>
  <!-- 第一行：标题 + 导出 -->
  <div class="header-row top">
    <h1>&#x1F9E0; __TITLE__</h1>
    <div class="btn-group">
      <span class="btn-group-label">导出</span>
      <button class="btn exp" id="save-btn" onclick="exportHTML()" title="保存当前编辑后的完整 HTML 文件">HTML</button>
      <button class="btn exp" onclick="exportAs('svg')" title="导出 SVG">SVG</button>
      <button class="btn exp" onclick="exportAs('png')" title="导出 PNG">PNG</button>
      <button class="btn exp" onclick="exportAs('jpg')" title="导出 JPG">JPG</button>
      <button class="btn exp" onclick="exportAs('pdf')" title="导出 PDF">PDF</button>
      <button class="btn exp" onclick="exportXmind()" title="导出 XMind">XMind</button>
    </div>
  </div>
  <!-- 第二行：视图控制 + 撤销 + 布局 -->
  <div class="header-row">
    <div class="btn-group">
      <span class="btn-group-label">视图</span>
      <button class="btn" onclick="resetView()" title="重置视图">&#x2299;</button>
      <button class="btn" onclick="expandAll()" title="全部展开">&#x229E;</button>
      <button class="btn" onclick="collapseAll()" title="全部折叠">&#x229F;</button>
      <button class="btn" onclick="zoomIn()" title="放大">&#xFF0B;</button>
      <button class="btn" onclick="zoomOut()" title="缩小">&#xFF0D;</button>
      <button class="btn" onclick="toggleTheme()" title="深色 / 浅色主题">&#x1F313;</button>
    </div>
    <div class="btn-group">
      <span class="btn-group-label">历史</span>
      <button class="btn undo-btn" id="undo-btn" onclick="undo()" title="撤销 (Ctrl+Z)" disabled>&#x21B6;</button>
      <button class="btn undo-btn" id="redo-btn" onclick="redo()" title="重做 (Ctrl+Y)" disabled>&#x21B7;</button>
    </div>
    <div class="btn-group">
      <span class="btn-group-label">布局</span>
      <button class="btn layout-btn active" id="layout-btn-0" onclick="switchLayout(0)" title="左右均衡">&#x21C6; 左右</button>
      <button class="btn layout-btn" id="layout-btn-1" onclick="switchLayout(1)" title="全向辐射">&#x2736; 辐射</button>
      <button class="btn layout-btn" id="layout-btn-2" onclick="switchLayout(2)" title="向右树形">&#x27A1; 树形</button>
      <button class="btn layout-btn" id="layout-btn-3" onclick="switchLayout(3)" title="垂直向下">&#x1F333; 垂直</button>
      <button class="btn layout-btn" id="layout-btn-4" onclick="switchLayout(4)" title="力导向动画">&#x26A1; 力导向</button>
      <button class="btn layout-btn" id="layout-btn-5" onclick="switchLayout(5)" title="时间线">&#x23E9; 时间线</button>
      <button class="btn layout-btn" id="layout-btn-6" onclick="switchLayout(6)" title="鱼骨图">&#x1F41F; 鱼骨</button>
      <button class="btn layout-btn" id="layout-btn-7" onclick="switchLayout(7)" title="括弧图">&#x7D; 括弧</button>
    </div>
    <span class="meta">双击/F2 编辑 &nbsp;·&nbsp; Enter 兄弟节点 &nbsp;·&nbsp; Tab 子节点 &nbsp;·&nbsp; 拖到目标改挂/拖开重排 &nbsp;·&nbsp; 超20字省略·双击看全文 &nbsp;·&nbsp; −/+ 折叠 &nbsp;·&nbsp; 拖根平移 &nbsp;·&nbsp; Del 删除 &nbsp;·&nbsp; Ctrl+Z 撤销 &nbsp;·&nbsp; HTML 键绑定文件后自动保存</span>
  </div>
</header>
<div id="wrap">
  <svg id="svg" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="4" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <linearGradient id="root-grad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#4c5fdb"/>
        <stop offset="100%" stop-color="#7c8cf8"/>
      </linearGradient>
    </defs>
    <g id="edges-g"></g>
    <g id="nodes-g"></g>
  </svg>
  <input id="label-editor" spellcheck="false"/>
  <div id="detail-pop"></div>
</div>
<div id="ctx-menu">
  <div class="ctx-item" onclick="ctxAction('edit')"><span class="ctx-icon">&#x270F;&#xFE0F;</span>编辑文字</div>
  <div class="ctx-item" onclick="ctxAction('add-child')"><span class="ctx-icon">&#xFF0B;</span>添加子节点</div>
  <div class="ctx-item" onclick="ctxAction('add-sibling')"><span class="ctx-icon">&#x21B5;</span>添加兄弟节点</div>
  <div class="ctx-sep"></div>
  <div class="ctx-item" style="font-size:11px;color:var(--dim-fg);padding:4px 16px;cursor:default;" id="ctx-color-label">更改节点颜色</div>
  <div class="ctx-colors" id="ctx-colors"></div>
  <div class="ctx-sep"></div>
  <div class="ctx-item danger" onclick="ctxAction('delete')"><span class="ctx-icon">&#x1F5D1;</span>删除节点</div>
</div>
<div id="toast"></div>
<script>
/*__MINDMAP_DATA_START__*/
const RAW   = __RAW_JSON__;
const TITLE = __TITLE_JSON__;
const INIT_THEME = "__THEME__";
/*__MINDMAP_DATA_END__*/
const THEMES={
  midnight:{bg:"#0d0f1a",nodeText:["#ffffff","#ffffff","#e0e4f0","#a8b0c8"]},
  paper:   {bg:"#f7f5ef",nodeText:["#ffffff","#26304a","#39435e","#5b6580"]},
};
let CUR_THEME=(typeof INIT_THEME!=="undefined"&&INIT_THEME in THEMES)?INIT_THEME
             :((document.body.dataset.theme in THEMES)?document.body.dataset.theme:"midnight");
document.body.dataset.theme=CUR_THEME;
function toggleTheme(){
  CUR_THEME=CUR_THEME==="midnight"?"paper":"midnight";
  document.body.dataset.theme=CUR_THEME;
  renderAll(TREE);
  showToast(CUR_THEME==="midnight"?"已切换到深空主题":"已切换到纸墨主题");
}
const SVG_NS = "http://www.w3.org/2000/svg";
const CFG = [
  {h:48,fs:16,fw:"700",rx:12,px:32,minW:180,maxW:420},
  {h:38,fs:13,fw:"600",rx: 8,px:24,minW:110,maxW:340},
  {h:30,fs:12,fw:"400",rx: 6,px:18,minW: 80,maxW:300},
  {h:26,fs:11,fw:"400",rx: 5,px:16,minW: 72,maxW:280},
];
const PALETTE=["#4A90D9","#E86C3A","#27AE60","#9B59B6","#E74C3C","#F39C12","#1ABC9C","#E91E63","#00BCD4","#8BC34A"];
const H_GAP=[0,64,48,40], V_GAP=[0,20,12,8];
const MIN_W=60, MIN_H=20, HW=7;

let nodeMap={}, _nid=0, selectedId=null, ctxTargetId=null;
let _lastDown={id:null,t:0}, _dblGuard=false;   // 双击检测：区分单击选中与双击编辑
let _pushScheduled=false;  // rAF throttle for pushAway
let _undoStack=[], _redoStack=[];   // undo/redo snapshot stacks
const MAX_UNDO=50;
const MAX_LABEL_CHARS=20;   // 节点标签超过此字符数即省略显示，双击进入编辑框看完整内容



function charW(ch, fs){ return ch.charCodeAt(0)>127 ? fs*0.92 : fs*0.58; }

// 按字符数截断（每个字符计 1，无论中英文）；超过 MAX_LABEL_CHARS 截断加省略号
function truncLabel(full){
  const s=String(full);
  const arr=Array.from(s);                      // 正确按码点计数（含 emoji）
  if(arr.length<=MAX_LABEL_CHARS) return {text:s, truncated:false};
  return {text:arr.slice(0,MAX_LABEL_CHARS).join("")+"…", truncated:true};
}

function measureW(text,depth){
  const c=CFG[Math.min(depth,CFG.length-1)];
  // 按【截断后】的显示文字计算宽度，保证省略后的节点宽度一致、不溢出
  const shown=truncLabel(text).text;
  let w=0; for(const ch of shown) w+=charW(ch,c.fs);
  return Math.max(c.minW, Math.min(c.maxW, w+c.px*2));
}

// 节点显示文字：超过 20 字符省略。返回 {text, truncated}
function displayLabel(node){
  return truncLabel(node.label||node.central||"");
}

function annotate(node, depth, branchColor){
  node._id=node._id||"n"+(++_nid); node._depth=depth;
  if(node._collapsed===undefined) node._collapsed=false;
  node._pinned=node._pinned||false;
  if(node._px===undefined) node._px=null;
  if(node._py===undefined) node._py=null;
  // 宽高始终按文字与层级自适应，不保留手动拉伸的旧尺寸
  node._w=measureW(node.label||node.central||"",depth);
  node._h=CFG[Math.min(depth,CFG.length-1)].h;
  // 缓存所属分支的主题色，O(1) 查色，避免 nodeColor 每帧递归
  if(depth===0) node._branchColor=null;
  else if(depth===1) node._branchColor=node.color||null;
  else node._branchColor=branchColor||null;
  nodeMap[node._id]=node;
  const bc = depth===1 ? (node.color||null) : branchColor||null;
  (node.children||[]).forEach(ch=>annotate(ch,depth+1,bc));
  (node.branches||[]).forEach(b=>annotate(b,1,null));
}

function visKids(node){return node._collapsed?[]:(node.children||[]);}

function newId(){_nid++;let id="n"+_nid;while(nodeMap[id]){_nid++;id="n"+_nid;}return id;}

/* ══ 拖拽改挂 (re-parent) 辅助 ═══════════════════════════════════════════ */
// 返回 node 的父节点（沿 TREE 递归查找），根节点返回 null
function findParent(targetId, node, parent){
  node=node||TREE; parent=parent||null;
  if(node._id===targetId) return parent;
  const kids=(node.branches||[]).concat(node.children||[]);
  for(const k of kids){ const r=findParent(targetId,k,node); if(r!==undefined) return r; }
  return undefined;
}
// dropId 是否是 dragId 自身或其后代（用于禁止把节点挂到自己子树里，避免成环）
function isSelfOrDescendant(dragNode, dropId){
  if(dragNode._id===dropId) return true;
  const kids=(dragNode.branches||[]).concat(dragNode.children||[]);
  return kids.some(k=>isSelfOrDescendant(k,dropId));
}
// 从原父节点的 branches/children 中移除 dragNode
function detachNode(dragNode){
  const parent=findParent(dragNode._id);
  if(parent===undefined||parent===null) return null; // 根节点不可脱离
  for(const key of ["branches","children"]){
    const arr=parent[key]; if(!arr) continue;
    const i=arr.findIndex(c=>c._id===dragNode._id);
    if(i>=0){ arr.splice(i,1); return parent; }
  }
  return null;
}
// 把 dragNode 挂到 newParent 下（根用 branches，其它用 children）
function attachNode(dragNode, newParent){
  const key = newParent._depth===0 ? "branches" : "children";
  if(!newParent[key]) newParent[key]=[];
  newParent[key].push(dragNode);
  newParent._collapsed=false;         // 自动展开，确保挂上的节点可见
}


let pos={};
let currentLayout=0;  // 0=左右均衡 1=辐射 2=向右树 3=垂直树 4=力导向

/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 0 — 左右均衡树（默认）
   分支均分左右，每侧垂直树形，S曲线+直角折线
══════════════════════════════════════════════════════════════════════════ */
function subtreeH(node){
  const vg=V_GAP[Math.min(node._depth,V_GAP.length-1)];
  const kids=visKids(node); if(!kids.length) return node._h;
  return Math.max(node._h,kids.reduce((s,k)=>s+subtreeH(k),0)+vg*(kids.length-1));
}

function layoutSubtree(node,cx,cy,side){
  pos[node._id]={x:cx,y:cy,parentId:pos[node._id]?.parentId,side};
  const kids=visKids(node); if(!kids.length) return;
  const vg=V_GAP[Math.min(node._depth+1,V_GAP.length-1)];
  const hg=H_GAP[Math.min(node._depth+1,H_GAP.length-1)];
  const maxCW=Math.max(...kids.map(k=>k._w));
  const childCX=cx+side*(node._w/2+hg+maxCW/2);
  const heights=kids.map(k=>subtreeH(k));
  const totalH=heights.reduce((a,b)=>a+b,0)+vg*(kids.length-1);
  let curY=cy-totalH/2;
  kids.forEach((kid,i)=>{
    const kcy=curY+heights[i]/2;
    pos[kid._id]={x:childCX,y:kcy,parentId:node._id,side};
    layoutSubtree(kid,childCX,kcy,side);
    curY+=heights[i]+vg;
  });
}

function layout0(tree){
  pos={};
  pos[tree._id]={x:0,y:0,parentId:null,side:0};
  const branches=tree.branches||[]; if(!branches.length) return;
  const nRight=Math.ceil(branches.length/2);
  function placeSide(brs,side){
    if(!brs.length) return;
    const maxBW=Math.max(...brs.map(b=>b._w));
    const branchCX=side*(tree._w/2+H_GAP[1]+maxBW/2);
    const heights=brs.map(b=>subtreeH(b));
    const totalH=heights.reduce((a,b)=>a+b,0)+V_GAP[1]*(brs.length-1);
    let curY=-totalH/2;
    brs.forEach((b,i)=>{
      const bcy=curY+heights[i]/2;
      pos[b._id]={x:branchCX,y:bcy,parentId:tree._id,side:side};
      layoutSubtree(b,branchCX,bcy,side);
      curY+=heights[i]+V_GAP[1];
    });
  }
  placeSide(branches.slice(0,nRight),1);
  placeSide(branches.slice(nRight),-1);
}

// 计算以 (x0,y0) 为中心、尺寸 w×h 的矩形边缘上，朝 (tx,ty) 方向的交点。
// 用于让所有布局的连线都从节点【边缘】而非中心发出，风格统一。
function rectEdgePoint(x0,y0,w,h,tx,ty){
  const dx=tx-x0, dy=ty-y0;
  if(dx===0&&dy===0) return {x:x0+w/2, y:y0};
  const hw=w/2, hh=h/2;
  // 与矩形四边求交，取最近的缩放系数
  const sx = dx!==0 ? hw/Math.abs(dx) : Infinity;
  const sy = dy!==0 ? hh/Math.abs(dy) : Infinity;
  const s = Math.min(sx,sy);
  return {x:x0+dx*s, y:y0+dy*s};
}

function edgePath0(px,py,pw,cx,cy,cw,depth,side,ph){
  /* 左右均衡布局：所有子节点连线都从父节点侧边的【同一点】（垂直中心）出发，
     汇聚到一点后再分别平滑弯向各子节点。曲线张力随水平间距自适应，出入口
     保持水平切线，避免生硬折角。                                          */
  const dx = cx - px;
  const s  = dx >= 0 ? 1 : -1;

  const x1 = px + s * pw/2;             // 父节点出口 x（侧边）
  const x2 = cx - s * cw/2;             // 子节点入口 x（侧边）
  const y1 = py;                         // 出口 y 固定为父节点中心 → 所有分支同一点出发

  if(Math.abs(cy - y1) < 2) return `M${x1.toFixed(1)},${y1.toFixed(1)} L${x2.toFixed(1)},${cy.toFixed(1)}`;

  const span = Math.abs(x2 - x1) || 1;
  const t = depth === 1 ? 0.55 : 0.48;
  const cp1x = x1 + s * span * t;
  const cp2x = x2 - s * span * t;
  return `M${x1.toFixed(1)},${y1.toFixed(1)} C${cp1x.toFixed(1)},${y1.toFixed(1)} ${cp2x.toFixed(1)},${cy.toFixed(1)} ${x2.toFixed(1)},${cy.toFixed(1)}`;
}

function edgePath1(px,py,pw,ph,cx,cy,cw,ch,depth){
  /* 辐射布局：从父节点边缘朝子节点方向出线、到子节点边缘，沿径向平滑贝塞尔 */
  const a=rectEdgePoint(px,py,pw,ph||30,cx,cy);   // 父边缘出口（朝子节点）
  const b=rectEdgePoint(cx,cy,cw,ch||26,px,py);   // 子边缘入口（朝父节点）
  const t = depth === 1 ? 0.5 : 0.42;
  const cp1x=a.x+(b.x-a.x)*t, cp2x=b.x-(b.x-a.x)*t;
  return `M${a.x.toFixed(1)},${a.y.toFixed(1)} C${cp1x.toFixed(1)},${a.y.toFixed(1)} ${cp2x.toFixed(1)},${b.y.toFixed(1)} ${b.x.toFixed(1)},${b.y.toFixed(1)}`;
}

function edgePath2(px,py,pw,cx,cy,cw,depth,ph){
  /* 树形（向右）：所有子节点连线从父节点右边【同一点】（中心）出发，
     转角用贝塞尔圆滑。                                                */
  const x1 = px + pw/2;
  const x2 = cx - cw/2;
  const y1 = py;                         // 出口 y 固定为父中心 → 同一点出发

  if(Math.abs(cy - y1) < 2) return `M${x1.toFixed(1)},${y1.toFixed(1)} L${x2.toFixed(1)},${cy.toFixed(1)}`;

  const span = Math.abs(x2 - x1) || 1;
  const t = 0.5;
  const cp1x = x1 + span * t;
  const cp2x = x2 - span * t;
  return `M${x1.toFixed(1)},${y1.toFixed(1)} C${cp1x.toFixed(1)},${y1.toFixed(1)} ${cp2x.toFixed(1)},${cy.toFixed(1)} ${x2.toFixed(1)},${cy.toFixed(1)}`;
}

function edgePath3(px,py,pw,ph,cx,cy,cw,ch,depth){
  /* 垂直树：从父节点下（或上）边缘出、到子节点上（或下）边缘入，垂直 S 曲线 */
  const sy = cy>=py ? 1 : -1;
  const y1 = py + sy*(ph||30)/2;      // 父上/下边缘
  const y2 = cy - sy*(ch||26)/2;      // 子下/上边缘
  if(Math.abs(cx - px) < 3) return `M${px.toFixed(1)},${y1.toFixed(1)} L${cx.toFixed(1)},${y2.toFixed(1)}`;
  const my = (y1 + y2) / 2;
  return `M${px.toFixed(1)},${y1.toFixed(1)} C${px.toFixed(1)},${my.toFixed(1)} ${cx.toFixed(1)},${my.toFixed(1)} ${cx.toFixed(1)},${y2.toFixed(1)}`;
}

function edgePath4(px,py,pw,ph,cx,cy,cw,ch){
  /* 力导向：从节点边缘出线的平滑弧线                          */
  const a=rectEdgePoint(px,py,pw||30,ph||30,cx,cy);
  const b=rectEdgePoint(cx,cy,cw||26,ch||26,px,py);
  const mx = (a.x+b.x)/2, my = (a.y+b.y)/2;
  const dx = b.x-a.x, dy = b.y-a.y, len = Math.sqrt(dx*dx+dy*dy)||1;
  const perp = Math.min(len*0.12, 24);
  const nx = -dy/len*perp, ny = dx/len*perp;
  return `M${a.x.toFixed(1)},${a.y.toFixed(1)} Q${(mx+nx).toFixed(1)},${(my+ny).toFixed(1)} ${b.x.toFixed(1)},${b.y.toFixed(1)}`;
}


function drawSpine3(){
  // 垂直树不需要装饰线，清除旧环形圈
  document.querySelectorAll(".circ-ring").forEach(e => e.remove());
  document.getElementById("fishbone-spine")?.remove();
}

/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 1 — 全辐射（圆形散射）
══════════════════════════════════════════════════════════════════════════ */
function layout1(tree){
  pos={};
  pos[tree._id]={x:0,y:0,parentId:null,side:1};
  const branches=tree.branches||[]; if(!branches.length) return;

  function leafCount(node){
    const kids=visKids(node);
    return kids.length?kids.reduce((s,k)=>s+leafCount(k),0):1;
  }
  const totalLeaves=branches.reduce((s,b)=>s+leafCount(b),0);
  const R1=Math.max(180, tree._w/2+120);
  const R2=120;

  let angle=-Math.PI/2;
  branches.forEach(branch=>{
    const frac=leafCount(branch)/totalLeaves;
    const span=frac*Math.PI*2;
    const mid=angle+span/2;
    angle+=span;
    const side=Math.cos(mid)>=0?1:-1;
    const bx=Math.cos(mid)*R1, by=Math.sin(mid)*R1;
    pos[branch._id]={x:bx,y:by,parentId:tree._id,side,angle:mid};
    const kids=visKids(branch);
    if(!kids.length) return;
    const fanSpan=Math.min(span*.8, Math.PI*.6);
    const fanStart=mid-fanSpan/2;
    kids.forEach((kid,i)=>{
      const ka=fanStart+(fanSpan*i)/(Math.max(kids.length-1,1))||mid;
      const kR=R1+R2+kid._w/2;
      const kx=Math.cos(ka)*kR, ky=Math.sin(ka)*kR;
      pos[kid._id]={x:kx,y:ky,parentId:branch._id,side:Math.cos(ka)>=0?1:-1,angle:ka};
      const gkids=visKids(kid);
      if(!gkids.length) return;
      const gFan=Math.min(fanSpan/(kids.length||1)*.9, Math.PI*.3);
      gkids.forEach((gk,j)=>{
        const ga=ka+(j-(gkids.length-1)/2)*gFan/(Math.max(gkids.length-1,1)||1);
        const gR=kR+R2*.7+gk._w/2;
        pos[gk._id]={x:Math.cos(ga)*gR,y:Math.sin(ga)*gR,parentId:kid._id,side:Math.cos(ga)>=0?1:-1,angle:ga};
      });
    });
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 2 — 向右树（Org Chart）
══════════════════════════════════════════════════════════════════════════ */
function subtreeH2(node){
  const vg=Math.max(V_GAP[Math.min(node._depth,V_GAP.length-1)],14);
  const kids=visKids(node); if(!kids.length) return node._h;
  return Math.max(node._h,kids.reduce((s,k)=>s+subtreeH2(k),0)+vg*(kids.length-1));
}
function layoutSubtree2(node,lx,cy){
  const kids=visKids(node); if(!kids.length) return;
  const hg=H_GAP[Math.min(node._depth+1,H_GAP.length-1)]+8;
  const vg=Math.max(V_GAP[Math.min(node._depth+1,V_GAP.length-1)],14);
  const maxCW=Math.max(...kids.map(k=>k._w));
  const childLX=lx+node._w+hg;
  const childCX=childLX+maxCW/2;
  const heights=kids.map(k=>subtreeH2(k));
  const totalH=heights.reduce((a,b)=>a+b,0)+vg*(kids.length-1);
  let curY=cy-totalH/2;
  kids.forEach((kid,i)=>{
    const kcy=curY+heights[i]/2;
    pos[kid._id]={x:childCX,y:kcy,parentId:node._id,side:1};
    layoutSubtree2(kid,childLX,kcy);
    curY+=heights[i]+vg;
  });
}
function layout2(tree){
  pos={};
  pos[tree._id]={x:0,y:0,parentId:null,side:1};
  const branches=tree.branches||[]; if(!branches.length) return;
  const hg=H_GAP[1]+8;
  const vg=Math.max(V_GAP[1],14);
  const maxBW=Math.max(...branches.map(b=>b._w));
  const branchLX=tree._w/2+hg;
  const branchCX=branchLX+maxBW/2;
  const heights=branches.map(b=>subtreeH2(b));
  const totalH=heights.reduce((a,b)=>a+b,0)+vg*(branches.length-1);
  let curY=-totalH/2;
  branches.forEach((b,i)=>{
    const bcy=curY+heights[i]/2;
    pos[b._id]={x:branchCX,y:bcy,parentId:tree._id,side:1};
    layoutSubtree2(b,branchLX,bcy);
    curY+=heights[i]+vg;
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 3 — 垂直树（Vertical Tree / Top-Down）
══════════════════════════════════════════════════════════════════════════ */
function subtreeW3(node){
  const hg=20;
  const kids=visKids(node);
  if(!kids.length) return node._w;
  const childrenW=kids.reduce((s,k)=>s+subtreeW3(k),0)+hg*(kids.length-1);
  return Math.max(node._w,childrenW);
}
function placeSubtree3(node,cx,top,parentId){
  const cy=top+node._h/2;
  pos[node._id]={x:cx,y:cy,parentId,side:1};
  const kids=visKids(node); if(!kids.length) return;
  const V_STEP=80, H_GAP_3=20;
  const childTop=top+node._h+V_STEP;
  const widths=kids.map(k=>subtreeW3(k));
  const totalW=widths.reduce((a,b)=>a+b,0)+H_GAP_3*(kids.length-1);
  let curX=cx-totalW/2;
  kids.forEach((kid,i)=>{
    const kidCX=curX+widths[i]/2;
    placeSubtree3(kid,kidCX,childTop,node._id);
    curX+=widths[i]+H_GAP_3;
  });
}
function layout3(tree){
  pos={};
  const branches=tree.branches||[];
  pos[tree._id]={x:0,y:0,parentId:null,side:1};
  if(!branches.length) return;
  const V_STEP=80, H_GAP_3=20;
  const top1=tree._h/2+V_STEP;
  const widths=branches.map(b=>subtreeW3(b));
  const totalW=widths.reduce((a,b)=>a+b,0)+H_GAP_3*(branches.length-1);
  let curX=-totalW/2;
  branches.forEach((branch,i)=>{
    const bx=curX+widths[i]/2;
    placeSubtree3(branch,bx,top1,tree._id);
    curX+=widths[i]+H_GAP_3;
  });
}


/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 4 — 力导向（Force-Directed）
   · Coulomb 斥力 + Hooke 弹簧 + Verlet 积分
   · 根节点固定在中心，其余节点自由浮动
   · 120 帧动画后定格
══════════════════════════════════════════════════════════════════════════ */
let _fdRunning = false;
let _fdTimer   = null;

function layout4(tree){
  stopFD();

  // ── 1. 收集所有节点（全树，不管 collapsed）────────────────────────────
  const all = [];
  ;(function walk(node){
    all.push(node);
    (node._depth===0 ? (node.branches||[]) : visKids(node)).forEach(walk);
  })(tree);

  // ── 2. 从树结构建边（不依赖 pos，避免 stale 问题）─────────────────────
  const edges = [];
  ;(function walkE(node){
    const kids = node._depth===0 ? (node.branches||[]) : visKids(node);
    kids.forEach(kid=>{ edges.push([node._id, kid._id]); walkE(kid); });
  })(tree);

  // ── 3. 先用 layout0 给一个合理初始骨架，再叠加力导向 ─────────────────
  layout0(tree);

  // ── 4. 给 pos 里没有的节点（collapsed）补一个随机初始位置 ───────────────
  const seed = () => (Math.random()-0.5)*80;
  all.forEach(node=>{
    if(!pos[node._id]){
      // 找父节点位置作为起点
      const parentId = (node._depth===0) ? null
        : edges.find(([a,b])=>b===node._id)?.[0] ?? null;
      const pp = parentId ? pos[parentId] : null;
      pos[node._id] = {
        x: (pp ? pp.x : 0) + seed(),
        y: (pp ? pp.y : 0) + seed(),
        parentId, side:1, vx:0, vy:0
      };
    } else {
      pos[node._id].vx = 0;
      pos[node._id].vy = 0;
    }
  });

  // ── 5. 力导向迭代 ────────────────────────────────────────────────────
  const K_REPEL  = 30000;
  const K_SPRING = 0.09;
  const DAMPING  = 0.80;
  const MAX_V    = 55;
  const FRAMES   = 130;
  function idealLen(depthA, depthB){ return 150 + Math.max(depthA,depthB)*35; }

  let frame = 0;

  function tick(){
    if(!_fdRunning || currentLayout!==4){ _fdRunning=false; return; }
    frame++;
    const cool = Math.max(0.04, 1 - frame/FRAMES);

    const fx={}, fy={};
    all.forEach(n=>{ fx[n._id]=0; fy[n._id]=0; });

    // Coulomb 斥力（所有节点对）
    for(let i=0;i<all.length;i++){
      const a=all[i], pa=pos[a._id];
      if(!pa) continue;
      for(let j=i+1;j<all.length;j++){
        const b=all[j], pb=pos[b._id];
        if(!pb) continue;
        let dx=pb.x-pa.x, dy=pb.y-pa.y;
        const dist2=dx*dx+dy*dy||0.01;
        const dist=Math.sqrt(dist2);
        // 额外排斥：节点尺寸内强推
        const minD=(a._w+b._w)*0.5+24;
        const f=K_REPEL/dist2*cool;
        const push=dist<minD?(minD-dist)*1.2:0;
        const ux=dx/dist, uy=dy/dist;
        fx[a._id]-=(f+push)*ux; fy[a._id]-=(f+push)*uy;
        fx[b._id]+=(f+push)*ux; fy[b._id]+=(f+push)*uy;
      }
    }

    // Hooke 弹簧引力（有边的节点对）
    edges.forEach(([aid,bid])=>{
      const pa=pos[aid], pb=pos[bid];
      if(!pa||!pb) return;
      const dx=pb.x-pa.x, dy=pb.y-pa.y;
      const dist=Math.sqrt(dx*dx+dy*dy)||0.01;
      const na=nodeMap[aid]||{_depth:0}, nb=nodeMap[bid]||{_depth:1};
      const target=idealLen(na._depth, nb._depth);
      const stretch=(dist-target)*K_SPRING*cool;
      const ux=dx/dist, uy=dy/dist;
      if(aid!==tree._id){ fx[aid]+=stretch*ux; fy[aid]+=stretch*uy; }
      fx[bid]-=stretch*ux; fy[bid]-=stretch*uy;
    });

    // 弱中心引力（防止整体漂移）
    all.forEach(node=>{
      if(node._id===tree._id) return;
      const p=pos[node._id]; if(!p) return;
      fx[node._id]-=p.x*0.006*cool;
      fy[node._id]-=p.y*0.006*cool;
    });

    // 更新速度和位置
    all.forEach(node=>{
      if(node._id===tree._id) return;
      const p=pos[node._id]; if(!p) return;
      p.vx=(p.vx+fx[node._id])*DAMPING;
      p.vy=(p.vy+fy[node._id])*DAMPING;
      const spd=Math.sqrt(p.vx*p.vx+p.vy*p.vy)||1;
      if(spd>MAX_V){ p.vx=p.vx/spd*MAX_V; p.vy=p.vy/spd*MAX_V; }
      p.x+=p.vx; p.y+=p.vy;
      p.side=p.x>=0?1:-1;
    });

    renderAll(tree);

    if(frame<FRAMES){
      _fdTimer=requestAnimationFrame(tick);
    } else {
      _fdRunning=false;
    }
  }

  _fdRunning=true;
  frame=0;
  _fdTimer=requestAnimationFrame(tick);
}

function stopFD(){
  _fdRunning = false;
  if(_fdTimer){ cancelAnimationFrame(_fdTimer); _fdTimer=null; }
}

function edgePath4(px,py,pw,ph,cx,cy,cw,ch){
  // 力导向：从节点边缘出线的平滑曲线
  const a=rectEdgePoint(px,py,pw||30,ph||30,cx,cy);
  const b=rectEdgePoint(cx,cy,cw||26,ch||26,px,py);
  const mx=(a.x+b.x)/2, my=(a.y+b.y)/2;
  const dx=b.x-a.x, dy=b.y-a.y, len=Math.sqrt(dx*dx+dy*dy)||1;
  // 控制点：垂直于连线方向偏移，形成弧线
  const perp = Math.min(len*0.15, 30);
  const nx=-dy/len*perp, ny=dx/len*perp;
  return `M${a.x.toFixed(1)},${a.y.toFixed(1)} Q${(mx+nx).toFixed(1)},${(my+ny).toFixed(1)} ${b.x.toFixed(1)},${b.y.toFixed(1)}`;
}

function drawSpine3(){
  document.querySelectorAll(".circ-ring,.fd-ring").forEach(e=>e.remove());
  document.getElementById("fishbone-spine")?.remove();
  document.getElementById("timeline-axis")?.remove();
}

/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 5 — 时间线（Timeline / 水平流程）
   · 中心节点在最左侧
   · 主分支从左到右等间距水平排列
   · 子节点垂直向下展开
   · 主分支之间有水平时间轴主干线
══════════════════════════════════════════════════════════════════════════ */
function subtreeH5(node){
  const vg=12;
  const kids=visKids(node); if(!kids.length) return node._h;
  return node._h + 60 + kids.reduce((s,k)=>s+k._h+vg,0) - vg;
}
function layout5(tree){
  pos={};
  const branches=tree.branches||[];
  // root at far left
  pos[tree._id]={x:0, y:0, parentId:null, side:1};
  if(!branches.length) return;

  const H_STEP = 220;  // horizontal distance between branch columns
  const V_TOP  = 90;   // vertical distance from timeline axis to first child

  // Place branches horizontally
  branches.forEach((b,i)=>{
    const bx = tree._w/2 + H_STEP * (i+1);
    pos[b._id]={x:bx, y:0, parentId:tree._id, side:1};

    // Children stacked vertically below
    const kids=visKids(b); if(!kids.length) return;
    let curY = V_TOP;
    kids.forEach(kid=>{
      pos[kid._id]={x:bx, y:curY, parentId:b._id, side:1};
      // Grandchildren further right
      const gkids=visKids(kid); if(!gkids.length){ curY+=kid._h+12; return; }
      let gy=curY;
      gkids.forEach(gk=>{
        pos[gk._id]={x:bx+kid._w/2+80+gk._w/2, y:gy, parentId:kid._id, side:1};
        gy+=gk._h+8;
      });
      curY=Math.max(curY+kid._h+12, gy);
    });
  });
}

function edgePath5(px,py,pw,ph,cx,cy,cw,ch,depth){
  ph=ph||30; ch=ch||26;
  if(depth===1){
    // Timeline axis: horizontal straight line, from node side edges
    const x1=px+pw/2, x2=cx-cw/2;
    return `M${x1.toFixed(1)},${py.toFixed(1)} L${x2.toFixed(1)},${cy.toFixed(1)}`;
  }
  // Branch to children: 垂直方向从父下边缘出、到子上边缘入
  if(Math.abs(cx-px)<3){
    const sy = cy>=py ? 1 : -1;
    const y1=py+sy*ph/2, y2=cy-sy*ch/2;
    return `M${px.toFixed(1)},${y1.toFixed(1)} L${cx.toFixed(1)},${y2.toFixed(1)}`;
  }
  // 横向（孙节点）：从侧边缘出/入
  const x1=px+pw/2, x2=cx-cw/2;
  const mid=(x1+x2)/2;
  if(Math.abs(cy-py)<3) return `M${x1.toFixed(1)},${py.toFixed(1)} L${x2.toFixed(1)},${cy.toFixed(1)}`;
  return `M${x1.toFixed(1)},${py.toFixed(1)} C${mid.toFixed(1)},${py.toFixed(1)} ${mid.toFixed(1)},${cy.toFixed(1)} ${x2.toFixed(1)},${cy.toFixed(1)}`;
}

/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 6 — 鱼骨图（Fishbone / Ishikawa）
   · 中心节点（鱼头）在右侧
   · 水平主干（鱼脊）从右向左延伸
   · 主分支交替从上下两侧 45° 斜向伸出（鱼骨）
   · 子节点沿鱼骨方向排列
══════════════════════════════════════════════════════════════════════════ */
function layout6(tree){
  pos={};
  const branches=tree.branches||[];
  // Fish head (root) on the right
  pos[tree._id]={x:0, y:0, parentId:null, side:1};
  if(!branches.length) return;

  const SPINE_STEP = 180;   // distance between bones along spine
  const BONE_LEN   = 130;   // length of each bone (diagonal)
  const SUB_GAP    = 36;    // gap between sub-nodes along bone
  const ANGLE      = Math.PI * 0.38; // ~68° from horizontal

  branches.forEach((b,i)=>{
    const spineX = -(tree._w/2 + 80 + SPINE_STEP * i);
    const upDown = (i % 2 === 0) ? -1 : 1;  // alternate up/down
    const bx = spineX - Math.cos(ANGLE) * BONE_LEN;
    const by = upDown * Math.sin(ANGLE) * BONE_LEN;
    pos[b._id]={x:bx, y:by, parentId:tree._id, side:-1, _spineX:spineX};

    // Children along the bone direction
    const kids=visKids(b); if(!kids.length) return;
    const dx = Math.cos(ANGLE) * SUB_GAP * upDown * 0;
    const dirX = -Math.cos(ANGLE);
    const dirY = upDown * Math.sin(ANGLE);
    kids.forEach((kid,j)=>{
      const dist = SUB_GAP * (j+1) + kid._w/2;
      const kx = bx + dirX * dist * 0.3;
      const ky = by + dirY * dist;
      pos[kid._id]={x:kx, y:ky, parentId:b._id, side:-1};

      // Grandchildren
      const gkids=visKids(kid); if(!gkids.length) return;
      gkids.forEach((gk,gi)=>{
        pos[gk._id]={
          x: kx - gk._w/2 - kid._w/2 - 30,
          y: ky + (gi - (gkids.length-1)/2) * (gk._h + 6),
          parentId:kid._id, side:-1
        };
      });
    });
  });
}

function edgePath6(px,py,pw,ph,cx,cy,cw,ch,depth,nid){
  ph=ph||30; ch=ch||26;
  if(depth===1){
    // 主骨：从鱼骨脊柱附着点，连到分支节点【边缘】（朝脊柱方向）
    const spineX = pos[nid]?._spineX;
    const sx = (spineX!==undefined) ? spineX : px;
    const b=rectEdgePoint(cx,cy,cw,ch,sx,py);
    return `M${sx.toFixed(1)},${py.toFixed(1)} L${b.x.toFixed(1)},${b.y.toFixed(1)}`;
  }
  // 子骨：父边缘 → 子边缘
  const a=rectEdgePoint(px,py,pw,ph,cx,cy);
  const b=rectEdgePoint(cx,cy,cw,ch,px,py);
  return `M${a.x.toFixed(1)},${a.y.toFixed(1)} L${b.x.toFixed(1)},${b.y.toFixed(1)}`;
}

/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT 7 — 括弧图（Brace Map / 层级分解）
   · 中心节点在最左侧
   · 父节点与子节点之间绘制 SVG 大括号 "}"
   · 大括号的尖端对准父节点右侧，两端包裹所有子节点
   · 强调 整体 → { 部分1, 部分2, ... } 的分解关系
══════════════════════════════════════════════════════════════════════════ */
function subtreeH7(node){
  const vg=16;
  const kids=visKids(node); if(!kids.length) return node._h;
  return Math.max(node._h, kids.reduce((s,k)=>s+subtreeH7(k),0)+vg*(kids.length-1));
}
function layout7(tree){
  pos={};
  pos[tree._id]={x:0, y:0, parentId:null, side:1};
  const branches=tree.branches||[]; if(!branches.length) return;

  const BRACE_W = 40;   // width of the brace symbol area
  const H_GAP_7 = 36;   // gap between parent right edge and brace
  const H_GAP_C = 20;   // gap between brace and children left edge

  function placeChildren(node, nodeRightX, cy){
    const kids=visKids(node); if(!kids.length) return;
    const vg=16;
    const maxCW = Math.max(...kids.map(k=>k._w));
    const childLX = nodeRightX + H_GAP_7 + BRACE_W + H_GAP_C;
    const childCX = childLX + maxCW/2;
    const heights = kids.map(k=>subtreeH7(k));
    const totalH = heights.reduce((a,b)=>a+b,0) + vg*(kids.length-1);
    let curY = cy - totalH/2;
    kids.forEach((kid,i)=>{
      const kcy = curY + heights[i]/2;
      pos[kid._id]={x:childCX, y:kcy, parentId:node._id, side:1};
      placeChildren(kid, childLX + maxCW/2, kcy);
      curY += heights[i] + vg;
    });
  }

  const maxBW = Math.max(...branches.map(b=>b._w));
  const branchLX = tree._w/2 + H_GAP_7 + BRACE_W + H_GAP_C;
  const branchCX = branchLX + maxBW/2;
  const heights = branches.map(b=>subtreeH7(b));
  const totalH = heights.reduce((a,b)=>a+b,0) + 16*(branches.length-1);
  let curY = -totalH/2;
  branches.forEach((b,i)=>{
    const bcy = curY + heights[i]/2;
    pos[b._id]={x:branchCX, y:bcy, parentId:tree._id, side:1};
    placeChildren(b, branchLX + maxBW/2, bcy);
    curY += heights[i] + 16;
  });
}

function edgePath7(px,py,pw,cx,cy,cw,depth){
  /*  Brace Map edge: smooth cubic Bezier with a visible "step" shape.
      Unlike tree layout's S-curve (which goes directly from parent to child),
      the brace path goes:  parent → horizontal exit → step down/up → horizontal enter → child
      This creates the visual "}" bracket grouping effect.
      Uses only C (cubic bezier) commands — no Q or L — for clean anti-aliased rendering.
  */
  const x1 = px + pw/2;       // parent right edge
  const x2 = cx - cw/2;       // child left edge
  const midX = x1 + (x2 - x1) * 0.42;  // vertical transit x

  // Same height → simple S-curve
  if(Math.abs(cy - py) < 4){
    const cp = x1 + (x2 - x1) * 0.5;
    return `M${x1},${py} C${cp},${py} ${cp},${cy} ${x2},${cy}`;
  }

  // Two-segment cubic bezier: parent→midpoint, midpoint→child
  // Segment 1: horizontal exit from parent, curve down/up to midX
  // Segment 2: from midX, curve horizontally into child
  return `M${x1},${py} C${midX},${py} ${midX},${py} ${midX},${(py+cy)/2} `
       + `C${midX},${cy} ${midX},${cy} ${x2},${cy}`;
}


/* ══════════════════════════════════════════════════════════════════════════
   LAYOUT DISPATCHER
══════════════════════════════════════════════════════════════════════════ */
function layout(tree){
  if(currentLayout===4){ layout4(tree); return; }
  stopFD();
  if(currentLayout===0) layout0(tree);
  else if(currentLayout===1) layout1(tree);
  else if(currentLayout===2) layout2(tree);
  else if(currentLayout===3) layout3(tree);
  else if(currentLayout===5) layout5(tree);
  else if(currentLayout===6) layout6(tree);
  else if(currentLayout===7) layout7(tree);
  _placeOrphans(tree);   // 兜底：确保每个可见节点都有位置（修复部分布局的固定深度限制）
}

/* 通用补位：有些布局（辐射/时间线/鱼骨）只硬编码了前几层，
   深层节点或切换布局后新增的节点会缺少 pos 记录而“消失”。
   这里递归遍历整棵可见树，为任何缺失 pos 的节点在其父节点附近补一个位置，
   使所有布局都能完整显示、并与其它布局保持同步。 */
function _placeOrphans(tree){
  function walk(node){
    const kids = node._depth===0 ? (node.branches||[]) : visKids(node);
    const pp = pos[node._id];
    // 同层已存在的兄弟，用来做垂直堆叠避免重叠
    let stackY = pp ? pp.y : 0;
    kids.forEach((kid,i)=>{
      if(!pos[kid._id] && pp){
        // 沿父节点所在侧水平偏移，纵向按序错开
        const side = pp.side || 1;
        const dx = (node._w/2 + kid._w/2 + 60) * side;
        pos[kid._id] = {
          x: pp.x + dx,
          y: pp.y + (i - (kids.length-1)/2) * (kid._h + 16),
          parentId: node._id,
          side: side
        };
      }
      walk(kid);
    });
  }
  walk(tree);
}

function edgePath(px,py,pw,cx,cy,cw,depth,side,nid,ph,ch){
  if(currentLayout===0) return edgePath0(px,py,pw,cx,cy,cw,depth,side,ph);
  if(currentLayout===1) return edgePath1(px,py,pw,ph,cx,cy,cw,ch,depth);
  if(currentLayout===2) return edgePath2(px,py,pw,cx,cy,cw,depth,ph);
  if(currentLayout===3) return edgePath3(px,py,pw,ph,cx,cy,cw,ch,depth);
  if(currentLayout===4) return edgePath4(px,py,pw,ph,cx,cy,cw,ch);
  if(currentLayout===5) return edgePath5(px,py,pw,ph,cx,cy,cw,ch,depth);
  if(currentLayout===6) return edgePath6(px,py,pw,ph,cx,cy,cw,ch,depth,nid);
  if(currentLayout===7) return edgePath7(px,py,pw,cx,cy,cw,depth);
  return edgePath0(px,py,pw,cx,cy,cw,depth,side,ph);
}

function switchLayout(n){
  stopFD();
  currentLayout=n;
  Object.values(nodeMap).forEach(node=>{node._pinned=false;node._px=null;node._py=null;});
  for(let i=0;i<8;i++){
    const btn=document.getElementById("layout-btn-"+i);
    if(btn) btn.classList.toggle("active",i===n);
  }
  rebuild();
  resetView();
}


function nodeColor(node){
  if(node.color) return node.color;
  // 使用 annotate 时缓存的分支颜色，O(1) 查找
  if(node._branchColor) return node._branchColor;
  return "#888";
}

function el(tag,attrs){
  const e=document.createElementNS(SVG_NS,tag);
  if(attrs) for(const[k,v]of Object.entries(attrs)) e.setAttribute(k,v);
  return e;
}

let edgeEls={}, nodeEls={};

function renderAll(tree){
  document.getElementById("nodes-g").innerHTML="";
  document.getElementById("edges-g").innerHTML="";
  edgeEls={}; nodeEls={};
  const all=[],q=[tree];
  while(q.length){const n=q.shift();all.push(n);(n._depth===0?(n.branches||[]):visKids(n)).forEach(c=>q.push(c));}
  const eg=document.getElementById("edges-g");
  all.forEach(node=>{
    const p=pos[node._id]; if(!p||p.parentId==null) return;
    const pp=pos[p.parentId]; if(!pp) return;
    const pNode=nodeMap[p.parentId]||tree, color=nodeColor(node), depth=node._depth, side=p.side||1;
    // 线宽和透明度随深度自然收细，产生视觉层次感
    const sw = depth===1 ? 2.2 : depth===2 ? 1.5 : 1.1;
    const so = depth===1 ? 0.80 : depth===2 ? 0.55 : 0.38;
    const path=el("path",{class:"edge",stroke:color,
      "stroke-width":sw,
      "stroke-opacity":so,
      "stroke-linecap":"round","stroke-linejoin":"round","data-nid":node._id});
    path.setAttribute("d",edgePath(pp.x,pp.y,pNode._w,p.x,p.y,node._w,depth,side,node._id,pNode._h,node._h));
    if(pNode._collapsed) path.style.display="none";
    eg.appendChild(path); edgeEls[node._id]=path;
  });
  const ng=document.getElementById("nodes-g");
  all.forEach(node=>renderNode(node,ng));
  drawDecorations();
  applyTransform();
}

// 绘制布局专属装饰线：鱼骨的主脊、时间线的时间轴；其它布局清除
function drawDecorations(){
  const eg=document.getElementById("edges-g");
  // 清除旧装饰
  eg.querySelectorAll(".decor-line").forEach(e=>e.remove());
  if(currentLayout===6){
    // 鱼骨主脊：从鱼头(根节点)左边缘水平延伸到最左侧鱼骨的附着点
    const root=TREE, rp=pos[root._id]; if(!rp) return;
    const branches=(root.branches||[]);
    let minSpineX=rp.x - root._w/2;
    branches.forEach(b=>{ const sx=pos[b._id]?._spineX; if(sx!==undefined) minSpineX=Math.min(minSpineX,sx); });
    const x1=rp.x - root._w/2;           // 鱼头左边缘
    const x2=minSpineX - 40;             // 稍微超出最后一根鱼骨，形成鱼尾
    const spine=el("path",{class:"edge decor-line",
      d:`M${x1.toFixed(1)},${rp.y.toFixed(1)} L${x2.toFixed(1)},${rp.y.toFixed(1)}`,
      stroke:"var(--fg)","stroke-width":3,"stroke-opacity":0.55,
      "stroke-linecap":"round",fill:"none"});
    eg.insertBefore(spine, eg.firstChild);   // 放最底层，鱼骨压在其上
  } else if(currentLayout===5){
    // 时间线主轴：贯穿所有主分支的水平线
    const root=TREE, rp=pos[root._id]; if(!rp) return;
    const branches=(root.branches||[]);
    if(!branches.length) return;
    let maxX=rp.x;
    branches.forEach(b=>{ const p=pos[b._id]; if(p) maxX=Math.max(maxX,p.x+ (nodeMap[b._id]._w)/2); });
    const x1=rp.x + root._w/2;
    const axis=el("path",{class:"edge decor-line",
      d:`M${x1.toFixed(1)},${rp.y.toFixed(1)} L${(maxX+20).toFixed(1)},${rp.y.toFixed(1)}`,
      stroke:"var(--fg)","stroke-width":2.5,"stroke-opacity":0.45,
      "stroke-linecap":"round",fill:"none"});
    eg.insertBefore(axis, eg.firstChild);
  }
}

function refreshEdgesFor(id){
  const p=pos[id]; if(!p) return;
  const node=nodeMap[id]||TREE, path=edgeEls[id];
  // 更新到父节点的边
  if(path&&p.parentId!=null){
    const pp=pos[p.parentId],pN=nodeMap[p.parentId]||TREE;
    if(pp) path.setAttribute("d",edgePath(pp.x,pp.y,pN._w,p.x,p.y,node._w,node._depth,p.side||1,id,pN._h,node._h));
  }
  // 只更新直接子节点的边（不再深度递归），用 visKids 跳过折叠子树
  const kids=node._depth===0?(node.branches||[]):visKids(node);
  kids.forEach(kid=>{
    const cp=pos[kid._id],cp2=edgeEls[kid._id];
    if(cp&&cp2) cp2.setAttribute("d",edgePath(p.x,p.y,node._w,cp.x,cp.y,kid._w,kid._depth,cp.side||1,kid._id,node._h,kid._h));
    // 继续向下更新（子节点位置没变，但父位置变了，所以子节点的边起点也变了）
    refreshEdgesFor(kid._id);
  });
}

function renderNode(node,g){
  const p=pos[node._id]; if(!p) return;
  const depth=node._depth, c=CFG[Math.min(depth,CFG.length-1)];
  const w=node._w, h=node._h, color=nodeColor(node);
  const label=node.label||node.central||"";
  const kids=node.children||node.branches||[];
  const grp=el("g",{class:"nd"+(node._id===selectedId?" selected":""),"data-id":node._id,
    transform:`translate(${p.x-w/2},${p.y-h/2})`});
  // selection ring
  grp.appendChild(el("rect",{class:"sel-ring",x:-3,y:-3,width:w+6,height:h+6,
    rx:c.rx+3,fill:"none",stroke:"#7c8cf8","stroke-width":"2","stroke-dasharray":"5 3",opacity:.8}));
  // bg
  const bg=el("rect",{class:"bg",width:w,height:h,rx:c.rx,ry:c.rx});
  if(depth===0){bg.setAttribute("fill","url(#root-grad)");bg.setAttribute("filter","url(#glow)");}
  else if(depth===1){bg.setAttribute("fill",color+"30");bg.setAttribute("stroke",color);bg.setAttribute("stroke-width","2");}
  else if(depth===2){bg.setAttribute("fill",color+"18");bg.setAttribute("stroke",color+"bb");bg.setAttribute("stroke-width","1.5");}
  else{bg.setAttribute("fill",color+"0e");bg.setAttribute("stroke",color+"77");bg.setAttribute("stroke-width","1");}
  // label（超长自动省略，完整内容点击节点查看）
  const tc=THEMES[CUR_THEME].nodeText[Math.min(depth,3)];
  const disp=displayLabel(node);
  const txt=el("text",{x:w/2,y:h/2,"dominant-baseline":"central","text-anchor":"middle",
    "font-size":c.fs,"font-weight":c.fw,fill:tc,style:"pointer-events:none;user-select:none;"});
  txt.textContent=disp.text;
  if(disp.truncated){
    grp.classList.add("truncated");
    const tnative=el("title"); tnative.textContent=label; grp.appendChild(tnative); // 悬停原生提示
  }
  grp.appendChild(bg); grp.appendChild(txt);
  // collapse toggle
  if(kids.length&&depth>0){
    const bx=w-9,by=h-9;
    const tg=el("g",{class:"tog","data-id":node._id});
    const tc2=el("circle",{cx:bx,cy:by,r:8,fill:color+"33",stroke:color,"stroke-width":"1.2"});
    const tt=el("text",{x:bx,y:by,"dominant-baseline":"central","text-anchor":"middle",
      "font-size":"11","font-weight":"700",fill:color,style:"pointer-events:none;user-select:none;"});
    tt.textContent=node._collapsed?"+":" −";
    tg.appendChild(tc2); tg.appendChild(tt);
    tg.addEventListener("mousedown",e=>e.stopPropagation());
    tg.addEventListener("click",e=>{e.stopPropagation();toggle(node._id);});
    grp.appendChild(tg);
  }
  grp.addEventListener("mousedown",e=>{
    if(e.target.closest(".tog")) return;
    e.stopPropagation();
    if(e.button!==0){ selectNode(node._id); return; }  // 右键仅选中，交给 contextmenu
    // 双击检测：短时间内在同一节点的第二次按下，视为进入编辑，
    // 不启动拖拽、也不在 mouseup 时触发折叠（否则父节点的双击会被折叠"吃掉"）
    const now=Date.now();
    if(_lastDown.id===node._id && now-_lastDown.t<400){
      _dblGuard=true;               // 让本次 mouseup 跳过默认处理
      _lastDown={id:null,t:0};
      selectNode(node._id);
      startEdit(node._id);
      return;
    }
    _lastDown={id:node._id,t:now};
    selectNode(node._id);
    // 拖动根节点 = 平移整张思维导图（而不是只移动根节点）
    if(node._depth===0){
      activeOp={type:"canvas",sx:e.clientX-T.x,sy:e.clientY-T.y};
      wrap.style.cursor="grabbing";
      return;
    }
    startNodeDrag(e,node);
  });
  grp.addEventListener("dblclick",e=>{
    e.stopPropagation();
    if(editingId!==node._id) startEdit(node._id);   // mousedown 未触发时兜底
  });
  grp.addEventListener("contextmenu",e=>{
    e.preventDefault(); e.stopPropagation(); selectNode(node._id); openCtxMenu(e.clientX,e.clientY,node._id);
  });
  g.appendChild(grp); nodeEls[node._id]=grp;
}

function patchNodeEl(node){
  const grp=nodeEls[node._id]; if(!grp) return;
  const p=pos[node._id]; if(!p) return;
  const w=node._w,h=node._h;
  grp.setAttribute("transform",`translate(${p.x-w/2},${p.y-h/2})`);
  const bg=grp.querySelector(".bg");if(bg){bg.setAttribute("width",w);bg.setAttribute("height",h);}
  const t=grp.querySelector("text[dominant-baseline]");
  if(t){t.setAttribute("x",w/2);t.setAttribute("y",h/2);
    const disp=displayLabel(node); t.textContent=disp.text;
    grp.classList.toggle("truncated",disp.truncated);
    let ti=grp.querySelector("title");
    if(disp.truncated){ if(!ti){ti=el("title");grp.appendChild(ti);} ti.textContent=node.label||node.central||""; }
    else if(ti){ ti.remove(); }
  }
  const sr=grp.querySelector(".sel-ring");if(sr){sr.setAttribute("width",w+6);sr.setAttribute("height",h+6);}
  const tg=grp.querySelector(".tog");
  if(tg){const bc=tg.querySelector("circle"),bt=tg.querySelector("text");
    if(bc){bc.setAttribute("cx",w-9);bc.setAttribute("cy",h-9);}
    if(bt){bt.setAttribute("x",w-9);bt.setAttribute("y",h-9);}}
}

/* ══ SELECTION ══ */
function _hideDetail(){ const d=document.getElementById("detail-pop"); if(d) d.style.display="none"; }
function _showDetailFor(id){
  const d=document.getElementById("detail-pop"); if(!d) return;
  const node=nodeMap[id]||(TREE._id===id?TREE:null); const p=pos[id];
  if(!node||!p){ _hideDetail(); return; }
  // 仅当内容被省略时才弹出完整内容
  if(!displayLabel(node).truncated){ _hideDetail(); return; }
  const full=node.label||node.central||"";
  d.innerHTML="";
  d.appendChild(document.createTextNode(full));
  const hint=el2("span","dp-hint","双击可编辑 · 点击空白关闭");
  d.appendChild(hint);
  d.style.display="block";
  // 定位在节点下方，超出视口则翻到上方/夹紧
  const nx=T.x+p.x*T.s, ny=T.y+p.y*T.s, hh=node._h*T.s;
  const wrapRect=document.getElementById("wrap").getBoundingClientRect();
  d.style.left="0px"; d.style.top="0px";               // 先复位以取真实尺寸
  const dw=d.offsetWidth, dh=d.offsetHeight;
  let left=nx-dw/2, top=ny+hh/2+8;
  left=Math.max(6, Math.min(left, wrapRect.width-dw-6));
  if(top+dh>wrapRect.height-6) top=ny-hh/2-dh-8;       // 下方放不下则放上方
  d.style.left=left+"px"; d.style.top=Math.max(6,top)+"px";
}
function el2(tag,cls,text){ const e=document.createElement(tag); if(cls)e.className=cls; if(text!=null)e.textContent=text; return e; }

function selectNode(id){
  if(selectedId&&nodeEls[selectedId]) nodeEls[selectedId].classList.remove("selected");
  selectedId=id;
  if(id&&nodeEls[id]) nodeEls[id].classList.add("selected");
  _hideDetail();
}

/* ══ CONTEXT MENU ══ */
function buildColorDots(){
  const cont=document.getElementById("ctx-colors"); cont.innerHTML="";
  const curNode=nodeMap[ctxTargetId];
  const curColor=curNode?.color||null;
  PALETTE.forEach(c=>{
    const d=document.createElement("div");
    d.className="color-dot"+(c===curColor?" active":"");
    d.style.background=c; d.title=c;
    d.onclick=()=>ctxAction("color",c); cont.appendChild(d);
  });
  const r=document.createElement("div");
  r.className="color-dot"+(curColor===null?" active":"");
  r.style.background="var(--hover-bg)";
  r.style.cssText+=";font-size:11px;display:flex;align-items:center;justify-content:center;";
  r.title="自动颜色";r.textContent="↺";r.onclick=()=>ctxAction("color",null);
  cont.appendChild(r);
}

function openCtxMenu(x,y,id){
  ctxTargetId=id; buildColorDots();
  // Update color label to show what will be changed
  const lbl=document.getElementById("ctx-color-label");
  if(lbl){
    const n=nodeMap[id];
    const depth=n?n._depth:0;
    if(depth===0)      lbl.textContent="更改根节点颜色";
    else if(depth===1) lbl.textContent="更改分支颜色（影响子节点默认色）";
    else               lbl.textContent="更改此节点颜色";
  }
  const menu=document.getElementById("ctx-menu"); menu.classList.add("open");
  menu.style.left=x+"px"; menu.style.top=y+"px";
  requestAnimationFrame(()=>{
    const r=menu.getBoundingClientRect();
    if(r.right>window.innerWidth)  menu.style.left=(x-r.width)+"px";
    if(r.bottom>window.innerHeight) menu.style.top=(y-r.height)+"px";
  });
}

function closeCtxMenu(){document.getElementById("ctx-menu").classList.remove("open");ctxTargetId=null;}

function ctxAction(action,extra){
  // Save target id BEFORE closeCtxMenu() nulls ctxTargetId
  const targetId=ctxTargetId;
  closeCtxMenu();
  const node=nodeMap[targetId]; if(!node&&action!=="delete") return;

  if(action==="edit"){
    setTimeout(()=>startEdit(targetId),0);
    return;
  }

  if(action==="add-child"){
    snapshotForUndo();
    const d=Math.min(node._depth+1,CFG.length-1);
    const nn={_id:newId(),label:"新节点",children:[],_depth:d,_collapsed:false,_pinned:false,_px:null,_py:null};
    nn._w=measureW("新节点",d); nn._h=CFG[d].h; nodeMap[nn._id]=nn;
    node._collapsed=false;  // 自动展开，确保新节点可见
    // Root node uses .branches, all others use .children
    if(node._depth===0){
      if(!node.branches) node.branches=[];
      node.branches.push(nn);
    } else {
      if(!node.children) node.children=[];
      node.children.push(nn);
    }
    rebuild();
    setTimeout(()=>{selectNode(nn._id);startEdit(nn._id);}, 60);
    return;
  }

  if(action==="add-sibling"){
    snapshotForUndo();
    const p=pos[targetId]; if(!p||!p.parentId){showToast("根节点无法添加兄弟节点");return;}
    const parent=nodeMap[p.parentId]||TREE;
    const arr=parent._depth===0?(parent.branches||[]):(parent.children||[]);
    const idx=arr.findIndex(c=>c._id===targetId);
    const d=node._depth;
    const nn={_id:newId(),label:"新节点",children:[],_depth:d,_collapsed:false,_pinned:false,_px:null,_py:null};
    nn._w=measureW("新节点",d); nn._h=CFG[Math.min(d,CFG.length-1)].h; nodeMap[nn._id]=nn;
    arr.splice(idx+1,0,nn); rebuild();
    setTimeout(()=>{selectNode(nn._id);startEdit(nn._id);}, 60);
    return;
  }

  if(action==="delete"){
    if(!node){return;} if(node._depth===0){showToast("不能删除根节点");return;}
    snapshotForUndo();
    const p=pos[targetId]; if(!p||!p.parentId) return;
    const parent=nodeMap[p.parentId]||TREE;
    const arr=parent._depth===0?(parent.branches||[]):(parent.children||[]);
    const idx=arr.findIndex(c=>c._id===targetId);
    if(idx>=0) arr.splice(idx,1);
    function rm(n){delete nodeMap[n._id];(n.children||[]).forEach(rm);}
    rm(node);
    if(selectedId===targetId) selectNode(null);
    rebuild(); return;
  }

  if(action==="color"){
    snapshotForUndo();
    // Set color on the exact node clicked — no walk-up to branch root
    if(extra===null) delete node.color; else node.color=extra;
    rebuild(); return;
  }
}

// Use mousedown (not click) to close menu so it doesn't race with menu item onclick
document.addEventListener("mousedown",e=>{
  const menu=document.getElementById("ctx-menu");
  if(menu.classList.contains("open")&&!menu.contains(e.target)) closeCtxMenu();
});
document.addEventListener("contextmenu",e=>{
  if(["wrap","svg","edges-g","nodes-g"].includes(e.target.id)||(e.target.tagName==="svg")||(e.target.parentElement&&e.target.parentElement.id==="edges-g"))
    e.preventDefault();
});

/* ══ UNDO / REDO ══════════════════════════════════════════════════════════
   操作前调用 snapshotForUndo()，将当前树结构序列化压入撤销栈。
   Ctrl+Z 弹出并恢复，Ctrl+Y/Ctrl+Shift+Z 重做。
════════════════════════════════════════════════════════════════════════ */
function _treeSnapshot(){
  // 序列化当前树（含颜色、折叠状态、位置）
  function snap(node){
    const out={label:node.label,central:node.central,color:node.color,
      _collapsed:node._collapsed,_pinned:node._pinned,_px:node._px,_py:node._py,
      _w:node._w,_h:node._h};
    if((node.children||[]).length)  out.children=(node.children||[]).map(snap);
    if((node.branches||[]).length)  out.branches=(node.branches||[]).map(snap);
    return out;
  }
  return JSON.stringify(snap(TREE));
}

function _restoreSnapshot(json){
  const saved=JSON.parse(json);
  function restore(live,saved){
    live.label=saved.label; live.central=saved.central;
    if(saved.color) live.color=saved.color; else delete live.color;
    live._collapsed=saved._collapsed||false;
    live._pinned=saved._pinned||false;
    live._px=saved._px??null; live._py=saved._py??null;
    live._w=saved._w||null; live._h=saved._h||null;
    // Rebuild children array from saved data
    if(saved.children){
      live.children=(saved.children).map(sc=>{
        const n={label:sc.label||"",children:[],branches:[]};
        restore(n,sc); return n;
      });
    } else { live.children=[]; }
    if(saved.branches){
      live.branches=(saved.branches).map(sb=>{
        const n={label:sb.label||"",children:[],branches:[]};
        restore(n,sb); return n;
      });
    }
  }
  restore(TREE,saved);
  // 清理所有可能持有旧节点引用的状态，防止 stale reference crash
  activeOp   = null;
  wrap.style.cursor = "";
  selectNode(null);
  ctxTargetId = null;
  _pushScheduled = false;
  // 关键修复：_nid 重置为 0 后，必须清除 TREE._id，否则 TREE 保留旧 _id（如 "n1"），
  // 而 annotate 从 n1 开始分配，导致第一个分支也拿到 "n1"，产生 ID 碰撞，
  // nodeMap["n1"] 被分支覆盖，TREE 从 nodeMap 消失，渲染完全混乱。
  delete TREE._id;
  _nid=0; nodeMap={};
  annotate(TREE,0,null);
  rebuild();
}

function snapshotForUndo(){
  _undoStack.push(_treeSnapshot());
  if(_undoStack.length>MAX_UNDO) _undoStack.shift();
  _redoStack=[];  // new action clears redo
  autosaveNow();  // 有绑定文件时，改动实时写回 HTML
}

function undo(){
  if(!_undoStack.length){ showToast("没有可撤销的操作",1600); return; }
  _redoStack.push(_treeSnapshot());
  _restoreSnapshot(_undoStack.pop());
  showToast("↩ 已撤销",1400);
  autosaveNow();
}

function redo(){
  if(!_redoStack.length){ showToast("没有可重做的操作",1600); return; }
  _undoStack.push(_treeSnapshot());
  _restoreSnapshot(_redoStack.pop());
  showToast("↪ 已重做",1400);
  autosaveNow();
}

/* ══ KEYBOARD ══ */
document.addEventListener("keydown",e=>{
  if(editingId!=null||e.target.id==="label-editor") return;
  // Enter：在选中节点上创建兄弟节点（根节点无兄弟，退化为创建子节点）
  if(e.key==="Enter"&&selectedId){
    e.preventDefault();
    const n=nodeMap[selectedId]||(TREE._id===selectedId?TREE:null);
    ctxTargetId=selectedId;
    ctxAction((n&&n._depth===0)?"add-child":"add-sibling");
    return;
  }
  // F2：编辑选中节点文字
  if(e.key==="F2"&&selectedId){e.preventDefault();startEdit(selectedId);return;}
  // Undo / Redo
  if((e.ctrlKey||e.metaKey)&&!e.shiftKey&&e.key==="z"){e.preventDefault();undo();return;}
  if((e.ctrlKey||e.metaKey)&&(e.key==="y"||(e.shiftKey&&e.key==="z"))){e.preventDefault();redo();return;}
  if((e.key==="Delete"||e.key==="Backspace")&&selectedId){
    e.preventDefault();
    ctxTargetId=selectedId; ctxAction("delete"); return;
  }
  if(e.key==="Tab"&&selectedId){
    e.preventDefault();
    ctxTargetId=selectedId; ctxAction("add-child"); return;
  }
  if(e.key==="Escape"){selectNode(null);closeCtxMenu();}
});

/* ══ DRAG REPULSION ══════════════════════════════════════════════════════
   链式传播算法：
   1. 以被拖动节点为压力源，计算每个节点到压力源的距离
   2. 按距离从近到远排序，依次推开——近的节点先让位，压力向外传播
   3. 推开时近压力源的节点固定（已被推过），只推远端节点
   4. 多轮迭代直到全局无重叠，避免振荡
════════════════════════════════════════════════════════════════════════ */
const DRAG_PAD = 10;
const MAX_ITER = 15;

function pushAway(draggedId){
  const allIds = Object.keys(pos);
  if(allIds.length < 2) return;

  // 预计算半尺寸
  const hw = {}, hh = {};
  allIds.forEach(id => {
    const n = nodeMap[id] || TREE;
    hw[id] = n._w/2 + DRAG_PAD/2;
    hh[id] = n._h/2 + DRAG_PAD/2;
  });

  const dp = pos[draggedId];

  for(let iter = 0; iter < MAX_ITER; iter++){
    let anyOverlap = false;

    // 按到拖动节点的距离从近到远排序，让压力从内向外传播
    const sorted = allIds.slice().sort((a, b) => {
      const pa = pos[a], pb = pos[b];
      const da = (pa.x-dp.x)**2 + (pa.y-dp.y)**2;
      const db = (pb.x-dp.x)**2 + (pb.y-dp.y)**2;
      return da - db;
    });

    for(let i = 0; i < sorted.length; i++){
      for(let j = i+1; j < sorted.length; j++){
        const ai = sorted[i], aj = sorted[j];  // ai 比 aj 更靠近拖动节点
        const pi = pos[ai], pj = pos[aj];
        if(!pi || !pj) continue;

        const dx = pj.x - pi.x;
        const dy = pj.y - pi.y;
        const overlapX = (hw[ai] + hw[aj]) - Math.abs(dx);
        const overlapY = (hh[ai] + hh[aj]) - Math.abs(dy);

        if(overlapX <= 0 || overlapY <= 0) continue;
        anyOverlap = true;

        // 关键：ai 更靠近压力源（已被处理过），固定 ai 只推 aj
        // 压力单向向外传播，不会产生振荡
        if(overlapX <= overlapY){
          pj.x += overlapX * (dx >= 0 ? 1 : -1);
        } else {
          pj.y += overlapY * (dy >= 0 ? 1 : -1);
        }
      }
    }

    if(!anyOverlap) break;
  }

  // 同步视觉、side 和 pinned 坐标
  allIds.forEach(id => {
    const p = pos[id]; if(!p) return;
    const n = nodeMap[id] || TREE;
    // 更新 side：始终以父节点为参照
    const parentP = p.parentId ? pos[p.parentId] : null;
    if(parentP) p.side = p.x >= parentP.x ? 1 : -1;
    // 注意：不在分离/推挤过程中回写 pinned 坐标，否则手动位置会被逐帧挤走
    patchNodeEl(n);
    refreshEdgesFor(id);
  });
}
/* ══ GLOBAL SEPARATION ═══════════════════════════════════════════════════
   布局完成后对所有节点做一次全局分离，确保不重叠。
   与 pushAway 的区别：没有固定压力源，每对重叠节点各自向外移动一半，
   适合初始布局、切换布局、添加/删除节点后的全局整理。
════════════════════════════════════════════════════════════════════════ */
function separateAll(){
  const allIds = Object.keys(pos);
  if(allIds.length < 2) return;

  const hw = {}, hh = {};
  allIds.forEach(id => {
    const n = nodeMap[id] || TREE;
    hw[id] = n._w/2 + DRAG_PAD/2;
    hh[id] = n._h/2 + DRAG_PAD/2;
  });

  // 预处理：给完全重合的节点施加微小扰动，防止对称死锁
  for(let i = 0; i < allIds.length; i++){
    for(let j = i+1; j < allIds.length; j++){
      const pi = pos[allIds[i]], pj = pos[allIds[j]];
      if(!pi||!pj) continue;
      if(Math.abs(pi.x-pj.x)<0.1 && Math.abs(pi.y-pj.y)<0.1){
        // 按索引差给一个确定性的角度扰动，避免随机性
        const angle = (j - i) * 2.399;  // 黄金角，均匀分布
        pj.x += Math.cos(angle) * 0.5;
        pj.y += Math.sin(angle) * 0.5;
      }
    }
  }

  const SEP_ITER = allIds.length * 4;  // 实测：n*4 覆盖 99% 的实际场景，50节点以内 <10ms

  for(let iter = 0; iter < SEP_ITER; iter++){
    let anyOverlap = false;

    for(let i = 0; i < allIds.length; i++){
      for(let j = i+1; j < allIds.length; j++){
        const ai = allIds[i], aj = allIds[j];
        const pi = pos[ai], pj = pos[aj];
        if(!pi || !pj) continue;

        const dx = pj.x - pi.x;
        const dy = pj.y - pi.y;
        const overlapX = (hw[ai] + hw[aj]) - Math.abs(dx);
        const overlapY = (hh[ai] + hh[aj]) - Math.abs(dy);
        if(overlapX <= 0 || overlapY <= 0) continue;
        anyOverlap = true;

        const fixI = (nodeMap[ai]||TREE)._depth === 0;
        const fixJ = (nodeMap[aj]||TREE)._depth === 0;
        if(overlapX <= overlapY){
          const push = overlapX * (dx >= 0 ? 1 : -1);
          if(!fixI && !fixJ){ pi.x -= push*0.5; pj.x += push*0.5; }
          else if(fixI) pj.x += push;
          else          pi.x -= push;
        } else {
          const push = overlapY * (dy >= 0 ? 1 : -1);
          if(!fixI && !fixJ){ pi.y -= push*0.5; pj.y += push*0.5; }
          else if(fixI) pj.y += push;
          else          pi.y -= push;
        }
      }
    }
    if(!anyOverlap) break;
  }

  // 同步 side / pinned 坐标
  allIds.forEach(id => {
    const p = pos[id]; if(!p) return;
    const n = nodeMap[id] || TREE;
    const parentP = p.parentId ? pos[p.parentId] : null;
    if(parentP) p.side = p.x >= parentP.x ? 1 : -1;
    // 注意：不在分离/推挤过程中回写 pinned 坐标，否则手动位置会被逐帧挤走
  });
}


/* ══ INTERACTION ══ */
let activeOp=null, T={x:0,y:0,s:1};
let _dropTarget=null;   // 拖拽改挂时当前悬停的新父节点候选
function _setDropTarget(id){
  if(_dropTarget===id) return;
  if(_dropTarget && nodeEls[_dropTarget]) nodeEls[_dropTarget].classList.remove("drop-target");
  _dropTarget=id;
  if(_dropTarget && nodeEls[_dropTarget]) nodeEls[_dropTarget].classList.add("drop-target");
}
function applyTransform(){
  if(typeof editingId!=="undefined"&&editingId!=null) finishEdit(true);
  const t=`translate(${T.x},${T.y}) scale(${T.s})`;
  document.getElementById("edges-g").setAttribute("transform",t);
  document.getElementById("nodes-g").setAttribute("transform",t);
  _hideDetail();
}
function svgXY(cx,cy){
  const r=document.getElementById("wrap").getBoundingClientRect();
  return{x:(cx-r.left-T.x)/T.s,y:(cy-r.top-T.y)/T.s};
}
function startNodeDrag(e,node){const sv=svgXY(e.clientX,e.clientY);activeOp={type:"nodedrag",node,ox:sv.x-pos[node._id].x,oy:sv.y-pos[node._id].y,moved:false};const g=nodeEls[node._id];if(g)g.style.pointerEvents="none";}

window.addEventListener("mousemove",e=>{
  if(!activeOp) return;
  if(activeOp.type==="canvas"){T.x=e.clientX-activeOp.sx;T.y=e.clientY-activeOp.sy;applyTransform();return;}
  if(activeOp.type==="nodedrag"){
    const sv=svgXY(e.clientX,e.clientY);
    if(!activeOp.moved&&Math.hypot(sv.x-pos[activeOp.node._id].x-activeOp.ox,sv.y-pos[activeOp.node._id].y-activeOp.oy)<2) return;
    activeOp.moved=true;
    const node=activeOp.node;
    node._pinned=true; node._px=sv.x-activeOp.ox; node._py=sv.y-activeOp.oy;
    pos[node._id].x=node._px; pos[node._id].y=node._py;
    // 实时更新 side：节点在父节点哪侧由实际坐标决定
    const _pp=pos[pos[node._id].parentId]; if(_pp) pos[node._id].side=pos[node._id].x>=_pp.x?1:-1;
    patchNodeEl(node); refreshEdgesFor(node._id);
    // 拖拽改挂：找出鼠标下方（或最近）的合法新父节点候选并高亮。
    // 注意：拖拽期间不做 pushAway，以免把落点目标挤走导致无法命中。
    // 策略：优先命中光标落在其框内的节点；若没有，则取容差范围内最近的合法节点，
    //       让改挂更容易触发（不必精确落在小节点上）。
    const curParent=findParent(node._id);
    const TOL=28;                 // 容差：光标离节点边缘 28px 内也算命中
    let inside=null, nearest=null, nearestD=Infinity;
    for(const id in pos){
      if(id===node._id) continue;
      const tp=pos[id], tn=nodeMap[id]||TREE; if(!tp) continue;
      // 跳过非法候选：自身/后代（成环）或当前父节点（无意义）
      if(isSelfOrDescendant(node,id)) continue;
      if(curParent && curParent._id===id) continue;
      const hw=tn._w/2, hh=tn._h/2;
      const dx=Math.max(Math.abs(sv.x-tp.x)-hw, 0);
      const dy=Math.max(Math.abs(sv.y-tp.y)-hh, 0);
      if(dx===0 && dy===0){ inside=id; break; }   // 光标在框内，直接选它
      const d=Math.hypot(dx,dy);
      if(d<nearestD){ nearestD=d; nearest=id; }
    }
    const validDrop = inside || (nearestD<=TOL ? nearest : null);
    _setDropTarget(validDrop);
    return;
  }
});
window.addEventListener("mouseup",e=>{
  if(!activeOp) return;
  if(activeOp.type==="nodedrag"){
    const _g=nodeEls[activeOp.node._id]; if(_g) _g.style.pointerEvents="";
    if(_dblGuard){ _dblGuard=false; }
    else if(activeOp.moved){
      const dragNode=activeOp.node;
      const dropId=_dropTarget;
      _setDropTarget(null);
      if(dropId && nodeMap[dropId] && !isSelfOrDescendant(dragNode,dropId)){
        // 拖拽改挂：从原父节点脱离，挂到目标节点下成为其子节点
        snapshotForUndo();
        const newParent=nodeMap[dropId];
        if(detachNode(dragNode)){
          attachNode(dragNode, newParent);
          // 改挂是结构性变化：清除【整棵树】所有节点的手动固定坐标，
          // 让整张图按布局算法重新整齐排布，避免“被移动子树整齐、周围旧手动位置错乱”的混合状态。
          delete TREE._id; _nid=0; nodeMap={}; annotate(TREE,0,null); // 重算 depth/颜色/id
          Object.values(nodeMap).forEach(n=>{ n._pinned=false; n._px=null; n._py=null; });
          TREE._pinned=false; TREE._px=null; TREE._py=null;
          rebuild();
          selectNode(dragNode._id);
          showToast("已挂到「"+(newParent.label||newParent.central||"目标节点")+"」下");
        }
      } else {
        // 非改挂的自由拖动：按落点在兄弟节点中重新排序，然后清除所有手动坐标、
        // 重新整齐布局。这样拖动只改变【顺序】，不会把节点钉在乱位、拉乱连线。
        reorderByDropPosition(dragNode);
        Object.values(nodeMap).forEach(n=>{ n._pinned=false; n._px=null; n._py=null; });
        TREE._pinned=false; TREE._px=null; TREE._py=null;
        snapshotForUndo();
        rebuild();
        selectNode(dragNode._id);
      }
    }
    // 单击节点体只选中，不折叠（折叠请用节点右下角的 −/+ 按钮），避免与双击编辑冲突
  }
  activeOp=null; wrap.style.cursor="";
});
const wrap=document.getElementById("wrap");
wrap.addEventListener("mousedown",e=>{
  if(activeOp) return;
  if(e.target===e.currentTarget||e.target.tagName==="svg"||["edges-g","nodes-g"].includes(e.target.id))
    {selectNode(null);closeCtxMenu();}
  if(e.button!==0) return;
  activeOp={type:"canvas",sx:e.clientX-T.x,sy:e.clientY-T.y}; wrap.style.cursor="grabbing";
});
wrap.addEventListener("wheel",e=>{
  e.preventDefault();
  const r=wrap.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
  const f=e.deltaY<0?1.11:0.9, ns=Math.min(Math.max(T.s*f,0.1),6);
  T.x=mx-(ns/T.s)*(mx-T.x); T.y=my-(ns/T.s)*(my-T.y); T.s=ns; applyTransform();
},{passive:false});
let tDrag=null;
wrap.addEventListener("touchstart",e=>{if(e.touches.length===1)tDrag={sx:e.touches[0].clientX-T.x,sy:e.touches[0].clientY-T.y};},{passive:true});
wrap.addEventListener("touchmove",e=>{if(tDrag&&e.touches.length===1){T.x=e.touches[0].clientX-tDrag.sx;T.y=e.touches[0].clientY-tDrag.sy;applyTransform();}},{passive:true});
wrap.addEventListener("touchend",()=>tDrag=null);

/* ══ COLLAPSE ══ */
function toggle(id){const n=nodeMap[id];if(!n)return;n._collapsed=!n._collapsed;rebuild();}
function expandAll(){Object.values(nodeMap).forEach(n=>n._collapsed=false);rebuild();}
function collapseAll(){Object.values(nodeMap).forEach(n=>{if(n._depth>=1)n._collapsed=true;});rebuild();}
// 拖放后按落点在兄弟节点中重新排序：横向布局按 Y 排、纵向布局按 X 排。
// 只改变节点在父节点 children/branches 数组中的顺序，不改父子关系。
function reorderByDropPosition(dragNode){
  const parent=findParent(dragNode._id);
  if(parent===undefined||parent===null) return;      // 根节点无兄弟
  const key = (parent.branches && parent.branches.some(c=>c._id===dragNode._id)) ? "branches" : "children";
  const arr=parent[key]; if(!arr||arr.length<2) return;
  // 判定排序轴：看同组兄弟当前坐标是横向铺开还是纵向铺开
  let minx=Infinity,maxx=-Infinity,miny=Infinity,maxy=-Infinity;
  arr.forEach(c=>{ const p=pos[c._id]; if(!p)return;
    minx=Math.min(minx,p.x);maxx=Math.max(maxx,p.x);
    miny=Math.min(miny,p.y);maxy=Math.max(maxy,p.y); });
  const horizontalStack = (maxy-miny) >= (maxx-minx);   // 兄弟主要沿 Y 排列 → 按 Y 排序
  const dp=pos[dragNode._id];
  const keyOf = horizontalStack ? (c=>pos[c._id]?pos[c._id].y:0) : (c=>pos[c._id]?pos[c._id].x:0);
  const dragKey = horizontalStack ? dp.y : dp.x;
  // 取出被拖节点，按坐标插回合适位置
  const others=arr.filter(c=>c._id!==dragNode._id);
  let idx=others.findIndex(c=>keyOf(c)>dragKey);
  if(idx<0) idx=others.length;
  others.splice(idx,0,dragNode);
  parent[key]=others;
}

function _applyPins(){
  // 把手动拖拽固定的坐标重新套回布局结果，使拖动位置在重排后保持
  Object.values(nodeMap).forEach(n=>{
    if(n._pinned && n._px!=null && n._py!=null && pos[n._id]){
      pos[n._id].x=n._px; pos[n._id].y=n._py;
    }
  });
}
function rebuild(){
  layout(TREE);
  _applyPins();    // 分离前套用手动坐标，让分离尽量尊重手动位置
  separateAll();   // 布局后全局分离，确保不重叠
  _applyPins();    // 分离后再套用一次，手动坐标为最终权威（避免被分离缓慢挤走）
  renderAll(TREE);
}

/* ══ INLINE LABEL EDIT ═══════════════════════════════════════════════════
   双击节点 / 选中后按 F2 或 Enter / 右键菜单「编辑文字」进入编辑；
   添加子节点、兄弟节点后自动进入编辑。
   Enter 或失焦提交，Esc 取消。提交后重测节点宽度并重新布局。
════════════════════════════════════════════════════════════════════════ */
let editingId=null;
function startEdit(id){
  finishEdit(true);
  _hideDetail();
  const node=nodeMap[id]||(TREE._id===id?TREE:null); if(!node) return;
  const p=pos[id]; if(!p) return;
  editingId=id;
  const inp=document.getElementById("label-editor");
  const c=CFG[Math.min(node._depth,CFG.length-1)];
  // 编辑框宽度：至少 220px（缩放后），方便编辑长内容；超过节点宽度时以节点中心为轴展开
  const w=Math.max(node._w*T.s, 220), h=Math.max(node._h*T.s,26);
  inp.style.left=(T.x+p.x*T.s-w/2)+"px";
  inp.style.top =(T.y+p.y*T.s-h/2)+"px";
  inp.style.width=w+"px"; inp.style.height=h+"px";
  inp.style.fontSize=Math.max(c.fs*T.s,10)+"px";
  inp.style.fontWeight=c.fw;
  inp.value=node.label||node.central||"";
  inp.style.display="block";
  inp.focus(); inp.select();
}
function finishEdit(commit){
  if(editingId==null) return;
  const inp=document.getElementById("label-editor");
  const node=nodeMap[editingId]||TREE;
  const val=inp.value;                       // 不 trim，允许用户保留/清空
  const cur=node.label||node.central||"";
  const id=editingId;
  editingId=null;
  inp.style.display="none";
  // 只要内容有变化就提交（包括改短、清空）——修复“删除内容删不掉”的问题。
  // 根节点不允许清空（否则整图失去中心）；其它节点允许空标签。
  if(commit && val!==cur && !(node._depth===0 && val.trim()==="")){
    snapshotForUndo();
    node.label=val;
    if(node._depth===0) node.central=val;
    node._w=measureW(val,node._depth);
    node._h=CFG[Math.min(node._depth,CFG.length-1)].h;
    rebuild();
    setTimeout(()=>selectNode(id),30);
  }
}
(function(){
  const inp=document.getElementById("label-editor");
  inp.addEventListener("keydown",e=>{
    e.stopPropagation();
    if(e.key==="Enter"){e.preventDefault();finishEdit(true);}
    else if(e.key==="Escape"){e.preventDefault();finishEdit(false);}
  });
  inp.addEventListener("blur",()=>finishEdit(true));
  inp.addEventListener("mousedown",e=>e.stopPropagation());
})();
function resetView(){T={x:wrap.clientWidth/2,y:wrap.clientHeight/2,s:1};applyTransform();}
function zoomIn(){T.s=Math.min(T.s*1.2,6);applyTransform();}
function zoomOut(){T.s=Math.max(T.s/1.2,0.1);applyTransform();}

/* ══ TOAST ══ */
function showToast(msg,dur=2400){const t=document.getElementById("toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),dur);}


/* ══ EXPORT ══ */
function getBounds(){
  let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;
  [...Object.values(nodeMap),TREE].forEach(n=>{
    const p=pos[n._id];if(!p)return;
    x0=Math.min(x0,p.x-n._w/2);x1=Math.max(x1,p.x+n._w/2);
    y0=Math.min(y0,p.y-n._h/2);y1=Math.max(y1,p.y+n._h/2);
  });
  const pad=60; return{x0:x0-pad,y0:y0-pad,w:x1-x0+pad*2,h:y1-y0+pad*2};
}

function buildExportSVG(){
  const b=getBounds();
  const clone=document.getElementById("svg").cloneNode(true);
  clone.querySelectorAll(".rh,.rh-b,.tog,.sel-ring").forEach(e=>e.remove());
  clone.querySelectorAll(".nd").forEach(g=>g.classList.remove("selected"));
  clone.querySelectorAll("#edges-g,#nodes-g").forEach(g=>g.removeAttribute("transform"));
  clone.setAttribute("viewBox",`${b.x0} ${b.y0} ${b.w} ${b.h}`);
  clone.setAttribute("width",Math.round(b.w)); clone.setAttribute("height",Math.round(b.h));
  clone.style.cssText="";
  const bg=document.createElementNS(SVG_NS,"rect");
  bg.setAttribute("x",b.x0);bg.setAttribute("y",b.y0);bg.setAttribute("width",b.w);bg.setAttribute("height",b.h);bg.setAttribute("fill",THEMES[CUR_THEME].bg);
  clone.insertBefore(bg,clone.firstChild);
  const st=document.createElementNS(SVG_NS,"style");
  st.textContent='text{font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;}';
  clone.insertBefore(st,clone.firstChild);
  return{svgEl:clone,b};
}

function dlBlob(blob,name){
  const url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download=name;document.body.appendChild(a);a.click();
  setTimeout(()=>{document.body.removeChild(a);URL.revokeObjectURL(url);},300);
}

function exportAs(fmt){
  showToast("正在导出 "+fmt.toUpperCase()+" …");
  const{svgEl,b}=buildExportSVG();
  const svgStr=new XMLSerializer().serializeToString(svgEl);
  const safe=TITLE.replace(/[\\/:*?"<>|]/g,"_");
  if(fmt==="svg"){dlBlob(new Blob([svgStr],{type:"image/svg+xml"}),safe+".svg");return;}
  const sc=fmt==="jpg"?2:2.5;
  const canvas=document.createElement("canvas"); canvas.width=b.w*sc; canvas.height=b.h*sc;
  const ctx=canvas.getContext("2d");
  if(fmt==="jpg"){ctx.fillStyle=THEMES[CUR_THEME].bg;ctx.fillRect(0,0,canvas.width,canvas.height);}
  const img=new Image();
  const bUrl=URL.createObjectURL(new Blob([svgStr],{type:"image/svg+xml"}));
  img.onload=()=>{
    ctx.drawImage(img,0,0,canvas.width,canvas.height); URL.revokeObjectURL(bUrl);
    if(fmt==="png") canvas.toBlob(bl=>dlBlob(bl,safe+".png"),"image/png");
    else if(fmt==="jpg") canvas.toBlob(bl=>dlBlob(bl,safe+".jpg"),"image/jpeg",0.93);
    else if(fmt==="pdf") makePDF(canvas,b,safe);
  };
  img.src=bUrl;
}

function makePDF(canvas,b,safe){
  const jData=canvas.toDataURL("image/jpeg",0.92).split(",")[1];
  const jBytes=Uint8Array.from(atob(jData),c=>c.charCodeAt(0));
  const W=Math.round(b.w),H=Math.round(b.h);
  const enc=new TextEncoder();
  function str(s){return enc.encode(s);}
  const stream=`q ${W} 0 0 ${H} 0 0 cm /Im1 Do Q`;
  const objs=[str("%PDF-1.4\n"),str("1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n"),
    str(`2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n`),
    str(`3 0 obj\n<</Type/Page/Parent 2 0 R/MediaBox[0 0 ${W} ${H}]/Contents 4 0 R/Resources<</XObject<</Im1 5 0 R>>>>>>\nendobj\n`),
    str(`4 0 obj\n<</Length ${stream.length}>>\nstream\n${stream}\nendstream\nendobj\n`),
    str(`5 0 obj\n<</Type/XObject/Subtype/Image/Width ${canvas.width}/Height ${canvas.height}/ColorSpace/DeviceRGB/BitsPerComponent 8/Filter/DCTDecode/Length ${jBytes.length}>>\nstream\n`),
    jBytes,str("\nendstream\nendobj\n"),
    str("xref\n0 6\n0000000000 65535 f \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n0\n%%EOF\n")];
  const total=objs.reduce((s,o)=>s+o.length,0); const buf=new Uint8Array(total); let off=0;
  for(const o of objs){buf.set(o,off);off+=o.length;}
  dlBlob(new Blob([buf],{type:"application/pdf"}),safe+".pdf");
}

/* ══ SAVE / EXPORT FULL HTML ═════════════════════════════════════════════
   把当前编辑后的整棵树（含颜色、折叠、手动位置、尺寸）写回一份完整的、
   自包含的 HTML 文件并下载。下次打开该文件即是当前状态——实现"节点的
   改动同步到整个 HTML 文件"。浏览器无法直接覆写本地原文件，因此这里
   下载一份新的 HTML，用户保存即可替换原文件。
════════════════════════════════════════════════════════════════════════ */
function _cleanTree(){
  // 保留数据 + 视觉状态，剔除运行时 id / 父指针等易失字段
  function clean(node){
    const out={};
    if(node.central!=null) out.central=node.central;
    if(node.label!=null)   out.label=node.label;
    if(node.color)         out.color=node.color;
    if(node._collapsed)    out._collapsed=true;
    if(node._pinned){ out._pinned=true; out._px=node._px; out._py=node._py; }
    const br=(node.branches||[]).map(clean);
    const ch=(node.children||[]).map(clean);
    if(br.length) out.branches=br;
    if(ch.length) out.children=ch;
    return out;
  }
  return clean(TREE);
}

function _buildCurrentHTML(){
  // 取当前页面完整 HTML 源码，替换数据块为当前编辑状态，返回完整 HTML 字符串
  let html="<!DOCTYPE html>\n"+document.documentElement.outerHTML;
  const dataJson=JSON.stringify(_cleanTree());
  const titleJson=JSON.stringify(TITLE);
  const block=
    "/*__MINDMAP_DATA_START__*/\n"+
    "const RAW   = "+dataJson+";\n"+
    "const TITLE = "+titleJson+";\n"+
    "const INIT_THEME = "+JSON.stringify(CUR_THEME)+";\n"+
    "/*__MINDMAP_DATA_END__*/";
  const re=/\/\*__MINDMAP_DATA_START__\*\/[\s\S]*?\/\*__MINDMAP_DATA_END__\*\//;
  if(!re.test(html)) return null;
  html=html.replace(re,block.replace(/\$/g,"$$$$"));
  html=html.replace(/(<body[^>]*\sdata-theme=")[^"]*(")/,'$1'+CUR_THEME+'$2');
  return html;
}

// ── File System Access API：把改动实时写回同一个 HTML 文件 ──────────────
let _fileHandle=null;         // 已绑定的文件句柄
let _autosaveTimer=null;      // 防抖计时器
const _fsaSupported = ("showSaveFilePicker" in window);

async function bindFile(){
  if(!_fsaSupported){ showToast("当前浏览器不支持实时保存，请用 Chrome/Edge，或用下载方式",3000); return; }
  try{
    const safe=TITLE.replace(/[\\/:*?"<>|]/g,"_");
    _fileHandle=await window.showSaveFilePicker({
      suggestedName: safe+".html",
      types:[{description:"HTML",accept:{"text/html":[".html"]}}],
    });
    await _writeToHandle();          // 立即写一次
    _updateSaveBtn();
    showToast("已绑定文件，之后的改动会自动保存",2600);
  }catch(err){ if(err && err.name!=="AbortError") showToast("绑定失败："+err.message,2800); }
}

async function _writeToHandle(){
  if(!_fileHandle) return false;
  const html=_buildCurrentHTML();
  if(html==null){ showToast("保存失败：未找到数据标记",2600); return false; }
  try{
    const w=await _fileHandle.createWritable();
    await w.write(html); await w.close();
    return true;
  }catch(err){ showToast("自动保存失败："+err.message,2800); return false; }
}

// 每次改动后调用：已绑定文件则防抖后静默写回
function autosaveNow(){
  if(!_fileHandle) return;
  if(_autosaveTimer) clearTimeout(_autosaveTimer);
  _autosaveTimer=setTimeout(async ()=>{
    _autosaveTimer=null;
    const ok=await _writeToHandle();
    if(ok){ const b=document.getElementById("save-btn"); if(b){b.textContent="✓ 已保存"; setTimeout(()=>_updateSaveBtn(),1200);} }
  },500);
}

function _updateSaveBtn(){
  const b=document.getElementById("save-btn"); if(!b) return;
  b.textContent = _fileHandle ? "● 自动保存" : "HTML";
  b.title = _fileHandle ? "改动会自动写回已绑定的 HTML 文件（点击可立即保存）"
                        : (_fsaSupported ? "点击选择文件后，之后所有改动自动保存回该文件"
                                         : "保存当前编辑后的完整 HTML 文件（下载）");
}

function exportHTML(){
  finishEdit(true);
  // 支持 File System Access 且尚未绑定 → 绑定并开启自动保存
  if(_fsaSupported && !_fileHandle){ bindFile(); return; }
  // 已绑定 → 立即写回
  if(_fileHandle){ _writeToHandle().then(ok=>{ if(ok) showToast("已保存到绑定文件",1800); }); return; }
  // 不支持 FSA → 回退为下载
  showToast("正在保存 HTML …");
  const html=_buildCurrentHTML();
  if(html==null){ showToast("保存失败：未找到数据标记",2600); return; }
  const safe=TITLE.replace(/[\\/:*?"<>|]/g,"_");
  dlBlob(new Blob([html],{type:"text/html;charset=utf-8"}),safe+".html");
  showToast("已保存 HTML（含当前所有改动）",2200);
}


/* ══ XMIND ══ */
function exportXmind(){
  showToast("正在生成 XMind …");

  // ── helpers ────────────────────────────────────────────────────────────
  function uid(){ return crypto.randomUUID().replace(/-/g,"").slice(0,26); }
  function xe(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
                                   .replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }

  // ── content.json  (XMind 2020+) ────────────────────────────────────────
  function xnJson(node){
    const kids=(node.branches||[]).concat(node.children||[]);
    const o={id:uid(),class:"topic",title:node.label||node.central||""};
    if(kids.length) o.children={attached:kids.map(xnJson)};
    if(node.color) o.style={id:uid(),properties:{
      "line-color":node.color,"background-color":node.color+"33",
      "border-line-color":node.color,"line-width":"2pt",
      "shape-class":"org.xmind.topicShape.roundedRect"}};
    return o;
  }
  const rootJson=xnJson(TREE);
  rootJson.structureClass="org.xmind.ui.map.unbalanced";
  const contentJson=[{id:uid(),class:"sheet",title:TITLE,rootTopic:rootJson,theme:{},extensions:[]}];

  // ── content.xml  (XMind 8) ─────────────────────────────────────────────
  function xnXml(node, depth){
    const kids=(node.branches||[]).concat(node.children||[]);
    const label=node.label||node.central||"";
    const ind="  ".repeat(depth);
    let s=`${ind}<topic id="${uid()}"`;
    if(depth===0) s+=' structure-class="org.xmind.ui.map.unbalanced"';
    s+=`>\n${ind}  <title>${xe(label)}</title>`;
    if(kids.length){
      s+=`\n${ind}  <children>\n${ind}    <topics type="attached">`;
      for(const c of kids) s+="\n"+xnXml(c,depth+3);
      s+=`\n${ind}    </topics>\n${ind}  </children>`;
    }
    s+=`\n${ind}</topic>`;
    return s;
  }
  const sheetId=uid();
  const xmlRoot=xnXml(TREE,0);
  const contentXml=`<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n`+
    `<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"\n`+
    `  xmlns:fo="http://www.w3.org/1999/XSL/Format"\n`+
    `  xmlns:svg="http://www.w3.org/2000/svg"\n`+
    `  xmlns:xhtml="http://www.w3.org/1999/xhtml"\n`+
    `  xmlns:xlink="http://www.w3.org/1999/xlink"\n`+
    `  version="2.0">\n`+
    `  <sheet id="${sheetId}">\n`+
    xmlRoot+"\n"+
    `    <title>${xe(TITLE)}</title>\n`+
    `  </sheet>\n`+
    `</xmap-content>`;
  const stylesXml=`<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n`+
    `<xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0" version="2.0"></xmap-styles>`;

  // ── metadata & manifest ────────────────────────────────────────────────
  const meta={modifier:"",created:new Date().toISOString().slice(0,19)+".000+0000",
               creator:{name:"OpenClaw MindMap",version:"5.0",platform:""}};
  const mf={"file-entries":{
    "content.json":{"media-type":"application/json"},
    "content.xml": {"media-type":"text/xml"},
    "styles.xml":  {"media-type":"text/xml"},
    "metadata.json":{"media-type":"application/json"},
    "manifest.json":{"media-type":"application/json"}}};

  // ── ZIP builder ────────────────────────────────────────────────────────
  function u16(v){const b=new Uint8Array(2);new DataView(b.buffer).setUint16(0,v,true);return b;}
  function u32(v){const b=new Uint8Array(4);new DataView(b.buffer).setUint32(0,v,true);return b;}
  function crc32(d){
    if(!crc32.t){crc32.t=new Uint32Array(256);for(let i=0;i<256;i++){let c=i;for(let j=0;j<8;j++)c=c&1?0xEDB88320^(c>>>1):c>>>1;crc32.t[i]=c;}}
    let c=0xFFFFFFFF;for(const b of d)c=crc32.t[(c^b)&0xFF]^(c>>>8);return(c^0xFFFFFFFF)>>>0;
  }
  function cat(...a){const t=a.reduce((s,x)=>s+x.length,0),o=new Uint8Array(t);let p=0;for(const x of a){o.set(x,p);p+=x.length;}return o;}
  const enc=new TextEncoder();
  const files=[
    ["manifest.json", enc.encode(JSON.stringify(mf,null,2))],
    ["content.json",  enc.encode(JSON.stringify(contentJson,null,2))],
    ["content.xml",   enc.encode(contentXml)],
    ["styles.xml",    enc.encode(stylesXml)],
    ["metadata.json", enc.encode(JSON.stringify(meta,null,2))],
  ];
  const lParts=[],cds=[];let dataOff=0;
  for(const[name,data]of files){
    const nb=enc.encode(name),crc=crc32(data),sz=data.length;
    const lh=cat(new Uint8Array([0x50,0x4B,0x03,0x04]),u16(20),u16(0),u16(0),u16(0),u16(0),
      u32(crc),u32(sz),u32(sz),u16(nb.length),u16(0),nb);
    const cd=cat(new Uint8Array([0x50,0x4B,0x01,0x02]),u16(20),u16(20),u16(0),u16(0),u16(0),u16(0),
      u32(crc),u32(sz),u32(sz),u16(nb.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(dataOff),nb);
    lParts.push(lh,data);cds.push(cd);dataOff+=lh.length+sz;
  }
  const cdBytes=cat(...cds);
  const eocd=cat(new Uint8Array([0x50,0x4B,0x05,0x06]),u16(0),u16(0),
    u16(files.length),u16(files.length),u32(cdBytes.length),u32(dataOff),u16(0));
  dlBlob(new Blob([cat(...lParts,cdBytes,eocd)],{type:"application/octet-stream"}),
    TITLE.replace(/[\\/:*?"<>|]/g,"_")+".xmind");
}

/* ══ BOOT ══ */
RAW._depth=0; RAW.label=RAW.central;
annotate(RAW,0);
const TREE=RAW;
layout(TREE);
separateAll();   // 初始布局后分离
renderAll(TREE);
resetView();
_updateSaveBtn();
</script>
</body>
</html>"""


def render_html(title, js_data, theme="midnight"):
    if theme not in THEMES:
        theme = "midnight"
    return (_HTML
            .replace("__TITLE__",      title)
            .replace("__RAW_JSON__",   js_data)
            .replace("__TITLE_JSON__", json.dumps(title, ensure_ascii=False))
            .replace("__THEME__",      theme)
            .replace("__DATE__",       datetime.now().strftime("%Y-%m-%d %H:%M")))


# ═══════════════════════════════════════════════════════════════════════════════
#  IMAGE / PDF EXPORT  —  Two backends, auto-selected by availability:
#
#    1. Playwright  (best quality — renders full interactive HTML in Chromium)
#    2. Pillow      (pure Python — works everywhere, only needs `pip install pillow`)
#
#  The script tries each backend in order and uses the first one that works.
#  On a typical Windows machine only Pillow is available, and that's fine.
#  Pillow is auto-installed if missing.
# ═══════════════════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────────────────────
# Font discovery  (cross-platform: Windows / macOS / Linux)
# ─────────────────────────────────────────────────────────────────────────────
_FONT_SEARCH_PATHS = {
    "Windows": [
        # CJK fonts commonly found on Windows
        r"C:\Windows\Fonts\msyh.ttc",        # 微软雅黑
        r"C:\Windows\Fonts\msyhbd.ttc",       # 微软雅黑 Bold
        r"C:\Windows\Fonts\simhei.ttf",       # 黑体
        r"C:\Windows\Fonts\simsun.ttc",       # 宋体
        r"C:\Windows\Fonts\simkai.ttf",       # 楷体
        r"C:\Windows\Fonts\STFANGSO.TTF",     # 华文仿宋
        r"C:\Windows\Fonts\STSONG.TTF",       # 华文宋体
        r"C:\Windows\Fonts\malgun.ttf",       # Malgun Gothic (Korean but has CJK)
        r"C:\Windows\Fonts\meiryo.ttc",       # Meiryo (Japanese but has CJK)
        r"C:\Windows\Fonts\segoeui.ttf",      # Fallback: Segoe UI (no CJK)
        r"C:\Windows\Fonts\arial.ttf",        # Fallback: Arial
    ],
    "Darwin": [  # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode MS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "Linux": [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/unifont/unifont.otf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}

_font_cache = {}  # (size, bold) → ImageFont


def _find_system_font():
    """Return the path to the best available font for the current OS."""
    system = platform.system()
    candidates = _FONT_SEARCH_PATHS.get(system, [])
    # Also merge Linux paths as generic fallback
    if system != "Linux":
        candidates = candidates + _FONT_SEARCH_PATHS["Linux"]
    for p in candidates:
        if Path(p).is_file():
            return p
    return None


def _get_font(size, bold=False):
    """Get a PIL ImageFont at the given size, with caching."""
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]

    from PIL import ImageFont

    font_path = _find_system_font()
    if font_path:
        try:
            # For .ttc files, index 0 is usually Regular, index 1 is Bold
            idx = 1 if bold and font_path.endswith((".ttc", ".TTC")) else 0
            fnt = ImageFont.truetype(font_path, size, index=idx)
            _font_cache[key] = fnt
            return fnt
        except Exception:
            try:
                fnt = ImageFont.truetype(font_path, size)
                _font_cache[key] = fnt
                return fnt
            except Exception:
                pass

    # Ultimate fallback: Pillow default bitmap font
    fnt = ImageFont.load_default()
    _font_cache[key] = fnt
    return fnt


# ─────────────────────────────────────────────────────────────────────────────
# Backend 1:  Playwright  (best quality — renders full interactive HTML)
# ─────────────────────────────────────────────────────────────────────────────
def _has_playwright():
    try:
        from playwright.sync_api import sync_playwright as _sp  # noqa: F401
        return True
    except ImportError:
        return False


def _export_image_playwright(html_str: str, out: str, fmt: str,
                             scale: float = 2.0, quality: int = 92):
    import tempfile, shutil

    pw_paths = [
        os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""),
        "/opt/pw-browsers",
        str(Path.home() / ".cache" / "ms-playwright"),
    ]
    for p in pw_paths:
        if p and Path(p).is_dir():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = p
            break

    from playwright.sync_api import sync_playwright

    tmp_dir = tempfile.mkdtemp(prefix="mindmap_")
    tmp_html = os.path.join(tmp_dir, "mindmap.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_str)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=[
                "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
            ])
            dpr = max(1.0, min(scale, 4.0))
            page = browser.new_page(
                viewport={"width": 2560, "height": 1440},
                device_scale_factor=dpr,
            )
            page.goto(f"file://{tmp_html}", wait_until="networkidle")
            page.wait_for_selector("#nodes-g .nd", timeout=8000)
            page.wait_for_timeout(600)

            bbox = page.evaluate(r"""() => {
                const nodesG = document.getElementById('nodes-g');
                const edgesG = document.getElementById('edges-g');
                if (!nodesG) return null;
                let minX=Infinity, minY=Infinity, maxX=-Infinity, maxY=-Infinity;
                for (const g of [nodesG, edgesG]) {
                    if (!g) continue;
                    for (const el of g.querySelectorAll('rect,text,path,circle')) {
                        const r = el.getBoundingClientRect();
                        if (r.width===0 && r.height===0) continue;
                        if (r.left<minX) minX=r.left; if (r.top<minY) minY=r.top;
                        if (r.right>maxX) maxX=r.right; if (r.bottom>maxY) maxY=r.bottom;
                    }
                }
                if (minX===Infinity) return null;
                const pad=40;
                return {x:Math.max(0,minX-pad),y:Math.max(0,minY-pad),
                        width:maxX-minX+pad*2,height:maxY-minY+pad*2};
            }""")

            clip = bbox if (bbox and bbox["width"] > 0) else None
            if not clip:
                wrap = page.query_selector("#wrap")
                clip = wrap.bounding_box() if wrap else None

            png_bytes = page.screenshot(type="png", clip=clip) if clip else page.screenshot(type="png")
            browser.close()

        from PIL import Image as PILImage
        img = PILImage.open(io.BytesIO(png_bytes))
        if fmt == "jpg":
            if img.mode in ("RGBA", "P"):
                bg = PILImage.new("RGB", img.size, (13, 15, 26))
                if img.mode == "P": img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[3]); img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
            img.save(out, "JPEG", quality=quality, optimize=True)
        else:
            img.save(out, "PNG", optimize=True)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
# Backend 2:  Pure Pillow  (works everywhere — only needs `pip install pillow`)
# ─────────────────────────────────────────────────────────────────────────────

def _pillow_measure_text(text, font):
    """Measure text width and height using the font."""
    bbox = font.getbbox(str(text))
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _strip_emoji_for_pillow(text):
    """Remove emoji characters that Pillow/system fonts can't render.
    Keeps the text content after the emoji prefix."""
    if not text:
        return text
    result = []
    i = 0
    while i < len(text):
        cp = ord(text[i])
        # Skip emoji code points
        if (cp >= 0x1F300 or                    # Misc Symbols & Pictographs+
            0x2600 <= cp <= 0x27BF or           # Misc Symbols, Dingbats
            0x2300 <= cp <= 0x23FF or           # Misc Technical
            cp == 0xFE0F or cp == 0xFE0E or     # Variation Selectors
            cp == 0x200D or                     # Zero Width Joiner
            0xE0020 <= cp <= 0xE007F or         # Tags
            0x1F900 <= cp <= 0x1F9FF or         # Supplemental Symbols
            0x1FA00 <= cp <= 0x1FA6F or         # Chess Symbols
            0x1FA70 <= cp <= 0x1FAFF or         # Symbols Extended-A
            0x2702 <= cp <= 0x27B0 or           # Dingbats
            0x231A <= cp <= 0x231B or           # Watch, Hourglass
            cp == 0x2B50 or cp == 0x2B55 or     # Star, Circle
            0x2934 <= cp <= 0x2935 or           # Arrows
            0x25AA <= cp <= 0x25FE or           # Geometric Shapes
            0x2190 <= cp <= 0x21FF or           # Arrows
            0x20E3 == cp):                      # Keycap
            i += 1
            continue
        result.append(text[i])
        i += 1
    return "".join(result).strip()


def _hex_to_rgb(h):
    """Convert '#RRGGBB' or '#RRGGBBAA' to (R,G,B) or (R,G,B,A)."""
    h = h.lstrip("#")
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return (128, 128, 128)


def _blend_alpha(fg_hex, bg_rgb=(13, 15, 26)):
    """Blend a hex color with alpha (e.g. '#4A90D930') onto a background."""
    c = _hex_to_rgb(fg_hex)
    if len(c) == 4:
        r, g, b, a = c
        af = a / 255.0
        return (
            int(r * af + bg_rgb[0] * (1 - af)),
            int(g * af + bg_rgb[1] * (1 - af)),
            int(b * af + bg_rgb[2] * (1 - af)),
        )
    return c[:3]


def _export_image_pillow(tree, positions, out: str, fmt: str,
                         scale: float = 2.0, quality: int = 92,
                         theme: str = "midnight"):
    """
    Render the mind map to PNG/JPG/PDF using only Pillow.
    Zero system dependencies — works on Windows/macOS/Linux with just
    `pip install pillow`.
    """
    from PIL import Image, ImageDraw

    th = THEMES.get(theme, THEMES["midnight"])
    BG_COLOR = th["bg_rgb"]
    NODE_TEXT = [tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) for c in th["node_text"]]

    nodes = flatten_tree(tree)
    cmap  = build_color_map(tree)
    minx, miny, maxx, maxy = bounding_box(positions, nodes, pad=80)
    W = maxx - minx
    H = maxy - miny

    # Apply scale
    s = scale
    img_w, img_h = int(W * s), int(H * s)
    img = Image.new("RGB", (img_w, img_h), BG_COLOR)
    draw = ImageDraw.Draw(img, "RGBA")  # RGBA for alpha blending

    def tx(x): return (x - minx) * s
    def ty(y): return (y - miny) * s

    # ── Draw edges ────────────────────────────────────────────────────────
    for node in nodes:
        p = positions.get(node["_id"])
        if not p or p.get("parent_id") is None:
            continue
        pp = positions.get(p["parent_id"])
        if not pp:
            continue
        pnode = next((n for n in nodes if n["_id"] == p["parent_id"]), None)
        if not pnode:
            continue

        color_hex = cmap.get(node["_id"], "#888888")
        depth = node["_depth"]

        # Opacity simulation: blend with background
        if depth == 1:
            alpha = 0.85
        elif depth == 2:
            alpha = 0.6
        else:
            alpha = 0.4
        ec = _hex_to_rgb(color_hex)[:3]
        edge_color = tuple(int(ec[i] * alpha + BG_COLOR[i] * (1 - alpha)) for i in range(3))

        sw = max(1, int((2.5 if depth == 1 else (1.8 if depth == 2 else 1.3)) * s))

        # Draw edge as a series of line segments approximating the Bezier
        px_s, py_s = tx(pp["x"]), ty(pp["y"])
        cx_s, cy_s = tx(p["x"]), ty(p["y"])
        pw_s = pnode["_w"] * s / 2
        cw_s = node["_w"] * s / 2

        if cx_s >= px_s:
            x1 = px_s + pw_s
            x2 = cx_s - cw_s
        else:
            x1 = px_s - pw_s
            x2 = cx_s + cw_s

        # All children leave from the SAME point (parent center) — matches HTML/SVG
        s_dir = 1 if cx_s >= px_s else -1
        y1 = py_s

        span = abs(x2 - x1) or 1
        tension = 0.55 if depth == 1 else 0.48
        cp1x = x1 + s_dir * span * tension
        cp2x = x2 - s_dir * span * tension
        steps = 28
        pts = []
        for t in range(steps + 1):
            t_f = t / steps
            u = 1 - t_f
            # P0=(x1,y1) P1=(cp1x,y1) P2=(cp2x,cy) P3=(x2,cy)
            bx = u**3 * x1 + 3*u**2*t_f*cp1x + 3*u*t_f**2*cp2x + t_f**3 * x2
            by = u**3 * y1 + 3*u**2*t_f*y1   + 3*u*t_f**2*cy_s + t_f**3 * cy_s
            pts.append((bx, by))
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=edge_color, width=sw)

    # ── Draw nodes ────────────────────────────────────────────────────────
    # Root gradient colors
    ROOT_GRAD_START = (76, 95, 219)   # #4c5fdb
    ROOT_GRAD_END   = (124, 140, 248) # #7c8cf8

    for node in nodes:
        p = positions.get(node["_id"])
        if not p:
            continue
        depth = node["_depth"]
        c = CFG[min(depth, len(CFG) - 1)]
        w_raw, h_raw = node["_w"], node["_h"]
        w_s, h_s = w_raw * s, h_raw * s
        nx = tx(p["x"]) - w_s / 2
        ny = ty(p["y"]) - h_s / 2
        rx = int(c["rx"] * s)
        color_hex = cmap.get(node["_id"], "#888888")
        label = display_label(node)

        if depth == 0:
            # Root: gradient-like fill (approximate with solid blend)
            root_color = tuple((ROOT_GRAD_START[i] + ROOT_GRAD_END[i]) // 2 for i in range(3))
            # Glow effect: draw a larger, blurred rect behind
            glow_pad = 6 * s
            glow_color = root_color + (60,)
            draw.rounded_rectangle(
                [nx - glow_pad, ny - glow_pad, nx + w_s + glow_pad, ny + h_s + glow_pad],
                radius=rx + int(glow_pad), fill=glow_color,
            )
            draw.rounded_rectangle([nx, ny, nx + w_s, ny + h_s], radius=rx, fill=root_color)
            text_color = NODE_TEXT[0]
        elif depth == 1:
            fill_color = _blend_alpha(color_hex + "30", BG_COLOR)
            outline_color = _hex_to_rgb(color_hex)[:3]
            ow = max(1, int(2 * s))
            draw.rounded_rectangle([nx, ny, nx + w_s, ny + h_s], radius=rx,
                                   fill=fill_color, outline=outline_color, width=ow)
            text_color = NODE_TEXT[1]
        elif depth == 2:
            fill_color = _blend_alpha(color_hex + "18", BG_COLOR)
            outline_color = _blend_alpha(color_hex + "bb", BG_COLOR)
            ow = max(1, int(1.5 * s))
            draw.rounded_rectangle([nx, ny, nx + w_s, ny + h_s], radius=rx,
                                   fill=fill_color, outline=outline_color, width=ow)
            text_color = NODE_TEXT[2]
        else:
            fill_color = _blend_alpha(color_hex + "0e", BG_COLOR)
            outline_color = _blend_alpha(color_hex + "77", BG_COLOR)
            ow = max(1, int(1 * s))
            draw.rounded_rectangle([nx, ny, nx + w_s, ny + h_s], radius=rx,
                                   fill=fill_color, outline=outline_color, width=ow)
            text_color = NODE_TEXT[3]

        # ── Draw text ─────────────────────────────────────────────────
        font_size = int(c["fs"] * s)
        is_bold = c["fw"] in ("bold", "600", "700")
        font = _get_font(font_size, bold=is_bold)

        # Strip emoji for Pillow (system fonts can't render color emoji)
        render_label = _strip_emoji_for_pillow(label)
        tw, th = _pillow_measure_text(render_label, font)
        text_x = tx(p["x"]) - tw / 2
        text_y = ty(p["y"]) - th / 2
        draw.text((text_x, text_y), render_label, fill=text_color, font=font)

    # ── Save ──────────────────────────────────────────────────────────────
    if fmt == "jpg":
        img = img.convert("RGB")
        img.save(out, "JPEG", quality=quality, optimize=True)
    elif fmt == "pdf":
        # Embed the rendered image into a single-page PDF via Pillow
        # Pillow can save PDF directly from an Image object
        img = img.convert("RGB")
        img.save(out, "PDF", resolution=72.0 * s)
    else:
        img.save(out, "PNG", optimize=True)



# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def _export_one(tree, title, fmt, out, args):
    """Export a single format. `tree` must be a fresh (unannotated) copy."""

    # ── XMind  (pure Python, no deps) ────────────────────────────────────
    if fmt == "xmind":
        open(out, "wb").write(build_xmind(tree, title))
        print(f"[mindmap] ✅ XMind → {out}"); return

    # ── SVG  (static, pure Python) ───────────────────────────────────────
    if fmt == "svg":
        _nid[0] = 0
        tree["_depth"] = 0; tree["label"] = tree["central"]
        annotate(tree, 0)
        positions = compute_layout(tree)
        svg_str = render_svg_static(tree, positions, include_xml_header=True,
                                    theme=args.theme)
        open(out, "w", encoding="utf-8").write(svg_str)
        print(f"[mindmap] ✅ SVG → {out}"); return

    # ── PNG / JPG / PDF  — auto-select best available backend ────────────
    if fmt in ("png", "jpg", "pdf"):

        # Backend 1: Playwright  (best quality for png/jpg)
        if fmt in ("png", "jpg") and _has_playwright():
            html_str = render_html(title, json.dumps(tree, ensure_ascii=False),
                                   theme=args.theme)
            _export_image_playwright(html_str, out, fmt,
                                     scale=args.scale, quality=args.quality)
            print(f"[mindmap] ✅ {fmt.upper()} → {out}  (via Playwright)"); return

        # Backend 2: Pillow  (pure Python, works everywhere)
        if not _ensure_pillow(auto_install=not args.no_auto_install):
            print("[mindmap] ERROR: Cannot export image — Pillow is required.", file=sys.stderr)
            sys.exit(1)

        _nid[0] = 0
        tree["_depth"] = 0; tree["label"] = tree["central"]
        annotate(tree, 0)
        positions = compute_layout(tree)
        _export_image_pillow(tree, positions, out, fmt,
                             scale=args.scale, quality=args.quality,
                             theme=args.theme)
        print(f"[mindmap] ✅ {fmt.upper()} → {out}  (via Pillow)"); return

    # ── HTML  (default) ──────────────────────────────────────────────────
    html = render_html(title, json.dumps(tree, ensure_ascii=False),
                       theme=args.theme)
    open(out, "w", encoding="utf-8").write(html)
    print(f"[mindmap] ✅ HTML → {out}")


def main():
    import copy
    args = parse_args()

    fmts, seen = [], set()
    for f in args.format.lower().split(","):
        f = f.strip()
        if not f:
            continue
        if f not in ("html", "svg", "png", "jpg", "pdf", "xmind"):
            print(f"[mindmap] ERROR: Unknown format '{f}'. "
                  "Valid: html, svg, png, jpg, pdf, xmind", file=sys.stderr)
            sys.exit(1)
        if f not in seen:
            fmts.append(f); seen.add(f)

    try:
        raw = load_data(args)
        tree = build_tree(raw)
    except ValueError as e:
        print(f"[mindmap] ERROR: {e}", file=sys.stderr); sys.exit(1)

    if not args.no_lint:
        lint_tree(tree)

    for fmt in fmts:
        if args.output is None:
            out = default_output(fmt)
        else:
            out = resolve_output(args.output, fmt)
        _export_one(copy.deepcopy(tree), args.title, fmt, out, args)


if __name__ == "__main__":
    main()
