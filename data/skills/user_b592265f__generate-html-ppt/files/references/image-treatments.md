# 图片处理范式（Image Treatments）

给 PPT 里的图片挑处理方式时,不要再默认套 `frame-img` + `figcaption` 的"卡片+图注"组合。本文件给出 **8 套语义清晰的范式（T1–T8）**,每套对应一种视觉气质和适用场景。生成时根据图片角色挑一套,而不是随手加圆角和阴影。

> **TL;DR**：默认走 T2（Float / 自由留白）。需要分组用 T6,需要设备感用 T4/T5,主视觉用 T1,数据大字报背景用 T7,只有 Beautiful Modern 的"卡片化"产品图才允许 T8。

---

## 为什么不再用"框架 + 图注"统一处理

---

旧范式把所有图片都塞进 `.frame-img`（圆角 + 阴影 + 边框）+ `figcaption`（"产品截图"/"原始截图"），导致：

1. **每张图都长得像缩略图**——和 Vercel/Linear/Stripe/Anthropic 等现代产品页完全脱节
2. **LLM 在缺语义时降级到"原始截图"**——读者一眼觉得是占位符
3. **大图被压缩到 562px 高度**——丢失冲击力
4. **多图混排时圆角阴影互相打架**——视觉噪音

新规则：**图自己会说话，框架和标签是噪音**。

---

## 8 套范式速查表

| ID | 范式 | 视觉描述 | 适用场景 | 默认类组合 | 标签 |
|---|---|---|---|---|---|
| **T1** | **Bleed** 全屏出血 | 图延伸到 slide 边缘,无框无标签 | 封面、章节幕封、转场、大主视觉 | `.t-bleed` | 无 |
| **T2** | **Float** 自由留白 | 图悬浮在 page 背景上,纯靠 padding 留白 | 照片、纪实、人物、产品摄影、混合图文 | `.t-float` (+ `.r-16x10` 等比例) | 仅当有"图说"价值时给极小斜体灰字 |
| **T3** | **Inset** 浅色基底 | 图嵌在比 page 略深/略浅的色块里,无边框无阴影,靠色阶分层 | UI 截图、dashboard、代码截图、证据图 | `.t-inset` | 无 |
| **T4** | **Browser Chrome** 简化浏览器框 | 现代风格浏览器 chrome(顶栏+三个点+地址栏),内部是真实截图 | Web 应用、网页、dashboard | `.t-browser` | 无 |
| **T5** | **Device Frame** 设备外框 | MacBook/iPhone 极简设备外框(扁平、不写实、不反光) | App、桌面应用、移动端 | `.t-device` | 无 |
| **T6** | **Quiet Frame** 极轻发丝线 | 多张图分组时,0.5px 同色系细线,无圆角无阴影 | 多图网格、证据墙、对比组 | `.t-quiet` | 组标题在外层,单图不加 |
| **T7** | **Backdrop** 背景虚化 | 图降到 30-40% 透明度/模糊作为 slide 背景,前景是文字和数据 | 大字报、Hero 数据页、章节过渡 | `.t-backdrop` | 无 |
| **T8** | **Edge Card** 极小圆角卡 | 6px 圆角 + 极轻阴影,**仅限** Beautiful Modern 营销首图 | APP Store 风产品卡、营销首图 | `.t-edge-card` | 可选 1 行小灰字 |

> 上面所有范式都默认 `border-radius: 0`,`box-shadow: none`。T8 是唯一允许圆角+阴影的范式,且必须显式标 `.t-edge-card` 才生效。
> 上面所有范式都默认 `border-radius: 0`,`box-shadow: none`。T8 是唯一允许圆角+阴影的范式,且必须显式标 `.t-edge-card` 才生效。

---

## 场景 → 范式映射

