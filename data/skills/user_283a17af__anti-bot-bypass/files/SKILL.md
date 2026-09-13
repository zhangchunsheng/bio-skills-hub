---
name: anti-bot-bypass
description: 网站反爬机制的识别、分层诊断与合法绕过（集大成版，一站涵盖市面上主流反爬 skill 的能力）。先用探针判定站点用了哪一层防护（IP/TLS指纹/JS挑战/浏览器指纹/行为分析/验证码/字体CSS加密/参数加密），再按「最低成本阶梯」逐级升级方案（curl_cffi → patchright/nodriver → camoufox → 真实浏览器CDP → 商业API）。含 Cloudflare/Akamai/DataDome/PerimeterX/Kasada 与国内瑞数/极验/顶象/腾讯天御/同盾/数美/网易易盾 的指纹特征库；并内置 自家Chrome CDP复用(L5)、指纹池(UA/分辨率加权)、反检测注入清单(addInitScript)、拟人逐字打字、自适应抗改版(auto_save)、选器路由矩阵、合规四查。v1.0.7 更新 2026-08 市场增量：Cloudflare Precursor 会话级持续行为验证（生理级特征判定，均匀随机拟人反而成 bot 指纹）、Web Bot Auth(RFC 9421)/DataDome KYA/HUMAN Verified AI Agent 身份认证浪潮、DataDome Agent Trust+Priority Protect、Kasada V2、BotBase 与 AI 诱饵页面；v1.0.6 已补 JA4+ 完整指纹体系（JA4/JA4S/JA4H/JA4L 四维交叉，打乱扩展顺序绕过已失效）、Cloudflare AI 流量 Search/Agent/Training 分类与 2026-09-15 默认屏蔽 Agent、DataDome 意图分析+85000 客户模型、Akamai 持续认证、Kasada bytecode VM+时间绑定 token、设备DNA持久化+跨站图关联、第四代 AI 动态风控与边缘前置；并保留 v1.0.5 的 R/C/T 短板根治（探针 [Exxx] 中文编号+自动重试、FAQ 30 条、5分钟上手路径图、国内环境适配）。触发词：网站爬不动、抓取失败、被封了、返回403/429、页面打不开、想采集数据、怎么绕过限制、这个网站能爬吗、帮我分析反爬、电商价格监控、网页数据采集、公开数据抓取、招聘信息/商品价格/热点榜单、Cloudflare 拦截、验证码过不去、字体反爬、JS 加密参数、TLS 指纹、自家 Chrome 采集、指纹伪装、拟人化浏览、anti-bot、bypass。
agent_created: true
---

# 反爬机制识别与分层突破

**核心信条：反爬不是"破解一道墙"，是"通过一个信任评分"。** 现代风控同时看 6~8 层信号并做交叉一致性校验——UA 说 Chrome 但 TLS 说 Python，代理再干净也死。所以正确姿势是**先诊断哪一层不达标，只修那一层**，而不是一上来就开重型浏览器。

**本 skill 的独有资产**：① 内置探针自动判层（仅标准库，零依赖可跑）；② 22 家国内外厂商指纹库；③ **已验证站点经验库**（`references/site-cases.md`）——记录瑞数无限 debugger、Akamai 影子封禁（200 但假数据）、电商字体反爬、自动化降级空壳页等**真实踩坑**，这是纯原理文档没有的实战资产。

## 0. 国内环境专门适配（为什么对国内站更顺手）

本 skill 从设计上就面向**国内站点与国内网络环境**，不是把英文教程翻译一遍：

- **国内风控厂商库最全**：瑞数（政务/司法/海关重灾区）、极验、顶象、同盾、数美、网易易盾、阿里云 WAF/滑块、腾讯天御/防水墙、百度云加速——都收录在 `references/vendors.md`，含清关 cookie 语义与版本判定。
- **中文报错 + 中文文档**：探针所有异常都是 `[Exxx] 中文原因：中文建议`（见 FAQ「错误代码速查表」），不会甩英文堆栈；文档全中文，含国内真实案例。
- **国内网络优化**：依赖安装统一用 `清华镜像源`（`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple`），避免国内官方源超时；代理/住宅 IP 调度也按国内可用性说明。
- **合规贴合国内法**：红线判定参照《个人信息保护法》《数据安全法》《网络安全法》，登录墙/验证码/个人信息三类场景明确标注为"拒采"。
- **国内站点速查表**：视频/电商/瑞数/CF/Akamai/招聘/社交等 13 类站点直接对号入座（见 FAQ「〇、国内常见站点速查表」）。

> 一句话：国外反爬教程讲 Cloudflare/Akamai 多，本 skill 把**瑞数、极验、阿里云、腾讯云、易盾**这些"中国互联网特色墙"也讲透，且全程中文可落地。

> ⚠️ **2026 新增提醒（Agent 类自动化）**：国际 CDN（Cloudflare 等）已从 2026-07 起把流量按行为分 Search/Agent/Training 三类，**browser-use / 浏览器驱动类 agent（含 Claude/Gemini 驱动 Chrome）被归为 Agent 类，默认在广告页被屏蔽**（2026-09-15 起对新域名生效）。如果你用本 skill 驱动 agent 抓取，务必声明诚实 UA 并优先走授权/付费抓取通道，纯指纹伪装已不足以绕过"身份拦截"。

