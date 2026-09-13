# -*- coding: utf-8 -*-
# new_announcement.py —— 数据驱动生成公告 docx（适配新版手改母版 04/05）
#
# ⚠️ 为什么用 lxml 而非 python-docx：
#   新版母版的免责声明是“红色 + 黑体18pt + 文本框(mc:AlternateContent)”形式。python-docx
#   在增删/移动段落重排 body 时会把文本框扁平化（丢 drawing），导致免责声明变普通段落、格式崩。
#   因此本脚本改用 lxml 直接改 word/document.xml：只替换固定字段的 run 文本、清空“重要提示+章节”
#   可变区后按新样式 ID 重建段落，全程不触碰免责声明文本框，完美保留。
#
# 新版母版样式 ID 映射：
#   af4 = 公告头（居中）   afa = 正文（两端对齐）
#   af5 = 标题区（黑体/18pt/加粗；红色在 run 级）
#   af7 = 一/二/三级标题（统一加粗、顶格）
#   afb = 重要提示（加粗）  afc = 落款（右对齐）
#
# 用法：
#   python new_announcement.py --base real --json ann.json --out 公告.docx
#   python new_announcement.py --base mask --json ann.json --out 公告_脱敏.docx
#
# JSON 结构见 scripts/sample_announcement.json
import argparse
import copy
import json
import os
import zipfile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
# 母版路径由 --base 参数传入（必传），不再硬编码。
# 用法：python new_announcement.py --base <母版docx完整路径> --json input.json --out output.docx

S_HEADER = "af4"
S_BODY = "afa"
S_TITLE = "af5"
S_HEADING = "af7"
S_NOTE = "afb"
S_SIGN = "afc"

MASK_COMPANY = "XX公司"
MASK_SIGN = "XX公司董事会"
REAL_NAMES = ["<COMPANY_FULL>", "<TARGET_CO>", "<TICKER>"]


def qn(tag):
    return "{%s}%s" % (W, tag)


def desensitize(text):
    for n in REAL_NAMES:
        text = text.replace(n, MASK_COMPANY)
    return text


def get_text(el):
    return "".join(t.text or "" for t in el.iter(qn("t")))


def style_of(p):
    pPr = p.find(qn("pPr"))
    if pPr is None:
        return None
    ps = pPr.find(qn("pStyle"))
    return ps.get(qn("val")) if ps is not None else None


def set_single_run_text(p, text):
    """用单 run 替换段落内容，保留第一个 run 的 rPr（如标题区红色）。"""
    runs = p.findall(qn("r"))
    if not runs:
        r = etree.SubElement(p, qn("r"))
        t = etree.SubElement(r, qn("t"))
        t.text = text
        return
    first = runs[0]
    t = first.find(qn("t"))
    if t is None:
        t = etree.SubElement(first, qn("t"))
    t.text = text
    for r in runs[1:]:
        p.remove(r)


def make_para(style_id, text, src_p=None):
    p = etree.Element(qn("p"))
    pPr = etree.SubElement(p, qn("pPr"))
    ps = etree.SubElement(pPr, qn("pStyle"))
    ps.set(qn("val"), style_id)
    # 严格继承模板段落级格式：缩进(ind) + 对齐(jc)
    # 模板的可视“首行缩进两格”写在样例段落的 pPr 上，而非样式定义，
    # 故重建段落时必须显式复制，否则正文/提示/标题会全部丢失缩进。
    if src_p is not None:
        src_pPr = src_p.find(qn("pPr"))
        if src_pPr is not None:
            for tag in ("ind", "jc"):
                el = src_pPr.find(qn(tag))
                if el is not None:
                    pPr.append(copy.deepcopy(el))
    if text:
        r = etree.SubElement(p, qn("r"))
        t = etree.SubElement(r, qn("t"))
        t.text = text
    return p


