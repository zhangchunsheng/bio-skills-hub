---
name: general-mirror-acceleration
description: 中国开发者通用镜像加速 — 覆盖 GitHub/HuggingFace/PyPI/npm/Docker/Go/Rust/Homebrew/Maven/Conda/APT/RubyGems/CocoaPods/Flutter/Chromium 等 16 类站点全链路加速。触发关键词：timeout、超时、不可达、连接失败、镜像、加速、github.com、huggingface.co、pypi.org、npm、cargo、go install、docker pull、apt-get、下载失败、too slow、connection reset。当任何下载/安装/pull/clone操作超时或极慢时自动加载此技能。
version: 3.0.0
trigger:
  - timeout
  - 超时
  - 不可达
  - 连接失败
  - connection reset
  - connection refused
  - 镜像
  - 加速
  - 下载失败
  - too slow
  - github.com
  - huggingface.co
  - pypi.org
  - npm
  - cargo
  - go install
  - docker pull
  - apt-get
  - curl.*timed out
  - Recv failure
  - Could not resolve host
  - SSL connect error
  - ConnectionResetError
  - dial tcp.*timeout
  - 配置镜像
---

# 通用镜像加速（General Mirror Acceleration）

> **一句话定位**：覆盖 GitHub / HuggingFace / PyPI / npm / Docker / Go / Rust / Homebrew / Maven / Conda / APT / RubyGems / CocoaPods / Flutter / Chromium 等 16 大品类的中国开发者全链路镜像加速方案，在下载/安装/clone/pull 超时或极慢时自动介入。

---

## ⛔ Agent 强制规则（最高优先级）

> **铁律：任何下载/安装/pull/clone 操作超时或失败时，必须立即、自动、不等BOSS提醒地执行以下决策链：**
>
> ```
> 超时/连接失败 → skill_view('general-mirror-acceleration') → 查对应品类镜像 → 设置环境变量/切源 → 重试
> ```
>
> **禁止行为：**
> - ❌ 超时后直接 kill 进程而不切换镜像源
> - ❌ 等 BOSS 说"走镜像啊""加速啊"才反应
> - ❌ 假设"直连多试几次也许能通"
>
> **正确行为（Playwright 实战验证）：**
> ```bash
> # 直连超时 → 立即切镜像，不等待
> export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
> playwright install chromium  # 30s 完成（直连超时→镜像秒下）
> ```
>
> 本规则已写入 MEMORY.md（2026-07-04 BOSS纠正），每次会话必注入。

---

## 一、触发条件

本技能在检测到以下**任意信号**时自动激活：

### 1.1 错误信号（自动识别）

| 信号类型 | 典型错误信息 |
|---------|------------|
| DNS 失败 | `curl: (6) Could not resolve host` |
| 连接超时 | `curl: (28) Operation timed out`、`dial tcp: i/o timeout` |
| 连接拒绝 | `Connection refused`、`curl: (7) Failed to connect` |
| 连接重置 | `Connection reset by peer`、`curl: (56) Recv failure` |
| SSL 错误 | `curl: (35) SSL connect error` |
| Python 异常 | `ConnectionResetError`、`TimeoutError`、`URLError` |
| Docker 超时 | `dial tcp: i/o timeout`、`net/http: TLS handshake timeout` |
| Git 慢速 | clone 速度 < 50 KB/s、卡住不动 |

### 1.2 品类词（触发品类定位）

```
github.com, huggingface.co, pypi.org, npm / node, cargo / crates.io,
go install / goproxy, docker pull, apt-get / apt, brew / homebrew,
maven / gradle, conda / anaconda, gem / rubygems, pod / cocoapods,
flutter / dart, chromium / electron / playwright / puppeteer
```

### 1.3 用户意图关键词

```
镜像, 加速, 超时, 不可达, too slow, 下载失败, 配置镜像,
连不上, 下不动, 卡住了, 网络问题, 国内加速, 换源
```

---

## 适用范围与限制

本工具利用国内镜像加速海外资源的下载访问，适用于中国大陆网络环境下因 GFW、国际带宽瓶颈等因素导致的连接问题。

### ✅ 可以解决的问题

