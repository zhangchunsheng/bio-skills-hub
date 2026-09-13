"""
AI拟人化写作助手 v8.2 — 数据管理工具
指纹提取/存储/加载 · 词库管理 · 历史记录 · AI味检测辅助
风格迁移由 AI 模型执行，本脚本只做数据层
"""

import json
import os
import sys
import re
import argparse
import traceback
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ============================================================
# 路径配置
# ============================================================
SKILL_DIR = Path(__file__).parent.parent  # scripts/ 的上级是技能根目录
DATA_DIR = SKILL_DIR / "data"
FINGERPRINTS_DIR = DATA_DIR / "fingerprints"
HISTORY_DIR = DATA_DIR / "history"
PATTERNS_FILE = DATA_DIR / "ai_patterns.json"
ERROR_LOG_FILE = DATA_DIR / "error.log"

def _load_doc_types():
    """从 doc_types.json 加载文档类型矩阵，文件损坏时降级为内置默认值"""
    dt_path = DATA_DIR / "doc_types.json"
    if dt_path.exists():
        try:
            with open(dt_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict) and "doc_types" in raw:
                return raw["doc_types"]
        except (json.JSONDecodeError, OSError, PermissionError) as e:
            log_error(e, "doc_types.json 损坏或不可读，使用内置默认值")
    # 内置默认（与 doc_types.json 保持同步）
    return {
        "doc_proposal": {"name": "企业方案/标书", "formal_min": 0.90, "colloquial_max": 0.10, "term_policy": "force_keep"},
        "doc_tech":     {"name": "技术文档/白皮书", "formal_min": 0.85, "colloquial_max": 0.15, "term_policy": "force_keep"},
        "doc_report":   {"name": "工作报告/复盘", "formal_min": 0.60, "colloquial_max": 0.65, "term_policy": "suggest_keep"},
        "doc_marketing":{"name": "产品介绍/营销", "formal_min": 0.50, "colloquial_max": 0.75, "term_policy": "optional"},
        "doc_email":    {"name": "邮件/通知", "formal_min": 0.55, "colloquial_max": 0.70, "term_policy": "suggest_keep"},
        "doc_social":   {"name": "社交/朋友圈", "formal_min": 0.20, "colloquial_max": 1.00, "term_policy": "never_keep"},
        "doc_note":     {"name": "笔记/随笔", "formal_min": 0.30, "colloquial_max": 0.90, "term_policy": "never_keep"},
    }

DOC_TYPE_MATRIX = _load_doc_types()


# ============================================================
# 异常处理
# ============================================================
class WritingError(Exception):
    def __init__(self, message: str, code: str, suggestion: str = ""):
        self.message = message
        self.code = code
        self.suggestion = suggestion
        super().__init__(message)


class InputError(WritingError):
    pass


class ConfigError(WritingError):
    pass


def log_error(error: Exception, context: str = ""):
    ERROR_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {context}\n  {type(error).__name__}: {error}\n")
        f.write(traceback.format_exc() + "\n")


def friendly_error(error: Exception) -> str:
    lines = [f"✗ {type(error).__name__}: {error}"]
    if hasattr(error, "code"):
        lines.append(f"  错误码: {error.code}")
    if hasattr(error, "suggestion") and error.suggestion:
        lines.append(f"  建议: {error.suggestion}")
    return "\n".join(lines)


# ============================================================
# 工具函数
# ============================================================
def ensure_dirs():
    for d in [DATA_DIR, FINGERPRINTS_DIR, HISTORY_DIR, FINGERPRINTS_DIR / "versions"]:
        d.mkdir(parents=True, exist_ok=True)


