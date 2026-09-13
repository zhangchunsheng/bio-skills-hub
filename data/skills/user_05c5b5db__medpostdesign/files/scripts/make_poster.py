#!/usr/bin/env python3
"""Render an A1 portrait academic poster PPTX from poster_data.POSTER.

Run from the project working directory:
    python scripts/make_poster.py

Requires: python-pptx, Pillow. Images referenced in poster_data are resolved
against resources/images/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import poster_common as C
from poster_data import POSTER

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

MM = 36000  # EMU per mm
FONT = "PingFang SC"


def emu(v):
    return Emu(int(v * MM))


def rgb(hex_str):
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---- shape helpers -----------------------------------------------------------
def add_rect(slide, left, top, width, height, fill, line_color=None, line_width=1):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, emu(left), emu(top),
                                   emu(width), emu(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line_color:
        shape.line.color.rgb = rgb(line_color)
        shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    if shape.has_text_frame:
        shape.text_frame.clear()
    return shape


def add_text(slide, left, top, width, height, text, size, color, bold=False,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, font_name=FONT):
    tb = slide.shapes.add_textbox(emu(left), emu(top), emu(width), emu(height))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = rgb(color)
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = align
    tf.vertical_anchor = valign
    return tb


def add_bullets(slide, left, top, width, height, lines, size=C.BODY_PT,
                color=C.COLORS["TEXT_DARK"], bullet="•"):
    tb = slide.shapes.add_textbox(emu(left), emu(top), emu(width), emu(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"{bullet} {line}"
        p.font.size = Pt(size)
        p.font.color.rgb = rgb(color)
        p.font.name = FONT
        p.space_after = Pt(8)
    return tb


def add_picture_fit(slide, img_fn, left, top, max_w, max_h):
    path = img_fn if os.path.isabs(img_fn) else os.path.join(C.IMG_DIR, img_fn)
    if not os.path.exists(path):
        add_text(slide, left, top, max_w, max_h, f"[image missing]\n{img_fn}",
                 C.SMALL_PT, C.COLORS["RED"])
        return
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(max_w / iw, max_h / ih)
    pw, ph = iw * scale, ih * scale
    # convert to mm
    pw_mm, ph_mm = pw / MM, ph / MM
    pl = left + (max_w - pw_mm) / 2
    pt = top + (max_h - ph_mm) / 2
    slide.shapes.add_picture(path, emu(pl), emu(pt), emu(pw_mm), emu(ph_mm))


def add_section_card(slide, left, top, width, height, sec, title_color=C.COLORS["MAIN_BLUE"]):
    add_rect(slide, left, top, width, height, C.COLORS["LIGHT_BG"], C.COLORS["LINE"], 0.75)
    title_h = 18 * MM
    add_text(slide, left + 4 * MM, top + 4 * MM, width - 8 * MM, title_h - 8 * MM,
             sec["title"], C.SECTION_PT, title_color, bold=True)
    body_top = top + title_h + 2 * MM
    body_h = height - title_h - 6 * MM
    img = sec.get("img")
    if img:
        img_h = (sec.get("img_h_mm") or 70) * MM
        img_y = top + height - img_h - 10 * MM
        add_picture_fit(slide, img, left + 6 * MM, img_y, width - 12 * MM, img_h)
        cap = sec.get("img_cap")
        if cap:
            add_text(slide, left + 6 * MM, img_y + img_h + 1 * MM, width - 12 * MM, 8 * MM,
                     cap, 12, C.COLORS["AUX_GRAY"], align=PP_ALIGN.CENTER)
        body_h = img_y - body_top - 4 * MM
    add_bullets(slide, left + 4 * MM, body_top, width - 8 * MM, body_h,
                sec.get("bullets", []), size=C.BODY_PT)


# ---- build -------------------------------------------------------------------
def main():
    prs = Presentation()
    prs.slide_width = emu(C.W_MM)
    prs.slide_height = emu(C.H_MM)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    W = C.W_MM
    M = C.M_MM
    G = C.G_MM
    COL_W = C.COL_W_MM

    # Top banner
    add_rect(slide, 0, 0, W, C.TOP_BANNER_H, C.COLORS["DARK_BLUE"])
    add_text(slide, M, 4 * MM, W - 2 * M, 12 * MM,
             "DRAFT — PENDING MEDICAL & REGULATORY REVIEW · 仅供内部审核 · 不得对外发布",
             C.DRAFT_PT, C.COLORS["WHITE"], bold=True,
             align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

    # Header
    add_text(slide, M, C.TOP_BANNER_H + 10 * MM, W - 2 * M, 45 * MM,
             POSTER["title"], C.TITLE_PT, C.COLORS["DARK_BLUE"], bold=True)
    add_text(slide, M, C.TOP_BANNER_H + 58 * MM, W - 2 * M, 22 * MM,
             POSTER.get("subtitle", ""), C.SUBTITLE_PT, C.COLORS["MID_BLUE"])
    if POSTER.get("author_line"):
        add_text(slide, M, C.TOP_BANNER_H + 88 * MM, W - 2 * M, 16 * MM,
                 POSTER["author_line"], C.SMALL_PT, C.COLORS["TEXT_GRAY"], align=PP_ALIGN.RIGHT)

    # Top 3-column section
    col_y = C.TOP_SEC_Y + 5 * MM
    col_h = C.TOP_SEC_H - 10 * MM
    for i, sec in enumerate(POSTER["top_sections"][:3]):
        x = M + i * (COL_W + G)
        add_section_card(slide, x, col_y, COL_W, col_h, sec)

    # Cases section
    cy = C.CASE_SEC_Y
    add_rect(slide, M, cy, W - 2 * M, C.CASE_TITLE_H, C.COLORS["MAIN_BLUE"])
    add_text(slide, M, cy + 8 * MM, W - 2 * M, 19 * MM,
             POSTER.get("cases_title", "04  Representative Cases 代表性病例"),
             C.SECTION_PT, C.COLORS["WHITE"], bold=True,
             align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

    card_y = cy + C.CASE_TITLE_H + 8 * MM
    card_h = C.CASE_SEC_H - C.CASE_TITLE_H - 16 * MM
    card_img_h = 140 * MM
    card_body_h = card_h - 10 * MM - card_img_h - 8 * MM - 10 * MM
    for i, case in enumerate(POSTER["cases"][:3]):
        cx = M + i * (COL_W + G)
        add_rect(slide, cx, card_y, COL_W, card_h, C.COLORS["WHITE"], C.COLORS["LINE"], 1)
        add_text(slide, cx + 5 * MM, card_y + 5 * MM, COL_W - 10 * MM, 10 * MM,
                 case["title"], 20, C.COLORS["MAIN_BLUE"], bold=True)
        add_picture_fit(slide, case["img"], cx + 5 * MM, card_y + 18 * MM,
                        COL_W - 10 * MM, card_img_h)
        add_bullets(slide, cx + 5 * MM, card_y + 18 * MM + card_img_h + 5 * MM,
                    COL_W - 10 * MM, card_body_h, case.get("bullets", []),
                    size=17, bullet="·")

    # Bottom two sections
    bot_left_w = (W - 2 * M - G) / 2
    bot_right_x = M + bot_left_w + G
    for i, sec in enumerate(POSTER["bottom_sections"][:2]):
        x = M if i == 0 else bot_right_x
        add_section_card(slide, x, C.BOT_SEC_Y, bot_left_w, C.BOT_SEC_H, sec)

    # Footer
    fy = C.BOT_SEC_Y + C.BOT_SEC_H
    add_rect(slide, 0, fy, W, C.FOOTER_H, C.COLORS["DARK_BLUE"])
    add_text(slide, M, fy + 5 * MM, W - 2 * M, C.FOOTER_H - 10 * MM,
             "\n".join(POSTER.get("footer_lines", [])), C.FOOT_PT,
             C.COLORS["WHITE"], align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP)

    # Speaker notes: Sources + Claim Audit
    notes = slide.notes_slide
    notes.notes_text_frame.text = POSTER.get("notes", "")

    os.makedirs("output", exist_ok=True)
    out = os.path.join("output", POSTER["out_pptx"])
    prs.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
