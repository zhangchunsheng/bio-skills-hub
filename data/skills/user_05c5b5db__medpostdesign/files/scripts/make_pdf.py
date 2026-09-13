#!/usr/bin/env python3
"""Render an A1 portrait academic poster PDF from poster_data.POSTER.

Run from the project working directory:
    python scripts/make_pdf.py

Requires: reportlab, Pillow. This is the LibreOffice-free fallback (the
soffice wrapper often exists on macOS but the LibreOffice.app binary is absent,
so PPTX->PDF fails). PDF->PNG QA is done with the system `pdftoppm`.

Font: tries PingFang.ttc / STHeiti Light.ttc, falls back to the built-in CID
font STSong-Light (always renders CJK even with no system CJK TTF).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import poster_common as C
from poster_data import POSTER

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image

# ---- layout in reportlab points (mm * mm) -----------------------------------
W = C.W_MM * mm
H = C.H_MM * mm
M = C.M_MM * mm
G = C.G_MM * mm
COL_W = C.COL_W_MM * mm

BANNER_H = C.TOP_BANNER_H * mm
HEADER_H = C.HEADER_H * mm
TOP_SEC_Y = C.TOP_SEC_Y * mm
TOP_SEC_H = C.TOP_SEC_H * mm
CASE_SEC_Y = C.CASE_SEC_Y * mm
CASE_TITLE_H = C.CASE_TITLE_H * mm
CASE_SEC_H = C.CASE_SEC_H * mm
BOT_SEC_Y = C.BOT_SEC_Y * mm
BOT_SEC_H = C.BOT_SEC_H * mm
FOOTER_H = C.FOOTER_H * mm


def hx(name):
    return HexColor(C.COLORS[name])


def pick_font():
    try:
        pdfmetrics.registerFont(TTFont("PingFang", "/System/Library/Fonts/PingFang.ttc"))
        return "PingFang"
    except Exception:
        try:
            pdfmetrics.registerFont(TTFont("Heiti", "/System/Library/Fonts/STHeiti Light.ttc"))
            return "Heiti"
        except Exception:
            return "STSong-Light"


CN = pick_font()
EN = "Helvetica"


def rect(c, x, y, w, h, fill, stroke=None, stroke_width=0):
    """x, y, w, h are in points; y is the top edge coordinate."""
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(stroke_width)
    else:
        c.setStrokeColor(fill)
    c.rect(x, H - y - h, w, h, fill=1, stroke=1 if stroke else 0)


def text(c, x, y, s, size, color, bold=False, align="L", font=None):
    """x, y are in points; y is the top edge baseline offset."""
    font = font or CN
    c.setFont(font + ("-Bold" if bold and font == EN else ""), size)
    if bold and font == CN:  # ttc bold unreliable; keep weight via size if needed
        c.setFont(CN, size)
    c.setFillColor(color)
    if align == "C":
        c.drawCentredString(x, H - y - size * 0.8, s)
    elif align == "R":
        c.drawRightString(x, H - y - size * 0.8, s)
    else:
        c.drawString(x, H - y - size * 0.8, s)


def wrap(c, x, y, w, h, lines, size, color, leading=1.3, bullet="·"):
    c.setFont(CN, size)
    c.setFillColor(color)
    line_h = size * leading
    cy = y
    max_chars = int(w / (size * 0.9))
    for line in lines:
        buf = f"{bullet} {line}"
        while buf:
            chunk = buf[:max_chars]
            if len(buf) > max_chars and buf[max_chars] not in " \n":
                cut = chunk.rfind(" ")
                if cut > max_chars * 0.6:
                    chunk = chunk[:cut]
            c.drawString(x, H - cy - size, chunk)
            buf = buf[len(chunk):].lstrip()
            cy += line_h
            if cy > y + h:
                break


def fit_image(c, img_fn, x, y, max_w, max_h):
    path = img_fn if os.path.isabs(img_fn) else os.path.join(C.IMG_DIR, img_fn)
    if not os.path.exists(path):
        c.setFillColor(hx("RED"))
        c.drawString(x, H - y - 12, f"[missing {os.path.basename(img_fn)}]")
        return
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(max_w / iw, max_h / ih)
    pw, ph = iw * scale, ih * scale
    left = x + (max_w - pw) / 2
    top = y + (max_h - ph) / 2
    c.drawImage(path, left, H - top - ph, width=pw, height=ph)


def section_card(c, x, y, w, h, sec, title_color=None):
    """Draw a top/bottom section card. x,y,w,h in points."""
    title_color = title_color or hx("MAIN_BLUE")
    rect(c, x, y, w, h, hx("LIGHT_BG"), hx("LINE"), 1)
    text(c, x + 4 * mm, y + 6 * mm, sec["title"], 22, title_color, bold=True)
    title_h = 18 * mm
    body_top = y + title_h + 2 * mm
    body_h = h - title_h - 6 * mm
    img = sec.get("img")
    if img:
        img_h = (sec.get("img_h_mm") or 70) * mm
        img_y = y + h - img_h - 8 * mm
        fit_image(c, img, x + 6 * mm, img_y, w - 12 * mm, img_h)
        if sec.get("img_cap"):
            text(c, x + w / 2, img_y + img_h + 2 * mm, sec["img_cap"], 10,
                 hx("AUX_GRAY"), align="C")
        body_h = img_y - body_top - 4 * mm
    wrap(c, x + 4 * mm, body_top, w - 8 * mm, body_h,
         sec.get("bullets", []), 15, hx("TEXT_DARK"))


def main():
    os.makedirs("output", exist_ok=True)
    c = canvas.Canvas(os.path.join("output", POSTER["out_pdf"]), pagesize=(W, H))

    # Top banner
    rect(c, 0, 0, W, BANNER_H, hx("DARK_BLUE"))
    text(c, W / 2, 6 * mm,
         "DRAFT — PENDING MEDICAL & REGULATORY REVIEW · 仅供内部审核 · 不得对外发布",
         13, hx("WHITE"), bold=True, align="C", font=CN)

    # Header
    text(c, M, BANNER_H + 12 * mm, POSTER["title"], 40,
         hx("DARK_BLUE"), bold=True, font=CN)
    if POSTER.get("subtitle"):
        text(c, M, BANNER_H + 55 * mm, POSTER["subtitle"], 17,
             hx("MID_BLUE"), font=EN)
    if POSTER.get("author_line"):
        text(c, W - M, BANNER_H + 82 * mm, POSTER["author_line"], 12,
             hx("TEXT_GRAY"), align="R", font=CN)

    # Top 3-column section
    col_y = TOP_SEC_Y + 5 * mm
    col_h = TOP_SEC_H - 10 * mm
    for i, sec in enumerate(POSTER["top_sections"][:3]):
        x = M + i * (COL_W + G)
        section_card(c, x, col_y, COL_W, col_h, sec)

    # Cases section
    rect(c, M, CASE_SEC_Y, W - 2 * M, CASE_TITLE_H, hx("MAIN_BLUE"))
    text(c, W / 2, CASE_SEC_Y + 11 * mm,
         POSTER.get("cases_title", "04  Representative Cases 代表性病例"),
         22, hx("WHITE"), bold=True, align="C", font=CN)

    card_y = CASE_SEC_Y + CASE_TITLE_H + 8 * mm
    card_h = CASE_SEC_H - CASE_TITLE_H - 16 * mm
    card_img_h = 155 * mm
    case_body_h = card_h - 18 * mm - card_img_h - 12 * mm
    for i, case in enumerate(POSTER["cases"][:3]):
        cx = M + i * (COL_W + G)
        rect(c, cx, card_y, COL_W, card_h, hx("WHITE"), hx("LINE"), 1)
        text(c, cx + 5 * mm, card_y + 7 * mm, case["title"], 16,
             hx("MAIN_BLUE"), bold=True, font=CN)
        fit_image(c, case["img"], cx + 5 * mm, card_y + 20 * mm,
                  COL_W - 10 * mm, card_img_h)
        wrap(c, cx + 5 * mm, card_y + 20 * mm + card_img_h + 6 * mm,
             COL_W - 10 * mm, case_body_h, case.get("bullets", []), 13,
             hx("TEXT_DARK"), leading=1.4, bullet="·")

    # Bottom section
    bot_left_w = (W - 2 * M - G) / 2
    bot_right_x = M + bot_left_w + G
    for i, sec in enumerate(POSTER["bottom_sections"][:2]):
        x = M if i == 0 else bot_right_x
        section_card(c, x, BOT_SEC_Y, bot_left_w, BOT_SEC_H, sec)

    # Footer
    footer_y = BOT_SEC_Y + BOT_SEC_H
    rect(c, 0, footer_y, W, FOOTER_H, hx("DARK_BLUE"))
    yf = footer_y + 6 * mm
    for line in POSTER.get("footer_lines", []):
        text(c, M, yf, line, 11, hx("WHITE"), font=CN)
        yf += 11 * mm

    c.save()
    print(f"Saved: output/{POSTER['out_pdf']}")


if __name__ == "__main__":
    main()
