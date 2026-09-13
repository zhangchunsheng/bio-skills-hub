# 八层反爬机制：原理 · 识别 · 对策

按"从网络层到内容层"排列。风控是**叠加+交叉校验**的：任一层不一致就掉分。修的时候一次只改一层，才能定位是谁在拦。

---

## 第 1 层：IP 信誉 / ASN / 频控

**原理**：请求还没进应用层就先查 IP。数据中心 ASN（AWS/GCP/阿里云/DO）段位公开可查，IPQS、Scamalytics 等库有欺诈评分；同一 IP 短时高频、同一 IP 跨多站异常出现，都掉分。

**症状**：突然全 403、429 Too Many Requests、封 1~3 小时后自动恢复、换手机热点立刻能访问。

**对策**：
- **限速比换 IP 重要**。请求间隔随机化（不是固定 sleep(2)，用重尾分布 `random.lognormvariate(math.log(2.5), 0.5)` 秒——行为分析站点会把均匀随机当指纹），同域并发 ≤3，避开整点齐发。
- 429 用指数退避 + 抖动：`sleep(2**attempt * 5 + random.uniform(0,2))`。
- IP 分级与价格（2026 行情）：数据中心（最便宜、最被封）< 住宅 IPRoyal ~$6/GB、Oxylabs ~$10/GB、Bright Data ~$15/GB < 移动 4G/5G $20~40/GB（运营商 NAT 共享，最受信任，封它会伤真实用户）。
- **会话粘滞（sticky session）**：拿到清关 cookie 后必须固定同一出口 IP，否则 cookie 立即失效（见第 4 层）。
- 反例：只换 IP 不修指纹 = 白花钱。干净住宅 IP + Python TLS 指纹依然被拦。

---

## 第 2 层：HTTP 头指纹

**原理**：不只看有没有 UA，还看**头的完整性、值的合理性、以及顺序**。真实 Chrome 的头顺序是固定的；`requests` 按 dict 序发，`axios` 在 Node 里也保证不了顺序。缺 `Accept-Encoding` 会导致服务端返回未压缩数据甚至直接拒绝；`Sec-CH-UA` 系列（客户端提示）缺失而 UA 声称 Chrome 120+ 是明显矛盾。

**易错字段**：
- `Accept` / `Accept-Language` / `Accept-Encoding`（含 `br`）
- `Referer`：从列表页进详情页要带对应 Referer，直连详情页反而可疑
- `Sec-Fetch-Dest/Mode/Site/User`、`Sec-CH-UA*`、`Upgrade-Insecure-Requests`
- 自定义头：`token`、`sign`、`X-Requested-With`（很多站的 XHR 接口必须带）

**对策**：直接用 `curl_cffi impersonate`，它把头序、ALPN、HTTP2 一并伪装，比手动拼头可靠。手写时用 `OrderedDict` 并对齐真实浏览器抓包顺序。

---

## 第 3 层：TLS / JA3 / JA4 + HTTP2 指纹

**原理**：TLS ClientHello 里的密码套件顺序、扩展列表、椭圆曲线、ALPN 组合会形成哈希。JA4 是 JA3 的升级版（截断 SHA-256，可读格式 `a_b_c`，含 ALPN 与 QUIC/HTTP3 支持），**捕获了 JA3 漏掉的库**。Chrome 145/146 是一种形状，`urllib3/OpenSSL` 是另一种。Akamai 还额外对 **HTTP/2 SETTINGS 帧**单独做哈希。

**JA4+ 完整指纹体系（2026 新标配）**：JA4 只是 JA4+ 体系的入口，它由四个相互关联的指纹做**多维交叉验证**：
- **JA4**：客户端 TLS 指纹（ClientHello）
- **JA4S**：服务器 TLS 指纹（ServerHello，用于识别"你伪装成的目标浏览器"是否自洽）
- **JA4H**：HTTP 指纹（header 顺序、`method`、伪头顺序、ALPN 协商结果）
- **JA4L**：网络位置指纹（ASN、IP 地理、数据中心/住宅分类）

