#!/usr/bin/env bash
# =============================================================================
# mirrors_config.sh — 16类镜像配置中心
# =============================================================================
# 纯数据+函数，供其他脚本 source 引用
#
# 功能:
#   1. 定义所有16类镜像的 URL 和优先级列表（关联数组）
#   2. detect_category() — 根据输入 URL 自动识别所属品类
#   3. get_mirrors() — 根据品类/URL 返回按优先级排序的镜像 URL 列表
#   4. convert_url() — 将原始 URL 转换为对应镜像的 URL
#
# 数据来源: 腾讯云服务器实测延迟 / 可达性
# =============================================================================

set -euo pipefail

VERSION="2026-07-05"

# ---------------------------------------------------------------------------
# 1. GitHub 相关镜像
# ---------------------------------------------------------------------------
# gitclone.com: 普通仓库 OK，大仓库可能超时
# ghproxy.net: raw 文件代理
# raw.gitmirror.com: raw 文件镜像
# ghp.ci: 间歇可用
declare -ga MIRRORS_GITHUB_CLONE=(
    "https://gitclone.com/github.com/{user}/{repo}"
    "https://mirror.ghproxy.com/https://github.com/{user}/{repo}.git"
    "https://ghp.ci/https://github.com/{user}/{repo}.git"
    "https://github.com/{user}/{repo}.git"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_GITHUB_RAW=(
    "https://raw.gitmirror.com/{user}/{repo}/{branch}/{path}"
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
    "https://ghp.ci/https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
    "https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_GITHUB_RELEASE=(
    "https://ghp.ci/https://github.com/{user}/{repo}/releases/download/{tag}/{file}"
    "https://mirror.ghproxy.com/https://github.com/{user}/{repo}/releases/download/{tag}/{file}"
    "https://github.com/{user}/{repo}/releases/download/{tag}/{file}"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_GITHUB_ARCHIVE=(
    "https://mirror.ghproxy.com/https://github.com/{user}/{repo}/archive/{ref}.tar.gz"
    "https://ghp.ci/https://github.com/{user}/{repo}/archive/{ref}.tar.gz"
    "https://github.com/{user}/{repo}/archive/{ref}.tar.gz"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 2. HuggingFace 镜像
# ---------------------------------------------------------------------------
# hf-mirror.com (196ms) > hf.xeduapi.com
declare -ga MIRRORS_HUGGINGFACE=(
    "https://hf-mirror.com"
    "https://huggingface.co"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 3. PyPI 镜像
# ---------------------------------------------------------------------------
# 中科大(82ms) > 阿里(108ms) > 清华(118ms) > 豆瓣(不可达) > 华为(429限流)
declare -ga MIRRORS_PYPI=(
    "https://mirrors.ustc.edu.cn/pypi/simple"
    "https://mirrors.aliyun.com/pypi/simple"
    "https://pypi.tuna.tsinghua.edu.cn/simple"
    "https://pypi.org/simple"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 4. npm 镜像
# ---------------------------------------------------------------------------
# npmmirror.com(91ms) > 清华(404)
declare -ga MIRRORS_NPM=(
    "https://registry.npmmirror.com"
    "https://registry.npmjs.org"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 5. Docker 镜像
# ---------------------------------------------------------------------------
# docker.1ms.run > docker.xuanyuan.me
declare -ga MIRRORS_DOCKER_HUB=(
    "https://docker.1ms.run"
    "https://docker.xuanyuan.me"
    "https://registry-1.docker.io"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_DOCKER_GHCR=(
    "https://ghcr.io"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_DOCKER_GCR=(
    "https://gcr.io"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_DOCKER_QUAY=(
    "https://quay.io"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 6. Go 模块代理
# ---------------------------------------------------------------------------
# goproxy.cn(52ms) > 阿里(404不可用)
declare -ga MIRRORS_GO=(
    "https://goproxy.cn,direct"
    "https://proxy.golang.org,direct"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 7. Rust (crates.io) 镜像
# ---------------------------------------------------------------------------
# 中科大(92ms) > 清华(148ms)
declare -ga MIRRORS_RUST=(
    "https://mirrors.ustc.edu.cn/crates.io-index"
    "https://mirrors.tuna.tsinghua.edu.cn/crates.io-index"
    "https://crates.io"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 8. APT 镜像
# ---------------------------------------------------------------------------
# 阿里(54ms) > 中科大(55ms) > 清华(137ms)
# Base URLs for APT repos (distribution/codename appended at usage)
declare -ga MIRRORS_APT=(
    "https://mirrors.aliyun.com"
    "https://mirrors.ustc.edu.cn"
    "https://mirrors.tuna.tsinghua.edu.cn"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 9. Conda 镜像
# ---------------------------------------------------------------------------
# 清华(119ms)
declare -ga MIRRORS_CONDA=(
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda"
    "https://repo.anaconda.com"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_CONDA_FORGE=(
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge"
    "https://conda.anaconda.org/conda-forge"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 10. Maven 镜像
# ---------------------------------------------------------------------------
# 腾讯云(49ms) > 华为云(514ms) > 官方(1643ms) — 阿里云路径变更不可用
declare -ga MIRRORS_MAVEN=(
    "https://mirrors.cloud.tencent.com/nexus/repository/maven-public/"
    "https://repo.huaweicloud.com/repository/maven/"
    "https://repo1.maven.org/maven2"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_MAVEN_GRADLE=(
    "https://mirrors.cloud.tencent.com/gradle/"
    "https://services.gradle.org/distributions/"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 11. RubyGems 镜像
# ---------------------------------------------------------------------------
# ruby-china(104ms)
declare -ga MIRRORS_RUBYGEMS=(
    "https://gems.ruby-china.com"
    "https://rubygems.org"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 12. Chromium / Playwright / Electron 镜像
# ---------------------------------------------------------------------------
# npmmirror(69-89ms)
declare -ga MIRRORS_CHROMIUM=(
    "https://npmmirror.com/mirrors/chromium-browser-snapshots/"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_PLAYWRIGHT=(
    "https://npmmirror.com/mirrors/playwright/"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_ELECTRON=(
    "https://npmmirror.com/mirrors/electron/"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_PUPPETEER=(
    "https://npmmirror.com/mirrors/puppeteer/"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 13. Flutter 镜像
# ---------------------------------------------------------------------------
# pub.flutter-io.cn(55ms) > storage.flutter-io.cn(100ms)
declare -ga MIRRORS_FLUTTER_PUB=(
    "https://pub.flutter-io.cn"
    "https://pub.dev"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_FLUTTER_STORAGE=(
    "https://storage.flutter-io.cn"
    "https://storage.googleapis.com"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 14. Homebrew 镜像 (macOS)
# ---------------------------------------------------------------------------
# 中科大(128ms) > 清华(967ms)
declare -ga MIRRORS_HOMEBREW_CORE=(
    "https://mirrors.ustc.edu.cn/homebrew-core.git"
    "https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
    "https://github.com/Homebrew/homebrew-core.git"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_HOMEBREW_BOTTLES=(
    "https://mirrors.ustc.edu.cn/homebrew-bottles"
    "https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
)  # 最后验证: 2026-07-04

declare -ga MIRRORS_HOMEBREW_CASK=(
    "https://mirrors.ustc.edu.cn/homebrew-cask.git"
    "https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask.git"
    "https://github.com/Homebrew/homebrew-cask.git"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 15. CocoaPods 镜像 (macOS)
# ---------------------------------------------------------------------------
# 清华(git ls-remote 可达)
declare -ga MIRRORS_COCOAPODS=(
    "https://mirrors.tuna.tsinghua.edu.cn/git/CocoaPods/Specs.git"
    "https://github.com/CocoaPods/Specs.git"
)  # 最后验证: 2026-07-04

# ---------------------------------------------------------------------------
# 16. 通用 HTTPS 代理 (GitHub raw/release/archive 等)
# ---------------------------------------------------------------------------
# gh-proxy.com > ghproxy.net > ghp.ci
declare -ga MIRRORS_HTTPS_PROXY=(
    "https://gh-proxy.com/"
    "https://mirror.ghproxy.com/"
    "https://ghp.ci/"
)  # 最后验证: 2026-07-04

# =============================================================================
# 主镜像索引: MIRRORS 关联数组 (品类 -> 优先级数组名)
# =============================================================================
declare -gA MIRRORS=(
    ["github-clone"]="MIRRORS_GITHUB_CLONE"
    ["github-raw"]="MIRRORS_GITHUB_RAW"
    ["github-release"]="MIRRORS_GITHUB_RELEASE"
    ["github-archive"]="MIRRORS_GITHUB_ARCHIVE"
    ["huggingface"]="MIRRORS_HUGGINGFACE"
    ["pypi"]="MIRRORS_PYPI"
    ["npm"]="MIRRORS_NPM"
    ["docker-hub"]="MIRRORS_DOCKER_HUB"
    ["docker-ghcr"]="MIRRORS_DOCKER_GHCR"
    ["docker-gcr"]="MIRRORS_DOCKER_GCR"
    ["docker-quay"]="MIRRORS_DOCKER_QUAY"
    ["go"]="MIRRORS_GO"
    ["rust"]="MIRRORS_RUST"
    ["apt"]="MIRRORS_APT"
    ["conda"]="MIRRORS_CONDA"
    ["conda-forge"]="MIRRORS_CONDA_FORGE"
    ["maven"]="MIRRORS_MAVEN"
    ["maven-gradle"]="MIRRORS_MAVEN_GRADLE"
    ["rubygems"]="MIRRORS_RUBYGEMS"
    ["chromium"]="MIRRORS_CHROMIUM"
    ["playwright"]="MIRRORS_PLAYWRIGHT"
    ["electron"]="MIRRORS_ELECTRON"
    ["puppeteer"]="MIRRORS_PUPPETEER"
    ["flutter-pub"]="MIRRORS_FLUTTER_PUB"
    ["flutter-storage"]="MIRRORS_FLUTTER_STORAGE"
    ["homebrew-core"]="MIRRORS_HOMEBREW_CORE"
    ["homebrew-bottles"]="MIRRORS_HOMEBREW_BOTTLES"
    ["homebrew-cask"]="MIRRORS_HOMEBREW_CASK"
    ["cocoapods"]="MIRRORS_COCOAPODS"
    ["https-proxy"]="MIRRORS_HTTPS_PROXY"
)  # 最后验证: 2026-07-04

# =============================================================================
# detect_category(url) — 根据输入 URL 自动识别所属品类
# =============================================================================
# 参数:
#   $1 — 要识别的 URL
# 输出:
#   品类名 (如 "pypi", "github-clone", "npm" 等)
#   未识别到返回空字符串
# =============================================================================
detect_category() {
    local url="${1:-}"

    if [[ -z "$url" ]]; then
        echo ""
        return 0
    fi

    local lower_url
    lower_url="$(echo "$url" | tr '[:upper:]' '[:lower:]')"

    # --- Homebrew (must precede GitHub to avoid misclassification) ---
    if echo "$lower_url" | grep -qE 'homebrew.*(core|bottles|cask)'; then
        if echo "$lower_url" | grep -qE 'bottles'; then
            echo "homebrew-bottles"
            return 0
        fi
        if echo "$lower_url" | grep -qE 'cask'; then
            echo "homebrew-cask"
            return 0
        fi
        echo "homebrew-core"
        return 0
    fi

    # --- CocoaPods (must precede GitHub to avoid misclassification) ---
    if echo "$lower_url" | grep -qE '(cocoapods|CocoaPods)'; then
        echo "cocoapods"
        return 0
    fi

    # --- GitHub ---
    if echo "$lower_url" | grep -qE 'github\.com/[^/]+/[^/]+/releases/download'; then
        echo "github-release"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'github\.com/[^/]+/[^/]+/archive/'; then
        echo "github-archive"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'github\.com/[^/]+/[^/]+(/.*)?\.git'; then
        echo "github-clone"
        return 0
    fi
    if echo "$lower_url" | grep -qE '(raw\.githubusercontent\.com)'; then
        echo "github-raw"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'github\.com'; then
        echo "github-clone"
        return 0
    fi

    # --- HuggingFace ---
    if echo "$lower_url" | grep -qE '(huggingface\.co|hf-mirror\.com)'; then
        echo "huggingface"
        return 0
    fi

    # --- PyPI ---
    # 单层匹配所有 PyPI 域名和路径模式（含 mirrors.* 镜像站 + /pypi/simple 路径）
    if echo "$lower_url" | grep -qE '(pypi\.org|pypi\.python\.org|pypi\.(tuna|douban)|mirrors\..*/pypi|/pypi/.*simple)'; then
        echo "pypi"
        return 0
    fi

    # --- npm ---
    if echo "$lower_url" | grep -qE '(registry\.npmjs\.org|registry\.npm|\.npmjs\.)'; then
        echo "npm"
        return 0
    fi

    # --- Docker ---
    if echo "$lower_url" | grep -qE '(registry-1\.docker\.io|docker\.io|hub\.docker\.com)'; then
        echo "docker-hub"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'ghcr\.io'; then
        echo "docker-ghcr"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'gcr\.io'; then
        echo "docker-gcr"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'quay\.io'; then
        echo "docker-quay"
        return 0
    fi

    # --- Go ---
    if echo "$lower_url" | grep -qE '(golang\.org|proxy\.golang|goproxy)'; then
        echo "go"
        return 0
    fi

    # --- Rust ---
    if echo "$lower_url" | grep -qE '(crates\.io|crates\.io-index)'; then
        echo "rust"
        return 0
    fi

    # --- APT ---
    if echo "$lower_url" | grep -qE '/(ubuntu|debian)/?(dists|pool|/?)'; then
        echo "apt"
        return 0
    fi
    if echo "$lower_url" | grep -qE '(archive\.ubuntu\.com|security\.ubuntu\.com|deb\.debian\.org|apt\.)'; then
        echo "apt"
        return 0
    fi

    # --- Conda ---
    if echo "$lower_url" | grep -qE 'conda-forge'; then
        echo "conda-forge"
        return 0
    fi
    if echo "$lower_url" | grep -qE '(anaconda\.(org|com)|conda\.anaconda|repo\.anaconda|repo\.continuum)'; then
        echo "conda"
        return 0
    fi

    # --- Maven ---
    if echo "$lower_url" | grep -qE '(maven\.org/maven2|repo1\.maven|maven\.apache)'; then
        echo "maven"
        return 0
    fi
    if echo "$lower_url" | grep -qE '(gradle\.org|services\.gradle)'; then
        echo "maven-gradle"
        return 0
    fi

    # --- RubyGems ---
    if echo "$lower_url" | grep -qE '(rubygems\.org|gems\.ruby)'; then
        echo "rubygems"
        return 0
    fi

    # --- Chromium / Playwright / Electron ---
    if echo "$lower_url" | grep -qE 'chromium'; then
        echo "chromium"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'playwright'; then
        echo "playwright"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'electron'; then
        echo "electron"
        return 0
    fi
    if echo "$lower_url" | grep -qE 'puppeteer'; then
        echo "puppeteer"
        return 0
    fi

    # --- Flutter ---
    if echo "$lower_url" | grep -qE '(pub\.dev|pub\.flutter|pub\.dartlang)'; then
        echo "flutter-pub"
        return 0
    fi
    if echo "$lower_url" | grep -qE '(storage\.googleapis\.com.*flutter|storage\.flutter)'; then
        echo "flutter-storage"
        return 0
    fi

    # --- 无法识别 ---
    echo ""
    return 0
}

# =============================================================================
# get_mirrors(category) — 返回指定品类按优先级排序的镜像 URL 列表
# =============================================================================
# 参数:
#   $1 — 品类名 (如 "pypi", "npm", "github-clone" 等)
# 输出:
#   每行一个镜像 URL，按优先级从高到低排列
#   品类不存在则输出空
# =============================================================================
get_mirrors() {
    local category="${1:-}"

    if [[ -z "$category" ]]; then
        return 0
    fi

    local arr_name="${MIRRORS[$category]:-}"

    if [[ -z "$arr_name" ]]; then
        return 0
    fi

    # 使用 nameref 引用数组并逐行输出
    local -n arr_ref="$arr_name" 2>/dev/null || {
        # nameref 不可用时使用 eval
        eval "local temp_arr=(\"\${${arr_name}[@]}\")"
        for item in "${temp_arr[@]}"; do
            echo "$item"
        done
        return 0
    }

    for item in "${arr_ref[@]}"; do
        echo "$item"
    done
}

# =============================================================================
# get_primary_mirror(category) — 返回指定品类的首选镜像（最高优先级）
# =============================================================================
# 参数:
#   $1 — 品类名
# 输出:
#   最高优先级的镜像 URL，或空字符串
# =============================================================================
get_primary_mirror() {
    local category="${1:-}"
    local arr_name="${MIRRORS[$category]:-}"

    if [[ -z "$arr_name" ]]; then
        return 0
    fi

    local -n arr_ref="$arr_name" 2>/dev/null || {
        eval "echo \"\${${arr_name}[0]:-}\""
        return 0
    }

    echo "${arr_ref[0]:-}"
}

# =============================================================================
# convert_url(url) — 将原始 URL 转换为镜像 URL 列表
# =============================================================================
# 参数:
#   $1 — 原始 URL
# 输出:
#   每行一个镜像 URL，按优先级从高到低，已替换占位符
#   转换失败返回原始 URL（作为回退）
# =============================================================================
convert_url() {
    local url="${1:-}"

    if [[ -z "$url" ]]; then
        return 0
    fi

    local category
    category="$(detect_category "$url")"

    if [[ -z "$category" ]]; then
        # 无法识别品类，返回原始 URL 作为唯一选项
        echo "$url"
        return 0
    fi

    local arr_name="${MIRRORS[$category]:-}"
    if [[ -z "$arr_name" ]]; then
        echo "$url"
        return 0
    fi

    # 尝试提取 GitHub 相关占位符
    local user repo branch path tag file ref

    # 通用: 解析 GitHub URL 片段
    if [[ "$category" == github-* ]]; then
        # 尝试从 URL 中提取 GitHub 的 user/repo
        if echo "$url" | grep -qE 'github\.com/([^/]+)/([^/]+)'; then
            user="$(echo "$url" | sed -nE 's|.*github\.com/([^/]+)/([^/]+).*|\1|p' | head -1)"
            repo="$(echo "$url" | sed -nE 's|.*github\.com/([^/]+)/([^/]+).*|\2|p' | head -1)"
            # 去掉 .git 后缀
            repo="${repo%.git}"
        elif echo "$url" | grep -qE 'raw\.githubusercontent\.com/([^/]+)/([^/]+)'; then
            user="$(echo "$url" | sed -nE 's|.*raw\.githubusercontent\.com/([^/]+)/.*|\1|p' | head -1)"
            repo="$(echo "$url" | sed -nE 's|.*raw\.githubusercontent\.com/[^/]+/([^/]+)/.*|\1|p' | head -1)"
        fi

        # 提取分支/路径 (raw)
        if echo "$url" | grep -qE 'raw\.githubusercontent\.com'; then
            branch="$(echo "$url" | sed -nE 's|.*raw\.githubusercontent\.com/[^/]+/[^/]+/([^/]+)/.*|\1|p' | head -1)"
            path="$(echo "$url" | sed -nE 's|.*raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/(.*)|\1|p' | head -1)"
        fi

        # 提取 tag/file (release)
        if echo "$url" | grep -qE 'releases/download'; then
            tag="$(echo "$url" | sed -nE 's|.*releases/download/([^/]+)/.*|\1|p' | head -1)"
            file="$(echo "$url" | sed -nE 's|.*releases/download/[^/]+/(.*)|\1|p' | head -1)"
        fi

        # 提取 ref (archive)
        if echo "$url" | grep -qE '/archive/'; then
            ref="$(echo "$url" | sed -nE 's|.*/archive/([^/]+)\.(tar\.gz|zip).*|\1|p' | head -1)"
        fi
    fi

    # 从镜像模板生成 URL
    local -n arr_ref="$arr_name" 2>/dev/null
    local has_nameref=$?
    local converted=()

    if [[ $has_nameref -eq 0 ]]; then
        for template in "${arr_ref[@]}"; do
            local result="$template"
            result="${result//\{user\}/${user:-}}"
            result="${result//\{repo\}/${repo:-}}"
            result="${result//\{branch\}/${branch:-}}"
            result="${result//\{path\}/${path:-}}"
            result="${result//\{tag\}/${tag:-}}"
            result="${result//\{file\}/${file:-}}"
            result="${result//\{ref\}/${ref:-}}"
            converted+=("$result")
        done
    else
        eval "local temp_arr=(\"\${${arr_name}[@]}\")"
        for template in "${temp_arr[@]}"; do
            local result="$template"
            result="${result//\{user\}/${user:-}}"
            result="${result//\{repo\}/${repo:-}}"
            result="${result//\{branch\}/${branch:-}}"
            result="${result//\{path\}/${path:-}}"
            result="${result//\{tag\}/${tag:-}}"
            result="${result//\{file\}/${file:-}}"
            result="${result//\{ref\}/${ref:-}}"
            converted+=("$result")
        done
    fi

    # 输出已转换的 URL，最后附加原始 URL 作为最终回退
    for item in "${converted[@]}"; do
        # 如果模板不含占位符或无法替换，则输出模板本身
        echo "$item"
    done

    # 如果原始 URL 不在镜像列表中，追加作为回退
    local found_original=false
    for item in "${converted[@]}"; do
        if [[ "$item" == "$url" ]]; then
            found_original=true
            break
        fi
    done
    if [[ "$found_original" == false ]]; then
        echo "$url"
    fi
}

# =============================================================================
# list_categories() — 列出所有支持的品类
# =============================================================================
list_categories() {
    printf "%-25s %s\n" "CATEGORY" "PRIMARY_MIRROR"
    printf "%-25s %s\n" "-------------------------" "----------------------------------------"
    for category in "${!MIRRORS[@]}"; do
        local primary
        primary="$(get_primary_mirror "$category")"
        printf "%-25s %s\n" "$category" "$primary"
    done | sort
}

# =============================================================================
# category_info(category) — 显示某个品类的详细信息
# =============================================================================
category_info() {
    local category="${1:-}"

    if [[ -z "$category" ]] || [[ -z "${MIRRORS[$category]:-}" ]]; then
        echo "Usage: category_info <category>"
        echo "Available categories:"
        list_categories
        return 1
    fi

    echo "Category: $category"
    echo "Mirrors (priority order):"
    local i=1
    while IFS= read -r mirror; do
        if [[ -n "$mirror" ]]; then
            printf "  [%d] %s\n" "$i" "$mirror"
            ((i++))
        fi
    done < <(get_mirrors "$category")
}

# =============================================================================
# get_all_categories() — 列出所有品类名，每行一个
# =============================================================================
get_all_categories() {
    for category in "${!MIRRORS[@]}"; do
        echo "$category"
    done | sort
}

# =============================================================================
# probe_method(category) — 返回该品类的探测方式: "http" 或 "git"
# =============================================================================
# git ls-remote 探测的品类: github-clone, homebrew-core, homebrew-cask, cocoapods
# 其余均为 HTTP HEAD 探测
probe_method() {
    local category="${1:-}"
    case "$category" in
        github-clone|homebrew-core|homebrew-cask|cocoapods)
            echo "git"
            ;;
        *)
            echo "http"
            ;;
    esac
}

# =============================================================================
# 自定义镜像注入: 用户可在 ~/.mirrors_custom.sh 中覆盖或追加镜像配置
# =============================================================================
# 格式示例:
#   # 追加 PyPI 镜像到最高优先级:
#   MIRRORS_PYPI=("https://my-private-pypi.example.com/simple" "${MIRRORS_PYPI[@]}")
#
#   # 新增一个自定义品类:
#   declare -ga MIRRORS_CUSTOM=("https://my-mirror.example.com")
#   MIRRORS["custom"]="MIRRORS_CUSTOM"
#
#   # 覆盖某个品类（完全替换）:
#   MIRRORS_NPM=("https://my-npm-registry.example.com" "https://registry.npmjs.org")
# =============================================================================
if [ -f "$HOME/.mirrors_custom.sh" ]; then
    source "$HOME/.mirrors_custom.sh"
fi

# =============================================================================
# 自测: 仅当直接执行时运行
# =============================================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "=== mirrors_config.sh 自测 ==="
    echo ""

    echo "--- detect_category 测试 ---"
    test_urls=(
        "https://github.com/user/repo.git"
        "https://raw.githubusercontent.com/user/repo/main/file.txt"
        "https://github.com/user/repo/releases/download/v1.0/file.tar.gz"
        "https://github.com/user/repo/archive/main.tar.gz"
        "https://huggingface.co/bert-base-uncased"
        "https://pypi.org/simple/requests"
        "https://registry.npmjs.org/lodash"
        "https://registry-1.docker.io/v2/"
        "https://proxy.golang.org/x/tools/@v/list"
        "https://crates.io/api/v1/crates"
        "http://archive.ubuntu.com/ubuntu/dists/jammy/main"
        "https://repo.anaconda.com/pkgs/main"
        "https://repo1.maven.org/maven2/org/apache"
        "https://rubygems.org/gems/rails"
        "https://pub.dev/packages/flutter"
        "https://storage.googleapis.com/flutter_infra_release"
        "https://github.com/Homebrew/homebrew-core.git"
    )
    for u in "${test_urls[@]}"; do
        cat="$(detect_category "$u")"
        printf "  %-65s -> %s\n" "$u" "$cat"
    done

    echo ""
    echo "--- get_mirrors 测试 ---"
    for cat in pypi npm go rust maven apt; do
        echo "  [$cat]:"
        while IFS= read -r m; do
            echo "    $m"
        done < <(get_mirrors "$cat")
    done

    echo ""
    echo "--- convert_url 测试 ---"
    echo "  Input: https://github.com/user/repo.git"
    while IFS= read -r m; do
        echo "    -> $m"
    done < <(convert_url "https://github.com/user/repo.git")

    echo ""
    echo "  Input: https://raw.githubusercontent.com/user/repo/main/README.md"
    while IFS= read -r m; do
        echo "    -> $m"
    done < <(convert_url "https://raw.githubusercontent.com/user/repo/main/README.md")

    echo ""
    echo "  Input: https://github.com/user/repo/releases/download/v1.0/app.tar.gz"
    while IFS= read -r m; do
        echo "    -> $m"
    done < <(convert_url "https://github.com/user/repo/releases/download/v1.0/app.tar.gz")

    echo ""
    echo "--- primary mirrors ---"
    for cat in pypi npm go rust maven apt docker-hub rubygems conda homebrew-core flutter-pub cocoapods; do
        printf "  %-20s -> %s\n" "$cat" "$(get_primary_mirror "$cat")"
    done

    echo ""
    echo "=== 自测完成 ==="
fi
