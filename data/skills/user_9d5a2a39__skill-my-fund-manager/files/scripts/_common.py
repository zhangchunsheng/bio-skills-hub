"""
我的基金经理 Skill - 共享工具模块
提供路径定位、HTTP请求（多级fallback）、反爬、编码处理、JSON读写等基础能力。
尽量使用标准库；requests 缺失时自动安装或回退到 urllib。
适配任意 agent 环境，不硬编码绝对路径。
"""

import os
import sys
import json
import time
import random
import re
import logging

# ============================================================
# 路径定位（基于 __file__，适配任意安装位置）
# ============================================================
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(SKILL_ROOT, "data")
MANAGERS_DIR = os.path.join(DATA_DIR, "managers")
PROGRESS_DIR = os.path.join(DATA_DIR, "progress")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
ROSTER_PATH = os.path.join(DATA_DIR, "roster.json")
REFERENCES_DIR = os.path.join(SKILL_ROOT, "references")


def ensure_dirs():
    """确保所有数据目录存在"""
    for d in [DATA_DIR, MANAGERS_DIR, PROGRESS_DIR, EXPORTS_DIR]:
        os.makedirs(d, exist_ok=True)


# ============================================================
# 日志
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("my-fund-manager")


# ============================================================
# 依赖管理：自动安装 requests（惰性初始化，无导入时副作用）
# ============================================================
_requests = None


def _get_requests():
    """
    惰性加载 requests，首次调用时才尝试导入/安装。
    避免导入 _common 时触发 pip install 的副作用。
    """
    global _requests
    if _requests is not None:
        return _requests or None
    try:
        import requests
        _requests = requests
        return requests
    except ImportError:
        log.info("requests 未安装，尝试自动安装...")
        try:
            import subprocess
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "requests"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            import requests as req_mod
            _requests = req_mod
            log.info("requests 安装成功")
            return req_mod
        except Exception as e:
            log.warning(f"requests 自动安装失败({e})，回退到 urllib")
            _requests = False  # 标记为已尝试但失败，避免重复安装
            return None


# ============================================================
# HTTP 请求（requests 优先，urllib fallback）
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

EASTMONEY_REFERER = "https://fund.eastmoney.com/"


def _random_delay(min_s=0.3, max_s=0.8):
    """随机延迟，降低被反爬概率"""
    time.sleep(random.uniform(min_s, max_s))


