# -*- coding: utf-8 -*-
"""
article-to-shortvideo · 渲染骨架（Python 兜底方案）
=================================================
把「短视频脚本」渲染为 9:16 竖屏 MP4（无声画面版，字幕已内嵌）。

依赖（managed python 3.13.12）：
    ...python.exe -m pip install pillow numpy opencv-python-headless

用法：
    ...python.exe render_template.py
默认产出 12 秒演示片（DURATION=12）。正式使用把 DURATION 改 60，
并把 SCENES 换成你的真实脚本内容即可。

视觉：医疗深蓝底 + 白底圆角要点卡 + 橙红/蓝强调 + 顶部进度条 + 底部字幕条。
中文：微软雅黑 msyh.ttc（index 1 = 粗体）。
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------- 画布 ----------------
W, H = 1080, 1920
FPS = 30
DURATION = 12          # 秒；正式片改 60
TOTAL = DURATION * FPS

# ---------------- 配色 ----------------
COLORS = {
    "bg":     (14, 42, 71),     # 0E2A47 医疗深蓝
    "bg2":    (20, 56, 92),     # 14385C 顶部次色
    "card":   (255, 255, 255),
    "ink":    (17, 24, 39),     # 卡内深灰文字
    "sub":    (96, 110, 130),   # 次要灰
    "white":  (255, 255, 255),
    "accent": (232, 84, 30),    # E8541E 橙红警示
    "blue":   (42, 111, 219),   # 2A6FDB 强调蓝
    "good":   (34, 160, 110),   # 22A06E 安全绿
}

# ---------------- 字体 ----------------
def _resolve_font():
    cands = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return None

FONT_PATH = _resolve_font()

def fnt(size, bold=False):
    if FONT_PATH and FONT_PATH.lower().endswith(".ttc"):
        idx = 1 if bold else 0
        return ImageFont.truetype(FONT_PATH, size, index=idx)
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()

# ---------------- 绘图辅助 ----------------
def t(d, s, x, y, size, color, bold=False, a=255, anchor="mm"):
    """写文字。color 为 (R,G,B)；a 为透明度 0-255。"""
    d.text((x, y), s, font=fnt(size, bold), fill=color + (int(a),), anchor=anchor)

def rr(d, box, r, fill=None, outline=None, width=3, a=255):
    """圆角矩形。fill/outline 为 (R,G,B)。"""
    if fill is not None:
        d.rounded_rectangle(box, radius=r, fill=fill + (int(a),))
    if outline is not None:
        d.rounded_rectangle(box, radius=r, outline=outline + (int(a),), width=width)

def progress_bar(d, f):
    """顶部 8px 进度条（全局进度）。"""
    d.rectangle([0, 0, W, 8], fill=(255, 255, 255, 60))
    pw = int(W * (f + 1) / TOTAL)
    d.rectangle([0, 0, pw, 8], fill=COLORS["accent"])

def subtitle_bar(img, text):
    """底部半透明字幕条 + 居中白字，返回合成后的 RGB 图。"""
    if not text:
        return img
    bar_h = 200
    y0 = H - bar_h
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([0, y0, W, H], fill=(8, 12, 20, 180))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, ov).convert("RGB")
    d = ImageDraw.Draw(img)
    # 自动按宽度折行（简单按字符数）
    max_chars = 22
    lines = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    lh = 56
    start_y = y0 + (bar_h - lh * len(lines)) // 2 + lh // 2
    for i, ln in enumerate(lines):
        t(d, ln, W // 2, start_y + i * lh, 44, COLORS["white"], bold=True)
    return img

# ---------------- 可复用场景组件 ----------------
def scene_hook(d, local, text):
    """开场钩子：大标题居中，前 12 帧淡入。"""
    a = min(255, local * 22)
    t(d, text, W // 2, H // 2 - 120, 78, COLORS["white"], bold=True, a=a)
    t(d, "—— 一次说清 ——", W // 2, H // 2 - 20, 40, COLORS["accent"], bold=True, a=a)

def scene_point_card(d, local, title, points, accent=COLORS["blue"]):
    """要点卡：标题 + 若干圆角条目，逐条入场。"""
    a0 = min(255, local * 22)
    t(d, title, W // 2, 330, 64, COLORS["white"], bold=True, a=a0)
    y = 500
    row_h = 165
    for i, p in enumerate(points):
        a = min(255, max(0, (local - i * 5) * 32))
        off = max(0, 40 - (local - i * 5) * 6)
        box = [120, y - off, W - 120, y + row_h - 30 - off]
        rr(d, box, 26, fill=COLORS["card"], a=a)
        rr(d, [120, y - off, 150, y + row_h - 30 - off], 26, fill=accent, a=a)
        t(d, str(i + 1), 135, y + (row_h - 30) // 2 - off, 52, COLORS["white"], bold=True, a=a)
        t(d, p, 185, y + (row_h - 30) // 2 - off, 40, COLORS["ink"], anchor="lm", a=a)
        y += row_h + 15

def scene_redline(d, local, lines):
    """安全红线：编号警示。"""
    a0 = min(255, local * 22)
    t(d, "⚠ 用药安全红线", W // 2, 330, 60, COLORS["accent"], bold=True, a=a0)
    y = 520
    for i, p in enumerate(lines):
        a = min(255, max(0, (local - i * 5) * 32))
        rr(d, [120, y, W - 120, y + 150], 22, fill=(60, 24, 16), outline=COLORS["accent"], width=3, a=a)
        t(d, "✕ " + p, 160, y + 75, 38, COLORS["white"], anchor="lm", a=a)
        y += 175

def scene_cta(d, local):
    """结尾互动。"""
    a = min(255, local * 22)
    t(d, "觉得有用？", W // 2, 700, 64, COLORS["white"], bold=True, a=a)
    t(d, "点赞 · 关注 · 评论", W // 2, 800, 60, COLORS["accent"], bold=True, a=a)
    labels = ["点赞收藏", "关注药师", "评论聊聊"]
    bw = 280
    gap = 30
    total_w = bw * 3 + gap * 2
    x = (W - total_w) // 2
    y = 980
    for lab in labels:
        rr(d, [x, y, x + bw, y + 110], 55, fill=COLORS["blue"], a=a)
        t(d, lab, x + bw // 2, y + 55, 38, COLORS["white"], bold=True, a=a)
        x += bw + gap
    t(d, "（科普仅供参考，用药请遵医嘱）", W // 2, 1180, 32, (180, 190, 205), a=a)

# ---------------- 分镜定义（换成你的真实内容） ----------------
# 每项：start/end 为帧号；subtitle 为底部字幕；draw 为绘制函数。
SCENES = [
    {"start": 0,   "end": 4 * FPS,  "subtitle": "科普文，也能变成短视频",
     "draw": lambda d, l: scene_hook(d, l, "一篇文章")},
    {"start": 4 * FPS, "end": 8 * FPS, "subtitle": "核心结论，一条说清",
     "draw": lambda d, l: scene_point_card(
         d, l, "三种要点卡",
         ["水龙头：少产尿酸", "下水道：多排尿酸", "达标值 < 360"], accent=COLORS["blue"])},
    {"start": 8 * FPS, "end": 11 * FPS, "subtitle": "安全红线要记牢",
     "draw": lambda d, l: scene_redline(
         d, l, ["起红疹立刻停药就医", "别自行加量"])},
    {"start": 11 * FPS, "end": TOTAL, "subtitle": "点赞关注，下次不迷路",
     "draw": lambda d, l: scene_cta(d, l)},
]

# ---------------- 逐帧绘制 ----------------
def draw_frame(f):
    img = Image.new("RGB", (W, H), COLORS["bg"])
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 150], fill=COLORS["bg2"])
    progress_bar(d, f)
    scene = None
    for s in SCENES:
        if s["start"] <= f < s["end"]:
            scene = s
            break
    if scene is None:
        scene = SCENES[-1]
    local = f - scene["start"]
    scene["draw"](d, local)
    img = subtitle_bar(img, scene["subtitle"])
    return img

# ---------------- 渲染 ----------------
def main():
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "_demo_render.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, FPS, (W, H))
    if not writer.isOpened():
        raise RuntimeError("VideoWriter 无法打开：检查 opencv-python-headless / fourcc / 输出路径")
    for f in range(TOTAL):
        arr = np.array(draw_frame(f))
        writer.write(arr[:, :, ::-1].copy())  # RGB -> BGR
        if f % 60 == 0:
            print(f"rendered {f}/{TOTAL}")
    writer.release()
    print("DONE ->", out_path)

if __name__ == "__main__":
    main()
