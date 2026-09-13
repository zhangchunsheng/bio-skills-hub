# 安全审查报告 — anti-bot-bypass

- **被审查对象**：`~/.workbuddy/skills/anti-bot-bypass/`（SKILL.md + scripts/probe.py + references/{mechanisms,vendors,toolbox}.md）
- **审查方式**：纯静态文本分析（只读），未执行被审查 skill 任何代码
- **审查日期**：2026-08-16
- **审查人**：skills-security-check 流程
- **结论**：✅ **Benign（可信，可安全使用）**

---

## 1. 文件清单与规模

| 文件 | 行数 | 性质 |
|---|---|---|
| SKILL.md | 154 | 知识文档 + 作业流程 |
| scripts/probe.py | 426 | 可运行诊断探针（仅标准库 + 可选 curl_cffi） |
| references/mechanisms.md | 175 | 八层机制原理与对策文档 |
| references/vendors.md | 131 | 厂商指纹库文档 |
| references/toolbox.md | 257 | 工具选型与代码模板文档 |

全部为本地新建文件，无外部下载源、无内嵌远程脚本。

## 2. 高危模式扫描结果

| 检查项 | 结果 |
|---|---|
| `curl \| bash` / `wget \| sh` 远程脚本执行 | ❌ 未命中 |
| `os.system` / `subprocess` / `popen` | ❌ 未命中 |
| `eval()` / `exec()` / `__import__()` 执行外部数据 | ❌ 未命中（文档提及用 hook 绕过 debugger，属教学说明，skill 不自动执行） |
| `rm -rf` / `shutil.rmtree` / `os.remove` 破坏性删除 | ❌ 未命中 |
| `requests.post` / socket 外联到第三方（数据外泄） | ❌ 未命中（probe.py 仅对**用户指定 target URL** 发 GET） |
| `base64.b64decode` 解码可执行代码 | ❌ 未命中 |
| 硬编码凭证 / API Key / 密码 | ❌ 未命中（命中的 `token`/`sign` 均为反爬 cookie 名与参数识别，非凭证） |
| 混淆/加密载荷 | ❌ 未命中（全部源码可读） |

## 3. 探针写操作范围确认（probe.py）

写操作全部收敛于用户显式传入的 `--save DIR`：

- `os.makedirs(a.save, exist_ok=True)` — 仅创建用户指定目录
- `open(os.path.join(a.save, ...), "w")` + `fh.write(r["body"])` — 仅落盘被抓取站点的响应 HTML，供人工核对

无任何写系统目录、无覆盖、无删除。

## 4. 网络行为确认

- `fetch_stdlib()`：用 `urllib` 对**用户传入的 URL** 发 GET（含 robots.txt 自检，同域名）。
- `fetch_impersonate()`：仅当已装 `curl_cffi` 时，对**同一目标 URL** 发第二轮 TLS 对照 GET。
- 默认开启 TLS 证书校验（`ssl.create_default_context()`）；仅 `--insecure` 显式关闭（用于本地抓包代理场景），并在 stderr 明确提示 MITM 防护失效。
- **无** 向任何第三方/攻击者域名回传数据。

## 5. 依赖与供应链

- 仅依赖：标准库 + 可选 `curl_cffi`（判层最准时建议装）。
- 依赖均在隔离 venv 安装（`~/.workbuddy/binaries/python/envs/antibot`），不污染系统 Python。
- 安装源约定为清华镜像（`pypi.tuna.tsinghua.edu.cn`），均为 PyPI 官方包，无未知/私有索引。
- 无 `requirements.txt` 锁定第三方未知包，无 `pip install` 从随机 URL 拉取。

## 6. 合规与伦理

- SKILL.md §0 明确**合规红线**：禁止绕过登录/付费墙、禁止高频 DoS、禁止抓取个人信息、禁止用验证码对抗身份核验。命中即拒绝。
- 全程强调"公开数据 + 授权 + robots.txt + 低频"，面向诊断与合法绕过，非攻击工具。

## 7. 残留风险与建议（非阻断）

- **教学性风险**：references 含 JS 逆向 / hook Function / JSRPC 等教学说明，使用者在对抗强风控时应自行确认授权与合法性。建议保持 §0 红线为强制前置。
- **误报面**：厂商指纹库基于 cookie/响应头/body 关键词，弱证据已标注"疑似仅 CDN"，判层以实际状态码为准——已在探针逻辑内处理。
- **时效**：反检测工具链落后于风控数周，文档已提示"先跑探针重新判层，再改方案"。

---

**最终判定**：无投毒、无远程执行、无供应链风险、无凭证泄露、无破坏性操作。可安全启用。
