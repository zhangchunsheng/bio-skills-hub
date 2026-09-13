# 工具箱：选型 + 可跑代码模板

约定：pip 一律 `-i https://pypi.tuna.tsinghua.edu.cn/simple`（国内镜像，几秒装完）；装在隔离 venv 里，不污染系统 Python。下面命令**任意系统通用**，无需改路径：

```bash
# 1. 建隔离 venv（不污染系统 Python）
python3 -m venv .venv
#    Windows 激活: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate

# 2. 装依赖
#    Windows 用 .venv\Scripts\python.exe；macOS/Linux 用 .venv/bin/python
.venv/Scripts/python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple curl_cffi patchright camoufox nodriver fonttools
.venv/Scripts/python.exe -m patchright install chromium     # 需要浏览器时
```

---

## L1 — curl_cffi（永远先试这个）

6.4MB，无浏览器，~125ms/请求，2026 基准对 31 个 Cloudflare 目标通过 26 个。

```python
from curl_cffi import requests
import time, random

session = requests.Session()

def fetch(url, retries=3):
    for i in range(retries):
        try:
            r = session.get(
                url,
                impersonate="chrome",          # 同时伪装 TLS(JA3/JA4)+HTTP2 SETTINGS+ALPN+头序
                timeout=20,
                headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"},
            )
            if r.status_code == 200:
                return r.text
            if r.status_code == 429:                     # 频控：退避 + 抖动
                time.sleep(2 ** i * 5 + random.uniform(0, 2)); continue
            if r.status_code in (403, 202, 412):         # 指纹不够或有 JS 挑战 → 升级
                return None
        except Exception:
            time.sleep(2)
    return None
```

要点：
- `impersonate` 目标要和 UA 一致（`"chrome"` 在 0.15.0 = Chrome 145/146 形状）；也可指定 `chrome131`、`safari180`、`firefox133`
- 复用 `Session` 保持 cookie 与连接
- 代理：`session.get(url, proxies={"http": p, "https": p})`
- 同类替代：`tls-client`、`primp`、`curl-impersonate`（二进制）

**JA4+ 自查与应对（2026 必看）**：
- `curl_cffi` 的 `impersonate="chrome"` 已同时伪造 **JA4 + JA4H + HTTP/2 SETTINGS + ALPN + 头序**，**一行即覆盖 JA4+ 四维**——这是 2026 年最便宜的 JA4+ 合规方案。
- ⚠️ **JA3 时代的"打乱 ClientHello 扩展顺序"绕过已失效**：JA4 对列表型字段做了排序标准化，打乱顺序哈希不变。任何教"乱序扩展"的老文章在 2026 都是错的。
- 自查本机发出请求的 JA4 形状是否自洽：访问指纹测试端点（如 `https://tls.spacerat.me/` 或自建 JA4 回显服务）看回显的 JA4 是否与 UA 声称的浏览器匹配；不匹配则仍有伪造缺口（典型：UA 写 Chrome 146 但 impersonate 用 chrome110）。
- 进阶（需要更底层控制）：`tls-client`（Go）、`utls`（Go）、`curl-impersonate`（二进制）可精确控制每一个 TLS 扩展、曲线与顺序。

---

## L2 — 代理轮换 + 会话粘滞

```python
import random
from curl_cffi import requests

class ProxyPool:
    """住宅代理：普通轮换 vs 粘滞会话。清关 cookie 必须配粘滞。"""
    def __init__(self, user, pwd, gateway):
        self.user, self.pwd, self.gw = user, pwd, gateway

    def rotating(self, country=None):
        u = self.user + (f"-country-{country}" if country else "")
        return self._fmt(u)

    def sticky(self, session_id=None):
        sid = session_id or random.randint(100000, 999999)
        return self._fmt(f"{self.user}-session-{sid}")     # 同一 sid → 同一出口 IP

    def _fmt(self, u):
        url = f"http://{u}:{self.pwd}@{self.gw}"
        return {"http": url, "https": url}
```

规则：
- **拿到 clearance cookie 后必须锁定同一出口 IP**（cf_clearance / _px3 都绑 IP）
- 代理地区要和 `Accept-Language`、时区、目标站受众一致（美国站 + 中文 header + 中国 IP = 三重不一致）
- IP 分级：数据中心（易封）< 住宅 $6~15/GB < 移动 $20~40/GB（最受信任）

---

## L3 — patchright（Playwright 直接替换，迁移成本最低）

