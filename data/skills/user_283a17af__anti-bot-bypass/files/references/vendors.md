# 风控厂商指纹库与对策（2026）

先认清对手，再决定砸多少成本。**同一站点可能叠加多层**（例：某海关平台 = 瑞数6代 VMP + 滑块 + SM4 响应加密 + 图片混淆字段 + IP 频控，共 5 层）。

---

## 国外四大

### Cloudflare（覆盖全网 20%+ 站点）
- **识别**：`cf_clearance` / `__cf_bm` / `cf-ray` 响应头 / `server: cloudflare` / `Just a moment...` / `challenges.cloudflare.com`
- **权重**：**JA4+ 指纹**（JA4/JA4S/JA4H/JA4L 四维交叉）> IP 信誉 > JS 挑战响应；2026 挑战页面**跑 150+ 浏览器环境检查**（WebGL renderer、canvas hash、AudioContext、navigator 属性一致性）；**按客户训练独立 ML 模型** —— 同一套指纹在 A 站通、B 站不通是正常现象
- **清关**：过挑战后发 `cf_clearance`，**绑定 IP + UA**，换任一即失效；`__cf_bm` 是短时 bot 管理 cookie（~30min）
- **档位差异大**：低敏感档 curl_cffi 一行就过（这也是它"最容易"的原因）；开了 Turnstile / 高敏感托管挑战才需要 L3
- **起点**：L1 → 不通再 L3（nodriver 在 2026 基准里对 Turnstile 站点表现最好）
- **⚠️ 2026 AI 流量分类（重大变化）**：Cloudflare 把自动化流量按**行为**分成三类，可独立管控：
  - **Search**（索引类爬虫，预期带来引荐流量）
  - **Agent**（实时替人干活的自动化，含 **browser-use agent——即 Claude/Gemini 驱动 Chrome 这类**）
  - **Training**（抓内容训练/微调模型）
  - **默认规则（2026-09-15 起对新域名生效）**：广告页默认屏蔽 **Training + Agent**，Search 默认放行；多用途爬虫（如 Googlebot 同时做 Search+Training）封锁任一功能即整体受限。
  - **对 agent 抓取的影响**：browser-use / 浏览器驱动类 agent 被归为 Agent 类，**在广告页（含大量电商/媒体页）默认被屏蔽**；Cloudflare 同时推 `content-use` robots.txt 信号 + Pay Per Crawl（HTTP 402 付费抓取）—— 合法抓取路径正从"绕过指纹"转向"拿到显式、诚实的访问许可"。
- **🆕 Precursor 持续行为验证（2026-07-13 GA）**：Turnstile 的补充引擎，**取代 JavaScript Detections（JSD）**。会话级持续验证：全程采集鼠标轨迹/键盘节奏/剪贴板活动/页面可见性，用**生理级特征**（腕部旋转弧度、生理手抖频率、认知识别延迟）区分真人 vs「高斯噪声 + 均匀延迟」仿真；与 `cf_clearance` 深度绑定，中途掉分动态升级挑战。站点双模式：Minimize Friction / Maximize Security。**含义：过 Turnstile 只是入场券，整段会话行为不达标照样出局**（判定与对策见 mechanisms.md §第 6 层）。
- **🆕 BotBase + Attribution Business Insights（2026-07-01）**：全网追踪 bot 的可搜索目录 + 爬取/引荐流量比例看板（产业观测面）。另有新一代 **AI 诱饵页面（honey pot）**：把可疑流量引流到仿真页浪费时间——表现为"抓取一直 200 但数据永远不对"，注意与影子封禁区分。