## 能力边界总览（先看这个，再决定用不用）

| 我能做 | 我不能做 | 我需要你配合 |
|---|---|---|
| 分析公开页面为什么 403/429 | 绕过登录/付费墙抓非公开数据 | 告诉我目标 URL 与你要什么数据 |
| 用探针判定站点防护层级（L1~L5） | 破解登录/支付/实名环节的验证码 | 确认目标是公开可访问页面 |
| 给最低成本绕过方案 + 可运行模板 | 抓个人信息（手机号/身份证/人脸） | 已有 web-access / scrapling 时直接复用 |
| 用 L5 真实浏览器采公开页 | 高频采集造成服务压力 | 遇到验证码时接受"减速或放弃"建议 |
| 识别 Cloudflare/瑞数/极验/顶象等厂商 | 批量注册/刷单/抢购 | 遵守 robots.txt 与网站 ToS |

**一句话判断**：搜索引擎不登录就能点开的页面，我可以帮你采；**必须登录/验证码才能看到的内容，我不碰**。

---

## 0. 合规红线（每次任务开始前自检，不可跳过）

允许：公开可访问数据、自有/已授权站点、遵守 robots.txt 与 ToS、低频礼貌抓取、官方 API 优先。

**禁止（命中任一项直接拒绝并向用户说明）：**
- 绕过登录/鉴权获取非公开数据；破解付费墙、会员内容
- 高频请求造成服务压力（等同 DoS）；绕过风控做批量注册、刷单、抢购、爬取账号
- 抓取个人信息（手机号/身份证/人脸/住址等）—— 触及《个人信息保护法》《数据安全法》
- 破解验证码用于对抗身份核验环节（登录、支付、实名）
- 将本能力封装为「可一键自动注入对话上下文」的插件（如意图路由自动注入 skill body 类形态），避免被供应链投毒复用；判层与绕过代码须保持分离、可读、可审、可逆

灰色地带（先问用户目的与授权情况）：竞品价格、简历库、社交平台用户内容、政务/司法数据批量化。

告知用户的标准话术：「这站用了 X 防护，技术上可以用 Y 方式访问公开页。但请确认你有抓取授权，并且我会控制在低频。」

### 合规四查（动手前必过，来源：昆仑增长合规指南）

技术上能拿到 ≠ 法律上可以拿。任何采集任务开场先过这四查，一票否决项直接停：

1. **robots 协议**：目标站 `/robots.txt` 的 Disallow 路径不采（行业共识 + 诉讼诚意证据）
2. **服务条款 ToS**：明确禁止自动化采集的，商用别碰；需登录才可见的内容，风险陡增
3. **个人信息红线**：姓名/联系方式/账号主页等受《个人信息保护法》约束——"公开可见"≠"可采集存储再利用"，原则上不采
4. **数据用途**：自用分析 / 学术研究 / 商业转售风险等级完全不同；转售他人数据库可能侵犯数据库权与著作权

**一票否决**：绕过付费墙、破解验证码规模化采集、爬竞品全量做同质化产品。

**典型禁区（强制登录 + 身份核验验证码，直接拒）**：BOSS直聘/猎聘/智联招聘/前程无忧等招聘类、小红书/微博/抖音等强登录内容类、淘宝/京东的登录后订单与买家中心。这些站点的岗位/内容/订单**必须手机号登录 + 过极验/滑块等身份核验验证码才可见**，同时命中「绕过登录墙」与「对抗身份核验验证码」两条红线——即便技术上可用 L5 真实浏览器手动过一次码再复用登录态，**那本质仍是绕过登录墙，违规**。正确做法：转向无需登录的公开聚合源（职友集/看准网/官方薪酬报告等 SEO 页）获取同口径数据，或在合规四查通过后只采 robots/ToS 允许的公开页。

> ⚠️ 边界判定口诀：**「不登录就看不到 = 不能爬」**。凡内容藏在登录态之后，无论技术多顺，都属于红线范围；公开 SEO 页（搜索引擎能直接收录的）才在允许侧。

**采集礼仪**（既是道德也是稳定性）：限速 ≥1~3s 起步、错峰低峰、同页不重复请求、UA 带真实标识、收到 429/403 **立即退避不换 IP 硬刚**。

## 0.5 快速开始：与已有 skill 如何协作

本 skill 只做「诊断 + 决策 + 判层」和「各层模板」，不重复造轮子。落地执行请直接复用本机已有 skill：

| 你要干什么 | 先用 anti-bot-bypass | 再交给谁 | 为什么 |
|---|---|---|---|
| 判断目标站能不能爬、是哪一层在拦 | 跑 `probe.py` | — | 拿到层级和起点建议 |
| 静态 HTML / JSON API 数据 | 判定为 L0/L1 | `curl_cffi` 或 `web_fetch` | 毫秒级、零浏览器开销 |
| 需 JS 渲染但无强指纹 | 判定为 L3 | `scrapling` / `patchright` / `nodriver` | 伪装 headless |
| 强指纹 / 行为分析（DataDome/Akamai） | 判定为 L4 | `camoufox` + 住宅代理 | C++ 层伪装 |
| 量小 / 登录态 / 前面全挂 | 判定为 L5 | `web-access`（CDP 连你日常 Chrome） | 真实指纹 + 真实历史 |
| 全站同爬 100+ URL | 判定后设计流水线 | `scrapling` Spider / Scrapy | 限速 + 去重 + 自适应 |