| 问题类型 | 典型现象 | 解决方案 |
|---------|---------|---------|
| 网络超时 | `Operation timed out`、`dial tcp: i/o timeout` | 镜像代理回退 |
| 连接拒绝 | `Connection refused`、`Failed to connect` | 切换国内镜像源 |
| 下载极慢 | clone 速度 < 50 KB/s、下载卡住不动 | 国内镜像 + 浅克隆优化 |
| DNS 解析失败 | `Could not resolve host`、DNS 污染 | DNS 切换 + 镜像直连 |

### ❌ 无法解决的问题

| 问题类型 | 典型现象 | 原因 |
|---------|---------|------|
| 账号/权限问题 | `403 Forbidden`、`401 Unauthorized` | 需要登录或授权，镜像无法绕过 |
| 防火墙/GFW 内容阻断 | 特定仓库/文件被墙 | 镜像代理同样受 GFW 管控，无法突破内容审查 |
| SSL 证书错误 | `SSL certificate problem`、证书过期 | 服务器端证书配置问题，与网络路径无关 |
| 认证/Token 问题 | GitHub token 过期、HuggingFace 认证失败 | 需要用户更新凭证，镜像无法替代 |
| 被屏蔽的仓库 | 仓库被 DMCA 下架或作者删除 | 源已不存在，镜像无法同步 |

> **一句话总结**：本工具解决"通不通"的问题（网络可达性），不解决"能不能"的问题（权限、审查、证书）。

---

## 二、使用入口

本技能提供三个核心脚本，覆盖「自动加速」「健康检测」「一键配置」三个层级。

### 2.1 运行时引擎 — `mirror_fetch.sh`（自动镜像切换）

核心入口。延迟探测 → 官方源超时 → 按优先级遍历镜像源 → 首达则返回。

```bash
# === GitHub 场景 ===
# git clone（自动走 gitclone.com → ghproxy.net → 直连）
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_fetch.sh \
  https://github.com/user/repo.git

# raw 文件下载
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_fetch.sh \
  https://raw.githubusercontent.com/user/repo/main/file.py  /tmp/file.py

# Releases 大文件
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_fetch.sh \
  https://github.com/user/repo/releases/download/v1.0/app.tar.gz  ./app.tar.gz

# === HuggingFace 场景 ===
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_fetch.sh \
  https://huggingface.co/bert-base-uncased

bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_fetch.sh \
  https://huggingface.co/user/model/resolve/main/config.json  /tmp/config.json

# === 通用 HTTPS URL（任意文件下载） ===
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_fetch.sh \
  https://cdn.example.com/large_file.tar.gz  /tmp/file.tar.gz
```

**工作流程**：对所有 URL 自动探测延迟，非 GitHub/HF 的通用 URL 自动走代理层回退（ghproxy.net → ghp.ci → gh-proxy.com）。

### 2.2 镜像健康检测 — `mirror_health_check.sh`

```bash
# 检测全部 16 品类镜像连通性
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_health_check.sh

# 仅检测指定品类
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_health_check.sh pypi
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_health_check.sh github
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_health_check.sh npm

# 更新镜像源列表 — 从远程拉取最新镜像 URL 配置
bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_health_check.sh --update
```

输出：各镜像的 HTTP 状态码、延迟（ms）、通过/失败汇总。

**`--update` 标志说明**：镜像源的可用性会随时间变化（某些镜像下线、新镜像上线、URL 变更），使用 `--update` 可将 `mirrors_config.sh` 中的镜像列表同步到最新版本，无需手动编辑配置文件。建议定期（如每月）或遇到全部镜像不可用时执行一次更新。

**`--update` 多源回退链**（v1.1.0 升级）：避免单一 GitHub Raw URL 在某些网络环境不可达，按顺序尝试 4 个源，第一个成功即用：

```
源1: raw.githubusercontent.com    ← 海外/可直连环境
源2: gh-proxy.com                  ← 国内首选代理
源3: mirror.ghproxy.com            ← 备选代理
源4: raw.gitmirror.com             ← 最后兜底
全部失败 → 保留旧配置, exit 0
```

每次下载后还会做内容校验（检查文件是否包含 `declare` 或 `VERSION` 关键字），防止 404 HTML 页面被误认为是有效配置文件。

### 2.3 一键系统镜像配置 — `setup_system_mirrors.sh`

