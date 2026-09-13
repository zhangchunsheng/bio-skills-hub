#!/bin/bash
# ============================================================
# mirror_health_check.sh v2.0 — 动态品类连通性+延迟测试
# 从 mirrors_config.sh 自动读取全部品类，不再硬编码
# 用法: bash mirror_health_check.sh [category|--update]
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/mirrors_config.sh"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# ============================================================
# 更新功能: --update / -u 标志
# ============================================================
do_update() {
    local remote_urls=(
        "https://raw.githubusercontent.com/pararadise93-dot/pararadise-skills/main/general-mirror-acceleration/scripts/mirrors_config.sh"
        "https://gh-proxy.com/https://raw.githubusercontent.com/pararadise93-dot/pararadise-skills/main/general-mirror-acceleration/scripts/mirrors_config.sh"
        "https://mirror.ghproxy.com/https://raw.githubusercontent.com/pararadise93-dot/pararadise-skills/main/general-mirror-acceleration/scripts/mirrors_config.sh"
        "https://raw.gitmirror.com/pararadise93-dot/pararadise-skills/main/general-mirror-acceleration/scripts/mirrors_config.sh"
    )
    local tmp_file="/tmp/mirrors_config_latest.sh"
    local local_file="$HOME/your-agent/skills/general-mirror-acceleration/scripts/mirrors_config.sh"

    echo -e "${CYAN}正在检查 mirrors_config.sh 更新...${NC}"

    local downloaded=false
    for url in "${remote_urls[@]}"; do
        echo -e "  尝试: ${url}" >&2
        if curl -sL --max-time 15 -o "$tmp_file" "$url" && [[ -s "$tmp_file" ]]; then
            if grep -qE '(declare|VERSION)' "$tmp_file" 2>/dev/null; then
                downloaded=true
                break
            else
                echo -e "  ${YELLOW}内容校验不通过，尝试下一个源${NC}" >&2
                rm -f "$tmp_file"
            fi
        else
            echo -e "  ${YELLOW}不可达，尝试下一个源${NC}" >&2
            rm -f "$tmp_file"
        fi
    done

    if [[ "$downloaded" != true ]] || [[ ! -s "$tmp_file" ]]; then
        echo -e "${YELLOW}所有更新源均不可达，保留当前配置${NC}"
        rm -f "$tmp_file"
        exit 0
    fi

    local remote_version local_version
    remote_version=$(grep -oP '^VERSION="[^"]*"' "$tmp_file" 2>/dev/null | head -1 | grep -oP '"[^"]*"' | tr -d '"' || true)
    local_version=$(grep -oP '^VERSION="[^"]*"' "$local_file" 2>/dev/null | head -1 | grep -oP '"[^"]*"' | tr -d '"' || true)

    if [[ -z "$remote_version" ]]; then
        echo -e "${YELLOW}无法获取远程版本信息，更新失败，保留当前配置${NC}"
        rm -f "$tmp_file"
        exit 0
    fi

    if [[ -z "$local_version" ]]; then
        echo -e "${YELLOW}本地配置无版本信息，将直接更新${NC}"
    fi

    if [[ -z "$local_version" ]] || [[ "$remote_version" > "$local_version" ]]; then
        cp "$local_file" "${local_file}.bak"
        echo -e "${GREEN}发现新版本: ${remote_version} (当前: ${local_version:-无})${NC}"
        echo ""
        echo -e "${CYAN}变更摘要:${NC}"
        diff --unified=3 "${local_file}.bak" "$tmp_file" 2>/dev/null | head -50 || echo "  (无法生成差异)"
        echo ""
        mv "$tmp_file" "$local_file"
        echo -e "${GREEN}✓ 已更新到版本 ${remote_version} (旧配置备份为 ${local_file}.bak)${NC}"
    else
        echo -e "${GREEN}已是最新版本 (${local_version})${NC}"
        rm -f "$tmp_file"
    fi
}

TIMEOUT=10
PASS=0; FAIL=0; SKIP=0

check() {
    local name="$1" url="$2" method="${3:-HEAD}"
    local start=$(date +%s%3N)
    local code
    if [ "$method" = "HEAD" ]; then
        code=$(curl -sI -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "000")
    else
        code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "000")
    fi
    local end=$(date +%s%3N)
    local latency=$((end - start))

    if [ "$code" = "000" ] || [ "$code" = "502" ] || [ "$code" = "503" ] || [ "$code" = "504" ]; then
        echo -e "  ${RED}✗${NC} $name → ${RED}不可达${NC} (${latency}ms)"
        FAIL=$((FAIL + 1))
    elif [ "$code" -ge 400 ]; then
        echo -e "  ${YELLOW}△${NC} $name → HTTP $code (${latency}ms)"
        PASS=$((PASS + 1))
    else
        echo -e "  ${GREEN}✓${NC} $name → HTTP $code (${latency}ms)"
        PASS=$((PASS + 1))
    fi
}