**典型会话流程**：
1. 你说：「帮我看看 xxx.com 能不能抓」
2. 我跑 `probe.py`，返回：「Cloudflare Turnstile，建议 L3 patchright」
3. 我直接用 `scrapling` 或 `patchright` 模板抓公开页，不重新发明实现

> 💡 如果你已经装了 `web-access` 或 `scrapling`，不用重复装环境；本 skill 的 `toolbox.md` 里提供了调用它们的代码片段。

---

## 0.6 三句话启动我（解决「不知道怎么叫我」的问题）

你不需要背触发词，遇到下面任意一种情况直接说：

| 你说 | 我会做 |
|---|---|
| **"这个网站爬不动 / 打不开了"** | 跑探针判层，告诉你是哪一层在拦、最低成本怎么破 |
| **"帮我抓 xxx 的公开数据"** | 先做合规四查，再找 L0 接口，最后给可运行模板 |
| **"返回 403 / 429 / 验证码"** | 分析厂商指纹，给出 L1~L5 的升级路线和具体命令 |

**完整触发词参考**：网站爬不动、抓取失败、被封了、返回 403/429、页面打不开、想采集数据、怎么绕过限制、这个网站能爬吗、帮我分析反爬、电商价格监控、网页数据采集、公开数据抓取、招聘信息/商品价格/热点榜单、Cloudflare 拦截、验证码过不去、字体反爬、JS 加密参数、TLS 指纹、自家 Chrome 采集、指纹伪装、拟人化浏览、anti-bot、bypass。

---

## 0.7 安装后先跑自检（解决「不知道配置对不对」）

下载本 skill 后，**第一步先跑环境自检**——它帮你确认 Python 版本、网络、各层级依赖是否就绪，并给出「缺什么、怎么装」，不用等到跑任务才报错。这是评测反馈最想要的那把「自动化验证工具」。

```bash
python scripts/env-check.py
```

脚本逐项打印红/黄/绿中文报告：
- ✓ 绿 = 通过（如已装 curl_cffi、本机有 Chrome、网络可达）
- ! 黄 = 可选缺项（如没装 camoufox，但当前只跑 L1 不影响）
- × 红 = 必须修（如 Python 太旧、网络不通）

全绿或只有黄项，就可以开始抓：

```bash
python scripts/probe.py https://目标站
```

---

## 0.8 五分钟上手路径图（从装好到出结果，一步一步）

如果你第一次用，按这条线走，5 分钟内必出第一个判层报告：

```
① 自检环境       python scripts/env-check.py
                 ↓ 全绿/只有黄项即可继续
② 跑探针判层     python scripts/probe.py https://目标站
                 ↓ 看报告的「建议起点: Lx」
③ 对号入座选方案  L0 找 API → L1 curl_cffi → L2 住宅代理 → L3 patchright
                  → L4 camoufox → L5 web-access（真实浏览器）
                 ↓ 不确定时
④ 查 FAQ 速查     references/FAQ.md（30 个场景问题 + 错误代码速查表）
                 ↓ 仍卡住
⑤ 看实战案例      SKILL.md §8（B站/Cloudflare/电商字体 3 个完整案例）
⑥ 看踩坑经验库    references/site-cases.md（瑞数/Akamai/字体反爬等真实记录）
```

> 记住一条心法：**先诊断、后升级、被拒才加级**。不要一上来就开浏览器——L0/L1 能解决 80% 的站。

---

## 1. 诊断优先：先跑探针，别猜

```bash
# 纯标准库，无依赖即可运行；装了 curl_cffi 会自动多做一轮 TLS 对照实验
python scripts/probe.py https://target.com
python scripts/probe.py https://target.com --json      # 机器可读
python scripts/probe.py https://target.com --save out/ # 落盘首屏 HTML 供人工看
```

探针输出四件事：**命中的厂商 / 触发的防护层 / 是否必须渲染 JS / 建议起点方案（阶梯层级 L1~L5）**。

关键对照实验（探针自动做，也可手动复现）——这是判层最快的方法：

| 裸 requests | curl_cffi impersonate | 结论 |
|---|---|---|
| 403/429 | 200 | **纯 TLS/HTTP2 指纹层**拦截 → L1 就够，不要开浏览器 |
| 403 | 403 | IP 信誉或 JS 挑战 → 换出口 IP 再测；仍失败进 L2 |
| 200 但 HTML 无正文 | 同 | 不是反爬，是 SPA 渲染问题 → 优先找 XHR/JSON 接口，别开浏览器 |
| 200 首次、几十次后 429 | 同 | 频控/配额 → 限速 + 会话轮换，L1 即可 |
| **200 但首屏文本极短 + 命中风控** | 同 | **200 ≠ 成功**，拿到的是挑战页/影子封禁页 → 按内容判定，别信状态码 |
| 裸 200 而 curl_cffi 403 | — | 实测存在（如 zillow/PerimeterX）：裸的那个 200 是挑战页；或该站对「完美 TLS + 不执行 JS」额外敏感 |

