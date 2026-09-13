# 指纹伪装与拟人化：可复用资产

集大成自 SkillHub 上 `stealth-browser-collector`（四段式编排：指纹池→去特征→拟人→落地）、`anti-bot-scraper`（纯手写反检测）、`coco-playwright-stealth` / `playwright-scraper-skill`（场景矩阵与实测）、`webclaw3`（受控组件输入）。

本文件给"挑身份 + 去痕迹 + 像人"三件可以直接抄的成品。所有内容默认用于**你自己的已登录账号 / 公开数据 + 低频**，合规红线见 `SKILL.md §0`。

---

## 1. 指纹池（挑一个像真人的身份）

风控第一关是「UA 说 Chrome 但别的信号说脚本」。所以身份三件套必须自洽：**UA × 视口分辨率 × 平台/机型 × 时区/语言** 要来自同一真实设备。下面给按真实市场份额加权的池。

### 1.1 桌面 UA 池（按权重随机取）

```python
# 权重 = 该浏览器在真实流量里的占比，随机取时按权重抽，别 uniform
DESKTOP_UA = [
    # Chrome / Windows（占比最高，首选）
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", 40),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", 12),
    # Edge / Windows
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0", 14),
    # Firefox / Windows
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0", 8),
    # Chrome / macOS
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", 12),
    # Safari / macOS
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15", 6),
    # Chrome / Linux（占比低，非必要别用，Linux 桌面 UA 反而显眼）
    ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", 3),
]
# 移动端 UA：某些站（小红书/抖音类）对移动 UA 更友好，但要和视口/机型配套
MOBILE_UA = [
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", 30),
    ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", 30),
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.0.0 Mobile/15E148 Safari/604.1", 10),
]

import random
def pick(pool):
    uas, ws = zip(*pool)
    return random.choices(uas, weights=ws, k=1)[0]
```

### 1.2 分辨率池（与 UA 平台自洽）

```python
# 桌面分辨率（与上面 Windows/Mac UA 配套）；移动与 iPhone/Android UA 配套
DESKTOP_VIEWPORT = [
    (1920, 1080, 38), (1536, 864, 18), (1440, 900, 14), (1366, 768, 12),
    (2560, 1440, 5), (1280, 720, 5), (1680, 1050, 3), (1360, 768, 3),
    (2560, 1600, 1), (1920, 1200, 1),
]
MOBILE_VIEWPORT = [(390, 844, 40), (393, 851, 25), (414, 896, 20), (375, 812, 15)]  # iPhone/Android 常见
```

**一致性铁律**：UA 说 Windows → 视口取桌面、时区取 `Asia/Shanghai`、语言 `zh-CN`；UA 说 iPhone → 视口取移动、`--use-mobile`、pixelRatio 3。任何跨平台错位（Win UA + Apple GPU、移动 UA + 桌面视口）会被一眼判机器。

> 更省事的做法：直接用 `camoufox`（Firefox C++ 层）或 `BrowserForge` 生成自洽指纹，别自己拼。

---

## 2. 反检测注入清单（页面加载前注入）

所有反检测代码**必须在 `addInitScript`（Playwright）/ `evaluateOnNewDocument`（puppeteer）里注入**，即页面任何脚本运行之前就生效。事后 `Object.defineProperty` patch 往往来不及——Challenge 脚本首行就读取。

### 2.1 纯手写注入（无第三方 stealth 插件，避免插件已知特征）

来源 `anti-bot-scraper`（实测 Cloudflare/PerimeterX 档可用）、`coco-playwright-stealth`。

```javascript
// initScript.js —— 通过 page.addInitScript({ content: `...` }) 注入
(() => {
  // 1. 隐藏 webdriver 标记（必需，缺失直接判机器）
  Object.defineProperty(navigator, 'webdriver', { get: () => false });

  // 2. UA 已在 launch context 设好；这里补 navigator.userAgent 一致性
  //    （若用 context.new_context(user_agent=...) 可不重复）

  // 3. WebGL / Canvas 微噪声：加「极小」随机偏移，大了反而异常
  const canvas = HTMLCanvasElement.prototype;
  const g = canvas.getContext;
  canvas.getContext = function (type, ...a) {
    const ctx = g.call(this, type, ...a);
    if (type === '2d') {
      const og = ctx.getImageData;
      ctx.getImageData = function (x, y, w, h, ...r) {
        const d = og.call(this, x, y, w, h, ...r);
        for (let i = 0; i < d.data.length; i += 4) {
          d.data[i]   += (Math.random() * 2 - 1) | 0;  // ±1，肉眼无感
          d.data[i+1] += (Math.random() * 2 - 1) | 0;
          d.data[i+2] += (Math.random() * 2 - 1) | 0;
        }
        return d;
      };
    }
    return ctx;
  };

  // 4. navigator.plugins / languages / hardwareConcurrency 伪装
  Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3].map(() => ({ name: 'Plugin', description: 'desc', filename: 'file' })) });
  Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
  Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
  Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });

  // 5. Chrome 专属：抹掉 headless 痕迹
  delete navigator.__proto__.webdriver;
})();
```