### Akamai Bot Manager
- **识别**：`_abck` / `bm_sz` / `ak_bmsc` / `bm_sv` cookie
- **权重**：`sensor_data`（JS 采集后 POST 的行为遥测）+ 深度指纹一致性 + JA4 + **HTTP/2 SETTINGS 帧单独哈希** + 跨站信誉关联（在别的 Akamai 站被标记过，进你这站前分就低）
- **🆕 持续认证（continuous authentication）**：单次初始检查不够，**整个会话持续重新评估行为**——中途行为异常会动态升级挑战；设备签名（HTTP/2 settings + header order）跨会话持久
- **致命点**：`_abck` 校验不通过时**不报错，返回假数据（影子封禁）**。必须做数据真实性回归校验
- **起点**：L4。需要真实鼠标/滚动行为 + 非常干净的住宅 IP + **长会话粘滞**（别频繁换 IP）

### DataDome
- **识别**：`datadome` cookie / 403 + DataDome 验证页 / `geo.captcha-delivery.com`
- **权重**：边缘实时评分（<2ms），最吃**浏览器指纹与 headless 检测**，其次会话级行为一致性；对数据中心 IP 极为敏感
- **特点**：惩罚"同一指纹高频复现" —— 指纹要跨会话变化，但每个会话内必须自洽
- **🆕 意图分析（intent analysis，2025 新增）**：不只判断"是不是自动化"，还评估"**访问目的是什么**"——直接抓取 vs 正常浏览的意图画像差异；并对 **LLM/AI 爬虫单独分类**管理
- **🆕 85,000+ 客户 ML 模型**：每个站点一个独立训练的模型，每天处理 **5 万亿+ 信号**，响应 <2ms —— **每个受保护站点都是独立任务，A 站生效的组合不能直接搬到 B 站**
- **🆕 Agent Trust + Priority Protect（2026-05）**：把 AI 流量细分 **4 类**（AI Crawler / AI Assistant / Agentic Browser / Autonomous Agent）分别管控，配动态 100 分信任评分；推 **KYA（Know Your Agent）认证**——agent 出示可验证身份换更高配额；Priority Protect 为限量发布/售票场景设"**虚拟候场室**"，把可疑 agent 挡在真实库存之外（票务/抢购场景的 agent 对抗进一步升级）
- **起点**：L4，硬化 Chromium/camoufox + 住宅或移动 IP + 5~10s 级慢速

### PerimeterX / HUMAN
- **识别**：`_px3` / `_pxhd` / `_pxvid` / `pxcts` / "Access to this page has been denied"
- **权重**：行为生物特征（鼠标轨迹、滚动速度、按键微时序）+ 跨导航的 cookie 状态连续性
- **🆕 跨站行为指纹（cross-site behavioral fingerprinting）**：在多个客户站点间追踪**行为一致性**——同一套工具/同一运营者在不同站点的行为模式会被关联，识别 bot 运营者
- **🆕 AgenticTrust + Verified AI Agent（2026）**：会话级 agent 治理 + 开源加密身份验证框架（Verified AI Agent），基于 SATORI 威胁情报数据集识别 agent 真实身份——方向与 Web Bot Auth 一致：**让 agent「持证上岗」，匿名 agent 越来越难混**
- **特点**：**放你进门，等关键动作（加购、提交、注册）时才收网**；clearance **强 IP 绑定，跨 IP 使用比不带 cookie 罚得更狠**
- **起点**：L4。持久化 browser context + 目标页前完整会话预热

### Kasada（最难之一）
- **识别**：`x-kpsdk-ct` / `x-kpsdk-cd` / `x-kpsdk-dv` 等 `x-kpsdk-*` 头、`ips.js` sensor
- **🆕 自研 bytecode VM（ips.js，~449KB）**：不是普通混淆脚本，而是带**自定义指令集 + 时间种子 + 完整性校验**的 VM，每次请求变化的字节码；用 MITM 中途 patch 脚本会让 VM **自检失败、自终止**并产出无效 token
- **🆕 时间绑定 token（KP_UIDz / x-kpsdk-* 家族）**：
  - 过挑战后发 `KP_UIDz` cookie（会话凭证），后续请求必须带 `x-kpsdk-ct`（challenge token）
  - token **时间绑定**：T=0 生成的 payload 在 T=60s 提交即被拒（防重放）；**IP 变更会破坏 IP 绑定的 token 验证**
  - 429 + `x-kpsdk-ct` 错误指示 = token 校验失败（过期/重放/换 IP/指纹漂移）