def read_input(path: str) -> str:
    if os.path.isfile(path):
        # 检测 BOM 确定编码
        with open(path, "rb") as fb:
            head = fb.read(4)
        # UTF-16 LE BOM (ff fe)
        if head[:2] == b'\xff\xfe':
            try:
                with open(path, "r", encoding="utf-16-le") as f:
                    return f.read()
            except (UnicodeDecodeError, OSError) as e:
                raise InputError(f"UTF-16 文件解码失败 {path}: {e}", "ENCODING_ERROR", "请将文件另存为 UTF-8 编码")
        # UTF-16 BE BOM (fe ff)
        if head[:2] == b'\xfe\xff':
            try:
                with open(path, "r", encoding="utf-16-be") as f:
                    return f.read()
            except (UnicodeDecodeError, OSError) as e:
                raise InputError(f"UTF-16 BE 文件解码失败 {path}: {e}", "ENCODING_ERROR", "请将文件另存为 UTF-8 编码")
        # UTF-8 BOM (ef bb bf)
        if head[:3] == b'\xef\xbb\xbf':
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    return f.read()
            except (UnicodeDecodeError, OSError) as e:
                raise InputError(f"UTF-8 BOM 文件解码失败 {path}: {e}", "ENCODING_ERROR", "请将文件另存为 UTF-8 编码")

        # 无 BOM，按常见编码依次尝试
        for enc in ["utf-8", "gbk", "gb18030"]:
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except PermissionError as e:
                raise InputError(f"没有权限读取文件 {path}", "FILE_PERMISSION_ERROR", "请检查文件权限设置")
            except OSError as e:
                raise InputError(f"读取文件失败 {path}: {e}", "FILE_READ_ERROR", "检查文件是否被占用或路径是否正确")

        raise InputError(
            f"无法识别文件编码 {path}，已尝试 UTF-8/GBK/GB18030/UTF-16",
            "ENCODING_ERROR",
            "请将文件另存为 UTF-8 编码后重试"
        )
    return path


def validate_input(text: str, min_chars: int = 10, label: str = "输入") -> str:
    if not text or not text.strip():
        raise InputError(f"{label}为空", "EMPTY_INPUT", "请提供有效文本")
    text = text.strip()
    if len(text) < min_chars:
        raise InputError(f"{label}仅{len(text)}字，需≥{min_chars}字", "TOO_SHORT")
    return text


def load_patterns() -> dict:
    if not PATTERNS_FILE.exists():
        raise ConfigError(
            f"词库文件不存在: {PATTERNS_FILE}",
            "MISSING_PATTERNS",
            "请确保 data/ai_patterns.json 存在，或重新下载技能包"
        )
    try:
        with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"词库文件 JSON 格式损坏: {e}",
            "CORRUPT_PATTERNS",
            f"请检查 {PATTERNS_FILE} 的 JSON 语法或重新下载技能包"
        )
    except (OSError, PermissionError) as e:
        raise ConfigError(
            f"词库文件读取失败: {e}",
            "READ_PATTERNS_ERROR",
            f"请检查 {PATTERNS_FILE} 的文件权限"
        )


# ============================================================
# 文档类型判定
# ============================================================
def detect_doc_type(text: str) -> dict:
    keywords = {
        "doc_proposal": ["方案", "标书", "承诺", "SLA", "服务标准", "质量保障"],
        "doc_tech":     ["架构", "接口", "部署", "代码", "API", "数据库", "配置"],
        "doc_report":   ["复盘", "总结", "本周", "计划", "完成", "进展"],
        "doc_marketing":["产品", "功能", "优惠", "购买", "限时", "体验"],
        "doc_email":    ["您好", "附件", "抄送", "回复", "收到"],
        "doc_social":   ["周末", "打卡", "好吃", "好看", "哈哈"],
        "doc_note":     ["笔记", "心得", "摘录", "学习了", "记录"],
    }
    scores = {}
    for dt, kws in keywords.items():
        scores[dt] = sum(1 for kw in kws if kw in text) / len(kws)
    if len(text) < 200:
        exclam = text.count("！") + text.count("!") + text.count("哈")
        if exclam > 2:
            scores["doc_social"] = max(scores.get("doc_social", 0), 0.7)
    best = max(scores, key=scores.get)
    return {
        "doc_type": best,
        "confidence": round(min(scores[best] * 1.5, 1.0), 2),
        "matrix": DOC_TYPE_MATRIX.get(best, DOC_TYPE_MATRIX["doc_report"]),
    }