**关键变化**：JA4 对列表型字段（扩展、密码套件）做了**排序标准化**——「打乱 ClientHello 扩展顺序」这种 JA3 时代的绕过手段**彻底失效**（打乱顺序 JA4 哈希不变）。截至 2026-04，全球前 1000 站 **65%+** 已部署 JA4+，电商/金融/社交爬虫重灾区部署率 **90%+**；Cloudflare、Akamai、AWS WAF、VirusTotal 均已集成。检测系统会把 JA4 指纹与请求间行为信号、ML 模型交叉——**即使指纹本身合法，行为异常也能被抓**。

**判定**：这是最容易确诊的一层——裸 requests 403 而浏览器正常 → 基本就是它。用 probe.py 的对照实验一测即知。

**对策**：
```python
from curl_cffi import requests
r = requests.get(url, impersonate="chrome")   # 一行同时伪造 TLS(JA3/JA4)+HTTP2+ALPN+头序
print(r.http_version)  # 应为 HTTP/2
```
- 其他实现：`tls-client`（Go 移植）、`curl-impersonate`（底层二进制）、`primp`。
- `impersonate` 目标要跟 UA 版本对齐，UA 写 Chrome 146 而伪装 chrome110 又是新的不一致。
- **无浏览器方案的天花板**：curl_cffi 在 2026 基准里 26/31 通过率，成本却只有浏览器的几十分之一——所以永远先试它。

---

## 第 4 层：JS 挑战与清关 cookie（clearance）

**原理**：服务端返回一个中间页（不是真内容），页面里的 JS 做环境检测/算力题，算完 POST 回去换一个"通行证" cookie。此后带着这个 cookie 才拿真数据。

**关键事实（决定整套架构）**：
- 清关 cookie **绑定 IP + UA**。Cloudflare 的 `cf_clearance` 换 IP 即失效；PerimeterX 的 `_px3` 跨 IP 使用比不带 cookie **罚得更重**（判定为 cookie 窃取）。
- 所以流程必须是：**同一 IP 上用真浏览器过一次挑战 → 导出 cookie → 后续 HTTP 请求复用同一 IP + 同一 UA**。这是"浏览器过关 + HTTP 高速抓取"的混合架构，兼顾成本与成功率。
- cookie 有有效期（分钟~小时级），要做失效重取。

**症状**：`Just a moment...` / `Checking your browser` / 首请求 202、412、503 而重试后正常。

**对策**：L3 起步（patchright / nodriver 执行挑战），拿到 cookie 后降回 L1 复用。

---

## 第 5 层：浏览器 / 设备指纹

**原理**：JS 采集数百项特征做一致性校验：
- 自动化痕迹：`navigator.webdriver`、CDP 泄漏（`Runtime.enable` 等）、chromedriver 注入的 `cdc_` 变量、`window.chrome` 缺失
- 硬件与渲染：Canvas 哈希、WebGL vendor/renderer、AudioContext、字体列表、screen 几何、`deviceMemory`、`hardwareConcurrency`
- 环境一致性：UA 说 Windows 但 WebGL 报 Apple GPU、时区与 IP 地理不符、语言与地区不符 —— **一眼假**
- WebRTC 泄漏真实 IP

**层级差异（重要）**：
- JS 层打补丁（`add_init_script` 改 `navigator.webdriver`）只能改 JS 可见属性，**C++ 层 API 改不到**，指纹检测脚本从底层读就穿。
- 所以要么用引擎层改过的浏览器（camoufox 在 Firefox C++ 层伪装 / CloakBrowser 49 处 Chromium C++ 补丁），要么用真实浏览器。

**对策阶梯**：`patchright`（补 CDP 泄漏，API 兼容 Playwright，迁移最便宜）→ `nodriver`（不带 Playwright 控制面，2026 基准 31/31）→ `camoufox`（Firefox 路线 + BrowserForge 生成自洽指纹）→ 真实浏览器 CDP 接管。

