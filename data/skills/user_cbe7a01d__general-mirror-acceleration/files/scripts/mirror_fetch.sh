#!/bin/bash
# ============================================================
# mirror_fetch.sh — 智能镜像下载器
# URL路由 → 品类识别 → 官方源探测 → 镜像切换下载
#
# 用法:
#   bash mirror_fetch.sh <URL> [目标路径]
#   bash mirror_fetch.sh https://github.com/user/repo.git
#   bash mirror_fetch.sh https://huggingface.co/bert-base-uncased /tmp/bert
#   bash mirror_fetch.sh https://example.com/file.tar.gz /tmp/file.tar.gz
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/mirrors_config.sh"

# ─── 颜色 (mirrors_config.sh 不定义颜色，由本脚本定义) ───
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

# ─── 超时 ───
readonly PROBE_TIMEOUT=3
readonly DOWNLOAD_TIMEOUT=30
readonly CLONE_TIMEOUT=120
readonly HEALTH_CHECK_TIMEOUT=1

# ─── 状态 ───
URL=""
TARGET=""
CATEGORY=""
USED_MIRROR="官方直连"
CACHE_TTL=300   # 延迟缓存5分钟
NO_CACHE=false  # --no-cache 标志

# ─── 日志 ───
log_info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}   $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err()   { echo -e "${RED}[ERR]${NC}  $*"; }
log_step()  { echo -e "${BOLD}[>>]${NC}  $*"; }

# ─── 使用说明 ───
usage() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║  mirror_fetch.sh — 智能镜像下载器                       ║
║                                                          ║
║  用法: bash mirror_fetch.sh <URL> [目标路径]             ║
║                                                          ║
║  支持品类:                                               ║
║    GitHub Clone/Release/Raw → gitclone/mirror.ghproxy/ghp.ci║
║    HuggingFace → hf-mirror.com                           ║
║    PyPI → 中科大/阿里/清华                                ║
║    npm → npmmirror.com                                   ║
║    Docker → 1ms.run/xuanyuan.me                          ║
║    Go → goproxy.cn                                       ║
║    Rust/Cargo → 中科大/清华                              ║
║    APT → 阿里云/中科大/清华                              ║
║    通用URL → gh-proxy/mirror.ghproxy/ghp.ci              ║
║                                                          ║
║  示例:                                                   ║
║    mirror_fetch.sh https://github.com/user/repo.git      ║
║    mirror_fetch.sh https://huggingface.co/bert /tmp/bert ║
║    mirror_fetch.sh https://example.com/file.tar.gz       ║
╚══════════════════════════════════════════════════════════╝
EOF
    exit 1
}

# ─── 解析参数 ───
parse_args() {
    # 处理 --help / -h
    for arg in "$@"; do
        case "$arg" in
            -h|--help)  usage; exit 0 ;;
            --no-cache) NO_CACHE=true ;;
        esac
    done
    # 过滤标志参数，取第一个非标志参数作为URL
    local filtered=()
    for arg in "$@"; do
        case "$arg" in
            -h|--help|--no-cache) ;;
            *) filtered+=("$arg") ;;
        esac
    done
    if [ ${#filtered[@]} -lt 1 ]; then
        usage
    fi
    URL="${filtered[0]}"
    TARGET="${filtered[1]:-}"

    if [ -z "$TARGET" ]; then
        TARGET=$(basename "$URL" | sed 's/[?#].*//')
        [ -z "$TARGET" ] && TARGET="downloaded_file"
        TARGET=$(echo "$TARGET" | sed 's/\.git$//')
    fi
}

# ─── HTTP 探测 ───
probe_http() {
    local url="$1" timeout="${2:-$PROBE_TIMEOUT}"
    local code start end latency
    start=$(date +%s%3N 2>/dev/null || echo 0)
    code=$(curl -sI -o /dev/null -w "%{http_code}" --max-time "$timeout" "$url" 2>/dev/null || echo "000")
    end=$(date +%s%3N 2>/dev/null || echo 0)
    latency=$((end - start))
    if [ "$code" = "000" ] || [ "$code" -ge 500 ]; then
        echo "unreachable"
        return 1
    fi
    echo "$latency"
    return 0
}

# ─── 镜像健康预检 (1s超时) ───
# 在尝试下载前快速探测镜像是否可达，跳过死掉的镜像
# 先尝试 HEAD 请求，失败则回退到 GET + Range: bytes=0-0
# 返回值: 0=健康, 1=不可达
probe_mirror_health() {
    local url="$1"
    local code

    # 第一次尝试: HEAD 请求
    code=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout "$HEALTH_CHECK_TIMEOUT" --max-time "$HEALTH_CHECK_TIMEOUT" -I "$url" 2>/dev/null)
    [ -z "$code" ] && code="000"

    # HEAD 成功且非客户端/服务端错误 → 通过
    if [ "$code" != "000" ] && [ "$code" -lt 400 ]; then
        echo "$code"
        return 0
    fi

    # 第二次尝试: GET + Range 字节范围请求 (绕过某些不支持 HEAD 的服务器)
    code=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout "$HEALTH_CHECK_TIMEOUT" --max-time "$HEALTH_CHECK_TIMEOUT" -H "Range: bytes=0-0" "$url" 2>/dev/null)
    [ -z "$code" ] && code="000"

    if [ "$code" != "000" ] && [ "$code" -lt 400 ]; then
        echo "$code"
        return 0
    fi

    echo "$code"
    return 1
}

