# L5 深潜：复用你自己的已登录 Chrome（CDP）

集大成自 `webclaw3`、`cdp-autorunner-skill`、`cdp-browser-master`、`browser-cdp-connect`。这是 2026 年反爬里**性价比最高、最被低估**的解法——真实浏览器 + 真实指纹 + 真实登录态，风控评分天然高，Cloudflare/Turnstile/DataDome/PerimeterX 基本不触发。

**什么时候必须走这条**：
- 目标站 headless 被硬封（贝壳 `hip.ke.com/forbidden`、自如 EdgeOne、小红书强反自动化）
- 需要登录态才能看的内容（你**自己的**账号，不是绕过登录墙）
- 前面 L1~L4 全挂、量又不大（千级以下）

> ⚠️ 合规边界：登录态复用只用于「你已正常登录的账号」做日常自动化。绝不用于绕过登录/鉴权拿非公开数据、不破解付费墙。操作前要向用户明示"会用你的 Chrome 登录态"。

---

## 1. 开启远程调试（两种方式）

### 方式 A：启动参数（最直白，反检测参数一起加）

```powershell
# 自动定位浏览器（优先 PATH，否则找标准安装目录），无需手写 exe 路径
function Start-CDP {
    param([int]$Port = 9223)
    $chrome = (Get-Command chrome -ErrorAction SilentlyContinue).Source
    if (-not $chrome) {
        $cands = @(
            "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
            "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
            "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
        )
        $chrome = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
    }
    if (-not $chrome) { Write-Warning "未找到 Chrome/Edge，请安装或用 patchright 自带 chromium"; return }
    Start-Process $chrome --remote-debugging-port=$Port --disable-blink-features=AutomationControlled
    Write-Host "CDP 已启动 → http://127.0.0.1:$Port/json"
}
Start-CDP -Port 9223
```
- **`--disable-blink-features=AutomationControlled` 是关键**：去掉 `navigator.webdriver=true` 这个最显眼的机器人标记
- 之后 CDP 端点：`http://127.0.0.1:9222/json`（列 tab）、`ws://127.0.0.1:9222/devtools/browser/<id>`

### 方式 B：chrome://inspect（更隐蔽，不动启动参数）

1. 用户 Chrome 地址栏打开 `chrome://inspect/#remote-debugging`
2. 勾选 "Allow remote debugging for this browser instance"
3. 生成 `%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort`（两行：端口 + wsPath UUID）
4. 拼 `ws://127.0.0.1:<port>/devtools/browser/<wsPath>`

**注意**：UUID 每次 Chrome 重启都变，必须脚本现读 `DevToolsActivePort`，不能硬编码。

> 本机已有 `web-access` skill 就是把这条路封装成 HTTP API（CDP proxy 127.0.0.1:3456）。日常直接用 web-access 即可，下面的代码是原理与兜底。

---

## 2. 连接发现 + 基础控制（Python websocket）

```python
import json, websocket  # pip install websocket-client
import requests as http

def get_cdp_ws(port=9222):
    tabs = http.get(f"http://127.0.0.1:{port}/json").json()
    # 选一个目标 tab，或开新 tab：POST /json/new?<url>
    return tabs[0]["webSocketDebuggerUrl"]

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url)
        self._id = 0
    def send(self, method, params=None, session=None):
        self._id += 1
        msg = {"id": self._id, "method": method, "params": params or {}}
        if session: msg["sessionId"] = session
        self.ws.send(json.dumps(msg))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self._id:
                return r.get("result")
    # 页面级操作要用 session：先 Target.attachToTarget 拿 sessionId
    def goto(self, url):   return self.send("Page.navigate", {"url": url})
    def eval(self, code):  return self.send("Runtime.evaluate", {"expression": code, "returnByValue": True})
    def click(self, sel):
        # 计算中心坐标后 Input.dispatchMouseEvent（比 element.click() 更像真人）
        ...
```

---

## 3. 智能等待（替代固定 sleep）

来源 `cdp-browser-master`：固定 `sleep(3)` 是随机挂的头号元凶——太短没渲染完，太长浪费。用**网络空闲检测**替代。

```javascript
// 在页面里轮询：无网络请求持续 500ms 即视为空闲
async function waitNetworkIdle(timeout = 10000) {
  const t0 = Date.now();
  let last = Date.now();
  const obs = new PerformanceObserver(list => { last = Date.now(); });
  obs.observe({ entryTypes: ['resource'] });
  return new Promise(res => {
    const iv = setInterval(() => {
      if (Date.now() - last > 500 || Date.now() - t0 > timeout) {
        clearInterval(iv); obs.disconnect(); res();
      }
    }, 200);
  });
}
// 跨页面导航（点击/回车后 URL 变）：用 location.href 轮询，
// 因为 MutationObserver 会随旧页面销毁而失效
```

等价地，Playwright 用 `page.wait_for_load_state("networkidle")`，puppeteer 用 `waitUntil: 'networkidle'`。**结论：永远等条件，不等固定时间。**

---

## 4. 多备选选择器降级（抗改版）

来源 `cdp-browser-master` `robustFind`：网站改版选择器就失效，所以每次定位提供"从精确到模糊"的多备选，第一个命中就用。