- **对策**：需完整浏览器执行 sensor（headless 极难），且要**锁定同一 IP 直到 token 生命周期结束** → L5 真实浏览器或 L6 商业 API
- **🆕 V2 平台（2026）**：客户端侦测传感器灵敏度 **15 倍提升**；混淆升级为**自研自定义解释器**；增强加密挑战的目标是**消灭 CAPTCHA**（无感判定直接放行/拦截）；对 headless 浏览器自动化的实时防御增强——**V1 时代的过挑战经验不能直接套用**，遇到 V2 站点预期成功率下降，预留 L6 预算

### 🆕 趋势：AI Agent 身份认证浪潮（2026 下半年）
- **Web Bot Auth（RFC 9421 + Ed25519 签名）**：IETF 工作组 2026 年初成立，标准定稿目标 2026-08；Cloudflare / Amazon / Akamai / OpenAI / Google 均在支持，Google 已测试 `agent.bot.goog` 域名验证。agent 用**密钥对自证身份**，站点验签后决定放行与配额。
- **含义**：合法自动化的通行路径正从「伪装成人类」转向「**诚实出示 agent 身份 + 拿授权**」——UA 伪造与 IP 白名单这类"匿名混入"策略在带头厂商处将逐步失效。自用低频抓取影响尚小（暂不强制），但做产品化 agent 要提前布局签名身份。
- 与 Cloudflare AI 三分类、DataDome KYA、HUMAN Verified AI Agent 是同一浪潮：**匿名 bot 的察觉成本趋零，持证 agent 才有配额**。

### 其他
- **Imperva/Incapsula**：`incap_ses_*` / `visid_incap_*` / `nlbi_*` / `x-iinfo` 头 / `_Incapsula_Resource` → L3
- **AWS WAF**：`aws-waf-token`、challenge.js → L2~L3
- **reCAPTCHA v3**：无感打分，不出题只降权 → 提分（真实浏览器 + 真实历史）比"解题"有效

---

## 国内厂商

### 瑞数 Ruishu（政务、司法、海关、专利、招投标高发）
**识别三连**（命中即确认）：
1. 首请求 target_url 返回 **202 或 412**（不是真内容）
2. 请求一个外链 js（同页面内容固定，可本地缓存）
3. 再次请求 target_url 才拿到数据

其他特征：
- cookie key 后缀为 **O/P** 或 **S/T**（`O`、`S` 结尾的来自首次响应），如 `FSSBBIl1UgzbN7N80T`
- 首响应 HTML 里有超长动态 `<meta content="...">`，后续 JS 解码它生成 window 属性
- 无限 `debugger` 反调试；`$_ts` 全局对象

**版本判定表**：
| 版本 | 首请求状态 | cookie 值前缀（T 结尾的） | 其他 |
|---|---|---|---|
| 3 代 | 202 | `3` | S/T 前带端口号 80/443 |
| 4 代 | 202 | `4` | S/T 前带端口号 |
| 5 代 | 412 | `5` | — |
| 6 代 | 412 | `6` | — |
| **vmp 版**（2022-04 后，改动很小） | 412 | `0` 或字母（**无数字**） | 有 `$_ts.nsd`；js 里能搜到 `<= 63` |

**解法（成本从低到高）**：
1. **自动化浏览器**（Selenium/patchright/CDP）直接让它自己跑完 —— 量小首选，最省人力
2. **JSRPC** —— 浏览器里暴露加密函数给本地脚本调，兼顾正确性与速度
3. **补环境** —— 扣核心 js 在 Node 补 window/document 执行，可脱离浏览器高并发（工程量大，推荐用于生产）
4. **算法逆向** —— vmp 字节码级还原，数天到数周，仅在极致性能需求下做