# ═══════════════════════════════════════════════════════════
# 延迟缓存 (TTL=300s) — 读/写
# ═══════════════════════════════════════════════════════════
LATENCY_CACHE="/tmp/.mirror_latency_cache"

read_cache() {
    local category="$1"
    local now cutoff
    now=$(date +%s)
    cutoff=$((now - CACHE_TTL))

    if [ ! -f "$LATENCY_CACHE" ]; then
        return 1
    fi

    local found=false
    while IFS='|' read -r cat url latency ts; do
        if [ "$cat" = "$category" ] && [ "$ts" -ge "$cutoff" ] 2>/dev/null; then
            echo "${url}|${latency}"
            found=true
        fi
    done < "$LATENCY_CACHE"
    $found && return 0 || return 1
}

write_cache() {
    local category="$1"
    shift
    local now
    now=$(date +%s)

    # 基于 mkdir 的互斥锁（兼容无 flock 环境）
    local lockdir="${LATENCY_CACHE}.lock"
    local retries=0
    while ! mkdir "$lockdir" 2>/dev/null; do
        retries=$((retries + 1))
        [ $retries -gt 20 ] && { log_warn "缓存锁超时，跳过写入"; return 0; }
        sleep 0.05
    done

    # 删除该品类的旧条目
    if [ -f "$LATENCY_CACHE" ]; then
        grep -v "^${category}|" "$LATENCY_CACHE" > "${LATENCY_CACHE}.tmp" 2>/dev/null
        mv "${LATENCY_CACHE}.tmp" "$LATENCY_CACHE" 2>/dev/null
    fi

    # 写入新条目
    for entry in "$@"; do
        IFS='|' read -r url latency <<< "$entry"
        echo "${category}|${url}|${latency}|${now}" >> "$LATENCY_CACHE"
    done

    rmdir "$lockdir" 2>/dev/null
}