| 图片角色 | 首选范式 | 备选 | 理由 |
|---|---|---|---|
| 封面主图 | T1 Bleed | T7 Backdrop | 满屏有冲击力,标题压在 quiet zone |
| 章节幕封背景 | T7 Backdrop | T1 Bleed | 模糊背景 + 大字标题最稳 |
| 纪实照片、人物 | T2 Float | T1 Bleed | Float 留白,不要被卡片框 |
| 产品摄影(相机、家具等) | T2 Float | T8 Edge Card | 营销首图可用 T8 |
| UI 截图(网页、App) | T3 Inset | T4 Browser | Inset 是默认,需要"是个网页"语境时用 T4 |
| Dashboard / 数据面板截图 | T3 Inset | T4 Browser | 同样默认 Inset |
| App Store / 产品详情页 | T8 Edge Card | T5 Device | Beautiful Modern 风格才用 T8 |
| 移动端 App 截图 | T5 Device | T3 Inset | 设备感强时用 T5,否则 Inset |
| 桌面端工作流截图 | T4 Browser | T3 Inset | "在浏览器里"语境用 T4 |
| 代码截图 | T3 Inset | — | 一定要 Inset + 暗底主题 |
| 证据墙 / 多平台截图组 | T6 Quiet Frame | — | 统一气质,不加单图标签 |
| 对比组(改版前后) | T6 Quiet Frame | — | 视觉等价,只靠位置/标题区分 |
| 数据大字报配图 | T7 Backdrop | T1 Bleed | 图做背景,前景大数字 |
| 配文小插图(icon-like) | T2 Float | — | 小图,Float 自然 |
| 信息图(已按槽位生成) | T1 Bleed | T2 Float | 已经做好就 Bleed,不要被框 |
| 草图/线框图/低保真 | T2 Float | T3 Inset | 草图要"还在画"的感觉,不要营销卡 |

---

## 8 套范式详细规范

### T1 · Bleed（全屏出血）

```html
<figure class="t-bleed" data-treatment="t-bleed">
  <img src="images/cover-hero.jpg" alt="主视觉">
</figure>
```

CSS 要点:
- `width: 100%; height: 100%; object-fit: cover;`
- 图延伸到 `.slide` 四个边缘,不进入 padding
- 标题压在图上时,先判断 quiet zone(约 30% 低细节区域);不够 quiet 就改用 T2

### T2 · Float（自由留白）

```html
<figure class="t-float r-16x10" data-treatment="t-float">
  <img src="images/photo.jpg" alt="纪实照片">
  <figcaption class="t-cap">上海徐汇 · 工作日的咖啡馆</figcaption>
</figure>
```

CSS 要点:
- 单纯 `padding` 留白,无边框无阴影无圆角
- 比例类(`.r-16x10` / `.r-4x3` / `.r-3x2`)决定画布尺寸
- `figcaption.t-cap` 仅当图说能补充新信息时使用,极小斜体灰字,**不写"产品截图"等空标签**

### T3 · Inset（浅色基底）

```html
<figure class="t-inset r-16x10" data-treatment="t-inset">
  <img src="images/dashboard.png" alt="数据面板截图">
</figure>
```

CSS 要点:
- 背景色 = page 背景同色系但略深(暗主题下)或略浅(亮主题下)5-8%
- `padding: 24-40px`,让图"嵌"在色块里
- 完全无边框、无圆角、无阴影
- 适合所有 UI/截图/dashboard/代码截图

### T4 · Browser Chrome（简化浏览器框）

```html
<figure class="t-browser r-16x10" data-treatment="t-browser">
  <div class="t-browser-bar">
    <span class="t-dot"></span><span class="t-dot"></span><span class="t-dot"></span>
    <span class="t-url">app.example.com/dashboard</span>
  </div>
  <img src="images/web-screenshot.png" alt="Web 应用截图">
</figure>
```

CSS 要点:
- 顶栏高度 ≈ 32-40px,3 个圆点(红/黄/绿 或 同色系灰点)
- 地址栏:极小字、灰、靠左
- 主体 = 真实截图,无圆角,无 border
- 比 Mac 风格窗口现代得多;**不要做高光、阴影、木纹底座等写实细节**

### T5 · Device Frame（设备外框）

```html
<figure class="t-device" data-treatment="t-device">
  <div class="t-device-shell t-device-mac">
    <div class="t-device-screen">
      <img src="images/mac-app.png" alt="桌面应用截图">
    </div>
  </div>
</figure>
```

CSS 要点:
- 扁平、不写实、无反光、无木纹
- 笔记本/手机都是单一色块轮廓 + 屏幕区
- 屏幕区填入截图,4px 圆角(设备本身可以有,截图无)
- 不要做"老 Mac OS X 拟物风"

### T6 · Quiet Frame（极轻发丝线）

```html
<section class="slide light">
  <div class="chrome"><div>Proof</div><div>页码</div></div>
  <div class="frame vstack">
    <div>
      <div class="kicker">Proof · 平台粉丝实证</div>
      <div class="h-xl">6 个平台 · 一组气质</div>
    </div>
    <div class="t-quiet-grid" data-treatment="t-quiet">
      <figure class="t-quiet r-16x10"><img src="images/weibo.png" alt="微博 289K"></figure>
      <figure class="t-quiet r-16x10"><img src="images/twitter.png" alt="推特 137K"></figure>
      <figure class="t-quiet r-16x10"><img src="images/wechat.png" alt="公众号 96K"></figure>
      <figure class="t-quiet r-16x10"><img src="images/jike.png" alt="即刻 26K"></figure>
      <figure class="t-quiet r-16x10"><img src="images/xhs.png" alt="小红书 19K"></figure>
      <figure class="t-quiet r-16x10"><img src="images/douyin.png" alt="抖音 10K"></figure>
    </div>
  </div>
  <div class="foot">
    <div>截图时间 · 2026.04</div>
    <div>页码</div>
  </div>
</section>
```