# ============================================================
# AI 味检测（辅助 AI 定位问题词）
# ============================================================
def detect_ai_flavor(text: str, doc_type: str = "doc_report") -> dict:
    patterns = load_patterns()
    global_markers = patterns.get("global_markers", {})
    doc_specific = patterns.get("doc_specific", {}).get(doc_type, {})
    exempt = set(doc_specific.get("exempt", []))
    extra = doc_specific.get("extra_markers", [])

    all_patterns = []
    for cat, words in global_markers.items():
        for w in words:
            if w not in exempt:
                all_patterns.append((w, cat))
    for w in extra:
        if w not in exempt:
            all_patterns.append((w, "extra"))

    findings = []
    total_matches = 0
    for pattern, category in all_patterns:
        count = text.count(pattern)
        if count > 0:
            positions = []
            idx = 0
            while True:
                idx = text.find(pattern, idx)
                if idx == -1:
                    break
                para = text[:idx].count("\n") + 1
                positions.append(f"第{para}段")
                idx += len(pattern)
            findings.append({"pattern": pattern, "category": category, "count": count, "positions": positions})
            total_matches += count

    total_words = len(re.findall(r'[\u4e00-\u9fff\w]+', text))
    ai_ratio = round(total_matches / max(total_words, 1), 2)

    return {
        "doc_type": doc_type,
        "total_chars": len(text),
        "ai_matches": total_matches,
        "ai_ratio": ai_ratio,
        "severity": "high" if ai_ratio > 0.1 else ("medium" if ai_ratio > 0.05 else "low"),
        "findings": findings,
    }