```bash
# 一键配置所有已安装工具的镜像源
bash ~/your-agent/skills/general-mirror-acceleration/scripts/setup_system_mirrors.sh all

# 仅配置指定品类
bash ~/your-agent/skills/general-mirror-acceleration/scripts/setup_system_mirrors.sh pypi
bash ~/your-agent/skills/general-mirror-acceleration/scripts/setup_system_mirrors.sh npm
bash ~/your-agent/skills/general-mirror-acceleration/scripts/setup_system_mirrors.sh go
bash ~/your-agent/skills/general-mirror-acceleration/scripts/setup_system_mirrors.sh cargo
bash ~/your-agent/skills/general-mirror-acceleration/scripts/setup_system_mirrors.sh docker

# 交互式菜单（列出所有可用品类）
bash ~/your-agent/skills/general-mirror-acceleration/scripts/setup_system_mirrors.sh
```

---

## 二、脚本架构

```
general-mirror-acceleration/  (v3.0.0)
├── SKILL.md                                 # 本文档
└── scripts/
    ├── mirror_fetch.sh                      # ★ 主引擎 — 并行探测 + 延迟缓存 + 自适应HTTP/Git
    ├── mirror_health_check.sh               # ★ 动态检测 — 从 mirrors_config.sh 自动生成全品类列表
    ├── setup_system_mirrors.sh              # 一键全家桶 — 9 工具自动配置 + 非破坏性APT
    └── mirrors_config.sh                    # 配置中心 — 30+ 品类镜像 + URL转换 + 探测方法路由
```

## 三、v3.0 核心升级

| 特性 | v1.0 | v3.0 |
|------|------|------|
| 镜像排序 | 固定优先级 | **并行探测 → 延迟排序**（最快优先） |
| 延迟缓存 | 无 | **`/tmp/.mirror_latency_cache`**（TTL=5分钟） |
| Git品类探测 | HTTP HEAD 无效等待 | **跳过HTTP探测，直接用 git ls-remote** |
| APT配置 | 覆盖 sources.list（破坏性）| **sed域名替换（保留PPA/自定义源）** |
| APT路径 | **缺失 /ubuntu/（P0 Bug）** | 自动补 `/ubuntu/` 或 `/debian/` |
| 健康检测 | 硬编码200+行 | **动态从 mirrors_config.sh 生成** |
| 一键配置 | 5工具 | **9工具**（+Docker/Maven/Conda/RubyGems） |
| 命令行 | 仅无参 | `--help` / `--no-cache` / `-h` / 品类别名 |
| 死代码 | `probe_official()` 从未调用 | 已删除，换并行探测引擎 |
---

## 四、主引擎工作流程（`mirror_fetch.sh` v3.0 决策树）

```
输入: URL [--no-cache] [--help]

  ├── 品类识别（detect_category，30+ 品类正则链）

  ├── 探测方法判定（probe_method）
  │     ├── github-clone / homebrew-* / cocoapods → git ls-remote
  │     └── 其余 → HTTP HEAD

  ├── 延迟缓存查询（/tmp/.mirror_latency_cache, TTL=300s）
  │     ├── 命中 + 未过期 → 直接按延迟排序 ⚡ 最快
  │     └── 未命中 / --no-cache ↓

  ├── 并行探测（parallel_rank_urls）
  │     └── 所有镜像 URL 同时探测（HTTP HEAD 或 git ls-remote）
  │         → 按实测延迟升序排列
  │         → 写入缓存（下次复用）

  ├── try_urls（按排序后顺序逐个尝试）
  │     ├── HTTP品类：1秒健康预检 → 跳过不可达
  │     ├── Git品类：跳过HTTP预检，直接下载
  │     └── 任一成功 → 返回结果

  ├── 通用代理回退（非包管理器品类）
  │     └── gh-proxy → mirror.ghproxy → ghp.ci

  └── 全部失败 → 报告 + 建议 mirror_health_check.sh
```

---

## 五、全品类镜像速查表

> **注意**：以下镜像 URL 以 `mirrors_config.sh` 为准，本表仅作快速参考。实际运行时由脚本自动选择最优镜像。

### 5.1 GitHub

**Git Clone**

| 优先级 | 镜像 | URL 模板 |
|--------|------|---------|
| 1 | gitclone.com | `https://gitclone.com/github.com/{USER}/{REPO}.git` |
| 2 | mirror.ghproxy.com | `https://mirror.ghproxy.com/https://github.com/{USER}/{REPO}.git` |
| 3 | ghp.ci | `https://ghp.ci/https://github.com/{USER}/{REPO}.git` |
| 4 | 直连 | `https://github.com/{USER}/{REPO}.git` |

**Raw 文件**