CSS 要点:
- 容器 `display: grid; grid-template-columns: repeat(N, 1fr); gap: 12-20px;`
- 单图:无圆角、无阴影,**0.5px 同色系细线** 包围(仅在亮主题需要分组时)
- **单图不加 figcaption**,组标题在 slide 顶部 `.h-xl` 或 `.kicker`
- 所有图必须用同一比例类,同一组内禁止混用 `h-22` / `h-26`

### T7 · Backdrop（背景虚化）

```html
<div class="slide dark">
  <div class="t-backdrop" data-treatment="t-backdrop">
    <img src="images/hero-photo.jpg" alt="">
  </div>
  <div class="frame center">
    <div class="kicker">Impact</div>
    <div class="h-hero">287<span class="unit">M</span></div>
    <div class="lead">全球用户已迁移至新平台</div>
  </div>
</div>
```

CSS 要点:
- `.t-backdrop` 绝对定位铺满 slide,`opacity: 0.3-0.4` 或 `filter: blur(12-20px)`
- 前景文字不进入图片区域或用半透明遮罩
- 暗主题下表现最佳,亮主题慎用

### T8 · Edge Card（极小圆角卡）

```html
<figure class="t-edge-card" data-treatment="t-edge-card">
  <img src="images/app-promo.png" alt="产品首图">
</figure>
```

CSS 要点:
- **唯一允许** `border-radius: 6px` + `box-shadow: 0 1px 3px rgba(0,0,0,0.08)` 的范式
- **仅限** Beautiful Modern 风格的"营销首图 / APP Store 风格卡片"场景
- 不允许在 Swiss 主题下使用(Swiss 主题的全局规则禁止圆角和阴影)
- 不允许在证据截图、UI 截图上使用(那些场景走 T3 / T4)

---

## 禁用项黑名单(全范式通用)

生成或评审时,如果命中以下任意一条,**必须删/改**:

- ❌ `<figcaption>原始截图</figcaption>` / `<figcaption>产品截图</figcaption>`
- ❌ `<figcaption>Screenshot</figcaption>` / `<figcaption>Untitled</figcaption>` / `<figcaption>Sample</figcaption>`
- ❌ 默认 `.frame-img` 自带 `border-radius: 12px+` + `box-shadow: 中-重`
- ❌ 给每张图都加 figcaption(无信息量的图注就是噪音)
- ❌ hover 时图片 `transform: scale(1.02)`(老 Beautiful 模板的旧行为)
- ❌ `object-fit: cover` 裁掉 UI 截图的左侧/右侧(关键按钮和文字通常在两侧)
- ❌ 在 T3/T4/T5/T6 上叠加 box-shadow(只有 T8 允许)
- ❌ 多图混排时用不同比例类(同一组必须同一比例)
- ❌ 截图外侧背景比截图本身更抢眼(背景是托底,不是主视觉)

---

## CSS 范式基座(可直接复制到 template 的 style 块)