```javascript
async function robustFind(browser, candidates) {
  for (const sel of candidates) {
    const hit = await browser.eval(`!!document.querySelector(${JSON.stringify(sel)})`);
    if (hit) return sel;
  }
  throw new Error("所有备选选择器都未命中: " + candidates.join(", "));
}
// 使用：从最精确到最宽松
const sel = await robustFind(browser, [
  '.bili-video-card__title',                 // ① 精确 class
  '[class*="video-card"] [class*="title"]',  // ② 模糊 class（哈希后缀也能命中）
  'h3.title',                                // ③ 语义 tag
  'a[href*="/video/"]'                       // ④ 属性选择器
]);
```

**选择器韧性优先级**（低→高 脆弱度）：`data-testid`/`data-*` > `[class*="xxx"]` 模糊 > 语义 role+文本 > 稳定 id/name > CSS 类名 > XPath 长路径（禁用 nth-child/长 XPath，布局一变就挂）。先 `count` 验证匹配数，再 `css` 提取，少走弯路。

---

## 5. 数据提取层级（ariaTree + eval + 穿透框架）

来源 `webclaw3`：先理解结构，再取数据，绝不拿纯文本正则硬抠。

| 层级 | 方法 | 适用 |
|---|---|---|
| L1 | `page.eval` + CSS selector | 首选：从 DOM 直接取结构化 JSON（保留 href/data-*） |
| L2 | ariaTree 直读 | 只需看全貌、确认数据项数量/结构 |
| L3 | `page.eval` 穿透框架数据层 | SPA 无语义 class，从 React/Vue 全局 store 拿原始对象 |
| L4 | 交互触发（click/翻页/滚动） | 数据需交互才出现 |

**L3 穿透入口**（SPA 哈希 class 定位不到时）：
```javascript
// React: 沿 fiber 找 memoizedProps
document.querySelector('#root').firstChild._reactRootContainer
  ._internalRoot.current.child.memoizedProps  // 或 __reactFiber$ 链路
// Vue: 组件实例
document.querySelector('[data-v-app]').__vue__.$data
// 全局状态
window.__NEXT_DATA__        // Next.js
window.__INITIAL_STATE__    // 多数 SPA
```

**提取纪律**：先用 `getText`/`innerHTML.substring(0,3000)` 侦察结构 → 再用 `eval` 取 `textContent` 原值 → 后处理才决定 split/regex/LLM。结构化数据一律 `JSON.stringify(Array.from(querySelectorAll(...)).map(...))`，**不要 getText 拿纯文本再正则**（丢 href/class/data-*，极脆弱）。

**浏览器内累积再导出**（避免 shell 中转大 JSON 丢数据）：
```javascript
// 翻页时累积到全局变量，全采完一次性导出
await page.eval("window.__collected = window.__collected || []; window.__collected.push(...)");
// 最后：
const all = await page.eval("JSON.stringify(window.__collected)");
```

---

## 6. 受控组件输入 + HttpOnly Cookie

**受控组件**（React/Vue input 不能用 `el.value=`）：见 `stealth-profiles.md §3` 的 `humanType`。

**HttpOnly Cookie**（document.cookie 拿不到）：用 CDP 命令
```python
session = cdp.send("Target.attachToTarget", {"targetId": tab_id, "flatten": True})
cookies = cdp.send("Network.getCookies", {"urls": ["https://target.com"]}, session["sessionId"])
# 拿到的含 HttpOnly，可直接喂回 L1 curl_cffi 高速抓取（锁定同一出口 IP）
```

---

## 7. SPA 内部路由（直接 navigate 子路由会 404）

来源 `cdp-browser-master` Minimax/Next.js 实战：Next.js/React 内部路由直接 `Page.navigate` 到子路由返回 404。正确姿势——**先入可访问的父页，再用 JS 点击侧边栏菜单（多是 div 不是 a）触发内部跳转**，跳转后 URL 变但页面不刷新。

```javascript
await browser.goto("https://app.com/user-center/basic-information");  // 可访问父页
await browser.eval(`(function(){
  for (const d of document.querySelectorAll('div'))
    if (d.innerText && d.innerText.trim() === 'Token Plan' && d.className.includes('cursor-pointer')) {
      d.click(); return 'clicked';
    }
})()`);
await waitNetworkIdle();  // 等 SPA 路由数据加载
```

---

## 8. 实测站点踩坑库（2026 验证）

| 站点 | headless 表现 | 用户 Chrome (CDP) | 要点 |
|---|---|---|---|
| 贝壳 sh.zu.ke.com | `hip.ke.com/forbidden` 硬封 | 正常（搜索+详情均可） | 必须 CDP |
| 安居客 | 403 + 验证码 | 正常 | — |
| 自如 ziroom.com | EdgeOne 防护 | 待验证 | — |
| 小红书 | 强反自动化（UA+行为） | 部分可用，先测能否正常浏览 | 选择器随时变，用探测模式 |
| B站 | web_fetch 空壳 | DOM 提取可用 | API 有 wbi 签名保护，必须走 DOM；播放量 `parseInt(play.replace(/\D/g,''))` |
| Discuss.com.hk | web_fetch 0% / Playwright Simple 20% | 纯 Playwright+Stealth **100%** | 验证：5 秒 200 OK |
| 淘宝 | — | cdp 可用 | CSS Modules 哈希 class；价格用 `¥(\d{2,4})(?=\+|优惠)` 防粘连 |
| 企查查 | 需登录 | MCP 官方 API 更稳（推荐） | 直接抓取 Cookie ~7 天过期 |

> 把你对每个站验证过的「选择器 / URL 模式 / 陷阱 / 日期」写进 `web-access` 的 `references/site-patterns/{domain}.md`，下次免重跑诊断。