def build(base_path, data, out_path, is_mask=False):
    z = zipfile.ZipFile(base_path)
    xml = z.read("word/document.xml")
    root = etree.fromstring(xml)
    body = root.find(qn("body"))
    paras = body.findall(qn("p"))

    # 各样式代表段落（用于严格继承模板的段落级缩进/对齐）
    style_rep = {}
    for p in paras:
        sid = style_of(p)
        if sid and sid not in style_rep:
            style_rep[sid] = p

    # --- 定位固定字段 ---
    header_p = next((p for p in paras if "证券代码" in get_text(p)), None)
    af5 = [p for p in paras if style_of(p) == S_TITLE]
    company_p = af5[0] if af5 else None
    title_p = af5[1] if len(af5) > 1 else None
    # 免责声明在文本框(mc:AlternateContent)内，文本在 VML fallback，run 级/lxml 文本级读不到，
    # 用文本框标记检测整段
    disc_p = next((p for p in paras
                   if ("txbxContent" in etree.tostring(p).decode()
                       or "mc:AlternateContent" in etree.tostring(p).decode())),
                  None)
    sign = [p for p in paras if style_of(p) == S_SIGN]
    sign_org_p = sign[0] if sign else None
    sign_date_p = sign[1] if len(sign) > 1 else None

    # --- 免责声明开关 ---
    if disc_p is not None and not data.get("disclaimer", True):
        body.remove(disc_p)
        disc_p = None

    # --- 公告头 ---
    if header_p is not None and not is_mask:
        h = data.get("header", {})
        hdr = "证券代码：{code}         证券简称：{short}         公告编号：{no}".format(
            code=h.get("code", "<TICKER>"),
            short=h.get("short", "<TARGET_CO>"),
            no=h.get("no", "2026-XXX"),
        )
        set_single_run_text(header_p, hdr)

    # --- 公司全称行 + 公告名称行（保留 run 级红色）---
    if company_p is not None:
        name = MASK_COMPANY if is_mask else data.get("title_full", "<COMPANY_FULL>")
        set_single_run_text(company_p, name)
    if title_p is not None:
        tn = data.get("title_name", "关于××事项的公告")
        if is_mask:
            tn = desensitize(tn)
        set_single_run_text(title_p, tn)

    # --- 重要提示内容（从 sections 抽 type=note）---
    sections = data.get("sections", [])
    note_secs = [s for s in sections if s.get("t") == "note"]
    note = note_secs[0].get("v", "") if note_secs else None
    if note and note.startswith("重要内容提示："):
        note = note[len("重要内容提示："):]
    body_sections = [s for s in sections if s.get("t") != "note"]

    # --- 清空“重要提示 + 章节”可变区（免责声明/标题之后、落款之前）---
    start_p = disc_p if disc_p is not None else (title_p if title_p is not None else company_p)
    bparas = body.findall(qn("p"))
    si = bparas.index(start_p) if start_p is not None else -1
    ei = bparas.index(sign_org_p) if sign_org_p is not None else len(bparas)
    for p in bparas[si + 1: ei]:
        body.remove(p)

    # --- 在 start_p 之后、落款之前，按序重建：空行 + 重要提示 + 章节 + 空行 ---
    anchor = [start_p]

    def emit(text, style):
        p = make_para(style, text, style_rep.get(style))
        if anchor[0] is not None:
            anchor[0].addnext(p)
        elif sign_org_p is not None:
            sign_org_p.addprevious(p)
        anchor[0] = p
        return p

    emit("", S_BODY)  # 免责声明后空行
    if note:
        emit("重要内容提示：", S_NOTE)
        emit(desensitize(note) if is_mask else note, S_BODY)
    for sec in body_sections:
        t = sec.get("t")
        v = sec.get("v", "")
        if is_mask:
            v = desensitize(v)
        emit(v, S_HEADING if t in ("h1", "h2", "h3") else S_BODY)
    emit("", S_BODY)  # 落款前空行

    # --- 落款 ---
    if sign_org_p is not None:
        org = MASK_SIGN if is_mask else data.get("sign_org", "<COMPANY_FULL>董事会")
        set_single_run_text(sign_org_p, org)
    if sign_date_p is not None:
        set_single_run_text(sign_date_p, data.get("sign_date", "2026年×月×日"))

    # --- 写回（其余部件原样拷贝）---
    new_doc = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as out:
        for item in z.infolist():
            data_bytes = new_doc if item.filename == "word/document.xml" else z.read(item.filename)
            out.writestr(item, data_bytes)
    print("SAVED:", out_path)


def main():
    ap = argparse.ArgumentParser(description="数据驱动生成公告 docx（数据驱动+母版保留样式）")
    ap.add_argument("--base", required=True, help="母版 docx 完整路径（必传）")
    ap.add_argument("--mask", action="store_true", help="脱敏模式（替换真实公司名称为 XX公司）")
    ap.add_argument("--json", required=True, help="内容 JSON 路径")
    ap.add_argument("--out", required=True, help="输出 docx 路径")
    args = ap.parse_args()

    if not os.path.exists(args.base):
        print(f"[错误] 母版不存在: {args.base}")
        return 1
    if not os.path.exists(args.json):
        print(f"[错误] JSON 不存在: {args.json}")
        return 1
    with open(args.json, encoding="utf-8") as f:
        data = json.load(f)
    build(args.base, data, args.out, is_mask=args.mask)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