```css
/* ============================================================
   IMAGE TREATMENTS (T1-T8) — 默认无圆角无阴影
   旧 .frame-img 仍可用,但默认边框/阴影/圆角都重置为 0;
   卡片感需要时显式加 .t-edge-card (T8) 才能拿回圆角阴影
   ============================================================ */

/* 基础容器:重置 frame-img 的默认卡片感 */
.frame-img,
figure[class^="t-"] {
  display: block;
  position: relative;
  border-radius: 0;          /* 默认无圆角 */
  box-shadow: none;          /* 默认无阴影 */
  border: 0;
  background: transparent;
  overflow: visible;
}
.frame-img img,
figure[class^="t-"] img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.frame-img.fit-contain img,
.t-inset.fit-contain img,
.t-float.fit-contain img { object-fit: contain; background: var(--b-bg, #fff); }

/* 比例类(全局通用) */
.r-21x9  { aspect-ratio: 21 / 9; }
.r-16x9  { aspect-ratio: 16 / 9; }
.r-16x10 { aspect-ratio: 16 / 10; }
.r-4x3   { aspect-ratio: 4 / 3; }
.r-3x2   { aspect-ratio: 3 / 2; }
.r-1x1   { aspect-ratio: 1 / 1; }
.r-3x4   { aspect-ratio: 3 / 4; }
.h-16    { height: 16vh; }
.h-18    { height: 18vh; }
.h-22    { height: 22vh; }
.h-26    { height: 26vh; }

/* T1 · Bleed */
.t-bleed {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.t-bleed img { object-fit: cover; }

/* T2 · Float —— 纯留白 */
.t-float {
  margin: 0;
  padding: 0;
}
.t-float img { object-fit: cover; object-position: center; }
.t-cap {
  display: block;
  margin-top: 12px;
  font-size: 12px;
  line-height: 1.5;
  font-style: italic;
  color: var(--b-text-muted, #6b7280);
  font-weight: 400;
}

/* T3 · Inset —— 浅色基底 */
.t-inset {
  padding: 28px;
  background: var(--b-bg-elevated, #f6f6f7);
  border-radius: 0;
}
.slide.dark .t-inset { background: rgba(255, 255, 255, 0.04); }
.t-inset img { object-fit: contain; object-position: center; }

/* T4 · Browser Chrome —— 简化浏览器框 */
.t-browser {
  display: flex;
  flex-direction: column;
  background: #1f2024;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.15);
}
.t-browser-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 14px;
  background: #2a2c31;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.t-browser-bar .t-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #4a4d54;
  display: inline-block;
}
.t-browser-bar .t-dot:nth-child(1) { background: #ff5f57; }
.t-browser-bar .t-dot:nth-child(2) { background: #febc2e; }
.t-browser-bar .t-dot:nth-child(3) { background: #28c840; }
.t-browser-bar .t-url {
  margin-left: 12px;
  flex: 1;
  height: 20px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  font-size: 11px;
  line-height: 20px;
  padding: 0 10px;
  color: rgba(255, 255, 255, 0.55);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.t-browser > img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  flex: 1;
}

/* T5 · Device Frame —— 极简设备外框 */
.t-device { padding: 0; }
.t-device-shell {
  position: relative;
  background: #1a1a1c;
  border-radius: 12px;
  padding: 12px 12px 24px;
  box-shadow: 0 12px 32px -10px rgba(0, 0, 0, 0.25);
}
.t-device-mac .t-device-screen {
  border-radius: 4px;
  overflow: hidden;
  aspect-ratio: 16 / 10;
  background: #000;
}
.t-device-mac .t-device-screen img { object-fit: cover; }
.t-device-iphone {
  width: 280px;
  margin: 0 auto;
  background: #1a1a1c;
  border-radius: 36px;
  padding: 8px;
  box-shadow: 0 12px 32px -10px rgba(0, 0, 0, 0.25);
}
.t-device-iphone .t-device-screen {
  border-radius: 28px;
  overflow: hidden;
  aspect-ratio: 9 / 19.5;
  background: #000;
}
.t-device-iphone .t-device-screen img { object-fit: cover; }

/* T6 · Quiet Frame —— 多图分组 */
.t-quiet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}
.t-quiet {
  margin: 0;
  border: 0.5px solid var(--b-border, #e5e7eb);
  border-radius: 0;
  background: transparent;
  overflow: hidden;
}
.slide.dark .t-quiet { border-color: rgba(255, 255, 255, 0.08); }
.t-quiet img { object-fit: cover; object-position: top center; }

/* T7 · Backdrop —— 背景虚化 */
.t-backdrop {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}
.t-backdrop img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(14px) brightness(0.45);
  opacity: 0.55;
  transform: scale(1.08);  /* 模糊后轻微放大,避免边缘露出 */
}
.slide.dark .t-backdrop img { filter: blur(14px) brightness(0.35); opacity: 0.6; }
.slide > .frame { position: relative; z-index: 1; }  /* 前景文字盖在 backdrop 之上 */

/* T8 · Edge Card —— 唯一允许圆角+阴影的范式 */
.t-edge-card {
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 8px 24px -10px rgba(0, 0, 0, 0.12);
  background: var(--b-bg-elevated, #fff);
}
.t-edge-card img { object-fit: cover; }
```

---

## data-treatment 自检属性

每张图在 HTML 里**显式标 `data-treatment="t-XXX"`**(即使范式是默认 T2,也要写明),让评审时一眼可见,不让 LLM 偷偷回退到旧的"frame-img + figcap"。