⚠️ 瑞数常与其他层叠加：滑块（`errorCode=501` 触发）、**SM4-ECB 响应加密**、关键字段用 Base64 PNG 图片下发（需 OCR，本机有 `tencentcloud-ocr` skill）、IP 频控封 1~3 小时。

### 腾讯天御（原防水墙）
- **识别**：`tdc.js` 文件、`collect` 加密参数、`t.captcha.qq.com`
- **难点**：jsvmp + 动态 js + 并发 IP 要求 + AIGC 图库 → **别硬逆，L5 真实浏览器最划算**

### 极验 Geetest
- **识别**：`geetest` 域名/标识、`gt` 与 `challenge` 参数、`static.geetest.com`
- **难点**：三代滑块要求人类拖动曲线（**先加速后减速**，带微抖动与过冲）
- **对策**：轨迹生成 + 缺口识别（CV 模板匹配或模型）；四代无感版优先靠提分避免触发

### 顶象 DingXiang
- **识别**：验证码带顶象标识、`ac` 加密参数、`dx.js`、`cap.dingxiang-inc.com`
- **难点**：动态 js + WebAssembly 无感验证 + 多种验证码类型（文字点选等）

### 同盾 TongDun
- **识别**：`fm.js`、`blackbox` 参数、`static.tongdun.net`；滑块版 `tdCaptcha.js` + `p1/p2/p3` 参数
- **难点**：动态 js、无感风控

### 数美 ShuMei
- **识别**：`fverify` 请求、`organization` 加密字段
- **难度**：相对低

### 网易易盾
- **识别**：`dun.163.com` / `cstaticdun.126.net`、`data`/`fp`/`cb` 参数
- **难点**：参数杂、并发环境要求

### 阿里云 WAF / 淘系
- **识别**：`acw_sc__v2`（有公开的 js 还原方案）、`acw_tc`、`nc_token`、滑块 `nc` 组件
- 淘系另有 `x5sec`、`_m_h5_tk`（token 与时间戳签名，`_m_h5_tk` 前半段参与 sign 计算）

### 其他
- **vaptcha**：`vaptcha-sdk.js`，手势识别
- **友验 Yotest**：`yotest.js`，jsvmp
- **ciyverify**：`cyverification.js`，jsvmp 多堆栈协程（很难）
- **百度云加速**：`yunsuo_session`

---

## 判定流程（30 秒确认对手）

```
1. 看 Set-Cookie 名字        → 命中上表任一即确定厂商
2. 看状态码 202/412          → 瑞数
3. 看响应头 cf-ray/x-datadome/x-kpsdk/x-iinfo → 对应厂商
4. 看 HTML 里加载的 js 文件名 → tdc.js / fm.js / dx.js / gt.js / ips.js
5. 都没有                    → 自研规则（通常弱，L1 + 限速即可）
```

或直接 `python scripts/probe.py <url>` 一把出结论。

---

## 时效性提醒

厂商侧持续迭代，**开源 stealth 方案落后风控通常数周**。一条流水线"上周还好，今天全挂"是常态，不是你的代码坏了。2026 进入第四代 **AI 动态风控**后，固定绕过方案有效期进一步从"数月"缩短到"数天"——大模型会实时生成新规则，今天写死的对策下周可能就失效。2026-07 起 **Cloudflare Precursor** 又把行为验证从入口延伸到整个会话，"过一次挑战吃遍全场"的旧经验加速失效。
- 先跑探针重新判层，再改方案，别盲目改代码
- 生产链路要有"成功率监控 + 数据真实性回归"，掉了立刻告警
- 把每个站点的**生效方案 + 失效日期**记进 `web-access/references/site-patterns/{domain}.md`，形成经验资产