| 优先级 | 镜像 | URL 模板 |
|--------|------|---------|
| 1 | raw.gitmirror.com | `https://raw.gitmirror.com/{USER}/{REPO}/{BRANCH}/{PATH}` |
| 2 | mirror.ghproxy.com | `https://mirror.ghproxy.com/https://raw.githubusercontent.com/{USER}/{REPO}/{BRANCH}/{PATH}` |
| 3 | ghp.ci | `https://ghp.ci/https://raw.githubusercontent.com/{USER}/{REPO}/{BRANCH}/{PATH}` |

**Releases 大文件**：`ghproxy.net` → `ghp.ci` → 断点续传（`curl -C -`）

### 5.2 HuggingFace

| 优先级 | 镜像 | URL / 配置 |
|--------|------|-----------|
| 1 | hf-mirror.com（首选） | `export HF_ENDPOINT=https://hf-mirror.com` |
| 2 | hf.xeduapi.com | URL 替换：`huggingface.co` → `hf.xeduapi.com` |
| 3 | modelscope.cn | 阿里魔搭社区（部分热门模型） |

### 5.3 PyPI / pip

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | 中科大 | `https://pypi.mirrors.ustc.edu.cn/simple` |
| 2 | 阿里云 | `https://mirrors.aliyun.com/pypi/simple` |
| 3 | 清华 TUNA | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 4 | 官方 | `https://pypi.org/simple` |

> 实测延迟：中科大 82ms > 阿里 108ms > 清华 118ms。豆瓣已不可达、华为云 429 限流，均已移除。

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
uv: export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5.4 npm / Node.js

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | npmmirror | `https://registry.npmmirror.com` |
| 2 | 官方 | `https://registry.npmjs.org` |

> 实测延迟：npmmirror 91ms。清华 npm 已测出 404，已移除。

```bash
npm config set registry https://registry.npmmirror.com
pnpm config set registry https://registry.npmmirror.com
yarn config set registry https://registry.npmmirror.com
```

### 5.5 Docker

| 优先级 | 镜像 | URL |
|--------|------|-----|
| 1 | docker.1ms.run | `https://docker.1ms.run` |
| 2 | docker.xuanyuan.me | `https://docker.xuanyuan.me` |
| 3 | 阿里云（需注册） | `https://{your_id}.mirror.aliyuncs.com` |

```json
{ "registry-mirrors": ["https://docker.1ms.run", "https://docker.xuanyuan.me"] }
```

### 5.6 Go Modules

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | goproxy.cn | `https://goproxy.cn` |
| 2 | 阿里云 | `https://mirrors.aliyun.com/goproxy/` |

```bash
go env -w GOPROXY=https://goproxy.cn,direct
```

### 5.7 Rust / Cargo

| 优先级 | 源 | Registry URL |
|--------|-----|-------------|
| 1 | 清华 TUNA (sparse) | `sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/` |
| 2 | 中科大 (sparse) | `sparse+https://mirrors.ustc.edu.cn/crates.io-index/` |

```toml
# ~/.cargo/config.toml
[source.crates-io]
replace-with = 'tuna-sparse'
[source.tuna-sparse]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
```

### 5.8 Homebrew (macOS)

| 优先级 | 源 | 环境变量 |
|--------|-----|---------|
| 1 | 清华 TUNA | `HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles` |
| 2 | 中科大 | `HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles` |

### 5.9 Maven / Gradle

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | 腾讯云 Maven | `https://mirrors.cloud.tencent.com/nexus/repository/maven-public/` |
| 2 | 华为云 Maven | `https://mirrors.huaweicloud.com/repository/maven/` |
| 3 | 官方 Maven Central | `https://repo1.maven.org/maven2/` |

> ⚠️ 阿里云 Maven 路径变更，已不可用（404）。

```xml
<!-- ~/.m2/settings.xml -->
<mirror>
  <id>aliyun</id>
  <mirrorOf>central</mirrorOf>
  <url>https://maven.aliyun.com/repository/public</url>
</mirror>
```

### 5.10 Conda / Anaconda

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | 清华 TUNA | `https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main` |
| 2 | 清华 conda-forge | `https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge` |

```yaml
# ~/.condarc
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

### 5.11 APT (Debian/Ubuntu)

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | 阿里云 | `https://mirrors.aliyun.com/ubuntu/` |
| 2 | 清华 TUNA | `https://mirrors.tuna.tsinghua.edu.cn/ubuntu/` |
| 3 | 中科大 | `https://mirrors.ustc.edu.cn/ubuntu/` |