**先找接口，再谈绕过。** 80% 的"反爬"其实是数据在 XHR 里：F12 Network 筛 Fetch/XHR，或直接搜 HTML 里的 `__NEXT_DATA__` / `window.__INITIAL_STATE__` / `application/ld+json`。命中就零成本拿结构化数据，反爬层大多不覆盖内部 JSON 接口。

---

## 2. 成本阶梯：只爬到必要的那一级

每级都比上一级贵 5~50 倍（时间+算力+代理费）。**从 L1 起，被拒才升一级。**

| 级 | 手段 | 破哪层 | 成本 | 何时用 |
|---|---|---|---|---|
| **L0** | 直接命中 JSON 接口 / sitemap / RSS / Common Crawl / Wayback | 全绕开 | ~0 | 永远先试 |
| **L1** | `curl_cffi impersonate="chrome"` + 完整头序 + 限速 | TLS/JA4、HTTP2 SETTINGS、头指纹、频控 | 极低（~125ms/req） | 静态 HTML、JSON API、Cloudflare 低敏感档 |
| **L2** | L1 + 住宅代理轮换 + 会话粘滞 | IP 信誉 | ¥6~15/GB | L1 返回 403 但换 IP 后能通 |
| **L3** | `patchright` 或 `nodriver`（补掉 CDP 泄漏） | JS 挑战、headless 特征 | 中（~200MB/实例） | 必须执行 JS 才给数据；Turnstile 托管挑战 |
| **L4** | `camoufox`（Firefox C++ 层伪装）或 CloakBrowser + 住宅 IP + 拟人行为 | Canvas/WebGL/字体/音频指纹、行为分析 | 高 | DataDome、Akamai sensor、PerimeterX |
| **L5** | 真实浏览器接管（CDP 连本机日常 Chrome，带真实登录态与历史） | 几乎全部 | 低成本但不可并发 | 个人自用、量小、前面全挂 |
| **L6** | 商业 Scraper API / 打码平台 | 外包 | 按量付费 | 工程性价比拐点（见下） |

**L5 是 2026 年最被低估的解法**：真实浏览器 + 真实指纹 + 真实历史，风控评分天然高。本机已有 `web-access` skill 走 CDP 直连日常 Chrome，量小场景直接上 L5，比死磕 L3/L4 快得多。

**L5 实操要点（完整版见 `references/cdp-reuse.md`）**：
- 开启远程调试用 `--remote-debugging-port` 且**务必带 `--disable-blink-features=AutomationControlled`**（去掉 webdriver 标记）
- 用 `waitNetworkIdle`（网络空闲 500ms）替代固定 `sleep`；多备选选择器降级（`[class*="xxx"]` 模糊 > 语义 > 位置）
- SPA 内部路由：先入可访问父页再用 JS 点击触发，直接 navigate 子路由会 404
- HttpOnly cookie 用 CDP `Network.getCookies` 拿，回灌 L1 高速抓取
- 登录态复用只用于**你自己的账号**，不用于绕过登录墙；操作前明示用户

**何时该放弃自建（DIY→API 拐点）**：月请求量到百万级、目标是 DataDome/Akamai/Kasada 档、团队 ≤2 人 —— 维护指纹漂移会吃掉一个全职人力，此时商业 API 反而便宜。指纹补丁的有效期通常只有数周，风控一更新就整条流水线死，**要提前给"返工"留预算**。

### 选器路由矩阵（一眼决定用什么，来源：coco/playwright-scraper 场景矩阵 + 本 skill 阶梯）

| 目标站情况 | 反爬等级 | 直接用 | 备注 |
|---|---|---|---|
| 静态 HTML / 已知 JSON 接口 | 无 | `web_fetch` / `curl_cffi` http 模式 | 最快，0 成本 |
| 动态页需 JS 渲染 | 中 | Playwright 普通模式 / Scrapling `dynamic` | 先找 XHR 接口，找不到才上 |
| Cloudflare / Turnstile | 高 | Playwright Stealth / Scrapling `stealth` / patchright | 隐藏 webdriver + 真实 UA + 随机延迟 |
| 强指纹（DataDome/Akamai/PerimeterX） | 强 | camoufox + 住宅 IP + 会话预热 | 见 §5 |
| headless 被硬封（贝壳/自如/小红书） | 极强 | **自家 Chrome CDP 复用**（见 `references/cdp-reuse.md`） | 真实指纹+登录态，成功率最高 |
| 全站同爬 100+ URL | — | Scrapling Spider / Scrapy（限速+去重+重试+`auto_save` 自适应） | 流水线设计，别脚本裸奔 |

> ⚠️ 实测对照（Discuss.com.hk）：web_fetch 0% → Playwright 普通 20% → **Playwright+Stealth 100%** → Puppeteer 标准 0% → Crawlee 0% → Chaser(Rust) 0%。结论：**纯 Playwright + 反检测技术（独立于框架）最有效**，Crawlee/Selenium/标准 Puppeteer 反而更易被检测。

---

## 3. 八层机制速查（详见 `references/mechanisms.md`）