git_lsremote() {
    local name="$1" url="$2"
    local start=$(date +%s%3N)
    local out
    # 用一个小而稳定的测试仓库 probe git clone 镜像
    local test_url="$url"
    # 如果URL包含{user}/{repo}模板，替换为测试仓库
    if echo "$test_url" | grep -q '{user}'; then
        test_url="${test_url//\{user\}/sindresorhus}"
        test_url="${test_url//\{repo\}/awesome}"
        test_url="${test_url//\{branch\}/main}"
        test_url="${test_url//\{path\}/readme.md}"
        test_url="${test_url//\{tag\}/v1.0}"
        test_url="${test_url//\{file\}/test}"
        test_url="${test_url//\{ref\}/main}"
    fi
    out=$(timeout $TIMEOUT git ls-remote --heads "$test_url" HEAD 2>/dev/null || echo "")
    local end=$(date +%s%3N)
    local latency=$((end - start))
    if [ -n "$out" ]; then
        echo -e "  ${GREEN}✓${NC} $name → OK (${latency}ms)"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗${NC} $name → ${RED}不可达${NC} (${latency}ms)"
        FAIL=$((FAIL + 1))
    fi
}

section() {
    echo ""
    echo -e "${CYAN}━━━ $1 ━━━${NC}"
}

# ============================================================
# 动态品类分组显示名
# ============================================================
category_group() {
    case "$1" in
        github-*)      echo "GitHub" ;;
        huggingface)   echo "HuggingFace" ;;
        pypi)          echo "PyPI / pip" ;;
        npm)           echo "npm / Node.js" ;;
        docker-*)      echo "Docker Registry" ;;
        go)            echo "Go Modules" ;;
        rust)          echo "Rust / Cargo" ;;
        apt)           echo "APT (Ubuntu/Debian)" ;;
        conda*)        echo "Conda / Anaconda" ;;
        maven*)        echo "Maven / Gradle" ;;
        rubygems)      echo "Ruby / RubyGems" ;;
        chromium|playwright|electron|puppeteer) echo "Chromium / Electron / Playwright" ;;
        flutter-*)     echo "Flutter / Dart" ;;
        homebrew-*)    echo "Homebrew (macOS)" ;;
        cocoapods)     echo "CocoaPods (macOS/iOS)" ;;
        https-proxy)   echo "通用HTTPS代理" ;;
        *)             echo "$1" ;;
    esac
}

# ============================================================
# 参数解析
# ============================================================
if [[ "${1:-}" == "--update" ]] || [[ "${1:-}" == "-u" ]]; then
    do_update
    exit 0
fi

# ============================================================
echo -e "${CYAN}╔══════════════════════════════════════════╗"
echo -e "║  全镜像加速 — 动态连通性测试 v2.0       ║"
echo -e "║  $(date '+%Y-%m-%d %H:%M:%S')                    ║"
echo -e "║  数据源: mirrors_config.sh v${VERSION}     ║"
echo -e "╚══════════════════════════════════════════╝${NC}"

# 如果指定了单个品类
if [ $# -ge 1 ] && [ "${1:-}" != "--all" ] && [ "${1:-}" != "-a" ]; then
    target_category="$1"
    # 品类别名映射
    case "$target_category" in
        github) target_category="github-clone" ;;
        docker) target_category="docker-hub" ;;
        brew|homebrew) target_category="homebrew-core" ;;
        flutter) target_category="flutter-pub" ;;
        conda-forge) target_category="conda-forge" ;;
    esac

    section "$(category_group "$target_category")"
    method=$(probe_method "$target_category" 2>/dev/null || echo "http")
    i=1
    while IFS= read -r url; do
        [ -z "$url" ] && continue
        label="${target_category}-${i}"
        if [ "$method" = "git" ]; then
            git_lsremote "$label" "$url"
        else
            check "$label" "$url" HEAD
        fi
        i=$((i + 1))
    done < <(get_mirrors "$target_category" 2>/dev/null || true)

    echo ""
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    TOTAL=$((PASS + FAIL + SKIP))
    echo -e "  通过: ${GREEN}$PASS${NC}  失败: ${RED}$FAIL${NC}  总计: $TOTAL"
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    exit 0
fi

# ============================================================
# 全品类检测（默认）
# ============================================================
# 按组聚合：同一 group 的品类合并显示
declare -A seen_groups=()

while IFS= read -r category; do
    [ -z "$category" ] && continue
    group=$(category_group "$category")

    if [ -z "${seen_groups[$group]:-}" ]; then
        seen_groups[$group]=1
        section "$group"
    fi

    method=$(probe_method "$category" 2>/dev/null || echo "http")
    i=1
    while IFS= read -r url; do
        [ -z "$url" ] && continue
        label="${category}"
        [ $i -gt 1 ] && label="${label}-${i}"
        if [ "$method" = "git" ]; then
            git_lsremote "$label" "$url"
        else
            check "$label" "$url" HEAD
        fi
        i=$((i + 1))
    done < <(get_mirrors "$category" 2>/dev/null || true)
done < <(get_all_categories)

# ─── 总结 ───
echo ""
echo -e "${CYAN}════════════════════════════════════════════${NC}"
TOTAL=$((PASS + FAIL + SKIP))
echo -e "  通过: ${GREEN}$PASS${NC}  失败: ${RED}$FAIL${NC}  跳过: ${YELLOW}$SKIP${NC}  总计: $TOTAL"
if [ $FAIL -eq 0 ]; then
    echo -e "  ${GREEN}✓ 所有镜像连通性正常${NC}"
else
    echo -e "  ${RED}✗ $FAIL 个镜像不可达${NC}"
fi
echo -e "${CYAN}════════════════════════════════════════════${NC}"
