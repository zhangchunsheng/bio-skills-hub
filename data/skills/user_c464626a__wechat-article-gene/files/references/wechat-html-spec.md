# 公众号编辑器兼容规范（WeChat HTML Spec）

公众号编辑器是"样式黑洞"，直接粘贴网页 HTML 必然丢失格式。本规范总结实测过的坑与解法，用于制作「一键复制专用页」。

## 编辑器的过滤规则（实测）

1. **剥离 `<style>` 标签与 class**：粘贴时只保留每个标签上的内联 `style` 属性——集中式 CSS 全部失效，所有样式必须写在 `style=""` 内联
2. **禁止外链图片**：本地路径 / 外网 URL 的 `<img>` 粘贴后必然失效，图片只能通过编辑器工具栏手动上传
3. **页面背景会被一起复制**：若复制范围或剪贴板序列化带上了页面背景色（如浅灰 `#f5f6f8`），粘贴后每行文字都垫灰底
4. **渐变降级**：`linear-gradient` 在部分手机客户端显示异常，CTA 卡片用纯色（如 `#2a5cff`）代替渐变
5. **暗色插件注入**：浏览器暗色模式插件会给 HTML 注入背景色，同样导致灰底

## 复制专用页（wechat.html）制作规则

以 `assets/wechat-template.html` 为骨架，规则：

1. **复制区内 100% 内联样式**，不使用任何 class 或 `<style>` 块作用于正文
2. **复制按钮用 Clipboard API 直接写入**（不要依赖 execCommand 选区复制）：
   ```js
   var html = '<section style="background-color:#ffffff;">' + zone.innerHTML + '</section>';
   await navigator.clipboard.write([new ClipboardItem({
     'text/html': new Blob([html], { type: 'text/html' }),
     'text/plain': new Blob([zone.innerText], { type: 'text/plain' })
   })]);
   ```
   外层显式白底 section 是兜底；同时保留 execCommand 选区复制作降级方案
3. **页面底色纯白**：`html, body { background: #ffffff; }`，就算用户手动 Ctrl+A 也带不出灰底
4. **顶部工具条不可选中**（`user-select: none`），避免被复制进去
5. **图片位置用虚线占位框**，框内标注对应文件名：
   ```html
   <section style="margin:22px 0;padding:26px 16px;border:2px dashed #b9c4ff;border-radius:10px;background:#f4f6ff;text-align:center;font-size:14px;color:#5160b8;line-height:1.8;">
   <b style="display:block;font-size:15px;margin-bottom:4px;color:#1c3fb0;">【插图 1 · 此处上传 images/02-xxx.png】</b>
   图片说明文字
   </section>
   ```

## 正文内联样式速查（实测可完整保留）

| 元素 | 样式 |
|---|---|
| 段落 | `margin:0 0 14px;font-size:16px;line-height:1.85;letter-spacing:.2px;color:#1f2329;` |
| h2 | `margin:30px 0 14px;font-size:20px;font-weight:700;padding-left:12px;border-left:4px solid #2a5cff;color:#1f2329;` |
| h3 | `margin:22px 0 10px;font-size:17px;color:#1c3fb0;font-weight:700;` |
| 引用块 | `margin:16px 0;padding:14px 18px;background:#f0f3ff;border-left:4px solid #c8d2ff;border-radius:6px;font-size:15px;color:#4e5969;line-height:1.8;` |
| 强调色加粗 | `<strong style="color:#1c3fb0;">` |
| 关键词高亮 | `<span style="background:#fff7d6;padding:1px 4px;border-radius:3px;font-weight:600;">` |
| 深色金句卡 | `margin:24px 0;padding:18px 20px;background:#0d1633;color:#ffffff;border-radius:12px;text-align:center;font-weight:600;` |
| 服务卡片 | `margin:12px 0;padding:14px 16px;border:1px solid #e5e6eb;border-radius:10px;` |
| CTA 卡 | `margin:26px 0 8px;padding:22px 18px;background:#2a5cff;border-radius:14px;text-align:center;` |
| 分隔符 | `<p style="margin:26px 0;text-align:center;color:#c9cdd4;font-size:14px;letter-spacing:8px;">···</p>` |
| 列表 | `padding-left:22px;margin:8px 0 14px;font-size:15.5px;line-height:1.85;color:#1f2329;`，li 加 `margin-bottom:6px;` |

## 用户操作指引（交付时随附）

1. 用 Chrome 打开 wechat.html → 点「一键复制正文」按钮（不要 Ctrl+A 手动全选）
2. 到 mp.weixin.qq.com 新建图文 → Ctrl+V，格式完整保留
3. 点击虚线占位框位置 → 编辑器工具栏「图片」→ 上传 `images/` 里对应文件
4. 封面在右侧设置里上传 `01-cover.png`（2.35:1 裁剪）
5. 若仍出现灰底：浏览器暗色插件注入所致，换 Chrome 无痕窗口打开复制