```bash
sudo sed -i 's|http://.*archive.ubuntu.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list
```

### 5.12 Ruby / RubyGems

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | ruby-china | `https://gems.ruby-china.com` |

```bash
gem sources --add https://gems.ruby-china.com --remove https://rubygems.org/
bundle config mirror.https://rubygems.org https://gems.ruby-china.com
```

### 5.13 CocoaPods (iOS/macOS)

| 优先级 | 源 | URL |
|--------|-----|-----|
| 1 | 清华 TUNA | `https://mirrors.tuna.tsinghua.edu.cn/git/CocoaPods/Specs.git` |

```bash
pod repo remove master
pod repo add master https://mirrors.tuna.tsinghua.edu.cn/git/CocoaPods/Specs.git
```

### 5.14 Flutter / Dart

| 优先级 | 源 | 配置 |
|--------|-----|------|
| 1 | Flutter 社区 | `FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn` |
| 1 | Pub 社区 | `PUB_HOSTED_URL=https://pub.flutter-io.cn` |

### 5.15 Chromium / Electron / Playwright

| 工具 | 环境变量 | 镜像 URL |
|------|---------|----------|
| Playwright | `PLAYWRIGHT_DOWNLOAD_HOST` | `https://npmmirror.com/mirrors/playwright/` |
| Electron | `ELECTRON_MIRROR` | `https://npmmirror.com/mirrors/electron/` |
| Puppeteer | `PUPPETEER_DOWNLOAD_HOST` | `https://npmmirror.com/mirrors` |
| Chromedriver | `CHROMEDRIVER_CDNURL` | `https://npmmirror.com/mirrors/chromedriver` |
| node-sass | `SASS_BINARY_SITE` | `https://npmmirror.com/mirrors/node-sass` |

### 5.16 通用代理（任意 HTTPS URL）

适用于不在上述 15 个品类中的任意 HTTPS 文件下载。

| 优先级 | 代理 | URL 模板 |
|--------|------|---------|
| 1 | gh-proxy.com | `https://gh-proxy.com/{ORIGINAL_URL}` |
| 2 | ghproxy.net | `https://ghproxy.net/{ORIGINAL_URL}` |
| 3 | ghp.ci | `https://ghp.ci/{ORIGINAL_URL}` |

```bash
# 一行兜底
curl -fsSL --max-time 30 "$URL" 2>/dev/null \
  || curl -fsSL --max-time 60 "https://gh-proxy.com/$URL" 2>/dev/null \
  || curl -fsSL --max-time 60 "https://ghproxy.net/$URL"
```

---

## 六、GitHub 后备策略（分层加速）

GitHub 是最容易出问题的源，本技能采用三层加速策略：

### 层级 1：镜像 clone（首选）
```
gitclone.com → ghproxy.net → 直连
```

### 层级 2：大仓库浅克隆优化
```bash
# 仅最新提交
git clone --depth 1 https://github.com/USER/REPO.git

# Blobless 克隆（无文件内容，按需拉取）
git clone --filter=blob:none https://github.com/USER/REPO.git

# 组合拳（超大仓库终极加速）
git clone --depth 1 --filter=blob:none --single-branch https://github.com/USER/REPO.git
```

### 层级 3：已知可直连域名（Azure CDN，不走 GFW）
以下 GitHub 相关域名通常可直连，不自动走镜像：
- `githubassets.com` — 静态资源
- `api.github.com` — API 请求
- `objects.githubusercontent.com` — LFS 存储

### 层级 4：通用代理回退
以上均失败时，走通用 HTTPS 代理层：
```
ghproxy.net → ghp.ci → gh-proxy.com（间歇可用）
```

---

## 七、故障排查流程

