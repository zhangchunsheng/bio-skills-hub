#!/bin/bash
# ============================================================
# setup_system_mirrors.sh — 一键配置系统镜像源
#
# 自动检测已安装工具，探测最快镜像并配置。
# 所有操作先备份原配置（.bak），输出变更摘要。
#
# 用法:
#   bash setup_system_mirrors.sh              # 交互式: 列出工具, 选择配置
#   bash setup_system_mirrors.sh all          # 配置所有已安装工具
#   bash setup_system_mirrors.sh pypi         # 仅配置 PyPI
#   bash setup_system_mirrors.sh npm          # 仅配置 npm
#   bash setup_system_mirrors.sh go           # 仅配置 Go
#   bash setup_system_mirrors.sh cargo|rust   # 仅配置 Cargo
#   bash setup_system_mirrors.sh apt          # 仅配置 APT (需 sudo)
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/mirrors_config.sh"

# ─── 颜色 ───
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ─── 状态跟踪 ───
declare -a CHANGES=()
CHANGE_COUNT=0
SKIP_COUNT=0
FAIL_COUNT=0

# ─── 日志 ───
log_info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}   $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err()   { echo -e "${RED}[ERR]${NC}  $*"; }
log_step()  { echo -e "${BOLD}[>>]${NC}  $*"; }

# ─── 备份 ───
backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        local bak="${file}.bak.$(date +%Y%m%d_%H%M%S)"
        cp "$file" "$bak"
        log_info "已备份: $bak"
    else
        log_info "新建配置 (无需备份): $file"
    fi
}

# ─── HTTP 探测 ───
probe_url() {
    local url="$1" timeout="${2:-2}"
    local code latency
    local start
    start=$(date +%s%3N 2>/dev/null || echo 0)
    code=$(curl -sI -o /dev/null -w "%{http_code}" --max-time "$timeout" "$url" 2>/dev/null || echo "000")
    local end
    end=$(date +%s%3N 2>/dev/null || echo 0)
    latency=$((end - start))
    if [ "$code" = "000" ] || [ "$code" -ge 500 ]; then
        echo "unreachable"
        return 1
    fi
    echo "$latency"
    return 0
}

# ─── 从品类镜像列表中选择最快的 ───
select_best_mirror() {
    local category="$1"
    local best_url="" best_label=""
    local best_latency=99999
    local mirrors=()

    while IFS= read -r url; do
        [ -n "$url" ] && mirrors+=("$url")
    done < <(get_mirrors "$category" 2>/dev/null || true)

    for mirror_url in "${mirrors[@]}"; do
        local latency
        latency=$(probe_url "$mirror_url" 2 2>/dev/null || echo "unreachable")
        if [ "$latency" != "unreachable" ] && [ "$latency" -lt "$best_latency" ] 2>/dev/null; then
            best_latency="$latency"
            best_url="$mirror_url"
            best_label="$mirror_url"
        fi
    done

    if [ -z "$best_url" ]; then
        echo ""
        return 1
    fi
    echo "${best_label}|${best_url}|${best_latency}"
    return 0
}

# ═══════════════════════════════════════════════════════════
# 检测已安装工具
# ═══════════════════════════════════════════════════════════
detect_tools() {
    local tools=()
    if command -v pip3 &>/dev/null || command -v pip &>/dev/null; then tools+=("pypi"); fi
    if command -v npm &>/dev/null; then tools+=("npm"); fi
    if command -v go &>/dev/null; then tools+=("go"); fi
    if command -v cargo &>/dev/null; then tools+=("rust"); fi
    if command -v apt-get &>/dev/null; then tools+=("apt"); fi
    if command -v docker &>/dev/null; then tools+=("docker"); fi
    if command -v mvn &>/dev/null || [ -f "$HOME/.m2/settings.xml" ]; then tools+=("maven"); fi
    if command -v conda &>/dev/null || [ -f "$HOME/.condarc" ]; then tools+=("conda"); fi
    if command -v gem &>/dev/null; then tools+=("rubygems"); fi
    printf '%s\n' "${tools[@]}"
}

tool_label() {
    case "$1" in
        pypi)     echo "PyPI (pip)" ;;
        npm)      echo "npm (Node.js)" ;;
        go)       echo "Go Modules" ;;
        rust)     echo "Rust / Cargo" ;;
        apt)      echo "APT (系统包)" ;;
        docker)   echo "Docker 镜像加速" ;;
        maven)    echo "Maven / Gradle" ;;
        conda)    echo "Conda / Anaconda" ;;
        rubygems) echo "RubyGems" ;;
        *)        echo "$1" ;;
    esac
}