```python
# pip install patchright && patchright install chromium
from patchright.sync_api import sync_playwright   # API 与 playwright 完全一致

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chrome",          # 用真实 Chrome，TLS 更真（不是 Chromium）
        headless=False,            # headless 仍是明显信号，能有头就有头
    )
    ctx = browser.new_context(
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        viewport={"width": 1440, "height": 900},
    )
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)                   # 等 JS 挑战自行完成
    html = page.content()

    # 关键：导出清关 cookie，后续降回 L1 高速抓取（务必保持同一 IP + 同一 UA）
    cookies = {c["name"]: c["value"] for c in ctx.cookies()}
    browser.close()
```

**nodriver**（2026 基准 31/31 冠军，控制面无 Playwright）：

```python
# pip install nodriver
import asyncio, nodriver as uc

async def main():
    browser = await uc.start(headless=False)
    page = await browser.get(url)
    await page.sleep(5)
    html = await page.get_content()
    await browser.stop()

asyncio.run(main())
```
注意：nodriver 是 asyncio 模型，**不是 Playwright 的 drop-in**，迁移要重写控制流。它是 undetected-chromedriver 作者的后继项目。

⚠️ **`undetected-chromedriver` 已停滞**（最后发布 3.5.5 / 2024-02，千余 issue 未处理），新项目不要用。
⚠️ **原生 Playwright / rebrowser-playwright** 在反检测基准里垫底，别用于对抗场景。

---

## L4 — camoufox（Firefox C++ 层伪装）+ 拟人行为

```python
# pip install camoufox && camoufox fetch
from camoufox.sync_api import Camoufox

with Camoufox(
    headless=True,               # 天生为 headless 设计，不是事后改造
    humanize=True,               # 内置鼠标轨迹拟人
    os=("windows",),             # 让 BrowserForge 生成自洽指纹（不会出现 Win UA + Apple GPU）
    geoip=True,                  # 按代理 IP 自动对齐时区/语言/经纬度
    proxy={"server": "http://user:pass@gw:port"},
) as browser:
    page = browser.new_page()
    page.goto(url)
    html = page.content()
```
- 内存 ~200MB（Chrome 800MB+），C++ 层伪装 navigator/screen/WebGL/字体/WebRTC/Canvas
- **坑**：维护已移交 Clover Labs，新版 experimental；生产用稳定版 `pip install camoufox`（alpha 是 `cloverlabs-camoufox`）；自行 build 必须 Linux（WSL 不行）
- 部分站点只封 Chrome 形状 → Firefox 形状反而能过；反之亦有

**拟人行为工具函数**（任何浏览器方案都该套上）。

> **🆕 延迟分布统一规则（v1.0.7，Precursor 对策）**：**人类节奏类延迟一律走 `human_delay`（对数正态重尾分布）**——Precursor 等生理级行为分析重点识破「均匀随机/高斯噪声」。仅**网络层重试退避**（如上面 fetch 的 `2**i*5 + uniform(0,2)`）继续用均匀抖动——那是给服务器看的限速礼貌，与行为分析无关，两者别混。