**微噪声原则**：Canvas/WebGL 偏移控制在 ±1~2，目的是让每次哈希不同（反关联），不是伪造完全不同的值。噪声过大 → 同一站多账号指纹明显异常 → 反向标记。

### 2.2 用现成插件（更快，但带已知特征）

- Playwright 系：`patchright`（已替你补 CDP 泄漏，首选）→ 或 `playwright-extra` + `puppeteer-extra-plugin-stealth`
- Puppeteer 系：`puppeteer-extra` + `puppeteer-extra-plugin-stealth` + `cheerio` 解析 + 住宅代理轮换 + `p-queue` 并发控制
- 实测（coco，Discuss.com.hk）：纯 Playwright + 手写/插件 stealth **100%**；Puppeteer 标准版 0%、Crawlee 0%、Chaser(Rust) 0% —— **纯 Playwright + 反检测技术（独立于框架）最有效**

### 2.3 无效措施（别浪费时间）

- ❌ 只改 UA —— 不够，TLS/头序/JS 指纹全漏
- ❌ 上 Crawlee / Selenium / 标准 Puppeteer —— 比裸 Playwright 更容易被检测
- ❌ Docker 隔离 —— 对 Cloudflare 毫无帮助（容器指纹更单一）
- ✅ 有效：隐藏 webdriver + 真实 UA + 随机延迟/滚动 + 避免框架特征 + `addInitScript` 前置注入

---

## 3. 拟人化输入（受控组件 + 逐字打字）

来源 `webclaw3`：React/Vue 受控组件直接 `el.value = x` 不会触发框架状态更新，必须走原生输入事件。

```javascript
// 在 page.evaluate 内执行：像人一样逐字符输入
function humanDelay(mu, sigma = 0.6) {
  // 对数正态重尾延迟（Box-Muller）——人类节奏禁用均匀随机（Precursor 识别特征）
  const u = 1 - Math.random(), v = Math.random();
  const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  return Math.max(30, Math.exp(Math.log(mu) + sigma * z));
}
function humanType(el, text) {
  const proto = HTMLInputElement.prototype;
  const desc = Object.getOwnPropertyDescriptor(proto, 'value');
  for (const ch of text) {
    desc.set.call(el, el.value + ch);
    el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: ch }));
    // 重尾键间延迟（中位 ~90ms）+ 10% 概率思考长停顿，偶有 1s+ 停顿
    await new Promise(r => setTimeout(r, humanDelay(Math.random() < 0.1 ? 900 : 90, 0.7)));
  }
  el.dispatchEvent(new Event('change', { bubbles: true }));
}
// 调用（注意要在 async IIFE 里）
```

配合 `toolbox.md` 里的 `human_move`（贝塞尔轨迹 + 认知识别延迟）、`human_scroll`（变速滚动）、`warmup`（会话预热）——所有延迟统一走 `human_delay`（对数正态重尾，见 toolbox.md 统一规则），形成完整「像人」闭环：先首页停留滚动预热 → 贝塞尔移动到搜索框 → 逐字打字 → 犹豫点击 → 变速滚动阅读。Precursor 站点再升一级：用 `replay_track` 回放人工录制的真实轨迹（保真度 > 数学合成）。

**逐字打字是抗行为分析的关键一招**：机器人 `el.value=` 瞬间填满，缺输入事件流；真人每秒 3~8 字符且有停顿。

---

## 4. 并发与限速（工程稳定性）

来源 `anti-bot-scraper`（批量模式 concurrency=3 自动限速）、`puppeteer-stealth-web-scraper`（p-queue）。

```python
# 批量抓多个 URL：并发 ≤3、自动限速、指数退避
import asyncio, random
SEM = asyncio.Semaphore(3)
async def safe_fetch(url, fn, tries=3):
    for i in range(tries):
        async with SEM:
            try:
                return await fn(url)
            except Exception:
                await asyncio.sleep(2 ** i * 3 + random.uniform(0, 2))
    return None
```

- 同域并发 ≤3，请求间隔随机 1.5~5s（合规指南建议 ≥1~3s 起步）
- 收到 429/403 **立即退避**，不要换 IP 硬刚——对抗升级没有赢家
- 错峰：避开目标站业务高峰（夜间/低峰）
- UA 带真实标识与联系方式（被投诉时是善意证明）