**指纹要"自洽"而非"随机"**：随机拼装的指纹反而稀有度高、更可疑。用 BrowserForge 这类按真实流量分布生成的方案。

**持久化设备指纹（设备 DNA，2026 强化）**：现代风控不再只看单次请求，而是把 50+ 硬件/浏览器特征（Canvas/WebGL 哈希、字体列表、系统 API 调用时序、电池 API、媒体设备、AudioContext、WebRTC、GPU 并发度）聚合成**长期稳定的设备 DNA**。后果：即使换 IP、换 UA，只要设备 DNA 不变，跨会话、跨 IP 仍被关联到同一台机器/VM —— **单纯 IP 轮换已经破防**。

**跨站图关联（coordinated detection）**：HUMAN、Kasada、Cloudflare 等用**图神经网络（GNN）**把「账号 × IP × 设备 ID」的互动做聚类。同一批 bot 用相似顺序访问相同页面、时间同步、设备 DNA 接近 → 被识别为 bot 农场整批封禁。**这直接击败了"多 IP 轮换"这种最朴素的对抗**——对抗要升级为"每个会话独立且自洽的设备 DNA + 独立住宅 IP + 不重复的行为序列"。

---

## 第 6 层：行为分析

**原理**：采集鼠标轨迹、滚动速度曲线、按键微观时序、页面停留、导航路径。真人的轨迹是带抖动的贝塞尔曲线、有过冲和回调；脚本是直线匀速或瞬移。Akamai 的 `sensor_data`、PerimeterX 的 Human Challenge、DataDome 的会话级行为模型都吃这一层。**PerimeterX 的特点是放你进来，等你点关键动作（加购/提交）时才收网。**

**症状**：首页正常、翻到第 N 页被封；点某个按钮后立刻 403；指纹完美但会话级被判定。

**对策**：
- 关键动作前做**会话预热**：先访问首页 → 停留 → 滚动 → 再进目标页，别直冲深链。
- 鼠标用多点贝塞尔插值移动而非 `mouse.move(x,y)` 一步到位；滚动分多次、变速、带回滚。
- 用 `clickAt`（CDP `Input.dispatchMouseEvent`，算真实用户手势）而非 JS `el.click()`。
- 停顿服从随机分布，页面间隔别整齐。
- **GUI 交互 > 构造 URL**：站内点击自然到达的 URL 天然带全上下文参数，手拼 URL 常缺隐式参数而触发风控。

**🆕 Precursor 持续验证（Cloudflare 2026-07-13 GA，第 6 层的分水岭）**：
- 反爬从「入口一次性验证」（Turnstile/验证码）转向**整个会话持续验证**：鼠标轨迹、键盘节奏、剪贴板活动、页面可见性全程被采集评分，与 `cf_clearance` 深度绑定——中途行为掉分会被动态升级挑战，甚至直接收回通行证。**"过一次挑战 = 全场安全"的旧假设失效。**
- 判定逻辑升级到**生理层**：真人轨迹带腕部旋转弧度、生理性手抖频率、目标出现到开始移动的认知识别延迟（~200ms）；而「高斯噪声叠加均匀随机延迟」的参数化仿真恰恰是它重点识破的特征——**老式拟人（均匀随机 + 贝塞尔）在 Precursor 站点反而成了 bot 指纹**。
- 站点可配双模式：Minimize Friction（低摩擦，静默评分）/ Maximize Security（高安全，主动升级挑战）。
- **对策升级**：
  1. **行为录制回放 > 参数化仿真**——用 L5 真实浏览器人工操作录制的轨迹回放，保真度远高于数学合成轨迹。
  2. 延迟分布改用**重尾分布**（如对数正态）而非均匀分布，并模拟认知识别延迟（视线到达目标后 ~200ms 才开始移动）。
  3. 高价值会话别追求纯自动化：**人机协同**（人过关键动作、机做翻页/采集）最稳。
  4. 症状识别：过了 Turnstile 后翻几页才被封 / 被弹回挑战页 → 大概率是 Precursor 会话掉分，别去狂换 IP。

---