| 属性值 | 范式 |
|---|---|
| `data-treatment="t-bleed"` | T1 |
| `data-treatment="t-float"` | T2 |
| `data-treatment="t-inset"` | T3 |
| `data-treatment="t-browser"` | T4 |
| `data-treatment="t-device"` | T5 |
| `data-treatment="t-quiet"` | T6 |
| `data-treatment="t-backdrop"` | T7 |
| `data-treatment="t-edge-card"` | T8 |

---

## 迁移清单(老 demo 改造时)

1. 把所有 `figcaption.img-cap` 文本为"原始截图/产品截图/Screenshot/Untitled"的全部删掉
2. 把所有隐式默认 `.frame-img`(圆角+阴影)的,改成显式 `.t-edge-card`(营销)或改用 T2/T3
3. 多图网格从 `figure.frame-img` 改成 `figure.t-quiet` + `.t-quiet-grid` 容器
4. 设备截图从外层 div hack 改成 `.t-device` / `.t-browser`
5. 评审时跑:

```bash
# 必须 0 命中
grep -rE "原始截图|产品截图|Untitled screenshot" references/ designs/ resources/ demo/ index.html
grep -rE "<figcaption[^>]*>截图" references/ designs/ resources/ demo/ index.html
grep -rE "frame-img[^>]*box-shadow" resources/ demo/  # 旧 frame-img 不应该还带 box-shadow
```

6. 每张 `<img>` 必须有 `data-treatment` 属性(`grep -E "<img" *.html | grep -v data-treatment` 应为 0)

---


---

## Default Double-Click Image Zoom & Lightbox (默认支持鼠标双击放大图片)

全库已**原生默认支持鼠标双击图片放大**。任何幻灯片中的 `<img>` 无需显式配置，**鼠标双击（dblclick）即可触发全屏毛玻璃居中放大（Lightbox）**，再次双击、点击背景、点击关闭按钮或按 `Esc` 键即可瞬间复原。

此外，8 套范式均支持在 `<img>` 或包裹容器上额外添加 `data-zoomable` 属性以启用**单击直接放大**。同 slide 内的多张图片自动归组，支持键盘左右键及悬浮箭头快速翻页。

**用法**:
- **默认双击**: 任何 `<img>` 自动支持双击放大，hover 状态默认呈现 `cursor: zoom-in`。
- **显式单击**: 在 `<img>` 或包裹 `<figure>` 上加 `data-zoomable` 即可启用单击放大。

```html
<!-- 默认图片：无需多余属性，直接支持双击放大 -->
<figure class="t-inset r-16x10" data-treatment="t-inset">
  <img src="images/dashboard.png" alt="数据面板截图">
</figure>

<!-- 显式单击放大支持 -->
<figure class="t-inset r-16x10" data-treatment="t-inset" data-zoomable>
  <img src="images/dashboard.png" alt="数据面板截图">
</figure>

<!-- 缩略图列表:同 slide 多张,自动归组,双击/点击均可全屏,左右键翻页 -->
<div class="t-quiet-grid">
  <figure class="t-quiet" data-treatment="t-quiet">
    <img src="images/screen-1.png" alt="界面 1">
  </figure>
  <figure class="t-quiet" data-treatment="t-quiet">
    <img src="images/screen-2.png" alt="界面 2">
  </figure>
  <figure class="t-quiet" data-treatment="t-quiet">
    <img src="images/screen-3.png" alt="界面 3">
  </figure>
</div>
```

**交互细节**:
- 鼠标移到幻灯片图片上 → `cursor: zoom-in`，提示可缩放
- **双击图片 / 单击 data-zoomable 图片** → 全屏深色毛玻璃背景 + `cubic-bezier` 弹簧物理放大 (0.94 → 1.0)
- **复原关闭方式**: 再次双击图片 / 单击任意背景 / 单击右上角 `×` / 按 `Esc`
- **组内翻页**: ← / → 键，或点两侧箭头按钮
- **组内计数器**: 左上角 `2 / 5` 徽章指示
- **纯净大图视觉 (No Text Display)**: 全屏放大视图仅聚焦图片本身，旁边及下方不展示任何文字标题、描述或图说，确保沉浸式的纯净视觉体验
- 打开时自动锁住 body 滚动，关闭后复原

## 何时读这份文档

- 生成新 slide 时:选范式 → 写 `data-treatment` → 用对应 CSS 类
- 评审现存 deck:跑迁移清单的 5 条 grep
- 用户反馈"图片丑/像占位符/像卡片":先看是不是默认走 T2/Float,再考虑是否需要 T3/T4 升级
- 不要做的事:不要在评审时给所有图加回 `border-radius` 和 `box-shadow` 来"救场",这正是这套范式要解决的问题