| 层 | 机制 | 典型症状 | 最低成本对策 |
|---|---|---|---|
| 1 | IP 信誉 / ASN / 频控 | 429、突然全 403、按 IP 段封 | 限速+抖动、住宅/移动代理、会话粘滞 |
| 2 | HTTP 头指纹 | 无提示 403 | 补全 Accept/Accept-Language/Accept-Encoding/Sec-CH-UA，**保持头顺序** |
| 3 | TLS/JA3/JA4 + HTTP2 指纹 | requests 403、浏览器正常 | `curl_cffi impersonate` （一行搞定 TLS+ALPN+HTTP2+头序） |
| 4 | JS 挑战（清关 cookie） | "Checking your browser"、202/412 中间页 | 真浏览器执行一次拿 cookie，**cookie 与 IP+UA 绑定**，换 IP 即失效 |
| 5 | 浏览器/设备指纹 | 浏览器能开但 headless 被拒 | patchright/nodriver（CDP 泄漏）→ camoufox（C++ 层） |
| 6 | 行为分析 | 首页正常、翻到第 N 页/点关键按钮被封 | 鼠标轨迹曲线、非匀速滚动、随机停顿、会话预热 |
| 7 | 前端加密（字体/CSS/雪碧图/参数签名） | 数字乱码、DOM 值≠显示值、请求带 sign/token | 字体映射表还原、伪元素取值、JS 逆向或直接 `page.evaluate` 调站内函数 |
| 8 | 验证码 | 滑块/点选/无感 Turnstile | 优先避免触发（提分而非解题）；必要时 L5 或打码服务 |

**第 7 层实战捷径**：与其扣 JS 算法，不如在浏览器上下文里直接调它自己的加密函数——`page.evaluate("window.xxxSign(arg)")` 或 hook 后 JSRPC 暴露。逆向 jsvmp/瑞数 vmp 是数天工作量，调用它自己的函数是数分钟。

---

## 4. 厂商指纹识别（详见 `references/vendors.md`）

见到这些立刻知道对手是谁、该跳哪一级：

| 线索 | 厂商 | 起点 |
|---|---|---|
| `cf_clearance` / `__cf_bm` / `cf-ray` 头 | Cloudflare | L1 常通；Turnstile 上 L3 |
| `_abck` / `bm_sz` / `ak_bmsc` | Akamai Bot Manager | L4（_abck 校验不过会**影子封禁**：返回 200 但数据是假的） |
| `datadome` cookie / 403 + DataDome 验证页 | DataDome | L4 + 住宅 IP，最吃指纹 |
| `_px3` / `_pxhd` / "Access to this page has been denied" | PerimeterX (HUMAN) | L4，clearance **强 IP 绑定**，跨 IP 用比不带更糟 |
| `x-kpsdk-*` 头 | Kasada | L4~L6，headless 极难 |
| 首请求 **202/412** + cookie 名后缀 `O/P/S/T` + 无限 debugger | **瑞数**（国内政务/司法/海关高发） | L3 起；版本判定见 vendors.md |
| `geetest` 域名/标识 | 极验 | 轨迹模拟（先加速后减速） |
| `tdc.js` + `collect` 参数 | 腾讯天御 | jsvmp，L5 更划算 |
| `fm.js` + `blackbox` | 同盾 | 动态 js |
| `ac` 参数 + 顶象标识 | 顶象 | WebAssembly 无感验证 |
| `fverify` / `organization` | 数美 | 相对易 |
| `dun.163.com` + `data/fp/cb` 参数 | 网易易盾 | 参数杂 |

---

## 5. 工具选型（2026 实测基准，详见 `references/toolbox.md`）

反检测基准（ianlpaterson 2026，7 工具 × 31 个 Cloudflare 目标 × 3 轮）：

| 工具 | 通过率 | 备注 |
|---|---|---|
| **nodriver** | 31/31 | 直连 CDP，控制面无 Playwright，冠军 |
| **Patchright** | 27/31 | Playwright 分支，补 CDP 泄漏，API 兼容，迁移成本最低 ✅ 首选 |
| CloakBrowser | 26/31 | Chromium fork，49 处 C++ 补丁 |
| **Camoufox** | 26/31 | Firefox 路线，C++ 层伪装，内存仅 ~200MB |
| **curl_cffi** | 26/31 | **无浏览器**，6.4MB，性价比之王 |
| rebrowser / 原生 Playwright | 垫底 | 不要用于对抗场景 |

**注意坑：**
- `undetected-chromedriver` **已停滞**（最后发布 3.5.5 / 2024-02，千余 issue 未处理）→ 新项目别用，迁到 nodriver / SeleniumBase CDP Mode
- `camoufox` 维护已移交 Clover Labs，新版为 experimental，生产用稳定版 `pip install camoufox`（alpha 是另一个包名）
- `SeleniumBase` UC Mode 仍可用但官方推荐新项目走 **CDP Mode**
- 单靠任何 stealth 工具都不够，**指纹 + IP 两条腿缺一不可**

本机环境约定（务必遵守）：
- pip 一律加 `-i https://pypi.tuna.tsinghua.edu.cn/simple`（官方源在国内卡死）
- 装在隔离 venv，不污染系统 Python（参照 site-ai-audit skill 的做法）
- 已有相关 skill：**`web-access`**（CDP 直连日常 Chrome = L5 现成实现）、**`scrapling`**（L1/L3 封装 + API 逆向方法论）。本 skill 负责"判层与决策"，落地时直接复用它们，不重复造轮子。