# ═══════════════════════════════════════════════════════════
# 并行探测 + 延迟排序 — 同时探测所有镜像，按实测延迟从快到慢返回
# ═══════════════════════════════════════════════════════════
parallel_rank_urls() {
    local method="$1"   # "http" 或 "git"
    shift
    local urls=("$@")

    if [ ${#urls[@]} -eq 0 ]; then
        return 0
    fi

    local tmpdir
    tmpdir=$(mktemp -d)
    local pids=()
    local idx=0

    for url in "${urls[@]}"; do
        [ -z "$url" ] && continue
        (
            local latency=99999
            if [ "$method" = "git" ]; then
                local start
                start=$(date +%s%3N 2>/dev/null || echo 0)
                if timeout "$PROBE_TIMEOUT" git ls-remote --heads "$url" HEAD &>/dev/null; then
                    local end
                    end=$(date +%s%3N 2>/dev/null || echo 0)
                    latency=$((end - start))
                fi
            else
                local result
                result=$(probe_http "$url" "$PROBE_TIMEOUT" 2>/dev/null || echo "unreachable")
                if [ "$result" != "unreachable" ]; then
                    latency="$result"
                fi
            fi
            echo "${url}|${latency}" > "${tmpdir}/${idx}"
        ) &
        pids+=($!)
        idx=$((idx + 1))
    done

    # 等待所有子进程
    for pid in "${pids[@]}"; do
        wait "$pid" 2>/dev/null || true
    done

    # 收集并排序 (按延迟升序，不可达的排末尾)
    {
        cat "${tmpdir}"/* 2>/dev/null | sort -t'|' -k2 -n | while IFS='|' read -r url latency; do
            [ "$latency" != "99999" ] && echo "$url"
        done
        # 不可达的排最后（给它们一次机会）
        cat "${tmpdir}"/* 2>/dev/null | sort -t'|' -k2 -n | while IFS='|' read -r url latency; do
            if [ "$latency" = "99999" ]; then
                echo "$url"
            fi
        done
    }

    local any_ok=false
    while IFS='|' read -r url latency; do
        if [ "$latency" != "99999" ]; then
            any_ok=true
            break
        fi
    done < <(cat "${tmpdir}"/* 2>/dev/null)

    # 写入缓存（仅写入可达的）
    if $any_ok && ! $NO_CACHE; then
        local cache_entries=()
        while IFS='|' read -r url latency; do
            if [ "$latency" != "99999" ]; then
                cache_entries+=("${url}|${latency}")
            fi
        done < <(cat "${tmpdir}"/* 2>/dev/null)
        if [ ${#cache_entries[@]} -gt 0 ]; then
            write_cache "$CATEGORY" "${cache_entries[@]}"
        fi
    fi

    rm -rf "$tmpdir"
    return 0
}

# ─── Git clone ───
git_clone_with_timeout() {
    local git_url="$1" dest="$2"
    timeout "$CLONE_TIMEOUT" git clone "$git_url" "$dest" 2>&1
}

# ─── 通用 curl 下载 ───
curl_download() {
    local src="$1" dest="$2"
    curl -fSL --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$dest" "$src" 2>&1
}

# ─── 执行下载 (返回0=成功) ───
do_download_from_url() {
    local src="$1" dest="$2" category="$3"

    case "$category" in
        github-clone)
            git_clone_with_timeout "$src" "$dest"
            ;;
        *)
            curl_download "$src" "$dest"
            ;;
    esac
}

# ─── 尝试一组 URL ───
try_urls() {
    local dest="$1" category="$2" label_prefix="$3"
    shift 3
    local urls=("$@")

    # 判断探测方式
    local method
    method=$(probe_method "$category" 2>/dev/null || echo "http")

    local i=0
    for mirror_url in "${urls[@]}"; do
        [ -z "$mirror_url" ] && continue
        i=$((i + 1))
        log_step "${label_prefix} [${i}/${#urls[@]}]: $mirror_url"

        # ─── 健康预检: HTTP品类做快速探测，Git品类跳过 ───
        if [ "$method" = "http" ]; then
            local health_code
            health_code=$(probe_mirror_health "$mirror_url" 2>/dev/null)
            [ -z "$health_code" ] && health_code="000"
            if [ "$health_code" = "000" ]; then
                log_warn "跳过 $mirror_url (不可达)"
                continue
            elif [ "$health_code" -ge 500 ]; then
                log_warn "跳过 $mirror_url (HTTP $health_code)"
                continue
            fi
            log_info "镜像健康检查通过 (HTTP $health_code)"
        fi

        # 清理之前可能失败的目录（先做安全校验）
        if [ "$category" = "github-clone" ] && [ -d "$dest" ]; then
            # 拒绝删除受保护路径
            case "$(realpath "$dest" 2>/dev/null || echo "$dest")" in
                /|/home|/etc|/usr|/var|/root|/boot|/opt|/srv)
                    log_err "拒绝删除受保护路径: $dest"
                    return 1
                    ;;
            esac
            rm -rf "$dest" 2>/dev/null || true
        fi

        if do_download_from_url "$mirror_url" "$dest" "$category"; then
            log_ok "成功: $mirror_url"
            USED_MIRROR="$mirror_url"
            return 0
        fi
        log_warn "失败: $mirror_url"
    done
    return 1
}

# ─── 下载: 缓存排序 + 镜像回退 ───
download_with_fallback() {
    local category="$1"

    # --- Step A: 获取 convert_url 转换后的镜像 URL 列表 ---
    local converted_urls=()
    while IFS= read -r line; do
        [ -n "$line" ] && converted_urls+=("$line")
    done < <(convert_url "$URL" 2>/dev/null || echo "$URL")

    if [ ${#converted_urls[@]} -eq 0 ]; then
        converted_urls+=("$URL")
    fi

    # --- Step B: 延迟排序（缓存优先 → 并行探测） ---
    local sorted_urls=()
    local method
    method=$(probe_method "$category" 2>/dev/null || echo "http")

    if ! $NO_CACHE; then
        # 尝试从缓存读取（5分钟内有效）
        local cached=()
        while IFS='|' read -r url latency; do
            cached+=("$url")
        done < <(read_cache "$CATEGORY" 2>/dev/null || true)
        if [ ${#cached[@]} -gt 0 ]; then
            log_info "使用缓存延迟数据 (${#cached[@]} 条)"
            sorted_urls=("${cached[@]}")
        fi
    fi

    if [ ${#sorted_urls[@]} -eq 0 ]; then
        # 缓存未命中 → 并行探测
        log_step "并行探测 ${#converted_urls[@]} 个镜像延迟..."
        while IFS= read -r url; do
            [ -n "$url" ] && sorted_urls+=("$url")
        done < <(parallel_rank_urls "$method" "${converted_urls[@]}")
        if [ ${#sorted_urls[@]} -gt 0 ]; then
            log_info "探测完成，按延迟排序"
        fi
    fi

    # 确保原始 URL 在列表中（作为兜底）
    local has_original=false
    for u in "${sorted_urls[@]}"; do
        [ "$u" = "$URL" ] && has_original=true && break
    done
    if ! $has_original; then
        sorted_urls+=("$URL")
    fi

    # --- Step C: 按排序后的顺序尝试 ---
    if [ ${#sorted_urls[@]} -gt 0 ]; then
        if try_urls "$TARGET" "$category" "下载" "${sorted_urls[@]}"; then
            return 0
        fi
    else
        # 回退：直接用convert_url输出
        if try_urls "$TARGET" "$category" "下载" "${converted_urls[@]}"; then
            return 0
        fi
    fi

    # --- Step D: 通用代理回退 (非包管理器品类) ---
    if [[ "$category" != "pypi" && "$category" != "npm" && "$category" != "docker-hub" && \
          "$category" != "docker-ghcr" && "$category" != "docker-gcr" && \
          "$category" != "docker-quay" && "$category" != "go" && "$category" != "rust" ]]; then
        log_step "通用代理回退..."
        local proxy_urls=()
        while IFS= read -r p; do
            [ -n "$p" ] && proxy_urls+=("${p}${URL}")
        done < <(get_mirrors "https-proxy" 2>/dev/null || echo "")
        if [ ${#proxy_urls[@]} -gt 0 ]; then
            if try_urls "$TARGET" "$category" "代理" "${proxy_urls[@]}"; then
                return 0
            fi
        fi
    fi

    return 1
}

# ═══════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════
main() {
    parse_args "$@"

    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════╗"
    echo -e "║  mirror_fetch.sh — 智能镜像下载器                 ║"
    echo -e "╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    log_info "URL:    $URL"
    log_info "目标:   $TARGET"

    # Step 1: 品类识别
    CATEGORY=$(detect_category "$URL" || echo "")
    if [ -z "$CATEGORY" ]; then
        log_warn "无法识别URL品类，作为通用URL处理"
        CATEGORY="https-proxy"
    fi
    log_info "品类:   $CATEGORY"
    if $NO_CACHE; then
        log_info "缓存:   已禁用 (--no-cache)"
    fi
    echo ""

    # Step 2: 缓存排序 + 并行探测 + 下载
    if download_with_fallback "$CATEGORY"; then
        echo ""
        echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
        log_ok "下载成功!"
        log_info "目标:    $TARGET"
        if [ -f "$TARGET" ]; then
            log_info "大小:    $(du -h "$TARGET" 2>/dev/null | cut -f1 || echo 'ok')"
        fi
        echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
        exit 0
    fi

    # Step 3: 全部失败
    echo ""
    echo -e "${RED}════════════════════════════════════════════════════${NC}"
    log_err "所有下载方式均失败！"
    echo ""
    echo -e "  建议:"
    echo -e "    1. 检查网络: ping -c 3 8.8.8.8"
    echo -e "    2. 检查DNS:  nslookup \$(echo '$URL' | awk -F/ '{print \$3}')"
    echo -e "    3. 使用代理: export https_proxy=http://your-proxy:port"
    echo -e "    4. 手动下载: curl -fSL -o '${TARGET}' '${URL}'"
    echo -e "    5. 健康检查: bash ${SCRIPT_DIR}/mirror_health_check.sh"
    echo -e "${RED}════════════════════════════════════════════════════${NC}"
    exit 1
}

main "$@"