# ============================================================
# 指纹提取（8维，纯统计）
# ============================================================
def extract_fingerprint(samples: list[str], user_id: str = "default") -> dict:
    samples = [s.strip() for s in samples if len(s.strip()) >= 50]
    if len(samples) < 3:
        raise InputError(
            f"需要≥3段≥50字样本，当前{len(samples)}段",
            "INSUFFICIENT_SAMPLES",
            f"还差{3 - len(samples)}段。来源：工作邮件、技术讨论、社交聊天各1段"
        )
    samples = samples[:3]
    all_text = "\n".join(samples)

    # 分词
    try:
        import jieba
        words = [w.strip() for w in jieba.cut(all_text) if len(w.strip()) >= 2]
    except ImportError:
        # 无 jieba：按标点/空格切分后取 2-4 字词片段
        raw_words = re.findall(r'[\u4e00-\u9fff]{2,4}|[a-zA-Z]+', all_text)
        words = [w for w in raw_words if len(w) >= 2]

    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1
    top_words = sorted(word_freq.items(), key=lambda x: -x[1])[:20]

    # 口语/书面比
    colloquial = sum(all_text.count(w) for w in ["其实", "说真的", "感觉", "还行", "吧", "嘛", "啦", "哈"])
    formal = sum(all_text.count(w) for w in ["因此", "然而", "此外", "综上所述", "基于", "通过"])
    colloquial_ratio = colloquial / (colloquial + formal + 1)

    # 句式
    sents = re.split(r'[。！？.!?]', all_text)
    sents = [s.strip() for s in sents if s.strip()]
    sent_lens = [len(s) for s in sents]
    avg_len = sum(sent_lens) / len(sent_lens) if sent_lens else 0
    total = len(sent_lens)
    short = sum(1 for l in sent_lens if l < 10) / max(total, 1)
    mid = sum(1 for l in sent_lens if 10 <= l <= 25) / max(total, 1)
    long = sum(1 for l in sent_lens if l > 25) / max(total, 1)

    # 情感
    pos = sum(all_text.count(w) for w in ["好", "棒", "不错", "优秀", "成功", "开心", "满意"])
    neg = sum(all_text.count(w) for w in ["差", "烂", "失败", "坑", "不行", "头疼", "烦"])
    pos_ratio = pos / (pos + neg + 1)

    # 标点
    tc = max(len(all_text), 1)
    comma_d = all_text.count("，") / tc
    dash_r = all_text.count("——") / tc
    exclam_r = all_text.count("！") / tc
    ellipsis_r = all_text.count("…") / tc

    # 论证
    data = sum(all_text.count(w) for w in ["%", "QPS", "ms", "次", "元", "万", "倍", "小时"])
    case = sum(all_text.count(w) for w in ["之前", "上次", "有一次", "踩过坑", "记得", "遇到过"])
    analogy = sum(all_text.count(w) for w in ["就像", "好比", "相当于", "说白了", "类似"])
    total_arg = data + case + analogy or 1
    arg_style = {
        "data_driven": round(data / total_arg, 2),
        "case_driven": round(case / total_arg, 2),
        "analogy": round(analogy / total_arg, 2),
        "direct_assertion": round(1 - (data + case + analogy) / total_arg, 2),
    }

    # 判断力
    strong = sum(all_text.count(w) for w in ["必须", "一定", "绝对", "别", "不要", "就是", "肯定"])
    suggestive = sum(all_text.count(w) for w in ["建议", "可以", "考虑", "最好", "推荐", "不妨"])
    neutral = sum(all_text.count(w) for w in ["可能", "也许", "大概", "似乎", "好像", "感觉"])
    total_judge = strong + suggestive + neutral or 1
    judgment = {
        "strong": round(strong / total_judge, 2),
        "suggestive": round(suggestive / total_judge, 2),
        "neutral": round(neutral / total_judge, 2),
    }

    # 结构
    paragraphs = [p.strip() for p in all_text.split("\n") if p.strip()]
    first_sents = [p.split("。")[0][:30] for p in paragraphs[:3]]
    direct_open = sum(1 for s in first_sents if len(s) < 20 and "？" not in s)
    struct_pref = "conclusion_first" if direct_open >= 2 else "progressive"
    numbered = sum(all_text.count(w) for w in ["第一", "第二", "第三", "其一", "其二"])
    bullet = all_text.count("- ") + all_text.count("· ")
    list_style = "colloquial_numbered" if numbered > bullet else "natural_break"
    trans = sum(all_text.count(w) for w in ["首先", "其次", "此外", "然而", "因此", "所以", "不过", "但是"])
    trans_style = "connector" if trans / max(len(paragraphs), 1) > 0.5 else "semantic_natural"

    # 场景覆盖
    scene_types = list(set(detect_doc_type(s)["doc_type"] for s in samples))

    # 健康度
    diversity = min(len(scene_types) * 3, 10)
    stability = min(int((1 - len(set(words)) / max(len(words), 1)) * 10), 10)

    fingerprint = {
        "user_id": user_id,
        "version": "8.0",
        "created_at": datetime.now().isoformat(),
        "scene_coverage": scene_types,
        "health_score": {
            "diversity": diversity,
            "stability": stability,
            "consistency": 8,
            "total": (diversity + stability + 8) // 3,
        },
        "core_fingerprint": {
            "avg_sentence_length": round(avg_len, 1),
            "sentence_distribution": {"short": round(short, 2), "mid": round(mid, 2), "long": round(long, 2)},
            "colloquial_ratio": round(colloquial_ratio, 2),
            "judgment_strength": judgment,
            "argument_style": arg_style,
            "structure_preference": struct_pref,
            "list_style": list_style,
            "transition_style": trans_style,
            "emotion_tone": {"positive_ratio": round(pos_ratio, 2), "humor_score": round(all_text.count("哈") / tc * 100, 2)},
            "paragraph_open_style": "direct" if direct_open >= 2 else "contextual",
            "paragraph_close_style": "action_oriented" if judgment["strong"] > 0.3 else "natural",
            "punctuation_profile": {
                "comma_density": round(comma_d, 2),
                "exclamation_rate": round(exclam_r, 2),
                "ellipsis_rate": round(ellipsis_r, 2),
                "dash_rate": round(dash_r, 2),
            },
        },
        "scene_layers": {},
    }

    for dt, m in DOC_TYPE_MATRIX.items():
        fingerprint["scene_layers"][dt] = {
            "formal_score": m["formal_min"],
            "colloquial_cap": m["colloquial_max"],
            "term_policy": m["term_policy"],
            "high_freq_words": [w for w, _ in top_words[:10]],
            "avoid_words": ["首先", "其次", "综上所述", "毋庸置疑", "全方位", "致力于"],
        }

    # 存盘（带异常处理）
    try:
        with open(FINGERPRINTS_DIR / f"{user_id}_core.json", "w", encoding="utf-8") as f:
            json.dump(fingerprint["core_fingerprint"], f, ensure_ascii=False, indent=2)
        with open(FINGERPRINTS_DIR / f"{user_id}_scenes.json", "w", encoding="utf-8") as f:
            json.dump(fingerprint["scene_layers"], f, ensure_ascii=False, indent=2)
    except (OSError, PermissionError) as e:
        log_error(e, "指纹存盘失败")
        raise ConfigError(
            f"指纹写入失败: {e}\n请检查磁盘空间和 data/fingerprints/ 目录权限",
            "WRITE_FINGERPRINT_ERROR",
            "检查磁盘空间是否充足，目录是否可写"
        )

    return fingerprint