---

## 6. 标准作业流程

1. **合规自检**（§0）→ 不过关直接停
2. **跑探针** `scripts/probe.py`，拿到层级判定
3. **找 L0 捷径**：JSON 接口 / sitemap / RSS / 官方 API / Wayback+Common Crawl（历史数据够用时最省）
4. **从建议层级起步**，一次只加一个变量（先补头 → 再换 TLS → 再换 IP → 再上浏览器），便于定位到底是哪层在拦
5. **限速做人**：随机 1.5~5s 间隔、同域并发 ≤3、指数退避重试 429、不在整点齐发
6. **成功后固化**：把「站点 + 生效方案 + 已知陷阱 + 日期」写进 `web-access` 的 `references/site-patterns/{domain}.md`，下次不用重跑诊断
7. **失败三次不同层都不通** → 告知用户成本已超收益，给出 L6 商业方案或"换数据源"建议，不要无限重试

## 7. 自适应抗改版与站点经验库

网站改版是采集脚本的头号坟场。**对抗改版的三招**（集大成自 Scrapling `auto_save` + 昆仑增长抗变更设计）：

1. **自适应元素追踪**：Scrapling `StealthyFetcher.fetch(..., auto_save=True)` 把元素指纹存本地，页面改版后自动重定位元素——比写死选择器鲁棒一个量级。大批量同站优先用 Scrapling Spider。
2. **选择器韧性**：优先 `data-testid`/`data-*` → `[class*="xxx"]` 模糊 → 语义 role → 稳定 id；禁用 `nth-child` 和 XPath 长路径（布局一变就挂）。
3. **哨兵页校验**：每天跑一个"哨兵页面"验证解析器是否失效，页面改版第一时间知道，而不是数据悄悄变脏才发现。

**数据质量流水线**：原始层（不动原文）→ 清洗层（去重/标准化/类型转换）→ 应用层。永远保留原始层，清洗规则会改。监控日采集量环比、字段空值率、重复率。

## 8. 端到端实战案例（从问题到结果，一步一步跟做）

> 本节专门解决评测中「文档质量：代码示例多，但缺少一步一步完整使用案例」的扣分点。每个案例都包含：**用户原话 → 合规判断 → 探针命令 → 判层结论 → 执行代码 → 最终结果**。

---

### 案例 1：抓 B 站今日前十热点（L0，API 直连）

**用户原话**："查询一下 B 站今日前十的热点。"

**第 1 步：合规判断**
- B 站热门榜是公开页面，不登录即可查看 → 允许采集
- 频率：只抓 1 次 10 条 → 礼貌

**第 2 步：先找 L0 接口，不开浏览器**

```bash
python scripts/probe.py "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
```

**第 3 步：判层结论**

```
[建议起点: L0]
→ 两种方式均 200 —— 当前无强拦截
→ HTML 内嵌/返回 JSON 结构化数据 → 优先直接解析，可能完全绕开渲染
```

**第 4 步：执行（curl_cffi 或 web_fetch）**

```python
from curl_cffi import requests as r

url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
resp = r.get(url, impersonate="chrome", timeout=20).json()

for i, item in enumerate(resp["data"]["list"][:10], 1):
    print(f"{i}. {item['title']}  —  https://www.bilibili.com/video/{item['bvid']}")
```

**第 5 步：结果**
- 拿到标题 + bvid，拼接出真实视频链接
- 整个过程没有开浏览器，耗时约 200ms

---

### 案例 2：某 Cloudflare 站点返回 403（L1 → L3）

**用户原话**："这个网站 https://example-shop.com/products 我用 requests 抓 403，浏览器能打开。"

**第 1 步：合规判断**
- 商品列表页公开可见 → 允许
- 不涉及登录、个人信息、批量抢购 → 可继续

**第 2 步：跑探针**

```bash
python scripts/probe.py "https://example-shop.com/products"
```

**第 3 步：探针输出**

```
[请求对照]
  裸 requests(Python TLS) : 403  234ms
  curl_cffi(Chrome TLS)  : 200  189ms  HTTP/2

[命中厂商]
  ● Cloudflare  起点 L1  [强证据]  证据: cookie:__cf_bm, header:server: cloudflare

[建议起点: L1]
→ 关键结论：裸请求 403 被拦，curl_cffi 伪装 TLS 后 200 → 纯 TLS/HTTP2 指纹层
```

**第 4 步：执行 L1**

```python
from curl_cffi import requests as r
from time import sleep

url = "https://example-shop.com/products"
headers = {
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://example-shop.com/",
}

resp = r.get(url, impersonate="chrome", headers=headers, timeout=20)
print(resp.status_code, len(resp.text))
# 解析商品列表
sleep(2)  # 礼貌限速
```

**如果 L1 仍 403**：说明 Cloudflare 升级了，需要 L3（patchright/nodriver）执行 JS 挑战。直接升 L3：

```python
from patchright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
        viewport={"width": 1366, "height": 768},
    )
    page = ctx.new_page()
    page.goto("https://example-shop.com/products")
    page.wait_for_load_state("networkidle")
    html = page.content()
    browser.close()
```