```
问题: 下载超时 / 连接失败 / 极慢
  │
  ├─ 1. 判断故障类型
  │     ├─ DNS 解析失败？ → 切换 DNS 到 114.114.114.114 或 223.5.5.5
  │     ├─ MTU 黑洞（部分 ISP PMTUD 问题）？ → 降低 MTU 到 1400
  │     └─ GFW RST / 连接拒绝？ → 走镜像加速
  │
  ├─ 2. 运行健康检查
  │     bash ~/your-agent/skills/general-mirror-acceleration/scripts/mirror_health_check.sh
  │     → 查看哪些镜像当前可达
  │
  ├─ 3. 尝试首选镜像
  │     ├─ 成功 → 完成
  │     └─ 失败 ↓
  │
  ├─ 4. 尝试备用镜像（按优先级遍历）
  │     ├─ 成功 → 完成
  │     └─ 失败 ↓
  │
  ├─ 5. 走 HTTP_PROXY（Clash/V2Ray/系统代理）
  │     export http_proxy=http://127.0.0.1:7890
  │     export https_proxy=http://127.0.0.1:7890
  │     ├─ 成功 → 完成
  │     └─ 失败 ↓
  │
  ├─ 6. 网络层排查
  │     ├─ 移动热点切换网络环境测试
  │     ├─ 检查防火墙/VPN 规则
  │     └─ ifconfig / ip addr 检查网卡状态
  │
  └─ 7. 全部失败
        → 等待网络恢复
        → 报告具体品类 + 错误信息，以便进一步诊断
```

### DNS 快速切换

| DNS 服务 | 运营商 | IP |
|---------|--------|-----|
| 114DNS | 114 | `114.114.114.114` |
| 阿里 DoH | 阿里云 | `223.5.5.5` |
| DNSPod | 腾讯 | `119.29.29.29` |
| 百度 | 百度 | `180.76.76.76` |

```bash
# Linux (systemd-resolved)
sudo resolvectl dns eth0 114.114.114.114 223.5.5.5

# 直接改 /etc/resolv.conf
echo -e "nameserver 114.114.114.114\nnameserver 223.5.5.5" | sudo tee /etc/resolv.conf
```

### MTU 调优

```bash
# 临时降低 MTU（解决 PMTUD 黑洞）
sudo ifconfig eth0 mtu 1400
# 恢复默认
sudo ifconfig eth0 mtu 1500
```

---

## 八、与 `git-clone-accelerator` 的关系

| 维度 | git-clone-accelerator（旧） | general-mirror-acceleration（新） |
|------|--------------------------|----------------------------------|
| 覆盖范围 | 仅 GitHub clone | 16 品类全链路 |
| 脚本数量 | 1 个 shell | 3 个 shell（引擎 + 检测 + 配置） |
| 品类感知 | 无 | URL 域名自动识别品类 |
| 健康检测 | 无 | 16 品类批量连通性 + 延迟测试 |
| 系统配置 | 无 | 一键全家桶镜像配置 |
| HugoFace | ❌ | ✅ 自动切换 hf-mirror.com |
| PyPI/npm/Go | ❌ | ✅ 速查 + 自动切换 |
| Docker | ❌ | ✅ Docker Hub 镜像加速 |
| 通用代理 | ❌ | ✅ 任意 HTTPS URL 代理回退 |
| 故障排查 | 无 | 完整 DNS/MTU/代理排查流程 |

**迁移指南**：`general-mirror-acceleration` 是 `git-clone-accelerator` 的全面升级替代品。旧脚本中的 GitHub clone 逻辑已整合到 `mirror_fetch.sh` 中，旧技能目录可安全删除。

---

## 九、关键坑（v3.0）

⚠️ **APT 路径陷阱（v1.0 P0 Bug，v3.0 已修复）** — `MIRRORS_APT` 只存域名不存完整路径，需在 `configure_apt()` 中追加 `/ubuntu/` 或 `/debian/`。修复方案：`best_url="${best_url}/${distro}"`。

⚠️ **并行探测 + `set -e` 的交互** — `wait` 等待的子进程返回非零时，如果不在 `|| true` 包裹中会触发 `set -e` 退出。`parallel_rank_urls()` 中的 `wait "$pid" 2>/dev/null || true` 是关键。

⚠️ **延迟缓存 TTL** — 300秒内复用，跨品类独立。`--no-cache` 可强制跳过缓存重新探测。

⚠️ **Git 品类 HTTP 探测陷阱** — `probe_mirror_health()` 对 git clone URL 做 HTTP HEAD 必定失败。v3.0 通过 `probe_method()` 返回值跳过。

⚠️ **速查表优先级必须来自实测数据，不能照搬参考模板**

⚠️ **`set -euo pipefail` 下 grep 返回非零会直接崩脚本** — `remote_version=$(grep ... || true)` 必须加 `|| true` 兜底。

⚠️ **`--update` 内容校验** — 下载的文件必须校验是否包含 `declare` 或 `VERSION` 关键字。

