# 腾讯云 COS 部署踩坑记录

记录将纯前端 H5 题库部署到腾讯云 COS 匿名桶时遇到的 5 层 bug 链。**推荐优先用 CloudStudio sandbox 部署**（零配置、自动正确 MIME、无缓存历史负担）；COS 仅在需要自定义域名/长期稳定链接时使用，且务必避开下列坑。

## Bug 链总览

```
桶名拼写错误 → createReadStream 空文件 → injectVersions 正则引号位置
  → CDN 忽略查询参数 → 裸路径空文件死循环
```

## 坑 1：桶名拼写（403 Access Denied）

用户提供的桶名可能漏字母（如 `generate` vs `generat`）。COS 桶名 = `<name>-<appId>`，必须完全匹配。
- 排查：`curl -I https://<bucket>.cos.<region>.myqcloud.com/` 看 403 还是 404。
- 修复：到 COS 控制台核对真实桶名。

## 坑 2：`fs.createReadStream` 在 Windows 中文路径下静默返回空流（最严重）

**现象**：部署脚本用 `fs.createReadStream(file)` 上传，上传"成功"但 COS 上文件 size=0、Content-Type 被设为 `application/xml`，浏览器打开是下载而非渲染。

**根因**：Node.js 的 `fs.createReadStream` 在 Windows 中文路径（如 `D:\农大\...`）下偶发静默失败，流不报错但读到 0 字节。COS SDK 收到空 Body 后用默认 Content-Type `application/xml`。

**修复**：改用 `fs.readFileSync(file)` 同步读取为 Buffer，再 `putObject({ Body: buffer, ContentType: '...' })`，并**显式指定 ContentType**。

```js
// ❌ 错误（Windows 中文路径静默空流）
cos.putObject({ Bucket, Key, Body: fs.createReadStream(file) });

// ✅ 正确
const buf = fs.readFileSync(file);
cos.putObject({ Bucket, Key, Body: buf, ContentType: mimeLookup(ext) });
```

## 坑 3：cache-busting 正则把 `?v=hash` 放到引号外

**现象**：注入 hash 引用时，正则错误生成 `href="css/style.css"?v=db4b1b5f`（`?v=` 在引号外），浏览器请求裸路径 `css/style.css` 而非带 hash 的文件名。

**修复**：正则用捕获组，确保 `?v=` 在引号内：
```js
// ❌ 错误
html.replace(/href="([^"]+\.css)"/, 'href="$1"?v=' + hash);
// ✅ 正确
html.replace(/href="([^"]+\.css)"/, 'href="$1?v=' + hash + '"');
```

## 坑 4：腾讯云 COS CDN 默认忽略 URL 查询参数

**现象**：用 `?v=<hash>` 做 cache-busting 无效，CDN 仍命中旧缓存（旧空文件）。

**根因**：腾讯云 COS CDN 默认**忽略 URL 查询参数**，`style.css?v=aaa` 和 `style.css?v=bbb` 命中同一缓存。

**修复**：改为**文件名 hash** 方案（`style.<hash>.css`），URL 完全不同，CDN 不可能命中旧缓存：
```js
// 文件名 hash：上传 css/style.db4b1b5f.css，index.html 引用该文件名
```

## 坑 5：裸路径空文件死循环（浏览器缓存死锁）

**现象**：改用文件名 hash 后，hash 路径文件正确，但**裸路径**（`css/style.css`）仍是旧的 0 字节空文件。浏览器缓存了旧版 index.html（引用裸路径）→ 请求裸路径 → 拿到空文件 → 页面无样式 → 无法自愈。

**修复**：部署时**同时上传裸路径兼容版**——hash 路径（immutable 1年）+ 裸路径（no-cache，内容=正确文件），覆盖旧的空文件：

```js
if (ext === '.css' || ext === '.js') {
  // 上传 hash 路径（长期缓存）
  await putObject(hashKey, buf, 'public, max-age=31536000, immutable');
  // 同时覆盖裸路径（no-cache，打破旧空文件缓存）
  await putObject(bareKey, buf, 'no-cache, must-revalidate');
}
```

并在 `index.html` 加防御性 meta：
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
```

## 坑 6：index.html 增量判断基于原始文件 MD5

**现象**：`index.html` 注入了 hash 引用后内容变了，但部署脚本的增量判断基于**原始文件** MD5，认为"没变化"而跳过上传，导致 COS 上 index.html 仍是旧版。

**修复**：增量判断基于**注入后的内容**（`uploadBody`）的 MD5：
```js
const uploadBody = injectVersions(html, hashes);
const uploadMd5 = md5(uploadBody);  // 用注入后的内容算 MD5
if (!FORCE && remoteEtag === uploadMd5) { skip; }
```

## 推荐部署方案对比

| 方案 | 配置复杂度 | MIME 正确性 | 缓存风险 | 自定义域名 |
|------|-----------|------------|---------|-----------|
| **CloudStudio sandbox** | 零配置 | 自动正确 | 无历史包袱 | 不支持 |
| **COS 匿名桶** | 中（凭证+桶+CDN） | 需显式设置 | 高（见上） | 支持 |
| **COS + CDN** | 高 | 需显式设置 | 高 | 支持 |

**结论**：开发/演示/小规模分发 → CloudStudio sandbox。生产/需自定义域名 → COS，但务必用 `readFileSync` + 文件名 hash + 裸路径兼容版 + 显式 ContentType。