```python
import random, math

def human_delay(mu=250, sigma=0.7, lo=30, hi=6000):
    """重尾延迟（对数正态）：mu=中位数毫秒，sigma=形状（0.6~1.0 越大越拖尾）。
    所有'人类节奏'等待统一用它，替代 randint/uniform。"""
    ms = random.lognormvariate(math.log(mu), sigma)
    return int(max(lo, min(ms, hi)))            # 钳位防极端值拖垮脚本

def human_move(page, x2, y2, steps=25):
    """贝塞尔轨迹 + 认知识别延迟 + 速度衰减手抖（Precursor 对策）"""
    # ① 认知识别延迟：视线到达目标后 ~200ms 才开始移动（真人生理特征）
    page.wait_for_timeout(human_delay(mu=200, sigma=0.6))
    x1, y1 = random.randint(0, 200), random.randint(0, 200)
    cx, cy = (x1 + x2) / 2 + random.randint(-120, 120), (y1 + y2) / 2 + random.randint(-120, 120)
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
        y = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
        # ② 速度衰减手抖：轨迹两端慢（手抖大）、中段快（手抖小）——真人特性
        speed = 1 - abs(0.5 - t) * 2
        jitter = random.uniform(-1.5, 1.5) * (1.6 - speed)
        page.mouse.move(x + jitter, y + jitter * 0.8)
        page.wait_for_timeout(human_delay(mu=15, sigma=0.5))

def human_scroll(page, total=3000):
    """变速分段滚动 + 偶尔回滚（重尾停顿）"""
    done = 0
    while done < total:
        d = int(min(max(random.lognormvariate(math.log(320), 0.5), 80), 900))
        page.mouse.wheel(0, d); done += d
        page.wait_for_timeout(human_delay(mu=550, sigma=0.8))    # 重尾：偶有长停顿（在看内容）
        if random.random() < 0.15:
            page.mouse.wheel(0, -random.randint(60, 180))
            page.wait_for_timeout(human_delay(mu=400, sigma=0.7))

def warmup(page, home, target):
    """会话预热：先首页停留滚动，再进目标页——PerimeterX/Akamai 必备"""
    page.goto(home, wait_until="domcontentloaded")
    page.wait_for_timeout(human_delay(mu=2800, sigma=0.5))
    human_scroll(page, 1200)
    page.goto(target, wait_until="domcontentloaded")

def human_type(page, selector, text):
    """逐字打字（抗行为分析）：重尾键间延迟 + 10% 概率思考长停顿；
    受控组件必须走原生 InputEvent，不能 el.value="" """
    page.focus(selector)
    for ch in text:
        page.keyboard.type(ch)
        if random.random() < 0.10:                              # 思考/回看，重尾长停顿
            page.wait_for_timeout(human_delay(mu=900, sigma=0.8))
        page.wait_for_timeout(human_delay(mu=90, sigma=0.6))    # 中位 90ms 键间延迟
    page.wait_for_timeout(human_delay(mu=400, sigma=0.7))

def replay_track(page, track):
    """回放人工录制的真实轨迹（Precursor 站首选：保真度 > 任何数学合成）。
    track: [(x, y, dt_ms), ...]——人工操作时用 DevTools Recorder 录制导出，
    或在 L5 真实浏览器里挂 CDP Input 事件监听录制，再转成该格式。"""
    for x, y, dt in track:
        page.mouse.move(x, y)
        page.wait_for_timeout(max(5, int(dt)))
```

> **指纹池 + 完整反检测注入 + 受控组件输入 + 并发限速**：见 `references/stealth-profiles.md`（含按真实份额加权的 UA/分辨率池、WebGL/Canvas 微噪声、React/Vue `humanType` 原生事件版）。
```

---

## L5 — 真实浏览器接管（本机现成，量小首选）

用已装的 **`web-access` skill**：CDP 直连你日常的 Chrome/Edge，天然带真实指纹、真实历史、真实登录态。风控评分天生高，Turnstile/DataDome/PerimeterX 基本不触发。

```bash
node "$SKILL_DIR/scripts/check-deps.mjs"                    # 启动 CDP proxy
curl -s -X POST --data-raw 'https://target.com' http://localhost:3456/new
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.body.innerText.slice(0,2000)'
curl -s -X POST "http://localhost:3456/clickAt?target=ID" -d 'button.next'   # 真实鼠标手势
```

**完整实操（连接发现 / 智能等待 / 多备选选择器 / SPA 路由 / HttpOnly cookie / 数据提取层级 / 实测踩坑库）见 `references/cdp-reuse.md`**。要点速记：

- 自启远程调试务必带 `--disable-blink-features=AutomationControlled`（去掉 webdriver 标记）；`chrome://inspect` 勾选远程调试更隐蔽（DevToolsActivePort 含每次变的 UUID）
- **永不用固定 sleep**：用 `waitNetworkIdle`（网络空闲 500ms）替代
- 选择器多备选降级：`[class*="xxx"]` 模糊 > 语义 role > 位置；禁用 `nth-child`/长 XPath
- SPA 内部路由：先入可访问父页再 JS 点击触发，直接 navigate 子路由会 404
- HttpOnly cookie 用 CDP `Network.getCookies` 拿，回灌 L1 高速抓取（锁同一出口 IP）

**限制**：不能大规模并发、会占用日常浏览器。适合个人自用、量在千级以下、或前面各级全挂时兜底。
**风险提示**：登录态复用只用于你自己的账号，不用于绕过登录墙；用登录态操作前要向用户明示。

---

## 反检测注入清单（页面加载前注入，所有浏览器方案通用）

来源 `anti-bot-scraper` / `coco-playwright-stealth` / `stealth-profiles.md`。完整代码（UA/分辨率加权池、WebGL/Canvas 微噪声、受控组件输入、拟人逐字打字、并发限速）见 **`references/stealth-profiles.md`**。

