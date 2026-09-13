#!/usr/bin/env python3
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml
from PIL import Image

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SCRIPT_REF_RE = re.compile(r"(?<![\w./-])((?:scripts|references|assets)/[A-Za-z0-9_./-]+)")
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME)\b|\[TODO|待补充", re.I)
FALSE_PROMISE_RE = re.compile(r"(?:100%|百分之百|保证排名|保证成功|绝对有效|零风险)", re.I)
ENGLISH_QUESTION_RE = re.compile(
    r"(?im)(?:^|[\s>*-])(?:what|which|when|where|why|how|can|could|would|should|do|does|did|is|are|please|tell\s+me)\b[^\n]{0,180}[?？]"
)
CHINESE_QUESTION_REQUIREMENT_RE = re.compile(
    r"(?:确认问题|向用户.{0,12}(?:提问|询问)|追问).{0,40}(?:必须|只能|一律).{0,20}中文|"
    r"(?:必须|只能|一律).{0,20}(?:使用|用).{0,8}中文.{0,30}(?:提问|询问|确认)"
)
JARGON = ("系统化赋能", "智能洞察", "全能大师", "专家系统", "降维打击", "闭环赋能")


def split_frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


def parse_frontmatter(front):
    data = {}
    lines = front.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.groups()
        if value in {">", "|", ">-", "|-"}:
            block = []
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index].startswith(" ")):
                block.append(lines[index].strip())
                index += 1
            data[key] = " ".join(item for item in block if item)
            continue
        parts = [value.strip().strip('"\'')]
        index += 1
        while index < len(lines) and lines[index].startswith(" ") and lines[index].strip():
            parts.append(lines[index].strip().strip('"\''))
            index += 1
        data[key] = " ".join(parts)
    return data


def heading(body):
    match = re.search(r"^#\s+(.+?)\s*$", body, re.M)
    return match.group(1).strip() if match else ""


def add(items, code, message, suggestion):
    items.append({"code": code, "message": message, "suggestion": suggestion})


def has_rs_circle_badge(path):
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except (ET.ParseError, OSError):
        return False
    circles = []
    texts = []
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "circle":
            circles.append(element.attrib)
        elif tag == "text" and "".join(element.itertext()).strip() == "RS":
            texts.append(element.attrib)
    has_circle = any(
        item.get("cx") == "420" and item.get("cy") == "420" and item.get("r") == "52"
        and str(item.get("fill", "")).startswith("#")
        for item in circles
    )
    has_text = any(
        item.get("x") == "420" and item.get("text-anchor") == "middle"
        and str(item.get("fill", "")).upper() == "#FFFFFF"
        for item in texts
    )
    return has_circle and has_text


def apply_mechanical_fixes(path, text, meta):
    fixed = "\n".join(line.rstrip() for line in text.splitlines()).rstrip() + "\n"
    name = meta.get("name", "")
    normalized = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if name and normalized and name != normalized:
        fixed = re.sub(r"(?m)^name:\s*.*$", f"name: {normalized}", fixed, count=1)
    if fixed != text:
        path.write_text(fixed, encoding="utf-8")
        return True
    return False