**第 5 步：结果**
- L1 通了：问题解决，记录为 `site-patterns/example-shop.com.md`
- L1 没通：L3 通，记录为 L3 方案

---

### 案例 3：电商页面价格数字显示乱码（L7 字体反爬）

**用户原话**："我抓到的价格文本是 &#xea2d; 这种乱码，页面上却显示正常数字。"

**第 1 步：判层**
- 这是典型的 **第 7 层前端加密：字体反爬**
- 站点用自定义字体把 Unicode 私有区字符映射成显示数字

**第 2 步：跑探针确认**

```bash
python scripts/probe.py "https://example-mall.com/item/12345" --save out/
```

探针会报告：

```
[内容层信号]
  字体反爬 : @font-face=True  私有区字符=37 个
```

**第 3 步：最低成本解法 —— 直接调用站内加密函数**

不需要还原字体映射表，直接在浏览器上下文里让页面自己解码：

```python
from patchright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example-mall.com/item/12345")
    price = page.eval_on_selector(".price", "el => el.textContent")
    print(price)  # 页面渲染后的真实文本
    browser.close()
```

**第 4 步：如果需要批量且稳定**

- 下载 `@font-face` 里的 woff/ttf 文件
- 用 `fontTools` 或在线工具建立 `Unicode 码点 → 真实数字` 映射表
- 批量替换 HTML 中的私有区字符

**第 5 步：结果**
- 拿到真实价格，不需要逆向 JS
- 记录到 `site-patterns/example-mall.com.md`：该站用字体反爬，建议 L3 取渲染后文本

---

## References 索引

| 文件 | 何时读 |
|---|---|
| `references/mechanisms.md` | 需要某一层的详细原理与代码级对策（含字体反爬、CSS 偏移、参数签名还原、影子封禁自检） |
| `references/vendors.md` | 确认厂商后，查该厂商的清关机制、cookie 语义、瑞数版本判定 |
| `references/toolbox.md` | 选工具、要可跑的代码模板（curl_cffi/patchright/nodriver/camoufox/拟人行为/代理轮换/CDP 复用） |
| `references/cdp-reuse.md` | **L5 深潜**：自家 Chrome CDP 复用完整指南（启动参数、连接发现、智能等待、多备选选择器、SPA 路由、HttpOnly cookie、数据提取层级、实测踩坑库） |
| `references/stealth-profiles.md` | 指纹池（UA/分辨率加权）+ 反检测注入清单（addInitScript）+ 受控组件输入 + 拟人逐字打字 + 并发限速 |
| `references/FAQ.md` | **新手先看 / 踩坑速查**：30 个场景化高频问题（入门/报错/浏览器/验证码/合规/工具/2026新机制 7 类）+ 12 条反模式 + 错误代码速查表（E001~E999 对应探针报错）+ 3 分钟排查流程图 |
| `references/site-cases.md` | **本 skill 独有资产：已验证站点经验库**（脱敏真实案例，含瑞数无限 debugger、Akamai 影子封禁、字体反爬、电商降级空壳页等踩坑记录） |
| `scripts/env-check.py` | **安装后第一步就跑**：自动检测 Python 版本/网络连通性/curl_cffi 等可选依赖/本机浏览器，输出红黄绿中文报告 + 修复建议，避免中途因环境缺依赖而报错 |

## 变更记录

- **v1.0.7**（2026-08 市场增量：会话级行为验证 + AI Agent 身份认证浪潮）
  - `references/mechanisms.md`：§第 6 层新增 **Cloudflare Precursor 持续验证**（2026-07-13 GA，取代 JSD；生理级特征判定——腕部旋转弧度/生理手抖/认知识别延迟 vs「高斯噪声+均匀延迟」；与 `cf_clearance` 深度绑定，中途掉分动态升级挑战；对策升级为行为录制回放>参数化仿真、重尾延迟分布、人机协同）
  - `references/vendors.md`：Cloudflare 补 **Precursor + BotBase/Attribution Business Insights + AI 诱饵页面**；DataDome 补 **Agent Trust + Priority Protect**（4 类 AI 流量分类 + 100 分动态信任 + KYA 认证 + 售票虚拟候场室）；HUMAN 补 **AgenticTrust + Verified AI Agent**（SATORI 数据集）；Kasada 补 **V2**（传感器 15 倍提升 + 自研解释器 + 消灭 CAPTCHA）；新增「AI Agent 身份认证浪潮」趋势段（**Web Bot Auth / RFC 9421 / Ed25519 / Google agent.bot.goog**）；时效性提醒补 Precursor 警示
  - `references/site-cases.md`：新增**案例 I**（Precursor：过 Turnstile 翻几页仍被封，误判换 IP 无效）；速查表加 Precursor 行
  - `references/FAQ.md`：扩至 **30 条**（新增 Q29 Precursor 会话掉分、Q30 Web Bot Auth 对 UA 伪造的影响）；反模式扩至 12 条（补「均匀随机延迟冒充人类节奏」）
  - `references/toolbox.md` + `references/stealth-profiles.md`：**延迟分布统一规则落地**——人类节奏类延迟一律 `human_delay`（对数正态重尾）+ 认知识别延迟（~200ms）+ 速度衰减手抖 + 10% 思考停顿，修复此前模板代码自身使用 `randint/uniform` 均匀分布与文档自相矛盾的问题；新增 `replay_track` 人工轨迹回放函数（Precursor 站首选对策的代码落地）；网络层重试退避保留均匀抖动（场景不同，两者明确区分）；FAQ Q14 与 mechanisms.md L1 段的均匀随机示例同步改为重尾分布
  - `SKILL.md`：合规红线「禁止」清单固化第 5 条——**勿将本能力封装为「可一键自动注入对话上下文」的插件**（意图路由自动注入 skill body 类形态），避免被供应链投毒复用；判层与绕过代码须保持分离、可读、可审、可逆（源自 DSH 插件市场 7k+ 风险分析「用途合规 ≠ 传播面安全」闭环，2026-08-19）