铁律：**所有反检测代码必须在 `addInitScript`（Playwright）/ `evaluateOnNewDocument`（puppeteer）注入**，即页面任何脚本运行前。事后 patch 来不及——Challenge 首行就读取。

```python
# Playwright：launch 后、goto 前注入
from patchright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=False)
    ctx = b.new_context(user_agent=pick(DESKTOP_UA), viewport={"width":1920,"height":1080})
    ctx.add_init_script(path="init_stealth.js")   # 内容见 stealth-profiles.md §2.1
    page = ctx.new_page(); page.goto(url)
```

**有效项**：隐藏 `navigator.webdriver`（必需）+ 真实 UA（含移动端）+ WebGL/Canvas 微噪声（±1~2，肉眼无感）+ `navigator.plugins/languages/hardwareConcurrency` 伪装 + 随机视口。
**无效项**：仅改 UA、上 Crawlee/Selenium、Docker 隔离（对 Cloudflare 无用）。
**插件 vs 纯手写**：`patchright`（已补 CDP 泄漏，首选）或 `playwright-extra`+stealth 插件即可；纯手写避免插件已知特征但更费事——两者都行。

---

## 自适应抗改版 + 并发（规模化必备）

**Scrapling `auto_save`（对抗网站改版）**：元素指纹存本地，页面改版自动重定位，比写死选择器鲁棒一个量级。

```python
from scrapling import StealthyFetcher
page = StealthyFetcher.fetch(url, headless=True, network_idle=True, auto_save=True)  # 自适应追踪
# 三种模式：http(curl_cffi TLS伪装) / stealth(Cloudflare) / dynamic(Playwright SPA)
```

**双引擎自动降级**：`huo15-js-scraper` 策略——企微文档/微信→Playwright；Cloudflare→scrapling stealth；Vue/React SPA→Playwright；静态→scrapling basic；失败自动切。

**并发控制**（来源 `puppeteer-stealth` p-queue / `anti-bot-scraper` 批量模式）：

```python
SEM = asyncio.Semaphore(3)          # 同域并发 ≤3
# 请求间隔随机 1.5~5s；429/403 立即退避，不换 IP 硬刚
# 企查查类：优先官方 MCP/API，直接抓取仅作备用（Cookie ~7 天过期）
```

---

## 混合架构（生产推荐）

成本最优解不是选一个工具，而是**分工**：

```
浏览器（L3/L4，少量实例）  →  过 JS 挑战 / 生成签名参数 / 拿 clearance cookie
                ↓ 导出 cookie + 锁定同一出口 IP + 同一 UA
curl_cffi（L1，高并发）    →  批量抓取正文/接口，速度是浏览器的几十倍
                ↓ cookie 失效（403 回归）
              自动回到浏览器重取，形成闭环
```

签名参数同理：浏览器里 `page.evaluate("window.sign(arg)")` 或 JSRPC 暴露函数，主流程仍用 HTTP 客户端跑。

---

## 内容层工具

**字体反爬还原**：
```python
from fontTools.ttLib import TTFont
font = TTFont("target.woff")
cmap = font.getBestCmap()          # {码位 int: 字形名}
# 用字形轮廓坐标做哈希，与基准字体的 0-9/常用字轮廓比对，建立 码位→真实字符 映射
```

**CSS 偏移取真值**（在浏览器里执行）：
```javascript
getComputedStyle(el, '::before').content     // 伪元素里的真值
```

**OCR**：本机有 `tencentcloud-ocr` skill（腾讯云高精度版），适合图片字段、雪碧图、瑞数图片下发字段。

**HTML→Markdown 省 token**：`r.jina.ai/<url>`（限 20 RPM，正文类页面适用）。

---

## 选型决策树

```
需要 JS 渲染吗？
├─ 否 → 有反爬吗？
│      ├─ 否 → requests（最快）
│      └─ 是 → curl_cffi impersonate            ← 90% 的"反爬"到这就解决了
└─ 是 → 先找 XHR/JSON 接口！找到就退回上面一支
       └─ 找不到 → 防护强度？
              ├─ 弱  → patchright (channel="chrome")
              ├─ 中  → patchright/nodriver + 住宅代理 + 拟人行为
              ├─ 强  → camoufox + 移动/住宅 IP + 会话预热
              └─ 极强/量小 → 真实浏览器 CDP（web-access skill）
批量 100+ URL 同站 → Scrapy / scrapling Spider（自带限速、去重、重试）
```