## 十、红线（必须遵守，v3.0 更新）

1. **自动触发，禁止跳过** — 任何下载/安装/pull/clone 操作遇到超时或极慢时，必须自动加载本技能。
2. **不要手动拼镜像 URL** — 所有镜像 URL 由 `mirrors_config.sh` 统一管理。
3. **并行探测优先** — v3.0 默认并行探测所有镜像，按实测延迟排序。不要假定某个镜像一定最快。
4. **优先使用缓存** — 5 分钟内相同品类的延迟数据走缓存，避免重复探测。`--no-cache` 仅调试用。
5. **Git 品类不跑 HTTP 探测** — `github-clone` / `homebrew-*` / `cocoapods` 品类直接用 git 操作，跳过 HTTP 健康预检。
6. **APT 非破坏性配置** — 只用 `sed` 替换域名，不覆盖整个 `sources.list`。
7. **失败必须上报** — 所有镜像均失败时输出明确错误信息并建议运行 `mirror_health_check.sh`。
8. **安全优先** — 安全场景优先使用官方源或高校/大厂镜像。
9. **不要一揽子全改** — 按域名精细化配置。

---

## 十一、常见问题（FAQ）

### Q1：某个镜像突然不可用了怎么办？

有以下三种方案，按推荐顺序排列：

1. **健康检测 + 手动替换** — 先运行 `mirror_health_check.sh` 确认哪些镜像已失效，然后编辑 `mirrors_config.sh`，将失效镜像替换为检测到可用的镜像。
2. **自定义镜像** — 在 `~/.mirrors_custom.sh` 中添加自定义镜像配置，该文件的优先级最高，会覆盖默认 `mirrors_config.sh` 中的设置。
3. **拉取最新列表** — 运行 `mirror_health_check.sh --update` 从远程拉取最新的镜像 URL 列表，无需手动编辑。

### Q2：需要 sudo 权限吗？

视具体脚本而定：

- **`setup_system_mirrors.sh`** — 涉及系统级配置修改（如 APT 源、Docker daemon.json）时需要 sudo，仅配置用户级工具（如 pip、npm、cargo）时不需要。
- **`mirror_fetch.sh`** — 完全不需要 sudo，仅做 HTTP 下载和 git clone 操作。
- **`mirror_health_check.sh`** — 不需要 sudo，仅做 HTTP 连通性探测。

### Q3：和代理/VPN 能共存吗？

可以。`mirror_fetch.sh` 的策略是"优先直达"：

- 先探测官方源是否可达且延迟正常
- 官方源可达 → 直接使用官方源（不走代理，也不走镜像）
- 官方源不可达 → 自动回退到国内镜像
- 如果你同时开着代理/VPN，官方源大概率可达，脚本会直接走代理通道

这意味着代理和镜像加速不会产生冲突：网络通畅时优先用代理（直连），网络受限时自动走镜像。

### Q4：Docker 镜像加速和 Docker Desktop 冲突吗？

不冲突。`setup_system_mirrors.sh` 配置的是 Docker 守护进程的 `daemon.json` 中的 `registry-mirrors` 字段，这是 Docker 原生的镜像加速机制。无论你使用的是 Docker Desktop、Docker Engine 还是其他 Docker 发行版，只要它们读取 `/etc/docker/daemon.json`（或对应的配置文件路径），该配置就能生效，不会与 Docker Desktop 的任何功能产生冲突。

### Q5：为什么镜像下载的内容和官方不一致？

镜像源采用定期同步机制，可能存在数分钟到数小时的同步延迟。对于安全敏感场景（如生产环境部署、密钥下载），建议：

1. 使用高校/大厂镜像（清华 TUNA、阿里云、中科大），这些源同步频率高、延迟低
2. 下载后校验文件的 SHA256/MD5 摘要，与官方公布的签名对比
3. 发布/部署关键组件时，尽量使用官方源或通过 VPN/代理直连

### Q6：如何添加自己常用的镜像源？

在用户主目录下创建 `~/.mirrors_custom.sh` 文件，按照与 `mirrors_config.sh` 相同的格式定义镜像。该文件由脚本自动加载，且优先级高于默认配置。示例格式：

```bash
# ~/.mirrors_custom.sh
GITHUB_CLONE_MIRRORS=(
  "https://my-mirror.example.com/github.com/{USER}/{REPO}.git|我的私有镜像"
)
```

添加后无需重启，所有脚本自动加载该文件。
