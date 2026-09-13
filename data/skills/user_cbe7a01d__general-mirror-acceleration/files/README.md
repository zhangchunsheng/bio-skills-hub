# general-mirror-acceleration

> **📦 技能摘要**
>
> 中国开发者通用镜像加速工具 — 覆盖 GitHub / HuggingFace / PyPI / npm / Docker / Go / Rust / Homebrew / Maven / Conda / APT / RubyGems / CocoaPods / Flutter / Chromium 等 16 大品类的全链路镜像加速方案。
>
> **核心能力：**
> - **智能下载引擎** — 并行探测所有镜像延迟，按实测速度排序，自动选择最快源
> - **延迟缓存** — 5 分钟内复用探测结果，重复下载秒级响应
> - **一键系统配置** — 自动检测已安装工具（pip/npm/go/cargo/apt/docker/maven/conda/gem），探测最快镜像并写入配置
> - **全品类健康检测** — 从配置中心动态生成 30+ 品类连通性报告
> - **Git/HTTP 自适应探测** — 对 git clone 品类自动跳过 HTTP 探测，避免无效等待
>
> **适用场景：** 在中国大陆网络环境下，任何下载/安装/pull/clone 操作遇到超时、连接失败、速度极慢时自动介入。
>
> **亮点：** 零 Python 依赖，纯 Bash 实现；并行探测 + 延迟缓存；非破坏性系统配置（sed 替换 + 自动备份 + 失败回滚）；16 大品类全覆盖。

## 安装与使用

### Linux / macOS (bash)

```bash
# 解压
unzip general-mirror-acceleration-v3.0.0.zip -d general-mirror-acceleration
cd general-mirror-acceleration

# 无依赖，直接使用！
# 智能下载
bash scripts/mirror_fetch.sh https://github.com/user/repo.git

# 健康检测
bash scripts/mirror_health_check.sh

# 一键配置系统镜像
bash scripts/setup_system_mirrors.sh all
```

### Windows (PowerShell)

```powershell
# 解压
Expand-Archive -Path general-mirror-acceleration-v3.0.0.zip -DestinationPath general-mirror-acceleration
cd general-mirror-acceleration

# (需要 Git Bash 或 WSL 运行 .sh 脚本)
# 在 Git Bash 中:
bash scripts/mirror_fetch.sh https://github.com/user/repo.git
bash scripts/mirror_health_check.sh
```

## 文件结构

```
general-mirror-acceleration/
├── SKILL.md                      # 完整文档
├── README.md                     # 本文件
└── scripts/
    ├── mirror_fetch.sh           # ★ 主引擎 — 并行探测 + 延迟缓存
    ├── mirror_health_check.sh    # 动态健康检测
    ├── setup_system_mirrors.sh   # 一键系统配置（9 工具）
    └── mirrors_config.sh         # 配置中心（30+ 品类）
```

## 依赖

- **必需**: bash ≥4.2, curl, git
- **可选**: python3 (Docker daemon.json 操作), docker, npm, go, cargo, apt-get, gem, conda, mvn (对应工具的一键配置)