def load_fingerprint(user_id: str = "default", doc_type: str = "doc_report") -> dict:
    core_path = FINGERPRINTS_DIR / f"{user_id}_core.json"
    scenes_path = FINGERPRINTS_DIR / f"{user_id}_scenes.json"
    if not core_path.exists():
        return {"error": "未找到指纹", "has_fingerprint": False}

    try:
        with open(core_path, "r", encoding="utf-8") as f:
            core = json.load(f)
    except (json.JSONDecodeError, OSError, PermissionError) as e:
        log_error(e, f"指纹文件损坏: {core_path}")
        return {
            "error": f"指纹文件损坏: {e}\n建议删除 {core_path} 后重新采集",
            "has_fingerprint": False,
            "corrupted": True,
            "suggestion": f"删除 {core_path} 后运行 extract 重新采集指纹",
        }

    scenes = {}
    if scenes_path.exists():
        try:
            with open(scenes_path, "r", encoding="utf-8") as f:
                scenes = json.load(f)
        except (json.JSONDecodeError, OSError, PermissionError) as e:
            log_error(e, f"场景层文件损坏: {scenes_path}")
            # 场景层损坏不阻断，降级为空场景继续
            scenes = {}

    return {
        "has_fingerprint": True,
        "core_fingerprint": core,
        "scene_layer": scenes.get(doc_type, {}),
        "doc_type_matrix": DOC_TYPE_MATRIX.get(doc_type, DOC_TYPE_MATRIX["doc_report"]),
    }


def list_fingerprints() -> list:
    if not FINGERPRINTS_DIR.exists():
        return []
    try:
        return [fp.stem.replace("_core", "") for fp in FINGERPRINTS_DIR.glob("*_core.json")]
    except (OSError, PermissionError) as e:
        log_error(e, "列出指纹失败")
        return []


# ============================================================
# 历史管理
# ============================================================
def save_history(original: str, rewritten: str, doc_type: str, intensity: str = "standard") -> str:
    rid = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{doc_type}"
    record = {
        "id": rid, "timestamp": datetime.now().isoformat(),
        "doc_type": doc_type, "intensity": intensity,
        "original": original, "rewritten": rewritten,
    }
    try:
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_DIR / f"{rid}.json", "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    except (OSError, PermissionError) as e:
        log_error(e, "历史记录写入失败")
        raise ConfigError(
            f"历史记录写入失败: {e}",
            "WRITE_HISTORY_ERROR",
            "检查磁盘空间和 data/history/ 目录权限"
        )

    index_path = HISTORY_DIR / "index.json"
    index = []
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            log_error(e, "历史索引损坏，重置")
            index = []
    index.insert(0, {"id": rid, "timestamp": record["timestamp"], "doc_type": doc_type})
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index[:20], f, ensure_ascii=False, indent=2)
    except (OSError, PermissionError) as e:
        log_error(e, "历史索引写入失败")
        # 索引写入失败不阻断主流程，记录已保存
    return rid


def list_history() -> list:
    index_path = HISTORY_DIR / "index.json"
    if not index_path.exists():
        return []
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, PermissionError) as e:
        log_error(e, "历史索引读取失败")
        return []


