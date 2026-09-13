# 白名单昵称自动读取模式（SHA-256 哈希，不存明文）

纯前端题库系统的登录方案：手机号 → SHA-256 哈希 → 白名单哈希比对。白名单仅存储
手机号哈希值与昵称映射（不存明文手机号，合规要求），用户无需手动填昵称，登录弹窗
只输手机号。

## 登录弹窗文案（标准）

- 标题：`🔒 请先登录`
- 副标题：`输入手机号（仅本地记录，不上传），系统生成你的专属学习档案`
- 输入框：仅一个手机号输入框（`maxlength=11`），**无昵称输入框**

> 「仅本地记录，不上传」指：用户输入的手机号只在浏览器本地做 SHA-256 哈希，再与
> fetch 下来的静态 `whitelist.json` 中的哈希值比对，不会 POST 到任何后端服务。白名单
> 是纯静态文件，前端拉取后本地匹配，登录态写入 LocalStorage。

## 白名单格式（`data/whitelist.json`）

```json
{
  "version": "2.0",
  "entries": [
    { "hash": "a6942f9771d67f34034d2f1926988ed3fad3bf1b4e7cedb9a31f31398dea43bc", "name": "张同学" },
    { "hash": "f1d8142cbb59c0a2f93f91fbe934f83f9afbdab0b8fafaabad0f842b32aab322", "name": "李同学" }
  ]
}
```

- `hash`：手机号的 SHA-256 哈希值（64 位 hex 小写）。
- `name`：该用户在界面上显示的昵称。

**兼容旧格式** `{ "hashes": ["sha256hex1", ...] }`（无昵称，`getNameFromHash` 返回空，
调用方用默认文案兜底）。

### 如何生成哈希

- **浏览器工具**：打开 `tools/gen-hash.html`，粘贴手机号列表（每行一个），点击生成，
  复制哈希值填入 `whitelist.json`。
- **命令行**：`echo -n "13800138000" | sha256sum`（注意 `-n` 去掉换行符）。
- **项目内**：`QuizApp.Crypto.sha256("13800138000")`（控制台调用）。

> 哈希时**不要加盐**，输入就是 11 位手机号字符串本身，UTF-8 编码后直接 SHA-256。

## crypto.js 核心方法

纯 JavaScript 实现，无外部依赖，兼容 `file://` 与 `http://` 协议。

### `sha256(message)`
计算字符串的 SHA-256 哈希值，返回 64 位 hex 小写字符串。

### `hashPrefix(message)`
取 `sha256(message)` 的前 8 位，作为用户数据隔离前缀。

## auth.js 核心方法

### `loadWhitelist()`
加载白名单，缓存到 `_entries`。支持新格式 `entries`（含 hash+name）与旧格式 `hashes`
（纯哈希数组）。失败时返回 `null`（降级模式：放行任意有效手机号，适合开发/演示；
生产环境应改为拦截所有登录）。

### `isWhitelisted(phoneHash)`
检查哈希是否在白名单中。接收的是**哈希值**（不是明文手机号），比对 `e.hash === phoneHash`。

### `getNameFromHash(phoneHash)`
根据哈希查白名单昵称。未找到返回 `null`，调用方用默认文案（如「备考学员」）兜底。

### `login(phone)`
登录流程（昵称自动读取，无需用户填）：
1. 校验手机号格式（`/^1[3-9]\d{9}$/`）
2. `loadWhitelist()` 加载白名单
3. 降级模式（`entries === null`）：放行，昵称用默认
4. `phoneHash = Crypto.sha256(phone)` 计算哈希
5. `isWhitelisted(phoneHash)` 比对哈希是否在白名单
6. 通过 → `getNameFromHash(phoneHash)` 自动读昵称 → `setLoginState(phone, hash8, name)`
7. `hash8 = phoneHash.substring(0, 8)` 作用户数据隔离前缀

### `getDisplayName()`
返回 `state.nickname`（trimmed）或默认文案。**永远不在 UI 显示原始或脱敏手机号**。

## UI 规范：右上角问候语

登录后右上角显示 `你好！{昵称}`（如「你好！张同学」），不显示手机号。
- 未登录时右上角显示「登录」按钮。
- **不需要用户手动填昵称的输入框**——昵称来自白名单。
- **无左下角用户卡**——用户信息只在右上角问候语体现。
- 修改昵称 = 改 `whitelist.json` 的 `name` 字段 + 重新部署，无需用户操作。

## 数据隔离与安全

- LocalStorage 存 `{ phone, phoneHash, nickname, loginTime, isLoggedIn }`，用哈希前 8 位
  作为用户标识。
- 用户数据隔离：`Storage` 用 `qb_{hash8}_` 前缀隔离不同用户的学习进度
  （如 `qb_a6942f97_mistakes`）。
- 白名单仅存哈希值，不存明文手机号；如需更高合规等级，可在部署侧加访问控制
  （私有桶 + 签名 URL），但前端比对逻辑不变。
- `crypto.js` 是纯 JS 实现，无外部依赖，兼容 `file://` 协议（离线可用）。