## 第 7 层：前端加密（内容层，与访问权限无关）

即使 200 拿到 HTML，数据也可能是假的/不可读的。

### 7.1 字体反爬
自定义 woff/ttf 把字符码位重映射：HTML 里是 `` 私有区字符（U+E000~U+F8FF），浏览器用字体渲染成 `3`。直接取 DOM 文本得到乱码。
**解法**：下载 woff → `fontTools.ttLib.TTFont` 读 `cmap` 与字形轮廓 → 与已知基准字体的轮廓做匹配（坐标哈希或图形相似度）建立"码位→真实字符"映射表 → 批量替换。站点会定期换字体，映射表要能自动重建。
```python
from fontTools.ttLib import TTFont
f = TTFont("target.woff")
cmap = f.getBestCmap()               # {码位: 字形名}
glyf = f["glyf"]                     # 轮廓，用于跟基准字体比对
```

### 7.2 CSS 偏移 / 伪元素 / 负边距
真值藏在 `::before{content:"2"}`、或用 `position/margin` 把干扰字符移出视口、或 DOM 里写 `¥200` 而 CSS 覆盖显示 `¥100`。
**解法**：不要读 `textContent`，要读**计算样式**：`getComputedStyle(el,'::before').content`；或渲染后 OCR 截图；或按 CSS 规则还原字符顺序。

### 7.3 雪碧图（CSS Sprites）
数字合成一张图，用 `background-position` 定位。
**解法**：按偏移量切图 + 建立"偏移→数字"对照表（偏移是固定步长，一次标定长期可用）。

### 7.4 请求参数签名 / 加密响应
参数带 `sign`、`nonce`、`timestamp`、`_signature`；响应体是 Base64 密文（国内常见 **SM4-ECB**，FK 常量 `0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dd` 可用于确认算法）。

**加密类型速判**：
| 特征 | 算法 |
|---|---|
| 定长 32/16 hex | MD5（js 里搜到 `0x67452301,0xefcdab89,0x98badcfe,0x10325476` 即确认） |
| 定长 64 / 128 hex | SHA-256 / SHA-512 |
| 长度随明文变、同明文密文不同 | AES-CBC/CTR（有随机 IV） |
| 长度恒等于密钥长度、与明文无关 | RSA |
| `A-Za-z0-9+/` 且以 `=` 结尾、`btoa` | Base64（编码非加密） |

**破解顺序（成本从低到高）**：
1. **直接调它自己的函数**（最优）：浏览器上下文里 `page.evaluate("window.sign('...')")`；函数没暴露就先 hook 到 `window`。数分钟搞定。
2. **JSRPC**：在浏览器里开 WebSocket 服务把加密函数暴露给本地脚本调用，兼顾速度与正确性。
3. **补环境**：把 js 扣下来在 Node 里跑，补 `window/document/navigator` 等缺失环境。工作量大但可脱离浏览器、可高并发。
4. **算法逆向**：完全还原成 Python。最贵，仅在需要极致性能时做。

**混淆识别**：
- obfuscator.io：`_0x` 开头变量名、大字符串数组 + `push/shift` 移位、控制流平坦化 → v_jstools / AST 解混淆
- JSFuck：只有 `[]()!+` → 控制台直接跑或 hook `eval`
- aa/jj 混淆：`Function`/`eval` 自执行 → hook `Function` 从 arguments 取源码
- Webpack：自执行函数 + 模块大数组 + 加载器（含 `exports`）→ 扣加载器 + 按需补模块，把核心函数提到 `window`
- **jsvmp / VMP**（瑞数、腾讯天御、字节系）：自定义字节码 + 虚拟机解释执行，还会 hook `XMLHttpRequest.prototype.open` 自动追加动态参数 → **别硬逆，走 JSRPC 或真浏览器**
- WebAssembly：核心算法编成 `.wasm` → 逆向门槛极高，同上

**反调试**：无限 `debugger`（用 DevTools "Never pause here" 或 hook `Function`/`eval` 过滤）、`console.log` 检测、窗口尺寸检测、`toString` 检测函数是否被改写。