def get_history(rid: str) -> dict:
    p = HISTORY_DIR / f"{rid}.json"
    if not p.exists():
        return {"error": f"未找到记录 {rid}"}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, PermissionError) as e:
        log_error(e, f"历史记录损坏: {rid}")
        return {"error": f"历史记录损坏: {e}"}


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="AI拟人化写作助手 v8 — 数据管理工具")
    sub = parser.add_subparsers(dest="command")

    # extract
    pe = sub.add_parser("extract", help="提取风格指纹")
    pe.add_argument("input", help="文本文件（3段，空行分隔）")
    pe.add_argument("user_id", nargs="?", default="default")

    # health
    ph = sub.add_parser("health", help="指纹健康度")
    ph.add_argument("user_id", nargs="?", default="default")

    # load
    pl = sub.add_parser("load", help="加载指纹（输出JSON）")
    pl.add_argument("doc_type", nargs="?", default="doc_report")
    pl.add_argument("user_id", nargs="?", default="default")

    # list
    sub.add_parser("list", help="列出所有指纹")

    # detect-doctype
    pd = sub.add_parser("detect-doctype", help="文档类型判定")
    pd.add_argument("input")

    # ai-flavor
    pf = sub.add_parser("ai-flavor", help="AI味检测")
    pf.add_argument("input")
    pf.add_argument("--doc-type", default=None)

    # history
    phist = sub.add_parser("history", help="历史管理")
    phist.add_argument("action", choices=["list", "show", "rollback"])
    phist.add_argument("id", nargs="?", default=None)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    try:
        ensure_dirs()
    except (OSError, PermissionError) as e:
        print(f"✗ 无法创建数据目录: {e}", file=sys.stderr)
        print(f"  请检查磁盘空间和 {DATA_DIR} 父目录权限", file=sys.stderr)
        sys.exit(5)

    try:

        if args.command == "extract":
            text = read_input(args.input)
            text = validate_input(text, 150, "样本")
            samples = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= 50]
            result = extract_fingerprint(samples, args.user_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.command == "health":
            core = FINGERPRINTS_DIR / f"{args.user_id}_core.json"
            if not core.exists():
                print("✗ 未找到指纹")
                return
            try:
                with open(core, "r", encoding="utf-8") as f:
                    c = json.load(f)
            except (json.JSONDecodeError, OSError, PermissionError) as e:
                print(f"✗ 指纹文件损坏: {e}")
                print(f"  建议删除 {core} 后重新采集")
                return
            print(f"平均句长: {c.get('avg_sentence_length', 'N/A')}字")
            print(f"口语比例: {c.get('colloquial_ratio', 'N/A')}")
            js = c.get("judgment_strength", {})
            print(f"判断力: 强断{js.get('strong','?')} / 建议{js.get('suggestive','?')} / 中性{js.get('neutral','?')}")
            print(f"结构偏好: {c.get('structure_preference', 'N/A')}")

        elif args.command == "load":
            fp = load_fingerprint(args.user_id, args.doc_type)
            print(json.dumps(fp, ensure_ascii=False, indent=2))

        elif args.command == "list":
            fps = list_fingerprints()
            if fps:
                print("=== 已存储指纹 ===")
                for f in fps:
                    print(f"  {f}")
            else:
                print("暂无指纹")

        elif args.command == "detect-doctype":
            text = read_input(args.input)
            text = validate_input(text, 10)
            r = detect_doc_type(text)
            m = r["matrix"]
            print(json.dumps({
                "doc_type": r["doc_type"],
                "name": m["name"],
                "confidence": r["confidence"],
                "constraints": {
                    "formal_min": m["formal_min"],
                    "colloquial_max": m["colloquial_max"],
                    "term_policy": m["term_policy"],
                }
            }, ensure_ascii=False, indent=2))

        elif args.command == "ai-flavor":
            text = read_input(args.input)
            text = validate_input(text, 10)
            dt = args.doc_type or detect_doc_type(text)["doc_type"]
            r = detect_ai_flavor(text, dt)
            print(f"=== AI味检测 [{dt}] ===")
            print(f"文本: {r['total_chars']}字 | AI味: {r['ai_matches']}处 ({r['ai_ratio']*100:.0f}%) | {r['severity']}")
            for f in r["findings"]:
                print(f"  ✗ 「{f['pattern']}」×{f['count']} — {', '.join(f['positions'])}")

        elif args.command == "history":
            if args.action == "list":
                recs = list_history()
                if recs:
                    print("=== 改写历史 ===")
                    for r in recs:
                        print(f"  {r['id']}  {r['timestamp']}  [{r['doc_type']}]")
                else:
                    print("暂无历史")
            elif args.action == "show" and args.id:
                r = get_history(args.id)
                if "error" in r:
                    print(f"✗ {r['error']}")
                else:
                    print(json.dumps(r, ensure_ascii=False, indent=2))
            elif args.action == "rollback" and args.id:
                r = get_history(args.id)
                if "error" in r:
                    print(f"✗ {r['error']}")
                else:
                    print(r["rewritten"])

    except InputError as e:
        print(friendly_error(e), file=sys.stderr)
        log_error(e, f"InputError/{args.command}")
        sys.exit(2)
    except ConfigError as e:
        print(friendly_error(e), file=sys.stderr)
        log_error(e, f"ConfigError/{args.command}")
        sys.exit(3)
    except Exception as e:
        print(f"✗ 未知错误: {e}", file=sys.stderr)
        log_error(e, f"Unhandled/{args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