def inspect_skill(skill_dir, fix=False):
    blockers, warnings = [], []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        add(blockers, "missing-skill-md", "缺少 SKILL.md", "创建标准 SKILL.md")
        return blockers, warnings, False
    text = skill_md.read_text(encoding="utf-8")
    front, body = split_frontmatter(text)
    meta = parse_frontmatter(front)
    changed = apply_mechanical_fixes(skill_md, text, meta) if fix else False
    if changed:
        text = skill_md.read_text(encoding="utf-8")
        front, body = split_frontmatter(text)
        meta = parse_frontmatter(front)

    if not front:
        add(blockers, "missing-frontmatter", "缺少 YAML frontmatter", "用 --- 包住 name 和 description")
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not name:
        add(blockers, "missing-name", "frontmatter 缺少 name", "填写小写连字符名称")
    elif not NAME_RE.fullmatch(name):
        add(blockers, "invalid-name", f"name 格式不正确: {name}", "只用小写字母、数字和连字符")
    if len(description) < 80:
        add(blockers, "short-description", f"description 只有 {len(description)} 字符", "说明谁在什么场景使用、做什么、输出什么")
    if description and not re.search(r"当用户|需要|适合|用于|使用", description):
        add(warnings, "unclear-trigger", "description 没有清楚说明触发场景", "加入用户何时需要此 Skill")
    if description and not re.search(r"输出|生成|得到|交付|报告|文件|清单|表格", description):
        add(warnings, "unclear-output", "description 没有说明最终产物", "写明会得到什么")

    title = heading(body)
    if not title:
        add(blockers, "missing-title", "正文缺少一级标题", "添加一个短而明确的标题")
    elif len(title) > 12:
        add(warnings, "long-title", f"标题长度为 {len(title)}", "中文标题优先控制在 4 至 8 字，必要时不超过 12 字")

    if PLACEHOLDER_RE.search(text):
        add(blockers, "placeholder", "存在 TODO 或占位内容", "补全内容后删除占位文本")
    if FALSE_PROMISE_RE.search(text):
        add(blockers, "false-promise", "包含无法验证的绝对承诺", "改成可验证的能力和边界")
    for term in JARGON:
        if term in text:
            add(warnings, "jargon", f"发现空泛表达: {term}", "改成普通用户能理解的具体动作")

    section_groups = {
        "input": ("你要提供什么", "输入", "所需材料"),
        "information-check": ("信息检查", "缺失信息处理", "输入检查"),
        "capability": ("能力", "能做什么"),
        "workflow": ("流程", "工作步骤", "怎么做"),
        "basis": ("依据说明", "判断依据", "输出依据"),
        "output": ("你会得到什么", "输出", "交付物"),
        "boundary": ("边界", "不能", "不适合", "限制"),
    }
    for code, choices in section_groups.items():
        if not any(choice in body for choice in choices):
            add(warnings, f"missing-{code}-section", f"缺少{code}相关章节", "补充清楚、非空的对应说明")

    if not re.search(r"^##\s+(?:信息检查|缺失信息处理|输入检查)\s*$", body, re.M):
        add(blockers, "missing-information-check", "没有独立的信息检查章节", "写清必填与可选信息，以及关键缺口如何向用户询问")
    elif not re.search(r"(?:必填|关键).{0,80}(?:询问|补充|确认)|(?:询问|补充|确认).{0,80}(?:必填|关键)", body, re.S):
        add(blockers, "unclear-missing-input-action", "没有明确要求对缺失的必填信息主动询问", "说明先检查已有上下文，关键必填信息缺失时先问用户")
    if not CHINESE_QUESTION_REQUIREMENT_RE.search(body):
        add(blockers, "missing-chinese-question-rule", "没有明确规定向用户确认时只能用中文提问", "在信息检查中加入中文提问要求")
    if ENGLISH_QUESTION_RE.search(body):
        add(blockers, "english-user-question", "发现可能向用户使用的英文提问模板", "把确认问题、追问、选项和问题示例改为中文")

    if not re.search(r"^##\s+(?:依据说明|判断依据|输出依据)\s*$", body, re.M):
        add(blockers, "missing-basis", "没有独立的依据说明章节", "说明结果依据哪些输入、证据、计算或检查，并区分推断与未知")
    elif not re.search(r"事实|推断|未知|来源|用户.{0,12}(?:材料|输入|说明)|检查结果|工具", body):
        add(blockers, "unclear-basis", "依据说明无法让用户核对结果从何而来", "列明用户材料、数据、工具或来源，并标注推断和未知")

    for ref in sorted(set(SCRIPT_REF_RE.findall(text))):
        clean = ref.rstrip(".,，。);；）`'")
        if not (skill_dir / clean).exists():
            add(blockers, "missing-resource", f"引用文件不存在: {clean}", "实现该文件或删除虚构引用")

    for script in sorted((skill_dir / "scripts").glob("*.py")) if (skill_dir / "scripts").exists() else []:
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as exc:
            add(blockers, "python-syntax", f"{script.name} 语法错误: {exc.msg}", "修复脚本并重新运行")

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        add(blockers, "missing-openai-yaml", "缺少 agents/openai.yaml", "生成界面元数据和内容匹配的头像")
    else:
        try:
            openai_data = yaml.safe_load(openai_yaml.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            add(blockers, "invalid-openai-yaml", f"agents/openai.yaml 无法解析: {exc}", "修复 YAML 格式")
            openai_data = {}
        interface = openai_data.get("interface", {}) if isinstance(openai_data, dict) else {}
        for key in ("display_name", "short_description", "default_prompt", "icon_small", "icon_large"):
            if not str(interface.get(key, "")).strip():
                add(blockers, f"missing-{key.replace('_', '-')}", f"agents/openai.yaml 缺少 {key}", "补充界面字段")
        for key in ("icon_small", "icon_large"):
            value = str(interface.get(key, "")).strip()
            if value:
                icon_path = (skill_dir / value).resolve()
                if not icon_path.exists():
                    add(blockers, "missing-avatar", f"头像文件不存在: {value}", "运行 generate_skill_avatar.py 生成头像")
                elif icon_path.suffix.lower() not in {".svg", ".png", ".webp"}:
                    add(blockers, "invalid-avatar-format", f"头像格式不支持: {value}", "使用 SVG、PNG 或 WebP")
                elif icon_path.suffix.lower() == ".svg" and not has_rs_circle_badge(icon_path):
                    add(blockers, "missing-rs-brand", f"SVG 头像缺少右下角圆形 RS 品牌章: {value}", "运行 generate_skill_avatar.py 重新生成头像")
        skillhub_avatar = skill_dir / "assets" / "avatar-skillhub.png"
        if not skillhub_avatar.is_file():
            add(blockers, "missing-skillhub-avatar", "缺少 Skill Hub 专用 PNG 头像", "运行 generate_skill_avatar.py 生成 assets/avatar-skillhub.png")
        else:
            try:
                with Image.open(skillhub_avatar) as image:
                    if image.format != "PNG" or image.size != (512, 512):
                        add(blockers, "invalid-skillhub-avatar", f"Skill Hub 头像必须是 512×512 PNG，当前为 {image.format} {image.size}", "重新生成 avatar-skillhub.png")
            except OSError as exc:
                add(blockers, "invalid-skillhub-avatar", f"Skill Hub PNG 头像无法读取: {exc}", "重新生成 avatar-skillhub.png")

    extras = [item.name for item in skill_dir.iterdir() if item.name.lower().startswith("readme")]
    if extras:
        add(warnings, "extra-readme", f"发现非必要说明文件: {', '.join(extras)}", "把必要说明放回 SKILL.md 或 references")
    return blockers, warnings, changed


def main():
    parser = argparse.ArgumentParser(description="检查 Agent Skill 的结构、表达和资源引用。")
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    blockers, warnings, changed = inspect_skill(args.skill_dir.resolve(), args.fix)
    score = max(0, 100 - len(blockers) * 15 - len(warnings) * 4)
    result = {
        "passed": not blockers and score >= 80,
        "score": score,
        "fixed": changed,
        "blockers": blockers,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"score={score} passed={result['passed']} blockers={len(blockers)} warnings={len(warnings)}")
        for item in blockers + warnings:
            print(f"- {item['code']}: {item['message']} -> {item['suggestion']}")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