---

## 第 8 层：验证码

**2026 现实（重要认知）**：打码平台对老式 reCAPTCHA v2 还有 ~95% 成功率，但对 Turnstile ~30%、DataDome ~10%。**趋势不是"解题"，而是"提高信任分让它根本不出现"。**

| 方案 | reCAPTCHA v2 | v3 | Turnstile | DataDome | 成本 | 维护 |
|---|---|---|---|---|---|---|
| 打码平台 | ✅ ~95% | ⚠️ ~60% | ❌ ~30% | ❌ ~10% | $1~3/千 | 低 |
| stealth 插件 | ⚠️ 不稳 | ⚠️ | ❌ 多被拦 | ❌ | 免费 | 极高 |
| 仅住宅代理 | ⚠️ 边缘 | ⚠️ | ❌ | ❌ | $6~20/GB | 低 |
| 会话复用（手动登录导出 cookie） | ✅ | ✅ | ✅ | ✅ | 免费 | 中（会过期） |
| **真实浏览器接管** | ✅ 极少触发 | ✅ | ✅ | ✅ | 本地免费 | 极低 |

国内验证码：极验三代滑块要模拟**先加速后减速**的人类拖动曲线并处理 `gt`/`challenge` 参数；顶象用 WebAssembly 做无感验证；文字点选/语序点选类需要模型识别。

**红线**：不得用于突破登录、支付、实名等身份核验环节。

---

## 2026 新机制：第四代 AI 动态风控 + 边缘前置

传统反爬是"固定规则 + 固定绕过"，绕过方案有效期以月计。2026 年已进入第四代：

**① 大模型自适应动态风控**
- 风控方用大模型**实时分析访问行为，自动生成全新拦截规则**，无需人工配置策略。
- 直接后果：辛辛苦苦配好的绕过方案，有效期从"数月"骤降到"数天"——这是 2026 年"脚本周一周三挂"现象加剧的根本原因。
- 应对哲学：不要追求"一劳永逸的绕过"，而要建"探针重判 → 自动适配 → 成功率监控告警"的运维闭环（见 §7 标准作业 / vendors.md 时效性提醒）。

**② 无感行为风控（影子封禁升级版）**
- 不弹验证码，只在后端**缓慢返回空数据 / 乱码 / 假列表**，爬虫难以察觉被风控，排查成本极高。
- 这是「附：影子封禁」的强化：Akamai `_abck` 校验不过就给假数据，现在更普遍。

**③ 边缘节点前置风控（CDN 边缘下沉）**
- 风控逻辑下沉到云厂商边缘 CDN 节点，异常请求在**接入网关直接拦截**，恶意流量连业务接口地址都拿不到。
- 后果：传统"先拿到 HTML 再分析"的前提被打破——连接口前就被边缘挡了，连挑战页都见不到。
- 应对：L1/L3 的 TLS/HTTP2 伪装必须到位（否则在边缘就死），且住宅/移动 IP 的"地域 + 语言 + 时区 + 受众"四重一致性比以往更重要。

**④ 多模态行为语义理解（第四代核心）**
- 亚马逊等已落地：把用户在站上的全部行为（搜索路径、停留时长、滚动模式、购物车操作、历史订单）作为**整体语义序列**，用 Transformer 编码做"真实用户 vs 机器"的语义级区分。
- 含义：单点行为伪装（如只模拟鼠标抖动）已经不够，要模拟"合理的人类任务流"（先搜索 → 浏览 → 停留 → 加购 → 结算），且整段序列自洽。

---

## 附：影子封禁（silent ban）—— 最坑的一种
状态码 200、页面结构正常，但**数据是假的或残缺的**（价格全一样、列表只有前几条、字段被打乱）。Akamai `_abck` 校验不过时就是这种表现。
**自检方法**：拿浏览器人工看到的真实值做基准，对抓取结果抽样比对；监控字段的分布突变（比如价格方差骤降为 0）。CI 里挂一个"金标准样本"回归测试，比等用户发现数据错了要好。