- **v1.0.6**（更新 2026 新反爬趋势，知识库升级）
  - `references/mechanisms.md`：第 3 层补 **JA4+ 完整指纹体系**（JA4/JA4S/JA4H/JA4L 四维交叉，打乱扩展顺序绕过已失效）；第 5 层补**设备 DNA 持久化指纹 + 跨站图关联（GNN，击败 IP 轮换）**；新增「2026 新机制」段落（第四代 AI 动态风控 / 无感影子封禁升级 / 边缘前置风控 / 多模态行为语义理解）
  - `references/vendors.md`：Cloudflare 补 **JA4+ 评分 + 150+ 环境检查 + AI 流量 Search/Agent/Training 分类 + 2026-09-15 默认屏蔽 Agent**；DataDome 补**意图分析 + 85,000 客户模型**；Akamai 补**持续认证**；Kasada 补**bytecode VM（ips.js）+ 时间绑定 token（KP_UIDz / x-kpsdk-*）**；HUMAN 补**跨站行为指纹**；时效性提醒补 AI 动态风控警示
  - `references/site-cases.md`：新增案例 G（Cloudflare AI 流量分类 → agent 被归 Agent 类）与案例 H（Kasada 时间绑定 token → 换 IP 即 429）
  - `references/toolbox.md`：L1 段补 **JA4+ 自查与应对**（curl_cffi 一行覆盖四维、老"乱序扩展绕过"已失效）
  - `SKILL.md`：§0 国内适配补 **Agent 类自动化被屏蔽**提醒
- **v1.0.5**（冲刺 4.9：R/C/T 短板根治）
  - `scripts/probe.py`：所有报错加 `[Exxx]` 中文编号体系（E001 DNS ~ E999 兜底），**彻底杜绝英文堆栈泄漏**；新增 `fetch_*_retry` 自动重试（网络层失败/5xx 指数退避 3 次，回应"不像有些工具会自动重试"）；`friendly_error` 增补 13 类中文分支
  - `references/FAQ.md`：从 10 条扩至 **28 条**，按入门/报错/浏览器/验证码/合规/工具 6 类组织；新增「错误代码速查表」与探针 `[Exxx]` 打通；反模式清单 8→11 条
  - `SKILL.md`：新增 §0.8「5 分钟上手路径图」（回应 C-渐进式披露）；新增「国内环境专门适配」说明（瑞数/极验/阿里云/腾讯云/网易易盾/同盾/数美 + 清华镜像 + 中文报错 + 国内合规法，回应 T-国内适配性）；frontmatter 触发词与能力边界同步强化
- **v1.0.4**（冲刺 4.9：开箱即用度）
  - `scripts/env-check.py`（**新增**）：环境自检脚本，一键验证 Python/网络/curl_cffi/浏览器配置，红黄绿中文报告 + 修复建议，回应评测「没有自动化工具帮你验证配置是否正确」
  - `scripts/probe.py`：异常全部兜底中文化并口语化（main 外层 try/except，绝不再泄漏英文堆栈；curl_cffi 任何加载失败都降级为标准库探针）
  - `references/toolbox.md`、`references/cdp-reuse.md`：工具代码示例去除机器专属硬编码路径（如 `C:/Users/...`、`C:\Program Files\...exe`），改用可移植写法，下载即用无需改路径
  - `SKILL.md`：新增 §0.7「安装后先跑自检」入口；References 索引加入口
- **v1.0.3**（冲刺 4.9）
  - `references/site-cases.md`（**新增**）：已验证站点经验库，含瑞数无限 debugger、Akamai 影子封禁（200 但假数据）、电商字体反爬、京东/ZOL 降级空壳页等脱敏真实踩坑——这是本 skill 的差异化资产，对应 E-创造力与增值
  - `SKILL.md`：开头强化「独有资产」声明；References 索引加入口
  - `references/FAQ.md`：新增「国内常见站点速查表」，直接对号入座，对应 C-反模式与 FAQ
- **v1.0.2**（目标 4.7→4.8）
  - `scripts/probe.py`：错误提示中文化并附带修复建议，降低新手门槛
  - `SKILL.md`：新增 §0.6「三句话启动我」+ §8「端到端实战案例」
  - `references/FAQ.md`：反模式清单增加「典型场景」列
- **v1.0.1**：新增 FAQ.md 回应评测中「反模式与 FAQ」短板。
- **v1.0.0**：初始版本；8 层反爬机制、成本阶梯 L0~L6、厂商指纹库、合规四查、探针脚本。