# ═══════════════════════════════════════════════════════════
# PyPI 配置
# ═══════════════════════════════════════════════════════════
configure_pypi() {
    echo ""
    echo -e "${CYAN}━━━ 配置 PyPI / pip ━━━${NC}"

    local best
    best=$(select_best_mirror "pypi" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 PyPI 镜像!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    local pip_config="$HOME/.pip/pip.conf"
    [ -f "$pip_config" ] && backup_file "$pip_config"

    local host
    host=$(echo "$best_url" | awk -F/ '{print $3}')

    mkdir -p "$HOME/.pip"
    if [ -f "$pip_config" ] && grep -q 'index-url' "$pip_config" 2>/dev/null; then
        sed -i "s|index-url.*|index-url = ${best_url}|" "$pip_config"
    else
        cat > "$pip_config" << EOF
[global]
index-url = ${best_url}
trusted-host = ${host}
EOF
    fi

    log_ok "PyPI → $best_url"
    CHANGES+=("pypi → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# npm 配置
# ═══════════════════════════════════════════════════════════
configure_npm() {
    echo ""
    echo -e "${CYAN}━━━ 配置 npm ━━━${NC}"

    if ! command -v npm &>/dev/null; then
        log_warn "npm 未安装"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local best
    best=$(select_best_mirror "npm" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 npm 镜像!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    local current
    current=$(npm config get registry 2>/dev/null || echo "")
    if [ "$current" = "$best_url" ]; then
        log_info "已是该镜像，跳过"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local npmrc="$HOME/.npmrc"
    [ -f "$npmrc" ] && backup_file "$npmrc"

    npm config set registry "$best_url" 2>&1
    log_ok "npm → $best_url"
    CHANGES+=("npm → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# Go 配置
# ═══════════════════════════════════════════════════════════
configure_go() {
    echo ""
    echo -e "${CYAN}━━━ 配置 Go Modules ━━━${NC}"

    if ! command -v go &>/dev/null; then
        log_warn "go 未安装"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local best
    best=$(select_best_mirror "go" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 Go proxy!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    local current
    current=$(go env GOPROXY 2>/dev/null || echo "")
    if [ "$current" = "$best_url" ]; then
        log_info "已是该镜像，跳过"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local go_env="$HOME/.go/env"
    [ -f "$go_env" ] && backup_file "$go_env"

    # 如果镜像 URL 已带 ,direct 后缀则不重复追加
    if echo "$best_url" | grep -q ',direct$'; then
        go env -w GOPROXY="$best_url" 2>&1
    else
        go env -w GOPROXY="${best_url},direct" 2>&1
    fi
    log_ok "Go → $best_url"
    CHANGES+=("go → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# Cargo / Rust 配置
# ═══════════════════════════════════════════════════════════
configure_rust() {
    echo ""
    echo -e "${CYAN}━━━ 配置 Rust / Cargo ━━━${NC}"

    if ! command -v cargo &>/dev/null; then
        log_warn "cargo 未安装"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local best
    best=$(select_best_mirror "rust" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 Cargo 镜像!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    local cargo_config="$HOME/.cargo/config.toml"
    [ -f "$cargo_config" ] && backup_file "$cargo_config"

    mkdir -p "$HOME/.cargo"

    # 检查是否已有 sparse 协议配置（新版 cargo），兼容两种格式
    if echo "$best_url" | grep -q 'sparse+'; then
        # Sparse registry
        cat > "$cargo_config" << EOF
[registries.crates-io]
protocol = "sparse"
index = "${best_url}"
EOF
    elif echo "$best_url" | grep -q 'crates.io-index'; then
        # Git-based registry (旧)
        cat > "$cargo_config" << EOF
[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "${best_url}"
EOF
    else
        # 直接 URL 格式，保持原样
        if [ -f "$cargo_config" ] && grep -q 'replace-with' "$cargo_config" 2>/dev/null; then
            sed -i "s|registry = .*|registry = \"${best_url}\"|" "$cargo_config"
        else
            cat >> "$cargo_config" << EOF

[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "${best_url}"
EOF
        fi
    fi

    log_ok "Cargo → $best_url"
    CHANGES+=("rust → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# APT 配置 — 非破坏性：sed替换域名，保留用户自定义源
# ═══════════════════════════════════════════════════════════
configure_apt() {
    echo ""
    echo -e "${CYAN}━━━ 配置 APT ━━━${NC}"

    if ! command -v apt-get &>/dev/null; then
        log_warn "apt-get 不可用 (非 Debian/Ubuntu?)"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    if [ "$(id -u)" -ne 0 ]; then
        log_warn "需要 root。请执行: sudo bash $0 apt"
        SKIP_COUNT=$((SKIP_COUNT + 1))
        return
    fi

    local best
    best=$(select_best_mirror "apt" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 APT 镜像!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    # 探测时使用 dists 子路径 → 配置时补回 /ubuntu/ 或 /debian/
    local distro
    distro=$(lsb_release -is 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "")
    [ -z "$distro" ] && distro="ubuntu"
    best_url="${best_url}/${distro}"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    local sources_file="/etc/apt/sources.list"
    if [ ! -f "$sources_file" ]; then
        log_err "找不到 $sources_file"; FAIL_COUNT=$((FAIL_COUNT + 1)); return
    fi

    # 备份
    backup_file "$sources_file"

    # 非破坏性替换：仅替换官方域名，保留自定义 PPA/第三方源
    local changed=false
    local official_domains=(
        "http://archive.ubuntu.com"
        "https://archive.ubuntu.com"
        "http://security.ubuntu.com"
        "https://security.ubuntu.com"
        "http://deb.debian.org"
        "https://deb.debian.org"
        "http://security.debian.org"
        "https://security.debian.org"
    )

    for domain in "${official_domains[@]}"; do
        if grep -qF "$domain" "$sources_file" 2>/dev/null; then
            sed -i "s|${domain}|${best_url}|g" "$sources_file"
            changed=true
        fi
    done

    if ! $changed; then
        log_warn "未在 sources.list 中找到官方域名，跳过"
        SKIP_COUNT=$((SKIP_COUNT + 1))
        return
    fi

    log_ok "APT → $best_url (非破坏性替换)"

    log_step "运行 apt-get update..."
    if apt-get update -qq 2>&1; then
        log_ok "apt-get update 成功"
    else
        log_err "apt-get update 失败，回滚配置"
        # 恢复最近的备份
        local latest_bak
        latest_bak=$(ls -t "${sources_file}.bak."* 2>/dev/null | head -1)
        if [ -n "$latest_bak" ] && [ -f "$latest_bak" ]; then
            cp "$latest_bak" "$sources_file"
            log_info "已回滚到: $latest_bak"
        fi
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi

    CHANGES+=("apt → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# Docker 配置
# ═══════════════════════════════════════════════════════════
configure_docker() {
    echo ""
    echo -e "${CYAN}━━━ 配置 Docker 镜像加速 ━━━${NC}"

    if ! command -v docker &>/dev/null; then
        log_warn "docker 未安装"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local best
    best=$(select_best_mirror "docker-hub" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 Docker 镜像!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    # 读取当前配置
    local daemon_json="/etc/docker/daemon.json"
    local current_mirrors=""
    if [ -f "$daemon_json" ]; then
        current_mirrors=$(python3 -c "import json; print(json.dumps(json.load(open('$daemon_json')).get('registry-mirrors', [])))" 2>/dev/null || echo "[]")
    fi

    # 构建新配置
    if [ "$(id -u)" -ne 0 ]; then
        log_warn "需要 root 权限写入 /etc/docker/daemon.json"
        log_info "建议: sudo mkdir -p /etc/docker && echo '{\"registry-mirrors\": [\"$best_url\"]}' | sudo tee /etc/docker/daemon.json"
        SKIP_COUNT=$((SKIP_COUNT + 1))
        return
    fi

    [ -f "$daemon_json" ] && backup_file "$daemon_json"
    mkdir -p /etc/docker

    python3 -c "
import json, sys
cfg = {}
try:
    cfg = json.load(open('$daemon_json'))
except: pass
cfg['registry-mirrors'] = ['$best_url']
json.dump(cfg, open('$daemon_json', 'w'), indent=2)
print('OK')
" 2>/dev/null || {
        echo "{\"registry-mirrors\": [\"$best_url\"]}" > "$daemon_json"
    }

    log_ok "Docker → $best_url"
    log_info "需要重启 Docker: sudo systemctl restart docker"
    CHANGES+=("docker → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# Maven 配置
# ═══════════════════════════════════════════════════════════
configure_maven() {
    echo ""
    echo -e "${CYAN}━━━ 配置 Maven ━━━${NC}"

    local best
    best=$(select_best_mirror "maven" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 Maven 镜像!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    local m2_dir="$HOME/.m2"
    local settings_file="$m2_dir/settings.xml"
    mkdir -p "$m2_dir"

    [ -f "$settings_file" ] && backup_file "$settings_file"

    cat > "$settings_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <mirrors>
    <mirror>
      <id>mirror</id>
      <mirrorOf>central</mirrorOf>
      <url>${best_url}</url>
    </mirror>
  </mirrors>
</settings>
EOF

    log_ok "Maven → $best_url"
    CHANGES+=("maven → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# Conda 配置
# ═══════════════════════════════════════════════════════════
configure_conda() {
    echo ""
    echo -e "${CYAN}━━━ 配置 Conda ━━━${NC}"

    if ! command -v conda &>/dev/null && [ ! -f "$HOME/.condarc" ]; then
        log_info "conda 未安装且无 .condarc，跳过"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local best_main
    best_main=$(select_best_mirror "conda" || echo "")
    local best_forge
    best_forge=$(select_best_mirror "conda-forge" || echo "")
    IFS='|' read -r _ main_url main_latency <<< "${best_main:-||}"
    IFS='|' read -r _ forge_url forge_latency <<< "${best_forge:-||}"

    local condarc="$HOME/.condarc"
    [ -f "$condarc" ] && backup_file "$condarc"

    cat > "$condarc" << EOF
default_channels:
  - ${main_url}/pkgs/main
  - ${main_url}/pkgs/r
custom_channels:
  conda-forge: ${forge_url}
  bioconda: ${main_url}/cloud/bioconda
EOF

    log_ok "Conda → $main_url"
    CHANGES+=("conda → $main_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# RubyGems 配置
# ═══════════════════════════════════════════════════════════
configure_rubygems() {
    echo ""
    echo -e "${CYAN}━━━ 配置 RubyGems ━━━${NC}"

    if ! command -v gem &>/dev/null; then
        log_info "gem 未安装，跳过"; SKIP_COUNT=$((SKIP_COUNT + 1)); return
    fi

    local best
    best=$(select_best_mirror "rubygems" || echo "")
    if [ -z "$best" ]; then
        log_err "无可用的 RubyGems 镜像!"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return
    fi
    IFS='|' read -r _ best_url best_latency <<< "$best"

    log_info "最佳镜像: $best_url (${best_latency}ms)"

    gem sources --add "$best_url" 2>/dev/null || true
    gem sources --remove https://rubygems.org 2>/dev/null || true

    if command -v bundle &>/dev/null; then
        bundle config mirror.https://rubygems.org "$best_url" 2>/dev/null || true
    fi

    log_ok "RubyGems → $best_url"
    CHANGES+=("rubygems → $best_url")
    CHANGE_COUNT=$((CHANGE_COUNT + 1))
}

# ═══════════════════════════════════════════════════════════
# 配置调度
# ═══════════════════════════════════════════════════════════
configure_tool() {
    case "$1" in
        pypi)          configure_pypi ;;
        npm)           configure_npm ;;
        go)            configure_go ;;
        rust|cargo)    configure_rust ;;
        apt)           configure_apt ;;
        docker)        configure_docker ;;
        maven|gradle)  configure_maven ;;
        conda)         configure_conda ;;
        rubygems|gem)  configure_rubygems ;;
        *)             log_err "未知工具: $1" ;;
    esac
}

# ═══════════════════════════════════════════════════════════
# 交互模式
# ═══════════════════════════════════════════════════════════
interactive_select() {
    local tools=()
    while IFS= read -r t; do
        [ -n "$t" ] && tools+=("$t")
    done < <(detect_tools)

    if [ ${#tools[@]} -eq 0 ]; then
        log_err "未检测到支持的工具 (pip/npm/go/cargo/apt)"
        log_info "请先安装至少一个工具"
        exit 1
    fi

    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════╗"
    echo -e "║  检测到以下已安装工具:                     ║"
    echo -e "╚════════════════════════════════════════════╝${NC}"
    echo ""

    local i=1
    for t in "${tools[@]}"; do
        echo -e "  ${BOLD}${i}.${NC} $(tool_label "$t")"
        i=$((i + 1))
    done
    echo -e "  ${BOLD}a.${NC} ${BOLD}全部配置${NC}"
    echo -e "  ${BOLD}q.${NC} 退出"
    echo ""

    read -r -p "请选择 [1-${#tools[@]}/a/q]: " choice

    case "$choice" in
        [Qq]) echo "已取消"; exit 0 ;;
        [Aa])
            for t in "${tools[@]}"; do configure_tool "$t"; done
            ;;
        *)
            if [ "$choice" -ge 1 ] 2>/dev/null && [ "$choice" -le "${#tools[@]}" ] 2>/dev/null; then
                configure_tool "${tools[$((choice - 1))]}"
            else
                log_err "无效选择"; exit 1
            fi
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════
# 摘要
# ═══════════════════════════════════════════════════════════
print_summary() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  配置摘要${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}"

    if [ ${#CHANGES[@]} -gt 0 ]; then
        echo ""
        echo -e "  ${GREEN}已变更 (${CHANGE_COUNT}):${NC}"
        for c in "${CHANGES[@]}"; do
            echo -e "    ${GREEN}✓${NC} $c"
        done
    fi

    if [ $SKIP_COUNT -gt 0 ]; then
        echo -e "\n  ${YELLOW}跳过: ${SKIP_COUNT}${NC}"
    fi
    if [ $FAIL_COUNT -gt 0 ]; then
        echo -e "\n  ${RED}失败: ${FAIL_COUNT}${NC}"
    fi

    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"

    if [ $CHANGE_COUNT -gt 0 ]; then
        echo ""
        echo -e "${GREEN}配置完成! 验证命令:${NC}"
        for c in "${CHANGES[@]}"; do
            case "$c" in
                pypi*)     echo "  pip config list" ;;
                npm*)      echo "  npm config get registry" ;;
                go*)       echo "  go env GOPROXY" ;;
                rust*)     echo "  cat ~/.cargo/config.toml" ;;
                apt*)      echo "  cat /etc/apt/sources.list" ;;
                docker*)   echo "  cat /etc/docker/daemon.json" ;;
                maven*)    echo "  cat ~/.m2/settings.xml" ;;
                conda*)    echo "  cat ~/.condarc" ;;
                rubygems*) echo "  gem sources -l" ;;
            esac
        done
        echo ""
        echo -e "  备份文件以 .bak.* 结尾"
    fi
    echo ""
}

# ═══════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════╗"
echo -e "║  setup_system_mirrors.sh                  ║"
echo -e "║  一键配置系统镜像源                        ║"
echo -e "╚════════════════════════════════════════════╝${NC}"

case "${1:-}" in
    ""|interactive|--interactive|-i)
        interactive_select
        ;;
    all|--all|-a)
        declare -a all_tools=()
        while IFS= read -r t; do [ -n "$t" ] && all_tools+=("$t"); done < <(detect_tools)
        for t in "${all_tools[@]}"; do configure_tool "$t"; done
        ;;
    pypi|pip)    configure_pypi ;;
    npm|node)    configure_npm ;;
    go|golang)   configure_go ;;
    cargo|rust)  configure_rust ;;
    apt|ubuntu|debian) configure_apt ;;
    docker)      configure_docker ;;
    maven|gradle) configure_maven ;;
    conda|anaconda) configure_conda ;;
    rubygems|gem) configure_rubygems ;;
    -h|--help|help|usage)
        cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║  setup_system_mirrors.sh — 一键配置系统镜像             ║
║                                                          ║
║  用法: bash setup_system_mirrors.sh [all|pypi|npm|go|cargo|apt|docker|maven|conda|rubygems]
║                                                          ║
║  无参数: 交互式检测 + 选择                               ║
║  all:    配置所有已安装工具                              ║
║                                                          ║
║  安全: 所有操作先备份原配置(.bak)，输出变更摘要           ║
╚══════════════════════════════════════════════════════════╝
EOF
        exit 0
        ;;
    *)
        log_err "未知参数: $1"
        echo "用法: bash setup_system_mirrors.sh [all|pypi|npm|go|cargo|apt|docker|maven|conda|rubygems]"
        exit 1
        ;;
esac

print_summary
