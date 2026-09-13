# -*- coding: utf-8 -*-
"""Generate share assets for the 动漫剧荒推荐 report（纯文字 · 仅动漫）。

设计方向（纯文字、无封面）：
   - 片单输出 = 作品名 + 标签 + 简介 + 推荐理由 四要素，纯文字卡片，不含任何封面图；
   - 推荐范围 = 仅动漫（不推荐任何电视剧 / 电影）。

   - Personality cards: 12 人格，各有签名色 + mascot + tagline + 六维 DNA 档案。
   - share_persona.png : 用户人格卡（热忱群像派）作为分享图。
   - share_list.png    : 纯文字片单长图。
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from works_pool import PERSONA_VECS, pool_query, infer_region_priority, name_key, series_key
from curation import is_blocked  # 争议作品兜底拦截（渲染层最后一道护栏）

# 路径一律相对脚本，确保 skill 包移动到任何机器都能跑
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STICK = os.path.join(ROOT, "assets", "stickers")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

def find_font():
    """优先用包内 assets/fonts 的嵌入字体（跨平台一致），否则回退到各 OS 常见中文字体。"""
    if os.path.isdir(FONT_DIR):
        for fn in sorted(os.listdir(FONT_DIR)):
            if fn.lower().endswith((".ttf", ".ttc", ".otf")):
                return os.path.join(FONT_DIR, fn)
    candidates = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError(
        "未找到中文字体：请在 assets/fonts/ 放入一个 CJK 字体（如 Hiragino Sans GB.ttc）")

FONT = find_font()

W = 1080
H = 1920

# ---------- tier palette（五档推荐：命名 + 低饱和主题色）----------
TIER = {
    "like":     ("你的本命", (201, 123, 98)),    # 珊瑚橙 #C97B62
    "expand":   ("上头预警", (111, 148, 102)),   # 抹茶绿 #6F9466
    "try":      ("开个盲盒", (95, 126, 150)),    # 雾霾蓝 #5F7E96
    "niche":    ("宝藏冷门", (138, 107, 159)),   # 香芋紫 #8A6B9F
    "neighbor": ("意外惊喜", (168, 126, 92)),    # 奶咖 #A87E5C
}

# 五档释义（用于片单图例，与标签成对展示）
TIER_DESC = {
    "like":     "跟你的观影 DNA 严丝合缝，闭眼入都稳的灵魂番",
    "expand":   "不是百分百对口，但那股劲一上来就停不下来",
    "try":      "跳出舒适区换换口味，说不定撞上意外之喜",
    "niche":    "不一定是热门作品，质量却在线，看完你会懂",
    "neighbor": "不在你原清单里，按口味顺手捞的，常常最戳人",
}

# 片单整体配色（奶油白底 + 深巧克力棕主色）
CREAM = (255, 247, 238)          # #FFF7EE 奶油白
CREAM_DEEP = (255, 240, 228)     # 底渐变下沿
COCOA = (92, 63, 43)             # #5C3F2B 深巧克力棕（头图/页脚主色）
COCOA_SOFT = (232, 201, 176)     # 头图浅蜜桃辅助文字
INK_TITLE = (74, 43, 26)         # 作品名标题 深棕
INK_BODY = (122, 106, 90)        # 简介正文 暖灰棕
INK_REASON = (184, 106, 78)      # 推荐理由 珊瑚棕
CARD_BORDER = (240, 224, 208)    # 卡片描边（更淡的暖色）

# ---------- color helpers ----------
def hx(s):
    s = s.lstrip("#")
    return (int(s[0:2],16), int(s[2:4],16), int(s[4:6],16))

def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def lum(c):
    r, g, b = [v/255 for v in c]
    return 0.2126*r + 0.7152*g + 0.0722*b

def ink_on(c):
    return "#1a1208" if lum(c) > 0.55 else "#ffffff"

def font(size, bold=True):
    try:
        return ImageFont.truetype(FONT, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.truetype(FONT, size, index=0)

# ---------- drawing helpers ----------
def vgradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=mix(top, bottom, t))
    return img

def radial_glow(size, color, a=120):
    s = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    cx = cy = size // 2
    for i in range(60, 0, -1):
        r = int(cx * i / 60)
        alpha = int(a * (1 - i/60) ** 1.4)
        sd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color + (alpha,))
    return s.filter(ImageFilter.GaussianBlur(8))

def rounded_card(x, y, w, h, r, fill, border=None, bw=0):
    w, h, r = int(round(w)), int(round(h)), int(round(r))
    # solid fill first, then mask corners -> no black corner artifacts
    layer = Image.new("RGBA", (w, h), fill + (255,))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    layer.putalpha(mask)
    if border:
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle([0, 0, w, h], radius=r, outline=border + (255,), width=bw)
    return layer

def _wrap_cjk(text, f, max_w):
    lines, cur = [], ""
    for ch in text:
        if text_w(cur + ch, f) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines or [text]

def text_w(txt, f):
    return ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=f)

def center(draw, xy, txt, f, fill, stroke=0, sc=None):
    x, y = xy
    if stroke:
        draw.text((x, y), txt, font=f, fill=sc or "#ffffff", anchor="mm", stroke_width=stroke)
    draw.text((x, y), txt, font=f, fill=fill, anchor="mm")

def center_left(draw, xy, txt, f, fill):
    draw.text(xy, txt, font=f, fill=fill, anchor="lm")

def center_right(draw, xy, txt, f, fill):
    draw.text(xy, txt, font=f, fill=fill, anchor="rm")

def pill(draw, cx, cy, txt, f, fill, fg, pad_x=22, h=None):
    w = text_w(txt, f) + pad_x*2
    h = h or (f.size + 24)
    x0, y0 = cx - w//2, cy - h//2
    draw.rounded_rectangle([x0, y0, x0+w, y0+h], radius=h//2, fill=fill)
    draw.text((cx, cy), txt, font=f, fill=fg, anchor="mm")

def draw_brandbar(draw, y0=0, bar_h=96, bg=COCOA):
    """头部品牌栏：左=动漫剧荒推荐（产品名，主） 右=Anime Recommender（技能名，次）。
    供一页图 / 人格卡 / 片单页脚统一调用，保证双名出现位置与层级一致。"""
    if bg is not None:
        draw.rectangle([0, y0, W, y0 + bar_h], fill=bg)
    # 底部分隔线（浅蜜桃，低存在感）
    draw.line([(0, y0 + bar_h), (W, y0 + bar_h)], fill=COCOA_SOFT, width=3)
    cy = y0 + bar_h // 2
    # 左：logo 标记（圆角暖橙）+ 动漫剧荒推荐
    ls = 56
    lx, ly = 52, cy - ls // 2
    draw.rounded_rectangle([lx, ly, lx + ls, ly + ls], radius=14, fill=(232, 160, 107))
    center(draw, (lx + ls // 2, cy), "剧", font(34, True), (255, 255, 255))
    center_left(draw, (lx + ls + 22, cy), "动漫剧荒推荐", font(40, True), (255, 255, 255))
    # 右：SKILL 胶囊 + Anime Recommender（字号加大、加粗，更显眼）
    snf = font(34, True); sn = "Anime Recommender"; snw = text_w(sn, snf)
    cf = font(18, True); ct = "SKILL"; cw = text_w(ct, cf) + 24
    chip_x = W - 52 - snw - 18 - cw
    draw.rounded_rectangle([chip_x, cy - 18, chip_x + cw, cy + 18], radius=9, fill=COCOA_SOFT)
    center(draw, (chip_x + cw // 2, cy), ct, cf, COCOA)
    center_right(draw, (W - 52, cy), sn, snf, COCOA_SOFT)

# ================= 12 人格数据 =================
# name, tagline, trio(3 tags), vec(沉浸/情感/智识/暗度/群像/冒险), top, bot, accent, sticker, rainbow?
PERSONAS = [
    dict(name="暗夜造梦师", tagline="在虚构宇宙里，把人性的深渊当游乐园",
         trio=["暗黑","世界观","人性深渊"], vec=(75,55,70,75,45,55),
         top="#1A1036", bot="#2E1F5E", accent="#8B7BF0",
         sticker="Mysterious_cool_anime_mascot_s_2026-08-20T14-11-38.png"),
    dict(name="温暖治愈系", tagline="用一部暖剧，把被生活揉皱的心抚平",
         trio=["温暖","日常","治愈"], vec=(35,75,35,20,55,35),
         top="#E08A6B", bot="#F2B39A", accent="#FFD9A0",
         sticker="Cozy_gentle_anime_mascot_stick_2026-08-20T14-11-38.png"),
    dict(name="智性探索者", tagline="不烧脑，毋宁死",
         trio=["烧脑","思辨","实验叙事"], vec=(55,35,80,45,30,70),
         top="#07343E", bot="#0F5C6B", accent="#2EC4B6",
         sticker="Pensive_spectacled_anime_masco_2026-08-20T14-29-41.png"),
    dict(name="情感深渊潜行者", tagline="越痛越上头，在悲剧里找自己",
         trio=["悲剧","情感冲击","挣扎"], vec=(50,75,40,75,45,35),
         top="#3A0F2A", bot="#5E1A47", accent="#F25C9A",
         sticker="Melancholic_teardrop_anime_mas_2026-08-20T14-29-41.png"),
    dict(name="冒险浪漫派", tagline="新鲜感 + 心动，一个都不能少",
         trio=["新鲜","浪漫","实验"], vec=(55,70,50,30,55,75),
         top="#8A1C55", bot="#C23B7A", accent="#FF9EC4",
         sticker="Playful_kaleidoscope_anime_mas_2026-08-20T14-29-41.png"),
    dict(name="世界观建筑师", tagline="为一整套设定，能聊三天三夜",
         trio=["设定","细节","宇宙"], vec=(80,50,70,30,30,50),
         top="#122B47", bot="#1E4A78", accent="#5BA7E0",
         sticker="Architect_like_anime_mascot_st_2026-08-20T14-29-41.png"),
    dict(name="纯粹感受者", tagline="别讲道理，把我的情绪填满就好",
         trio=["直觉","情绪","沉浸"], vec=(35,75,25,25,55,35),
         top="#C99A00", bot="#E8B53A", accent="#FFE08A",
         sticker="Joyful_carefree_anime_mascot_s_2026-08-20T14-29-41.png"),
    dict(name="暗黑实验家", tagline="越怪越爽，挑战底线才带劲",
         trio=["前卫","挑衅","极限"], vec=(50,35,65,75,30,75),
         top="#0E0E18", bot="#1E1E30", accent="#2EE6A6",
         sticker="Avant_garde_glitchy_anime_masc_2026-08-20T14-29-41.png"),
    dict(name="现实凝视者", tagline="拒绝造梦，只想看清人间真实",
         trio=["冷峻","真实","思考"], vec=(30,55,70,65,45,50),
         top="#243029", bot="#3A4A3F", accent="#A3C9A8",
         sticker="Stern_realistic_anime_mascot_s_2026-08-20T14-29-41.png"),
    dict(name="复杂共情者", tagline="灰度里的人性，比非黑即白更迷人",
         trio=["灰度","复杂","共情"], vec=(55,65,65,60,45,50),
         top="#2E2540", bot="#4A3F5C", accent="#C8B6FF",
         sticker="Empathetic_conflicted_anime_ma_2026-08-20T14-29-41.png"),
    dict(name="热忱群像派", tagline="为「一群普通人并肩成长」热血到爆",
         trio=["热血","治愈","群像"], vec=(45,70,50,25,90,55),
         top="#A8401A", bot="#C2562B", accent="#FFD9BF",
         sticker="Cheerful_energetic_anime_masco_2026-08-20T14-11-38.png"),
    dict(name="多元观影者", tagline="今天的口味，由心情决定",
         trio=["多元","均衡","无固定"], vec=(50,50,50,50,50,50),
         top="#6C5CE7", bot="#C77DFF", accent="#FFE08A", rainbow=True,
         sticker="Whimsical_starry_eyed_anime_ma_2026-08-20T14-29-41.png"),
]

DIMS = ["沉浸度","情感度","智识度","暗度","群像度","冒险度"]

def _mascot_image(p, size):
    """返回人格 mascot 的 RGBA 图（已圆形裁切，size × size）。

    贴图来源优先级（保证任意分发形态都能出图）：
      ① stickers_data.load(人格名) —— base64 内嵌，随包分发，无需 PNG 文件，
         因此 SkillHub 等「禁止上传二进制」的平台也能渲染卡通形象；
      ② assets/stickers/<sticker>.png —— 完整包（含 PNG）时的高清贴图；
      ③ 降级：贴图都缺失时画「签名色圆盘 + 人格名前两字」，出图不中断。
    """
    name = p.get("name")
    # ① base64 内嵌贴图（首选，跨平台零依赖文件）
    try:
        from stickers_data import load as _load_sticker
        st = _load_sticker(name)
        if st is not None:
            st = st.resize((size, size), Image.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
            st.putalpha(ImageChops.multiply(mask, st.split()[3]))
            return st
    except Exception:
        pass
    # ② assets/stickers PNG（完整包）
    path = os.path.join(STICK, p.get("sticker") or "")
    if p.get("sticker") and os.path.isfile(path):
        try:
            st = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
            st.putalpha(ImageChops.multiply(mask, st.split()[3]))
            return st
        except Exception:
            pass
    # ③ 降级签名色徽章
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img)
    dd.ellipse([0, 0, size - 1, size - 1], fill=p.get("accent") or "#8B7BF0")
    label = (p.get("name") or "?")[:2]
    f = font(max(18, int(size * 0.30)), True)
    dd.text((size / 2, size / 2), label, font=f, fill=(255, 255, 255), anchor="mm")
    return img


def build_persona(p, idx, out_path):
    top, bot, accent = hx(p["top"]), hx(p["bot"]), hx(p["accent"])
    accent_fg = ink_on(accent)

    # background (gradient, or rainbow for 多元观影者)
    if p.get("rainbow"):
        canvas = Image.new("RGB", (W, H))
        d0 = ImageDraw.Draw(canvas)
        for y in range(H):
            t = y / (H-1)
            hue = 280 - 200*t   # violet -> orange
            d0.line([(0, y), (W, y)], fill=hsl(hue, 0.55, 0.42 + 0.06*math.sin(t*3)))
        bg_deep = hx("#6C5CE7")
    else:
        canvas = vgradient(W, H, top, bot)
        bg_deep = top
    d = ImageDraw.Draw(canvas)

    # geometric motif: big accent ring behind mascot
    glow = radial_glow(760, accent, 130); canvas.paste(glow, (W//2-380, 470-380), glow)

    # top brand + kicker + index（动漫剧荒推荐 × Anime Recommender）
    center_left(d, (60, 80), "动漫剧荒推荐", font(34, True), "#ffffff")
    center_right(d, (W-60, 80), "Anime Recommender", font(32, True), "#ffffff")
    center_left(d, (60, 118), "我的观影人格  PERSONALITY", font(24, False), accent)
    center_right(d, (W-60, 118), f"No.{idx+1:02d} / 12", font(26, False), accent)

    # HERO name (huge, outlined for legibility on any bg)
    nm = p["name"]; nsize = 128 if len(nm) <= 5 else 108
    nf = font(nsize, True)
    stroke_c = mix(bg_deep, (0,0,0), 0.5)
    center(d, (W//2, 344), nm, nf, "#ffffff", stroke=7, sc=stroke_c)

    # mascot badge
    cx, cy, r = W//2, 722, 196
    d.ellipse([cx-r-16, cy-r-16, cx+r+16, cy+r+16], fill=(255,255,255))
    d.ellipse([cx-r-16, cy-r-16, cx+r+16, cy+r+16], outline=accent, width=8)
    st = _mascot_image(p, 2*r)          # 贴图缺失时自动降级为签名色徽章
    canvas.paste(st, (cx-r, cy-r), st)

    # tagline pill
    pill(d, W//2, 1002, p["tagline"], font(33, True), accent, accent_fg, pad_x=40, h=72)

    # trio tags (outline pills on dark panel area)
    tri = p["trio"]; tf = font(26, True)
    tws = [text_w(t, tf) + 44 for t in tri]
    gap = 18; total = sum(tws) + gap*(len(tri)-1)
    sx = (W-total)//2
    for i, t in enumerate(tri):
        x = sx + sum(tws[:i]) + gap*i
        d.rounded_rectangle([x, 1074, x+tws[i], 1118], radius=22, outline=accent, width=3)
        d.text((x+tws[i]//2, 1096), t, font=tf, fill=accent, anchor="mm")

    # DNA spec panel (dark, technical "spec sheet" look)
    panel_x, panel_y, panel_w, panel_h = 60, 1162, W-120, 600
    panel = mix(bg_deep, (0,0,0), 0.5)
    panel_layer = rounded_card(panel_x, panel_y, panel_w, panel_h, 30, panel, border=accent, bw=3)
    canvas.paste(panel_layer, (panel_x, panel_y), panel_layer)
    center_left(d, (panel_x+46, panel_y+52), "观影 DNA · 六维档案", font(30, True), "#ffffff")
    center_right(d, (panel_x+panel_w-46, panel_y+52), "6-DIM PROFILE", font(24, False), accent)

    rows_y = panel_y + 110
    for i, (dim, v) in enumerate(zip(DIMS, p["vec"])):
        ry = rows_y + i*74
        cyrow = ry + 30
        center_left(d, (panel_x+46, cyrow), dim, font(30, True), "#ffffff")
        bx0 = panel_x+235; bx1 = panel_x+panel_w-150; bw = bx1-bx0
        d.rounded_rectangle([bx0, cyrow-13, bx1, cyrow+13], radius=13, fill=mix(panel,(255,255,255),0.14))
        fw = int(bw*v/100)
        if fw > 4:
            d.rounded_rectangle([bx0, cyrow-13, bx0+fw, cyrow+13], radius=13, fill=accent)
        center_right(d, (panel_x+panel_w-46, cyrow), f"{v:02d}", font(32, True), accent)

    # footer CTA
    d.rectangle([0, 1788, W, H], fill=accent)
    center(d, (W//2, 1856), "你也来测测你的观影人格      @动漫剧荒推荐", font(34, True), accent_fg)

    canvas.save(out_path)
    print("saved", out_path)

def hsl(h, s, l):
    h = h % 360
    c = (1 - abs(2*l-1)) * s
    x = c * (1 - abs((h/60) % 2 - 1))
    m = l - c/2
    if   h < 60:  r,g,b = c,x,0
    elif h < 120: r,g,b = x,c,0
    elif h < 180: r,g,b = 0,c,x
    elif h < 240: r,g,b = 0,x,c
    elif h < 300: r,g,b = x,0,c
    else:         r,g,b = c,0,x
    return (int((r+m)*255), int((g+m)*255), int((b+m)*255))

# ================= 图2 片单长图 =================
# 纯文字数据：每部 = (作品名, 标签, 分层, 简介, 推荐理由)，无封面字段。
WORKS = [
 ("排球少年!!","运动·热血","like","少年日向加入排球部，从零开始追逐全国大赛的热血物语。","一群少年为排球燃烧青春，群像燃系天花板"),
 ("强风吹拂","长跑·群像","like","十名大学生组队挑战箱根驿传长跑接力，羁绊与汗水交织。","十人接力跑箱根，羁绊与热血并存"),
 ("食戟之灵","美食·热血","like","天才少年幸平创真在精英料理学校以料理对决证明自己。","料理对决看得人饿又燃"),
 ("吹响！上低音号","音乐·群像","like","弱校管乐社一群少女为全国大会拼尽青春。","弱校乐团逆袭，青春群像神作"),
 ("白箱","职场·群像","like","五个少女在动画制作一线跌撞成长，致敬幕后职人。","动画制作一线的热血职人剧"),
 ("灵能百分百","成长·治愈","like","拥有超能力的少年茂夫学会接纳普通的自己。","灵能力少年的温柔成长"),
 ("灌篮高手","篮球·群像","like","问题少年樱木花道在篮球场上找到人生热爱。","国民级运动热血番"),
 ("齐木楠雄的灾难","喜剧·群像","like","拥有全能力的最强超能力者只想低调过普通生活。","超能力者的搞笑日常"),
 ("蜂蜜与四叶草","艺术·群像","like","美大青年们的恋爱、迷茫与温柔成长。","美大青年的温柔青春"),
 ("冰上的尤里","花滑·成长","expand","退役花滑选手与天才少年师徒携手重返赛场。","花滑竞技术与师徒情"),
 ("黄金神威","冒险·群像","expand","北海道淘金热中，退伍兵与阿伊努少女的硬核冒险。","北海道淘金冒险，硬核又欢乐"),
 ("花牌情缘","竞技·成长","expand","少女千早为竞技歌牌拼尽青春，纯粹而动人。","竞技与青春的纯粹"),
 ("银河英雄传说","太空·史诗","try","星际帝国与自由行星联盟的权谋与战争史诗。","星际权谋史诗"),
 ("药师少女的独语","奇幻·推理","try","穿越少女在异世界后宫以药学智慧破局。","后宫医女的智慧群像"),
 ("乒乓","运动·克制","niche","两名乒乓少年在球台两端的克制与燃烧。","凌厉写实的乒乓物语"),
 ("葬送的芙莉莲","奇幻·治愈","niche","精灵法师在勇者死后踏上理解人性的漫长旅程。","冒险后的治愈与告别"),
 ("银之匙","田园·青春","niche","都市少年在农业高中重新认识土地与劳动。","农业高中的踏实成长"),
 ("元气囝仔","海岛·治愈","niche","都市少年在离岛收获温柔人情与慢生活。","离岛生活的温柔群像"),
 ("编舟记","职场·匠心","niche","一群编辑用十五年编纂一本国语辞典的匠心职人剧。","辞典编辑的慢热职人剧"),
 ("青之芦苇","足球·青春","niche","被淘汰的天才少年在弱小高中足球队重燃梦想。","足球少年的群像成长"),
]

# 作品池名称 -> 条目（用于补足时回填 简介/理由）
_POOL_MAP = None
def pool_map():
    global _POOL_MAP
    if _POOL_MAP is None:
        try:
            from works_pool import WORKS_POOL
            _POOL_MAP = {w["name"]: w for w in WORKS_POOL}
        except Exception:
            _POOL_MAP = {}
    return _POOL_MAP

def _drop_blocked(works):
    """剔除争议/应屏蔽作品（渲染层兜底）。返回 (干净名单, 被剔除的作品名列表)。

    用途：名单可能由 pool_query 生成（已被拦截过），也可能由调用方直接传入
    （例如 LLM 凭自身知识补充的作品，未经过 pool_query 的黑名单）。
    在此统一二次过滤，确保被屏蔽作品绝不会渲染进成图。
    """
    kept, dropped = [], []
    for w in works or []:
        if is_blocked(w.get("name", "")):
            dropped.append(w.get("name", ""))
        else:
            kept.append(w)
    return kept, dropped


def _dedupe_series(works, per_series=1):
    """同系列限流（渲染层兜底）。返回 (去重后名单, 被剔除的作品名列表)。

    pool_query / finalize_reco 已按 series_key 限流，但调用方（LLM）传入的名单
    可能含同系列多部（同一 IP 的不同季 / 剧场版 / 带副标题的续作，如
    「排球少年!! 第二季」与「排球少年!! 乌野高中 VS 白鸟泽学园高中」）。
    在此统一再限一次，确保成图里每个系列最多 per_series 部。
    """
    seen, out, dropped = {}, [], []
    for w in works or []:
        sk = series_key(w.get("name", ""))
        if seen.get(sk, 0) >= per_series:
            dropped.append(w.get("name", ""))
            continue
        seen[sk] = seen.get(sk, 0) + 1
        out.append(w)
    return out, dropped


def build_list(works=None, status_text=None, out_path=None, persona_name="热忱群像派",
               user_vec=None, region_priority=None):
    """渲染推荐片单（纯文字，无封面）。
    每部 = 作品名 + 标签 + 简介 + 推荐理由 四要素，白卡片 + 分层色条。
    works: list of dict {name, cat, tier, synopsis?, reason?}
           不传时按 persona_name + user_vec 从作品池个性化取 20 部。
    user_vec: 用户六维 DNA；不传则回退到该人格锚向量（等价旧 demo 行为）。
    region_priority: 区域优先级（应来自用户作品名单推断），透传给 pool_query，
                     使主档贴合用户偏好的地区，而非写死日本第一。
    """
    from collections import Counter
    if works is None:
        uv = user_vec if user_vec is not None else PERSONA_VECS.get(persona_name)
        works = pool_query(persona_name, user_vec=uv, domain="动漫",
                          region_priority=region_priority, n=20)
    # 争议作品兜底：名单无论来自 pool_query 还是调用方直接传入，一律二次拦截，
    # 防止 LLM 凭自身知识补充的作品绕过 pool_query 黑名单。
    works, dropped = _drop_blocked(works)
    if dropped:
        print(f"[curation] 已拦截争议作品 {len(dropped)} 部：{'、'.join(dropped)}")
    # 同系列限流兜底：同一 IP 的不同季/剧场版/副标题续作只留 1 部
    works, dup_dropped = _dedupe_series(works)
    if dup_dropped:
        print(f"[series] 已剔除同系列重复 {len(dup_dropped)} 部：{'、'.join(dup_dropped)}")
    n = len(works)
    cnt = Counter(w["tier"] for w in works)
    return _build_list_text(works, status_text, out_path, persona_name, n, cnt)

# ---------------- 文本优先布局（封面可选）----------------
def _build_list_text(works, status_text, out_path, persona_name, n, cnt):
    pad = 52; inner = 42
    full = W - 2*pad
    gap_card = 20
    legend_keys = [k for k in ["like", "expand", "try", "niche", "neighbor"] if cnt.get(k, 0) > 0]
    legend_h = (len(legend_keys) * 40 + 66) if legend_keys else 0
    title_zone = 288
    status_zone = 96 if status_text else 0
    head_bottom_pad = 40          # legend 面板下方露出的深咖色条带厚度
    header_h = title_zone + legend_h + status_zone + head_bottom_pad
    footer_h = 280

    def measure(w):
        name = w["name"]
        syn = (w.get("synopsis") or "").strip()
        rsn = (w.get("reason") or "").strip()
        tw = full - 2*inner
        nf = font(40, True)
        while text_w(name, nf) > tw and nf.size > 22:
            nf = font(nf.size - 2, True)
        name_h = nf.size + 12
        tags_h = 46
        syn_lines = _wrap_cjk(syn, font(27, False), tw)[:3] if syn else []
        syn_h = len(syn_lines) * 38 + (10 if syn_lines else 0)
        rsn_lines = _wrap_cjk("推荐理由 · " + rsn, font(26, False), tw)[:2] if rsn else []
        rsn_h = len(rsn_lines) * 37 + (10 if rsn_lines else 0)
        body = name_h + 10 + tags_h + 12 + syn_h + rsn_h
        return body + 2*inner

    heights = [measure(w) for w in works]
    content_h = (sum(heights) + gap_card * (n - 1)) if n else 0
    Hh = header_h + content_h + footer_h

    canvas = vgradient(W, Hh, CREAM, CREAM_DEEP)
    d = ImageDraw.Draw(canvas)

    # ---- header（深巧克力棕 + 奶油白文字）----
    d.rectangle([0, 0, W, header_h], fill=COCOA)
    glow = radial_glow(560, (255, 255, 255), 80); canvas.paste(glow, (W - 320, -180), glow)
    center(d, (W//2, 84), f"{persona_name} · 专属片单", font(32, False), COCOA_SOFT)
    center(d, (W//2, 168), f"为你精选 {n} 部", font(70, True), CREAM)
    center(d, (W//2, 256), "从最合拍到越级惊喜，按你的口味排好了", font(29, False), COCOA_SOFT)

    # ---- 档位图例（标签 + 释义成对展示）----
    if legend_keys:
        ly = title_zone
        panel = rounded_card(pad, ly, full, legend_h, 20, CREAM, border=CARD_BORDER, bw=2)
        canvas.paste(panel, (pad, ly), panel)
        row_y = ly + 30
        for k in legend_keys:
            cy = row_y + 20
            d.ellipse([pad + 30 - 8, cy - 8, pad + 30 + 8, cy + 8], fill=TIER[k][1])
            lf = font(26, True)
            lname = f"{TIER[k][0]} {cnt[k]}"
            center_left(d, (pad + 52, cy), lname, lf, INK_TITLE)
            dw = text_w(lname, lf) + 22
            center_left(d, (pad + 52 + dw, cy), TIER_DESC.get(k, ""), font(23, False), INK_BODY)
            row_y += 40

    # ---- status bar ----
    if status_text:
        sb_y = title_zone + legend_h
        sb = rounded_card(40, sb_y, W - 80, 64, 16, (255, 255, 255))
        canvas.paste(sb, (40, sb_y), sb)
        center(d, (W//2, sb_y + 32), status_text, font(27, True), COCOA)

    # ---- cards ----
    y = header_h + pad
    for w, ch in zip(works, heights):
        name = w["name"]; cat = w["cat"]; tier = w["tier"]
        syn = (w.get("synopsis") or "").strip()
        rsn = (w.get("reason") or "").strip()
        tw = full - 2*inner
        card = rounded_card(pad, y, full, ch, 22, (255, 255, 255), border=CARD_BORDER, bw=2)
        canvas.paste(card, (pad, y), card)
        accent = TIER.get(tier, ("推荐", (150, 140, 130)))[1]
        d.rectangle([pad, y + 14, pad + 6, y + ch - 14], fill=accent)

        tx = pad + inner
        ty = y + inner
        nf = font(40, True)
        while text_w(name, nf) > tw and nf.size > 22:
            nf = font(nf.size - 2, True)
        center_left(d, (tx, ty + nf.size//2), name, nf, INK_TITLE)
        ty += nf.size + 14

        badge = TIER.get(tier, ("推荐", (150, 140, 130)))
        bf = font(22, True)
        bw_ = int(text_w(badge[0], bf) + 26)
        bl = rounded_card(tx, ty, bw_, 40, 20, badge[1]); canvas.paste(bl, (int(tx), int(ty)), bl)
        center(d, (tx + bw_//2, ty + 20), badge[0], bf, "#ffffff")
        tf = font(22, False)
        tw_ = int(text_w(cat, tf) + 26)
        tag_x0 = int(tx + bw_ + 12)
        tl = rounded_card(tag_x0, ty, tw_, 40, 20, (247, 238, 227)); canvas.paste(tl, (tag_x0, int(ty)), tl)
        center(d, (tag_x0 + tw_//2, ty + 20), cat, tf, (154, 106, 78))
        ty += 40 + 14

        if syn:
            for ln in _wrap_cjk(syn, font(27, False), tw)[:3]:
                center_left(d, (tx, ty + 14), ln, font(27, False), INK_BODY); ty += 38
            ty += 6
        if rsn:
            for ln in _wrap_cjk("推荐理由 · " + rsn, font(26, False), tw)[:2]:
                center_left(d, (tx, ty + 13), ln, font(26, False), INK_REASON); ty += 37
        y += ch + gap_card

    # ---- footer ----
    fy = Hh - footer_h
    d.rectangle([0, fy, W, Hh], fill=COCOA)
    glow2 = radial_glow(560, (255, 255, 255), 80); canvas.paste(glow2, (-200, fy - 130), glow2)
    center(d, (W//2, fy + 104), "测测你的观影人格", font(48, True), CREAM)
    center(d, (W//2, fy + 178), "同款报告 + 定制片单，免费生成", font(29, False), COCOA_SOFT)
    center(d, (W//2, fy + 240), "动漫剧荒推荐 · Anime Recommender", font(32, True), CREAM)

    out = out_path or os.path.join(ROOT, "share_list.png")
    canvas.save(out)
    print("saved", out, "size", canvas.size)

# ================= 反馈循环：可运行重推（接入作品池补足）=================
PERSONA_DEFAULT = "热忱群像派"

def plan_regenerate(feedback, persona=PERSONA_DEFAULT, target=20, user_vec=None,
                    region_priority=None):
    """计算反馈后的最终片单（不含渲染）。本 skill 仅推荐动漫。

    设计：直接让 pool_query 在「排除反馈作品」的前提下生成 target 部——
    pool_query 内部已含「近名去重 + 同系列限流 + 不足回填」，因此：
      - 看过的 / 不喜欢的 被剔除，并自动补充未看过的相邻推荐（而非变少）；
      - 全程恒为 target 部，且不会出现「同名异写」或「同系列扎堆」。
    补足严格限定在【动漫】方向内，并按用户推断的区域优先级排序、
    跨区作品降级 neighbor —— 杜绝电视剧/电影/跨区作品混入，也不写死日本。
    返回 (works列表, status文案)。
    """
    mode = feedback.get("mode", "dislike")
    items = set(feedback.get("items", []))
    reject_tags = feedback.get("reject_tags", [])
    blocked = set(items)

    uv = user_vec if user_vec is not None else PERSONA_VECS.get(persona)

    # 基准片单（不含排除项），用于统计「被剔除 / 被补充」数量
    base0 = pool_query(persona, user_vec=uv, domain="动漫",
                       region_priority=region_priority, n=target)
    base_names = {w["name"] for w in base0}

    # 因标签被避开的作品（reject_tags）一并加入排除，使其不进入最终片单
    if reject_tags:
        for w in base0:
            if any(tag in w["cat"] for tag in reject_tags):
                blocked.add(w["name"])

    # 最终片单：pool_query 在排除 blocked 的前提下生成 target 部
    # （内部已做 近名去重 + 同系列限流 + 不足回填，恒为 target 部）
    final = pool_query(persona, user_vec=uv, domain="动漫",
                       region_priority=region_priority,
                       exclude=list(blocked), n=target)

    removed = len(base_names & blocked)
    added = len([w for w in final if w["name"] not in base_names])
    if mode == "dislike":
        status = f"已剔除 {removed} 部不喜欢的作品，并补充 {added} 部没看过的新推荐"
    else:  # seen
        status = f"已排除 {removed} 部已看作品，并补充 {added} 部没看过的新推荐"

    # 兜底回填 简介/理由（pool_query 已带齐，这里仅作保险）
    pm = pool_map()
    for w in final:
        if not w.get("synopsis") or not w.get("reason"):
            p = pm.get(w["name"])
            if p:
                w.setdefault("synopsis", p.get("synopsis", ""))
                w.setdefault("reason", p.get("reason", ""))

    return final, status

def regenerate(feedback, out_path, persona=PERSONA_DEFAULT, user_vec=None,
               region_priority=None):
    works, status = plan_regenerate(feedback, persona=persona, user_vec=user_vec,
                                    region_priority=region_priority)
    # 争议作品兜底：先过滤再渲染；返回值同样保持干净，
    # 因为调用方（LLM）可能直接拿它展示文字片单，不会经过 build_list。
    works, dropped = _drop_blocked(works)
    if dropped:
        print(f"[curation] 已拦截争议作品 {len(dropped)} 部：{'、'.join(dropped)}")
    works, dup_dropped = _dedupe_series(works)
    if dup_dropped:
        print(f"[series] 已剔除同系列重复 {len(dup_dropped)} 部：{'、'.join(dup_dropped)}")
    build_list(works=works, status_text=status, out_path=out_path,
               persona_name=persona)
    return works

# ⚠️ 已弃用 / 请勿调用：本 skill 当前只生成两张图（share_persona.png + share_list.png）。
# 一页图（share_onepage.png）已从产物中移除，main() 不再调用本函数。
# 若执行引擎看到此处，切勿自行调用 build_one_page，否则会产生多余的第三张图。
def build_one_page(persona="热忱群像派", works=None, out_path=None, user_vec=None,
                   region_priority=None):
    """一页图：观影人格头部（六维 DNA）+ 推荐名单（纯文字，无封面）。
    复用现有构建块（TIER / CREAM / COCOA / font / rounded_card / _wrap_cjk），
    与 share_list 共享同一套视觉方案（奶油底 + 深棕头 + 五档标签）。
    【DEPRECATED】产物已精简为两张图，勿调用。"""
    from collections import Counter
    p = next(x for x in PERSONAS if x["name"] == persona)
    if works is None:
        uv = user_vec if user_vec is not None else PERSONA_VECS.get(persona)
        works = pool_query(persona, user_vec=uv, domain="动漫",
                          region_priority=region_priority, n=20)
    cnt = Counter(w["tier"] for w in works)

    pad = 52; inner = 42
    full = W - 2*pad
    gap_card = 20
    head_h = 888          # 人格头部（深棕，含品牌栏 + 卡通形象）
    legend_h = 112        # 五档图例（一行）
    foot_h = 220

    def measure(w):
        name = w["name"]
        syn = (w.get("synopsis") or "").strip()
        rsn = (w.get("reason") or "").strip()
        tw = full - 2*inner
        nf = font(40, True)
        while text_w(name, nf) > tw and nf.size > 22:
            nf = font(nf.size - 2, True)
        name_h = nf.size + 12
        tags_h = 46
        syn_lines = _wrap_cjk(syn, font(27, False), tw)[:2] if syn else []
        syn_h = len(syn_lines) * 38 + (10 if syn_lines else 0)
        rsn_lines = _wrap_cjk("推荐理由 · " + rsn, font(26, False), tw)[:2] if rsn else []
        rsn_h = len(rsn_lines) * 37 + (10 if rsn_lines else 0)
        body = name_h + 10 + tags_h + 12 + syn_h + rsn_h
        return body + 2*inner

    heights = [measure(w) for w in works]
    content_h = (sum(heights) + gap_card * (len(works) - 1)) if works else 0
    Hh = head_h + legend_h + content_h + foot_h

    canvas = vgradient(W, Hh, CREAM, CREAM_DEEP)
    d = ImageDraw.Draw(canvas)

    # ---- 人格头部（深巧克力棕 + 品牌栏）----
    d.rectangle([0, 0, W, head_h], fill=COCOA)
    glow = radial_glow(560, (255, 255, 255), 80); canvas.paste(glow, (W - 320, -180), glow)

    # 品牌栏：动漫剧荒推荐（产品名）× Anime Recommender（技能名）
    draw_brandbar(d, y0=0, bar_h=96, bg=None)

    # 卡通形象（圆形徽章，与观影人格卡一致）
    mx, my, mr = W // 2, 248, 104
    d.ellipse([mx-mr-14, my-mr-14, mx+mr+14, my+mr+14], fill=(255, 255, 255))
    d.ellipse([mx-mr-14, my-mr-14, mx+mr+14, my+mr+14], outline=CREAM, width=6)
    st = _mascot_image(p, 2*mr)         # 贴图缺失时自动降级为签名色徽章
    canvas.paste(st, (mx-mr, my-mr), st)

    center(d, (W//2, 402), "我的观影人格 · PERSONALITY", font(26, False), COCOA_SOFT)
    nm = p["name"]; nsize = 92 if len(nm) <= 5 else 76
    center(d, (W//2, 462), nm, font(nsize, True), CREAM)
    pill(d, W//2, 530, p["tagline"], font(29, True), (255, 247, 238), COCOA, pad_x=36, h=62)

    # 六维 DNA 条形
    rows_y = 588
    bar_x0 = 330; bar_x1 = W - 270
    for i, (dim, v) in enumerate(zip(DIMS, p["vec"])):
        ry = rows_y + i * 46
        cy = ry + 14
        center_left(d, (pad + 20, cy), dim, font(27, True), COCOA_SOFT)
        d.rounded_rectangle([bar_x0, cy - 12, bar_x1, cy + 12], radius=12,
                            fill=mix(COCOA, (255, 255, 255), 0.16))
        fw = int((bar_x1 - bar_x0) * v / 100)
        if fw > 6:
            d.rounded_rectangle([bar_x0, cy - 12, bar_x0 + fw, cy + 12], radius=12, fill=CREAM)
        center_right(d, (W - pad - 20, cy), f"{v:02d}", font(28, True), CREAM)

    # ---- 五档图例（一行：色点 + 标签名）----
    leg_y = head_h
    d.rectangle([0, leg_y, W, leg_y + legend_h], fill=CREAM)
    d.line([(pad, leg_y + legend_h), (W - pad, leg_y + legend_h)], fill=CARD_BORDER, width=2)
    keys = [k for k in ["like", "expand", "try", "niche", "neighbor"] if cnt.get(k, 0) > 0]
    slot = full // len(keys) if keys else 0
    for i, k in enumerate(keys):
        cx = pad + slot * i + slot // 2
        cy = leg_y + legend_h // 2
        d.ellipse([cx - 96 - 9, cy - 9, cx - 96 + 9, cy + 9], fill=TIER[k][1])
        center_left(d, (cx - 96 + 24, cy), TIER[k][0], font(28, True), INK_TITLE)

    # ---- 推荐名单（纯文字卡片）----
    y = head_h + legend_h + pad
    for w, ch in zip(works, heights):
        name = w["name"]; cat = w["cat"]; tier = w["tier"]
        syn = (w.get("synopsis") or "").strip()
        rsn = (w.get("reason") or "").strip()
        tw = full - 2*inner
        card = rounded_card(pad, y, full, ch, 22, (255, 255, 255), border=CARD_BORDER, bw=2)
        canvas.paste(card, (pad, y), card)
        accent = TIER.get(tier, ("推荐", (150, 140, 130)))[1]
        d.rectangle([pad, y + 14, pad + 6, y + ch - 14], fill=accent)

        tx = pad + inner
        ty = y + inner
        nf = font(40, True)
        while text_w(name, nf) > tw and nf.size > 22:
            nf = font(nf.size - 2, True)
        center_left(d, (tx, ty + nf.size//2), name, nf, INK_TITLE)
        ty += nf.size + 14

        badge = TIER.get(tier, ("推荐", (150, 140, 130)))
        bf = font(22, True)
        bw_ = int(text_w(badge[0], bf) + 26)
        bl = rounded_card(tx, ty, bw_, 40, 20, badge[1]); canvas.paste(bl, (int(tx), int(ty)), bl)
        center(d, (tx + bw_//2, ty + 20), badge[0], bf, "#ffffff")
        tf = font(22, False)
        tw_ = int(text_w(cat, tf) + 26)
        tag_x0 = int(tx + bw_ + 12)
        tl = rounded_card(tag_x0, ty, tw_, 40, 20, (247, 238, 227)); canvas.paste(tl, (tag_x0, int(ty)), tl)
        center(d, (tag_x0 + tw_//2, ty + 20), cat, tf, (154, 106, 78))
        ty += 40 + 14

        if syn:
            for ln in _wrap_cjk(syn, font(27, False), tw)[:2]:
                center_left(d, (tx, ty + 14), ln, font(27, False), INK_BODY); ty += 38
            ty += 6
        if rsn:
            for ln in _wrap_cjk("推荐理由 · " + rsn, font(26, False), tw)[:2]:
                center_left(d, (tx, ty + 13), ln, font(26, False), INK_REASON); ty += 37
        y += ch + gap_card

    # ---- 页脚 ----
    fy = Hh - foot_h
    d.rectangle([0, fy, W, Hh], fill=COCOA)
    glow2 = radial_glow(560, (255, 255, 255), 80); canvas.paste(glow2, (-200, fy - 120), glow2)
    center(d, (W//2, fy + 80), "测测你的观影人格", font(44, True), CREAM)
    center(d, (W//2, fy + 150), "同款报告 + 定制片单，免费生成 · @动漫剧荒推荐", font(27, False), COCOA_SOFT)

    out = out_path or os.path.join(ROOT, "share_onepage.png")
    canvas.save(out)
    print("saved", out, "size", canvas.size)
    return out

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="动漫剧荒推荐 · 生成分享图（人格卡 + 一页图 + 片单）")
    ap.add_argument("--persona", default="热忱群像派", help="观影人格名（默认：热忱群像派）")
    ap.add_argument("--out-dir", default=None, help="输出目录（默认：脚本同级）")
    ap.add_argument("--skip-demo", action="store_true", help="跳过 dislike/seen 演示图生成")
    args = ap.parse_args()
    out_dir = os.path.abspath(args.out_dir) if args.out_dir else ROOT
    os.makedirs(out_dir, exist_ok=True)

    # 用户人格卡（可分享封面图）
    user = next(i for i, p in enumerate(PERSONAS) if p["name"] == args.persona)
    build_persona(PERSONAS[user], user, os.path.join(out_dir, "share_persona.png"))

    # 地区优先级由「用户作品名单」推断（不再写死日本优先）
    try:
        import dna_analyzer as _dna
        region_priority = infer_region_priority(list(_dna.USER_WORKS.keys()))
    except Exception:
        region_priority = None
    print(">>> 地区优先级（由样本作品名单推断）：",
          " > ".join(region_priority) if region_priority else "（无，回退冷启动）")

    # 纯文字片单（无封面）
    build_list(persona_name=args.persona, user_vec=PERSONA_VECS.get(args.persona),
               region_priority=region_priority,
               out_path=os.path.join(out_dir, "share_list.png"))

    if not args.skip_demo:
        # 反馈循环演示：可运行重推（Chapter 9）
        demo_dislike = dict(mode="dislike",
                            items=["排球少年!!", "灌篮高手", "齐木楠雄的灾难"],
                            reject_tags=["运动", "喜剧"])
        regenerate(demo_dislike, os.path.join(out_dir, "share_list_v2_dislike.png"),
                   user_vec=PERSONA_VECS.get(args.persona), region_priority=region_priority)
        demo_seen = dict(mode="seen",
                         items=["排球少年!!", "强风吹拂", "食戟之灵", "吹响！上低音号"])
        regenerate(demo_seen, os.path.join(out_dir, "share_list_seen_demo.png"),
                   user_vec=PERSONA_VECS.get(args.persona), region_priority=region_priority)

    print("✅ 全部生成完成，输出目录：", out_dir)