def http_get(url, params=None, referer=EASTMONEY_REFERER, encoding=None, timeout=15, retries=3):
    """
    HTTP GET 请求，requests 优先，urllib fallback。
    自动携带反爬头、随机延迟、重试。
    返回响应文本（str）。失败返回 None。
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": referer,
        "Accept": "*/*",
    }

    req_lib = _get_requests()  # 模块级 requests（不再是循环内复用）
    for attempt in range(retries):
        try:
            if req_lib:
                resp = req_lib.get(url, params=params, headers=headers, timeout=timeout)
                if encoding:
                    resp.encoding = encoding
                else:
                    resp.encoding = resp.apparent_encoding
                if resp.status_code == 200:
                    _random_delay()
                    return resp.text
                else:
                    log.warning(f"HTTP {resp.status_code} (attempt {attempt+1}): {url}")
                    # v2.0 修复：非 200 也需要延迟，避免反爬
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt + random.uniform(0, 1))
            else:
                # urllib fallback — 使用本地变量 urllib_request，避免覆盖外层 req_lib
                import urllib.request
                import urllib.parse
                full_url = url
                if params:
                    full_url += "?" + urllib.parse.urlencode(params)
                urllib_request = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(urllib_request, timeout=timeout) as resp:
                    raw = resp.read()
                    enc = encoding or "utf-8"
                    _random_delay()
                    return raw.decode(enc, errors="replace")
        except Exception as e:
            log.warning(f"请求失败 (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt + random.uniform(0, 1))

    log.error(f"请求最终失败: {url}")
    return None


def http_post(url, json_body=None, referer=EASTMONEY_REFERER, timeout=15, retries=3, extra_headers=None):
    """
    HTTP POST 请求（JSON body），requests 优先，urllib fallback。
    用于 AMAC 等需要 POST 的 API。
    返回响应文本（str）。失败返回 None。
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": referer,
        "Accept": "*/*",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    req_lib = _get_requests()
    for attempt in range(retries):
        try:
            if req_lib:
                resp = req_lib.post(url, json=json_body, headers=headers, timeout=timeout)
                if resp.status_code == 200:
                    _random_delay()
                    return resp.text
                else:
                    log.warning(f"HTTP POST {resp.status_code} (attempt {attempt+1}): {url}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt + random.uniform(0, 1))
            else:
                import urllib.request
                data = json.dumps(json_body).encode("utf-8") if json_body else b""
                urllib_request = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(urllib_request, timeout=timeout) as resp:
                    _random_delay()
                    return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            log.warning(f"POST 请求失败 (attempt {attempt+1}/{retries}): {e}")
            time.sleep(2 ** attempt + random.uniform(0, 1))

    log.error(f"POST 请求最终失败: {url}")
    return None


def http_get_jsonp(url, params=None, referer=EASTMONEY_REFERER, encoding="utf-8", timeout=15):
    """
    获取东方财富 JS 变量格式的数据（如 var apidata={...}; var returnjson={...}）。
    使用平衡括号匹配提取第一个完整 JSON 对象并返回 dict。失败返回 {"_raw": text}。
    """
    text = http_get(url, params=params, referer=referer, encoding=encoding, timeout=timeout)
    if not text:
        return None
    json_str = _find_balanced_json(text)
    if json_str:
        # v2.1 修复：先按原文解析（合法双引号 JSON），失败再处理单引号变体。
        # 盲目 replace("'", '"') 会破坏值内合法撇号（如 "O'Hara"、"It's"）。
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        converted = _convert_single_quote_json(json_str)
        if converted:
            try:
                return json.loads(converted)
            except json.JSONDecodeError:
                pass
    return {"_raw": text}


def _convert_single_quote_json(json_str):
    """把东财 jsonp 的单引号 JSON 转为双引号格式（尊重字符串边界与转义）。
    仅转换作为字符串定界符的单引号，值内双引号转义为 \\\"。失败返回 None。"""
    out = []
    in_string = False
    escape = False
    for ch in json_str:
        if escape:
            out.append(ch)
            escape = False
            continue
        if ch == '\\':
            out.append(ch)
            escape = True
            continue
        if in_string:
            if ch == "'":
                out.append('"')
                in_string = False
            elif ch == '"':
                out.append('\\"')
            else:
                out.append(ch)
            continue
        if ch == "'":
            out.append('"')
            in_string = True
        else:
            out.append(ch)
    return "".join(out)


def _find_balanced_json(text):
    """在文本中找到第一个平衡的 JSON 对象字符串，正确处理嵌套括号、转义引号。
    v2.1 修复：同时支持单引号字符串（东财 jsonp 场景），避免字符串内括号误判。"""
    start = text.find('{')
    if start == -1:
        return None
    depth = 0
    quote = None  # 当前字符串定界符：'"' 或 "'"，None 表示不在字符串内
    escape = False
    for i, ch in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch == '"' or ch == "'":
            quote = ch
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


# ============================================================
# JSON 读写（安全处理大文件、编码）
# ============================================================
def read_json(path, default=None):
    """安全读取 JSON 文件，失败返回 default"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def write_json(path, data):
    """安全写入 JSON 文件（ensure_ascii=False 保留中文），先写临时文件再原子替换"""
    ensure_dirs()
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)  # 原子替换（Windows/Linux 均支持）
    finally:
        # 确保临时文件被清理（写入失败时不残留）
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


# ============================================================
# 经理档案路径工具
# ============================================================
def manager_path(manager_id):
    """获取经理档案 JSON 路径"""
    safe_id = re.sub(r"[^\w\-]", "_", str(manager_id))
    return os.path.join(MANAGERS_DIR, f"{safe_id}.json")


def load_manager(manager_id):
    """加载单个经理档案"""
    return read_json(manager_path(manager_id), default=None)


def save_manager(manager_id, data):
    """保存单个经理档案"""
    write_json(manager_path(manager_id), data)


def list_manager_files():
    """列出所有已存档的经理文件 ID"""
    if not os.path.isdir(MANAGERS_DIR):
        return []
    return [
        f.replace(".json", "")
        for f in os.listdir(MANAGERS_DIR)
        if f.endswith(".json")
    ]


# ============================================================
# HTML 文本清洗
# ============================================================
def strip_html(html_str):
    """去除 HTML 标签，保留纯文本"""
    if not html_str:
        return ""
    # 替换常见 HTML 实体（覆盖常见 14 种）
    # v2.0 修复：&nbsp; 用 U+00A0 真正的不间断空格，避免被 strip+压缩空白时丢失
    html_str = html_str.replace("&nbsp;", " ").replace("&amp;", "&")
    html_str = html_str.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    html_str = html_str.replace("&apos;", "'").replace("&#39;", "'")
    html_str = html_str.replace("&mdash;", "—").replace("&ndash;", "–")
    html_str = html_str.replace("&hellip;", "…").replace("&laquo;", "«").replace("&raquo;", "»")
    html_str = html_str.replace("&lsquo;", "'").replace("&rsquo;", "'")
    html_str = html_str.replace("&ldquo;", '"').replace("&rdquo;", '"')
    # 数字字符引用（&#123; 形式）
    html_str = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))) if int(m.group(1)) < 0x110000 else m.group(0), html_str)
    # 十六进制字符引用（&#x1F; 形式）
    html_str = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)) if int(m.group(1), 16) < 0x110000 else m.group(0), html_str)
    # 去除标签
    text = re.sub(r"<[^>]+>", "", html_str)
    # 压缩普通空白（不破坏   不间断空格）
    text = re.sub(r"[ \t\n\r\f\v]+", " ", text)
    # 首尾空白（也不影响  ）
    return text.strip()


# ============================================================
# 进度追踪（断点续传）
# ============================================================
def load_progress(task_name):
    """加载任务进度"""
    path = os.path.join(PROGRESS_DIR, f"{task_name}.json")
    return read_json(path, default={"done": [], "pending": []})


def save_progress(task_name, progress):
    """保存任务进度"""
    path = os.path.join(PROGRESS_DIR, f"{task_name}.json")
    write_json(path, progress)


# ============================================================
# 自检
# ============================================================
if __name__ == "__main__":
    ensure_dirs()
    print(f"Skill Root: {SKILL_ROOT}")
    print(f"Data Dir:   {DATA_DIR}")
    print(f"Roster:     {ROSTER_PATH}")
    req = _get_requests()
    print(f"requests:   {'可用' if req else '不可用(urllib fallback)'}")
    # 测试东方财富连通性
    test = http_get("https://fundf10.eastmoney.com/", timeout=10)
    print(f"东方财富连通: {'是' if test else '否'}")
