#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反爬防护探针 — 判定目标站点用了哪一层防护，输出建议的最低成本方案层级。

用法:
    python probe.py https://target.com
    python probe.py https://target.com --json
    python probe.py https://target.com --save out/        # 落盘 HTML 供人工检查
    python probe.py https://target.com --proxy http://127.0.0.1:7890

依赖: 仅标准库即可运行。
      若已安装 curl_cffi，会自动多做一轮"浏览器 TLS 指纹"对照实验（强烈建议装，判层最准）:
      pip install curl_cffi -i https://pypi.tuna.tsinghua.edu.cn/simple
"""

import sys
import os
import re
import ssl
import json
import gzip
import zlib
import time
import argparse
import urllib.request
import urllib.error
from urllib.parse import urlparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------- 厂商指纹库
# (厂商, 起始层级, [cookie 名片段], [响应头片段], [响应体关键词])
# 强证据 = cookie 命中 或 body 挑战关键词命中；弱证据 = 仅响应头（可能只是用了该家 CDN，未开 bot 防护）
VENDORS = [
    ("Cloudflare", "L1", ["cf_clearance", "__cf_bm", "__cfduid"], ["cf-ray", "cf-mitigated", "server: cloudflare"],
     ["challenges.cloudflare.com", "cf-challenge", "Checking your browser", "Just a moment", "turnstile"]),
    ("Akamai Bot Manager", "L4", ["_abck", "bm_sz", "ak_bmsc", "bm_sv"], ["x-akamai", "server: akamaighost"],
     ["_abck", "bm_sz"]),
    ("DataDome", "L4", ["datadome"], ["x-datadome", "x-dd-b"],
     ["datadome", "geo.captcha-delivery.com"]),
    ("PerimeterX / HUMAN", "L4", ["_px3", "_pxhd", "_pxvid", "pxcts"], ["x-px"],
     ["px-captcha", "Access to this page has been denied", "perimeterx", "human-challenge"]),
    ("Kasada", "L4", ["kpsdk"], ["x-kpsdk-ct", "x-kpsdk-cd", "x-kpsdk"],
     ["kpsdk"]),
    ("Imperva / Incapsula", "L3", ["incap_ses", "visid_incap", "nlbi_"], ["x-iinfo", "x-cdn: incapsula"],
     ["_Incapsula_Resource"]),
    ("AWS WAF", "L2", ["aws-waf-token"], ["x-amzn-waf"], ["awswaf"]),
    ("瑞数 Ruishu", "L3", ["FSSBBIl1Ugz", "ssxmod_itna", "ssxmod_"], [],
     ["$_ts", "_$ca", "$_ts.nsd", "clearInterval(_$"]),
    ("腾讯天御/防水墙", "L5", [], [], ["tdc.js", "turing.captcha", "t.captcha.qq.com", "captcha.gtimg.com"]),
    ("极验 Geetest", "L3", ["geetest"], [], ["geetest", "gt.js", "gcaptcha", "static.geetest.com"]),
    ("顶象 DingXiang", "L4", [], [], ["dingxiang", "dx.js", "dx-captcha", "cap.dingxiang-inc.com"]),
    ("同盾 TongDun", "L3", [], [], ["fm.js", "blackbox", "static.tongdun.net"]),
    ("数美 ShuMei", "L2", [], [], ["fverify", "ishumei", "smcaptcha"]),
    ("网易易盾 Dun", "L3", [], [], ["dun.163.com", "cstaticdun.126.net", "yidun"]),
    ("vaptcha", "L3", [], [], ["vaptcha"]),
    ("友验 Yotest", "L4", [], [], ["yotest.js", "fastyotest"]),
    ("reCAPTCHA", "L4", [], [], ["recaptcha/api.js", "g-recaptcha", "recaptcha/enterprise"]),
    ("hCaptcha", "L3", [], [], ["hcaptcha.com", "h-captcha"]),
    ("阿里云 WAF / 滑块", "L3", ["acw_sc__v2", "acw_tc", "cdn_sec_tc"], [], ["acw_sc__v2", "nc_token"]),
    ("百度云加速", "L2", ["yunsuo_session"], ["yunjiasu"], ["yunsuo"]),
]

BROWSER_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,image/apng,*/*;q=0.8"),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


def _decode_body(raw, encoding_hdr, charset=None):
    if encoding_hdr:
        enc = encoding_hdr.lower()
        try:
            if "gzip" in enc:
                raw = gzip.decompress(raw)
            elif "deflate" in enc:
                try:
                    raw = zlib.decompress(raw)
                except zlib.error:
                    raw = zlib.decompress(raw, -zlib.MAX_WBITS)
        except Exception:
            pass
    for cs in [charset, "utf-8", "gbk", "latin-1"]:
        if not cs:
            continue
        try:
            return raw.decode(cs, errors="replace")
        except Exception:
            continue
    return str(raw[:200000])


def friendly_error(exc, timeout=20):
    """把任何技术性异常翻译成中文 + 修复建议 + 错误编号，绝不暴露英文堆栈/类名。
    返回格式固定为 `[Exxx] 中文原因：中文建议`，便于 FAQ「错误代码速查」对应。
    """
    msg = str(exc).lower()
    if any(k in msg for k in ("getaddrinfo failed", "name or service not known",
                              "could not resolve", "nodename nor servname", "no address associated")):
        return "[E001] DNS 解析失败：URL 域名拼写有误，或本机网络/代理不通。检查链接，或更换网络后再试"
    if "certificate verify failed" in msg or ("ssl" in msg and "certificate" in msg) or "certificate has expired" in msg:
        return "[E002] TLS 证书校验失败：目标站证书过期/异常，或你正在用抓包代理。可加 --insecure 跳过校验（仅调试用）"
    if "timed out" in msg or "timeout" in msg or "operation too slow" in msg or "deadline" in msg or "took too long" in msg:
        return f"[E003] 连接超时（默认 {timeout}s）：目标响应慢、被墙或代理不稳。可加大 --timeout，或换网络/代理重试"
    if "connection refused" in msg or "no route to host" in msg or "failed to connect" in msg or "connection failed" in msg:
        return "[E004] 网络层无法到达目标：对方端口未开、防火墙拦截、VPN/代理异常或目标已宕机。换网络/代理再试"
    if "reset" in msg or "connection aborted" in msg or "broken pipe" in msg or "remote disconnected" in msg or "connection closed" in msg:
        return "[E005] 连接被对方重置：多半是风控在丢请求。减小并发、加随机延时，本探针会自动重试"
    if "proxy" in msg:
        return "[E006] 代理连接失败：检查 --proxy 地址是否可达，格式是否为 http://host:port"
    if "decode" in msg or "utf-8" in msg or "gbk" in msg or "codec" in msg or "charmap" in msg:
        return "[E007] 响应编解码异常：页面编码少见，探针已按 gbk/latin-1 降级处理，可忽略"
    if "json" in msg:
        return "[E008] JSON 解析失败：目标返回了非 JSON 内容（可能是挑战页/拦截页），探针已忽略，请结合状态码判断"
    if "too many" in msg or ("rate" in msg and "limit" in msg):
        return "[E009] 触发频次限制：目标在限流。请降低请求频率、加大间隔并带随机抖动，不要硬刚"
    if "invalid" in msg and ("url" in msg or "scheme" in msg):
        return "[E010] URL 格式无效：请确认以 http:// 或 https:// 开头"
    if "permission" in msg or "denied" in msg:
        return "[E011] 文件写入被拒：保存 HTML 时无权写入 --save 指定目录，换一个有写入权限的路径"
    if "no such file" in msg or "not found" in msg:
        return "[E012] 文件/路径不存在：检查 --save 目录路径是否正确"
    if "curl_cffi" in msg or "impersonate" in msg or "cffi" in msg or "requests.exceptions" in msg:
        return "[E013] TLS 伪装库异常：curl_cffi 版本或依赖有问题。可重装（pip install -U curl_cffi -i 清华源）或暂时只用标准库探针"
    # 兜底：绝不暴露英文类名校名，给统一中文 + 文档指引
    return ("[E999] 未预期的网络/解析异常。请先尝试：① 加大 --timeout；② 更换网络或代理；"
            "③ 仍不行就把上面场景反馈给我，我帮你定位（附上 E001~E013 任意编号更易排查）")


def fetch_stdlib(url, proxy=None, timeout=20, insecure=False):
    """裸标准库请求：TLS 指纹 = Python/OpenSSL，最容易被 L3 层拦。
    默认校验证书；仅在显式 --insecure（如需经本地抓包代理）时才关闭。"""
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    handlers = [urllib.request.HTTPSHandler(context=ctx)]
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    cookiejar_hdrs = []
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    t0 = time.time()
    try:
        resp = opener.open(req, timeout=timeout)
        raw = resp.read(600000)
        hdrs = dict(resp.headers.items())
        cookiejar_hdrs = resp.headers.get_all("Set-Cookie") or []
        body = _decode_body(raw, hdrs.get("Content-Encoding"), resp.headers.get_content_charset())
        return {"ok": True, "status": resp.status, "headers": hdrs, "cookies": cookiejar_hdrs,
                "body": body, "ms": int((time.time() - t0) * 1000), "final_url": resp.geturl()}
    except urllib.error.HTTPError as e:
        raw = b""
        try:
            raw = e.read(600000)
        except Exception:
            pass
        hdrs = dict(e.headers.items()) if e.headers else {}
        cookiejar_hdrs = e.headers.get_all("Set-Cookie") or [] if e.headers else []
        body = _decode_body(raw, hdrs.get("Content-Encoding"))
        return {"ok": True, "status": e.code, "headers": hdrs, "cookies": cookiejar_hdrs,
                "body": body, "ms": int((time.time() - t0) * 1000), "final_url": url}
    except Exception as e:
        return {"ok": False, "error": friendly_error(e, timeout), "status": 0,
                "headers": {}, "cookies": [], "body": "", "ms": int((time.time() - t0) * 1000)}


def fetch_impersonate(url, proxy=None, timeout=20, insecure=False):
    """curl_cffi：伪装真实 Chrome 的 TLS/JA4 + HTTP2 SETTINGS + 头序。"""
    try:
        from curl_cffi import requests as creq
    except Exception:
        # 任何原因装不上/报错（ImportError、版本冲突、缺二进制）都不影响标准库探针
        return None
    t0 = time.time()
    try:
        kw = {"impersonate": "chrome", "timeout": timeout, "verify": not insecure}
        if proxy:
            kw["proxies"] = {"http": proxy, "https": proxy}
        r = creq.get(url, **kw)
        return {"ok": True, "status": r.status_code, "headers": dict(r.headers),
                "cookies": [f"{k}={v}" for k, v in r.cookies.items()],
                "body": r.text[:600000], "ms": int((time.time() - t0) * 1000),
                "http_version": str(getattr(r, "http_version", "?"))}
    except Exception as e:
        return {"ok": False, "error": friendly_error(e, timeout), "status": 0,
                "headers": {}, "cookies": [], "body": "", "ms": int((time.time() - t0) * 1000)}


def match_vendors(resp):
    hay_hdr = " ".join(f"{k}: {v}" for k, v in resp.get("headers", {}).items()).lower()
    hay_ck = " ".join(resp.get("cookies", [])).lower()
    hay_body = (resp.get("body") or "")[:400000].lower()
    hits = []
    for name, level, cks, hdrs, bodies in VENDORS:
        ev, strong = [], False
        for c in cks:
            if c.lower() in hay_ck:      # 只在 Set-Cookie 里找，避免 CDN 响应头造成误报
                ev.append(f"cookie:{c}"); strong = True
        for b in bodies:
            if b.lower() in hay_body:
                ev.append(f"body:{b}"); strong = True
        for h in hdrs:
            if h.lower() in hay_hdr:
                ev.append(f"header:{h}")
        if ev:
            hits.append({"vendor": name, "suggest_level": level, "evidence": ev[:4],
                         "strength": "strong" if strong else "weak"})
    return hits


def analyze_content(body):
    """检测 JS 渲染需求、字体反爬、CSS 偏移、参数加密、混淆等第 7/8 层线索。"""
    f = {}
    low = body.lower()

    # --- 是否需要 JS 渲染 ---
    text = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    f["visible_text_len"] = len(text)
    spa = [m for m in ["__next_data__", "window.__initial_state__", "window.__nuxt__",
                       "id=\"app\"", "id=\"root\"", "ng-app", "data-reactroot"] if m in low]
    f["spa_markers"] = spa
    f["needs_js"] = len(text) < 500 and bool(spa or "<script" in low)
    f["embedded_json"] = [m for m in ["__next_data__", "window.__initial_state__", "window.__nuxt__",
                                      "application/ld+json", "application/json"] if m in low]

    # --- 字体反爬 ---
    f["font_antiscrape"] = bool(re.search(r"@font-face", low)) and bool(
        re.search(r"\.(woff2?|ttf|eot)|base64,d09gm|base64,aujpaaa", low))
    pua = re.findall(r"&#x(e[0-9a-f]{3}|f[0-8][0-9a-f]{2});|\\u(e[0-9a-f]{3})", body, re.I)
    f["pua_glyph_count"] = len(pua)  # Unicode 私有区字符 = 字体映射反爬强信号

    # --- CSS 偏移 / 伪元素 / 雪碧图 ---
    f["css_pseudo_content"] = len(re.findall(r"::(?:before|after)\s*\{[^}]*content", low))
    f["sprite_hint"] = low.count("background-position") > 5

    # --- 参数加密 / 签名 ---
    sig = set(re.findall(r"[\"'&?]((?:x-)?(?:sign|signature|token|nonce|timestamp|_signature|sig|auth|verify)[a-z_]*)"
                         r"[\"']?\s*[:=]", low))
    f["signature_params"] = sorted(sig)[:8]

    # --- JS 混淆 / 反调试 ---
    f["obfuscation"] = {
        "ob_hex_names": len(re.findall(r"_0x[0-9a-f]{4,6}", body)) > 20,
        "jsfuck": "[]+[]" in body and body.count("!+[]") > 10,
        "eval_or_Function": bool(re.search(r"\b(eval|new Function)\s*\(", body)),
        "wasm": ".wasm" in low or "webassembly" in low,
        "anti_debug": "debugger" in low,
        "infinite_debugger": body.count("debugger") > 2,
    }
    return f


def check_robots(url, proxy=None):
    p = urlparse(url)
    r = fetch_stdlib(f"{p.scheme}://{p.netloc}/robots.txt", proxy=proxy, timeout=10)
    if not r["ok"] or r["status"] != 200:
        return {"available": False}
    body = r["body"][:20000]
    return {
        "available": True,
        "disallow_all": bool(re.search(r"(?im)^\s*user-agent:\s*\*\s*$[\s\S]{0,200}?^\s*disallow:\s*/\s*$", body)),
        "sitemaps": re.findall(r"(?im)^\s*sitemap:\s*(\S+)", body)[:5],
        "crawl_delay": (re.findall(r"(?im)^\s*crawl-delay:\s*(\S+)", body) or [None])[0],
    }


def decide(bare, imp, vendors, content):
    """输出建议层级与理由。"""
    reasons, level = [], "L1"
    bs, is_ = bare["status"], (imp or {}).get("status")

    blocked = bs in (401, 403, 405, 406, 429, 202, 412, 418, 503, 520, 521, 522)
    if bs in (202, 412):
        reasons.append(f"首请求 {bs} —— 瑞数系典型的三次请求模式（202/412 → 外链 js → 再请求）")
    if bs == 429:
        reasons.append("429 频控：先降速 + 抖动 + 指数退避，不必升级方案")

    if imp is None:
        reasons.append("未安装 curl_cffi，跳过 TLS 对照实验（建议装上，判层最准）")
    elif blocked and is_ == 200:
        level = "L1"
        reasons.append(f"关键结论：裸请求 {bs} 被拦，curl_cffi 伪装 TLS 后 200 → **纯 TLS/HTTP2 指纹层**，"
                       "L1 一行 impersonate 即可，不要开浏览器")
    elif blocked and is_ and is_ != 200:
        level = "L2"
        reasons.append(f"裸请求与 TLS 伪装均被拦（{bs}/{is_}）→ 不只是指纹层：先换出口 IP 验证 IP 信誉（L2），"
                       "仍失败说明有 JS 挑战，升 L3")
    elif not blocked and is_ == 200:
        reasons.append("两种方式均 200 —— 当前无强拦截，重点是限速与会话卫生")
    elif bs == 200 and is_ and is_ != 200:
        reasons.append(f"反直觉现象：裸请求 200 而 TLS 伪装 {is_} → 那个 200 极可能是挑战页/软封禁页而非真内容；"
                       "也可能该站对『完美 Chrome TLS + 不执行 JS』的组合额外敏感。**判定成功要看内容，不看状态码**")

    strong_v = [v["vendor"] for v in vendors if v["strength"] == "strong"]
    if bs == 200 and content["visible_text_len"] < 300 and strong_v:
        reasons.append(f"⚠ 200 ≠ 成功：首屏可见文本仅 {content['visible_text_len']} 字符且命中 {strong_v} → "
                       "拿到的是挑战页或影子封禁内容。务必用『人工浏览器看到的真实值』做基准校验数据真实性")

    if content["needs_js"]:
        if level in ("L1",):
            level = "L3"
        reasons.append(f"首屏可见文本仅 {content['visible_text_len']} 字符 + SPA 标记 {content['spa_markers']} "
                       "→ 内容靠 JS 渲染。**先找 XHR/JSON 接口（L0），命中就零成本**，找不到才上 L3")
    if content["embedded_json"]:
        reasons.append(f"HTML 内嵌结构化数据 {content['embedded_json']} → 优先直接解析，可能完全绕开渲染")

    top = [v for v in vendors if v["suggest_level"] in ("L4", "L5") and v["strength"] == "strong"]
    if top:
        level = max([level] + [v["suggest_level"] for v in top])
        reasons.append(f"命中重型风控 {[v['vendor'] for v in top]}（强证据）→ 需指纹级伪装 + 住宅 IP + 拟人行为（{level}）；"
                       "量小场景直接考虑 L5 真实浏览器接管（本机 web-access skill）")
    weak = [v["vendor"] for v in vendors if v["strength"] == "weak"]
    if weak:
        reasons.append(f"{weak} 仅命中响应头（弱证据）→ 大概率只是用了该家 CDN，未必开启 bot 防护，"
                       "不要因此提前升级方案，以实际状态码为准")

    if content["font_antiscrape"] or content["pua_glyph_count"] > 5:
        reasons.append(f"字体反爬信号（@font-face + 私有区字符 {content['pua_glyph_count']} 个）→ "
                       "需下载 woff 建映射表还原，与访问层无关，见 mechanisms.md §7")
    if content["css_pseudo_content"] > 3:
        reasons.append(f"检测到 {content['css_pseudo_content']} 处 ::before/after content → CSS 偏移反爬，"
                       "取值要读计算样式而非 DOM 文本")
    if content["signature_params"]:
        reasons.append(f"请求签名参数线索 {content['signature_params']} → 捷径是在浏览器上下文里直接调站内加密函数，"
                       "别硬扣 JS")
    ob = content["obfuscation"]
    if ob["infinite_debugger"]:
        reasons.append("存在无限 debugger 反调试 → 用 Never pause here 或 hook Function 绕过")
    if ob["wasm"]:
        reasons.append("检测到 WebAssembly → 算法逆向成本极高，优先 L5 或 JSRPC 调用原函数")
    if ob["ob_hex_names"]:
        reasons.append("检测到 obfuscator 风格 _0x 混淆 → 需要时用 AST/解混淆工具，但通常无需还原全部逻辑")

    return level, reasons


def _needs_retry(result, attempt, max_retries, base_delay):
    """判断上次请求是否值得重试（仅瞬时故障：网络层失败 / 服务端 5xx）。
    4xx（403/429 等）是确定性结果，重试无意义，直接返回不重试。"""
    if result is None:
        return False, 0
    status = result.get("status", 0)
    transient = (not result.get("ok")) or (500 <= status < 600)
    if not transient or attempt >= max_retries:
        return False, 0
    return True, base_delay * (2 ** (attempt - 1))  # 指数退避：2s → 4s → 8s


def fetch_stdlib_retry(url, proxy=None, timeout=20, insecure=False, max_retries=3, base_delay=2):
    """带自动重试的标准库请求：网络抖动/5xx 时指数退避自动重跑，用户无需手动多跑。"""
    last = None
    for i in range(1, max_retries + 1):
        last = fetch_stdlib(url, proxy, timeout, insecure)
        retry, delay = _needs_retry(last, i, max_retries, base_delay)
        if not retry:
            return last
        why = last.get("error") or f"HTTP {last.get('status')}"
        print(f"  ↻ 第 {i} 次请求未成功（{why}），{delay}s 后自动重试…", file=sys.stderr)
        time.sleep(delay)
    return last


def fetch_impersonate_retry(url, proxy=None, timeout=20, insecure=False, max_retries=3, base_delay=2):
    """带自动重试的 TLS 伪装请求；curl_cffi 未安装时返回 None（不重试）。"""
    last = None
    for i in range(1, max_retries + 1):
        last = fetch_impersonate(url, proxy, timeout, insecure)
        if last is None:
            return None  # 库没装，没必要重试
        retry, delay = _needs_retry(last, i, max_retries, base_delay)
        if not retry:
            return last
        why = last.get("error") or f"HTTP {last.get('status')}"
        print(f"  ↻ 第 {i} 次 TLS 伪装请求未成功（{why}），{delay}s 后自动重试…", file=sys.stderr)
        time.sleep(delay)
    return last


def main():
    ap = argparse.ArgumentParser(description="反爬防护探针")
    ap.add_argument("url")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--save", metavar="DIR", help="把响应 HTML 落盘")
    ap.add_argument("--proxy", help="http://host:port")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--insecure", action="store_true",
                    help="关闭 TLS 证书校验（仅在走本地抓包代理时用；会失去 MITM 防护）")
    a = ap.parse_args()

    url = a.url if a.url.startswith("http") else "https://" + a.url

    bare = fetch_stdlib_retry(url, a.proxy, a.timeout, a.insecure)
    if not bare["ok"] and "certificate" in (bare.get("error") or "").lower() and not a.insecure:
        print("  ! 证书校验失败。若目标站证书确有问题或你在用抓包代理，可加 --insecure 重试", file=sys.stderr)
    imp = fetch_impersonate_retry(url, a.proxy, a.timeout, a.insecure)
    src = imp if (imp and imp.get("ok") and imp.get("body")) else bare
    vendors = match_vendors(bare)
    if imp and imp.get("ok"):
        seen = {v["vendor"] for v in vendors}
        vendors += [v for v in match_vendors(imp) if v["vendor"] not in seen]
    content = analyze_content(src.get("body") or "")
    robots = check_robots(url, a.proxy)
    level, reasons = decide(bare, imp, vendors, content)

    if a.save:
        os.makedirs(a.save, exist_ok=True)
        host = urlparse(url).netloc.replace(":", "_")
        for tag, r in (("bare", bare), ("impersonate", imp)):
            if r and r.get("body"):
                with open(os.path.join(a.save, f"{host}.{tag}.html"), "w", encoding="utf-8") as fh:
                    fh.write(r["body"])

    result = {
        "url": url,
        "bare_request": {"status": bare["status"], "ms": bare["ms"], "error": bare.get("error"),
                         "set_cookie": [c.split("=")[0] for c in bare["cookies"]][:12],
                         "server": bare["headers"].get("Server")},
        "impersonated_request": ({"status": imp["status"], "ms": imp["ms"], "error": imp.get("error"),
                                  "http_version": imp.get("http_version")} if imp else "curl_cffi 未安装"),
        "vendors": vendors,
        "content_signals": content,
        "robots": robots,
        "suggested_level": level,
        "reasons": reasons,
    }

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    B, E = "\033[1m", "\033[0m"
    print(f"\n{B}=== 反爬探针报告 ==={E}  {url}\n")
    print(f"{B}[请求对照]{E}")
    print(f"  裸 requests(Python TLS) : {bare['status']}  {bare['ms']}ms  "
          f"{('ERR ' + bare['error']) if bare.get('error') else ''}")
    if imp:
        print(f"  curl_cffi(Chrome TLS)  : {imp['status']}  {imp['ms']}ms  "
              f"HTTP/{imp.get('http_version','?')}  {('ERR ' + imp['error']) if imp.get('error') else ''}")
    else:
        print("  curl_cffi              : 未安装（建议: pip install curl_cffi -i 清华源）")
    ck = [c.split("=")[0] for c in bare["cookies"]][:12]
    if ck:
        print(f"  Set-Cookie             : {', '.join(ck)}")

    print(f"\n{B}[命中厂商]{E}")
    if vendors:
        for v in vendors:
            mark = "●" if v["strength"] == "strong" else "○"
            tag = "强证据" if v["strength"] == "strong" else "弱证据(疑似仅CDN)"
            print(f"  {mark} {v['vendor']:<22} 起点 {v['suggest_level']}  [{tag}]  证据: {', '.join(v['evidence'])}")
    else:
        print("  未识别到已知商业风控指纹（可能是自研规则或无防护）")

    print(f"\n{B}[内容层信号]{E}")
    print(f"  首屏可见文本      : {content['visible_text_len']} 字符"
          f"{'  ← 需要 JS 渲染' if content['needs_js'] else ''}")
    if content["embedded_json"]:
        print(f"  内嵌结构化数据    : {content['embedded_json']}")
    if content["font_antiscrape"] or content["pua_glyph_count"]:
        print(f"  字体反爬          : @font-face={content['font_antiscrape']}  私有区字符={content['pua_glyph_count']}")
    if content["css_pseudo_content"]:
        print(f"  CSS 伪元素 content: {content['css_pseudo_content']} 处")
    if content["signature_params"]:
        print(f"  签名参数线索      : {content['signature_params']}")
    ob = {k: v for k, v in content["obfuscation"].items() if v}
    if ob:
        print(f"  JS 混淆/反调试    : {list(ob.keys())}")

    print(f"\n{B}[robots.txt]{E}")
    if robots.get("available"):
        print(f"  全站 Disallow: {robots['disallow_all']}   Crawl-delay: {robots.get('crawl_delay')}")
        if robots.get("sitemaps"):
            print(f"  Sitemap: {robots['sitemaps']}")
        if robots["disallow_all"]:
            print("  ⚠ 该站 robots 禁止全部抓取 —— 先与用户确认授权情况再继续")
    else:
        print("  无 robots.txt 或不可达")

    print(f"\n{B}[建议起点: {level}]{E}")
    for r in reasons:
        print(f"  → {r}")
    print(f"\n  阶梯: L0 找接口 → L1 curl_cffi → L2 +住宅代理 → L3 patchright/nodriver "
          f"→ L4 camoufox+拟人 → L5 真实浏览器CDP → L6 商业API")
    print("  记住: 每级贵 5~50 倍, 被拒才升级。详见 SKILL.md §2\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[已取消] 你按了 Ctrl+C", file=sys.stderr)
    except SystemExit:
        raise
    except Exception as e:
        # 最后兜底：绝不让英文堆栈直接暴露给新手
        print(f"\n[探针异常] {friendly_error(e)}", file=sys.stderr)
        print("若无法解决，把上面这行信息发给我，或加 --insecure / --timeout 重试。", file=sys.stderr)
        sys.exit(1)
