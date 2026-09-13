# -*- coding: utf-8 -*-
"""
药学科普漫画 → 独立 Word 文档生成器（数据驱动）。
每则漫画（COMICS 中的一个 dict）生成一份同名的 .docx，含：
  标题/副标题/关键词、导语、起承转合四段（分镜图 + 角色对白）、
  可选「药师插话」、结尾「药师说·临床要点」、免责声明。

用法：
  1. 编辑下方 COMICS 列表（填入你的故事与分镜图路径）。
  2. 运行：python build_comic_docx.py
  3. 在当前目录得到每个故事的 .docx。

依赖：pip install python-docx
"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# ============ 配置区：按你的故事修改 ============
BASE = os.getcwd()                       # 输出与图片基准目录
PANELS = os.path.join(BASE, "comic_panels")  # 分镜图所在文件夹

# 颜色
INK = RGBColor(0x22, 0x22, 0x22)
RED = RGBColor(0xC0, 0x39, 0x2B)
BLUE = RGBColor(0x1F, 0x4E, 0x79)
ORANGE = RGBColor(0xD3, 0x54, 0x00)
STAGE_COLOR = {"起": RGBColor(0x27, 0xAE, 0x60),
               "承": BLUE,
               "转": RED,
               "合": RGBColor(0x8E, 0x44, 0xAD)}

# 示例数据（替换成你自己的故事）
COMICS = [
    {
        "title": "老周停药惊魂记",
        "subtitle": "方向：降压药能自己停吗？——高血压最常见的致命误区",
        "chip": "关键词：擅自停药 · 血压反弹 · 急诊",
        "lead": "高血压有个「温柔的陷阱」：药一吃上去，血压就乖了，人也就放松了。"
                "但「血压正常」是药在「压着」它，不是病好了。下面这段，是老周真实演绎的翻车现场。",
        "panels": [
            {"stage": "起 · 错误认知", "image": "Old_Master_Q_gag_comic__black__2026-08-10T09-01-20.png",
             "speaker": "老周：", "text": "“120/80，稳了！这降压药我吃了大半年，肯定根治啦——明儿起不吃了，省钱又省事！”（顺手把药瓶扔上天）", "red": False},
            {"stage": "承 · 暗中埋雷", "image": "Monochrome_pen_cartoon_like_La_2026-08-10T09-01-19.png",
             "speaker": "老周：", "text": "几天后搬东西，突然眼前发黑、天旋地转，扶着墙直晃：“咦？咋站都站不稳……”", "red": False},
            {"stage": "转 · 冲突爆发", "image": "Hong_Kong_humor_comic_strip__i_2026-08-10T09-01-19.png",
             "speaker": "医生：", "text": "“老周！你擅自停降压药，血压飙到 190！差点脑出血！这药是『长期稳住』，不是『治好就扔』！”", "red": True},
            {"stage": "合 · 改正收尾", "image": "Black_and_white_hand_drawn_com_2026-08-10T09-01-19.png",
             "speaker": "老周：", "text": "“药师啊，以后血压再漂亮我也不敢自己停了。”", "red": False,
             "speaker2": "药师：", "text2": "“对喽，调药找医生，别跟自己的血管赌气。”👍"},
        ],
        "info": "血压计上那个漂亮数字，是药物在你身体里「撑着」的结果。高血压大多是终身病，靠药「稳住」，不是「治好就扔」。",
        "info_after": 1,  # 在第几段之后插入「药师插话」（0 起算；None 则不插）
        "rx": [
            "多数高血压需长期甚至终身服药。血压「正常」是药物在「压着」，擅自停药极易反弹，可诱发心梗、脑卒中等急症。",
            "减量或停药必须由医生评估，切莫凭感觉。定期监测、规律复诊，才是和血压相处的正确姿势。",
        ],
    },
    {
        "title": "西柚刺客",
        "subtitle": "方向：他汀类降脂药 + 西柚（葡萄柚）——被忽视的食物相互作用",
        "chip": "关键词：他汀 · 西柚 · CYP3A4 · 伤肌肉",
        "lead": "很多人以为「吃药忌口」只是别喝酒。其实有一种水果，对他汀类降脂药来说，"
                "是低调又危险的「隐形刺客」——西柚（葡萄柚）。",
        "panels": [
            {"stage": "起 · 错误认知", "image": "Old_Master_Q_style_ink_gag_pan_2026-08-10T09-01-19.png",
             "speaker": "老周：", "text": "体检血脂偏高，攥着他汀药瓶乐呵：“降脂药嘛，一天一颗，小意思！”", "red": False},
            {"stage": "承 · 暗中埋雷", "image": "Lao_Fu_Zi_monochrome_comic__th_2026-08-10T09-01-19.png",
             "speaker": "老周：", "text": "迷上西柚：“这玩意清火又减肥，我一天半个，美滋滋！”（大口啃）", "red": False},
            {"stage": "转 · 真相点破", "image": "Black_and_white_pen_comic_like_2026-08-10T09-01-19.png",
             "speaker": "药师：", "text": "“你吃他汀还猛啃西柚？西柚把肝脏代谢酶『绑』住了，他汀全堆在血里，伤肌肉伤肝！”", "red": True},
            {"stage": "合 · 改正收尾", "image": "Humorous_ink_drawing_in_the_Ol_2026-08-10T09-01-20.png",
             "speaker": "老周：", "text": "把西柚扔进垃圾桶，改举苹果：“原来西柚是『隐形刺客』！”", "red": False,
             "speaker2": "药师：", "text2": "“吃他汀期间，西柚、橙柚先歇歇，水果换苹果香蕉更安全。”👍"},
        ],
        "info": "西柚里的「呋喃香豆素」会抑制肝脏里的 CYP3A4 酶——这酶正好是很多他汀的代谢通道。酶被「绑住」，他汀就堆在血里下不来。",
        "info_after": 1,
        "rx": [
            "阿托伐他汀、辛伐他汀等经 CYP3A4 代谢，大量西柚会显著升高其血药浓度，增加肌病/横纹肌溶解、肝损伤风险。",
            "服他汀期间避免大量西柚，其他橙柚类也需留意；用药前问药师，别让「健康水果」变「伤身刺客」。",
        ],
    },
]
# ============ 以下一般无需修改 ============


def set_cjk(run, font="微软雅黑"):
    run.font.name = font
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = rpr.makeelement(qn('w:rFonts'), {})
        rpr.append(rf)
    for a in ('w:ascii', 'w:eastAsia', 'w:hAnsi'):
        rf.set(qn(a), font)


def add_stage(doc, stage_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"【{stage_text}】")
    r.bold = True
    r.font.size = Pt(13)
    set_cjk(r)
    key = stage_text[0]
    r.font.color.rgb = STAGE_COLOR.get(key, INK)


def add_image(doc, img_path, width=4.6):
    if os.path.exists(img_path):
        doc.add_picture(img_path, width=Inches(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        warn = doc.add_paragraph()
        wr = warn.add_run(f"[图片缺失：{img_path}]")
        wr.italic = True
        set_cjk(wr)
        wr.font.color.rgb = RGBColor(0x99, 0x99, 0x99)


def add_dialogue(doc, who, text, red=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    r1 = p.add_run(who)
    r1.bold = True
    r1.font.size = Pt(12.5)
    set_cjk(r1)
    r1.font.color.rgb = RED if red else BLUE
    r2 = p.add_run(text)
    r2.font.size = Pt(12.5)
    set_cjk(r2)
    r2.font.color.rgb = INK


def add_info(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.15)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    r0 = p.add_run("💡 药师插话：")
    r0.bold = True
    r0.font.size = Pt(12)
    set_cjk(r0)
    r0.font.color.rgb = ORANGE
    r = p.add_run(text)
    r.font.size = Pt(12)
    set_cjk(r)
    r.font.color.rgb = RGBColor(0x5A, 0x4A, 0x2A)


def add_rx(doc, points):
    title = doc.add_paragraph()
    title.paragraph_format.space_before = Pt(10)
    tr = title.add_run("药师说 · 临床要点")
    tr.bold = True
    tr.font.size = Pt(14)
    set_cjk(tr)
    tr.font.color.rgb = RED
    for t in points:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(t)
        r.font.size = Pt(12)
        set_cjk(r)
        r.font.color.rgb = INK


def build_one(comic):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "微软雅黑"
    style.font.size = Pt(12)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

    # 抬头
    h = doc.add_paragraph(); h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hr = h.add_run(comic["title"]); hr.bold = True; hr.font.size = Pt(20)
    set_cjk(hr); hr.font.color.rgb = RED if "停药" in comic["title"] else ORANGE
    s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = s.add_run(comic["subtitle"]); sr.font.size = Pt(12); set_cjk(sr)
    sr.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cr = c.add_run(comic["chip"]); cr.font.size = Pt(11); cr.italic = True
    set_cjk(cr); cr.font.color.rgb = INK

    # 导语
    lp = doc.add_paragraph(); lp.paragraph_format.space_after = Pt(8)
    lr = lp.add_run(comic["lead"]); lr.font.size = Pt(12.5); set_cjk(lr)
    lr.font.color.rgb = INK

    info_after = comic.get("info_after", None)
    for i, panel in enumerate(comic["panels"]):
        add_stage(doc, panel["stage"])
        add_image(doc, os.path.join(PANELS, panel["image"]))
        add_dialogue(doc, panel.get("speaker", ""), panel.get("text", ""),
                     red=panel.get("red", False))
        if panel.get("speaker2"):
            add_dialogue(doc, panel["speaker2"], panel.get("text2", ""))
        if info_after is not None and i == info_after and comic.get("info"):
            add_info(doc, comic["info"])

    add_rx(doc, comic.get("rx", []))

    foot = doc.add_paragraph()
    fr = foot.add_run("⚠️ 仅供健康科普，不能替代医生诊疗。具体用药请遵医嘱或咨询药师。")
    fr.font.size = Pt(10); fr.italic = True; set_cjk(fr)
    fr.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    safe = "".join(ch for ch in comic["title"] if ch.isalnum() or ch in "一二三四五六七八九十")
    out = os.path.join(BASE, f"{comic['title']}.docx")
    doc.save(out)
    return out


if __name__ == "__main__":
    for comic in COMICS:
        print("已生成:", build_one(comic))
