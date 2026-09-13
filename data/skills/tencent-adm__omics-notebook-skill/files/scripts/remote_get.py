#!/usr/bin/env python3
"""
下载远程 Notebook 实例的 .ipynb 文件到本地（Python 实现）

固定获取 notebook_id 对应的 NotebookCosUri 所指向的 .ipynb 文件，
通过 Jupyter Contents API（GET /api/contents/{path}）读取内容并保存到本地。

依赖：pip install requests

用法 — 作为模块导入：
    from remote_get import remote_get_file
    local_path = remote_get_file(
        notebook_id="notebook-xxx",
        local_path="./demo.ipynb",   # 可选，不传则用远程文件名
    )

用法 — 命令行：
    python remote_get.py <notebookId> [localPath]
    示例: python remote_get.py notebook-xxx
          python remote_get.py notebook-xxx ./demo.ipynb
"""

import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

# ---------- CLI 调用 ----------

_OMICS_CLI_PATH = os.environ.get("OMICS_CLI_PATH", "omics")


def _run_omics(*args: str) -> str:
    """执行 omics CLI 命令并返回 stdout，失败抛异常"""
    cmd = [_OMICS_CLI_PATH, *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"omics {' '.join(args)} 失败 (exit {result.returncode}): {result.stderr.strip()}")
    return result.stdout.strip()


# ---------- auth ----------

SCRIPT_DIR = Path(__file__).resolve().parent
# 使用 omics login 生成的凭证文件（omics whoami 显示的存储路径）
AUTH_FILE = Path(os.environ.get(
    "OMICS_AUTH_FILE",
    Path.home() / ".omics-platform-cli" / "auth.json",
))

_OMICS_SESSION: str | None = None


def _load_session() -> str:
    global _OMICS_SESSION
    if _OMICS_SESSION is not None:
        return _OMICS_SESSION
    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        auth = json.load(f)
    sid = auth.get("session_id")
    if not sid:
        raise RuntimeError("auth.json 缺少 session_id")
    _OMICS_SESSION = sid
    return sid


# ---------- helpers ----------

DEFAULTS = {
    "xsrf_token": "xrsf_token",
    "timeout": 300,
}


def _create_session(base: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": base,
        "Referer": f"{base}/tree",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
        ),
        "Cookie": f"omics_session={_load_session()}; _xsrf={DEFAULTS['xsrf_token']}",
        "X-XSRFToken": DEFAULTS["xsrf_token"],
    })
    return session


def _resolve_instance_info(notebook_id: str) -> tuple[str, str]:
    """
    根据 notebook_id 解析 instance_url 和 remote_notebook_path。

    步骤：
      1. omics notebook list -o json → 找到目标实例，取 InstanceUrl / NotebookCosUri / CosBucketMounts
      2. omics cos list-mount -o json → 获取环境挂载列表
      3. 合并 CosBucketMounts + cos 挂载列表为总挂载列表
      4. 解析 NotebookCosUri (cos://bucket/subpath/filename.ipynb) → 匹配挂载点 → 确定 MountPath
      5. remote_notebook_path = MountPath + 文件名.ipynb

    返回: (instance_url, remote_notebook_path)
    """
    # 1. 列 notebook 实例
    raw = _run_omics("notebook", "list", "-o", "json")
    items = json.loads(raw)
    target = next((item for item in items if item.get("NotebookId") == notebook_id), None)
    if target is None:
        raise RuntimeError(f"notebook list 中未找到 {notebook_id}，请确认实例存在或已配置正确环境")

    instance_url = target.get("InstanceUrl") or ""
    notebook_cos_uri = target.get("NotebookCosUri") or ""
    nb_cos_mounts = target.get("CosBucketMounts") or []

    if not instance_url:
        raise RuntimeError(f"{notebook_id} 的 InstanceUrl 为空，实例可能尚未就绪")
    if not notebook_cos_uri:
        raise RuntimeError(f"{notebook_id} 的 NotebookCosUri 为空")

    print(f"   ✓ 目标实例: {notebook_id}")
    print(f"   ✓ InstanceUrl: {instance_url}")
    print(f"   ✓ NotebookCosUri: {notebook_cos_uri}")

    # 2. 列环境 COS 挂载
    raw_mounts = _run_omics("cos", "list-mount", "-o", "json")
    env_mounts = json.loads(raw_mounts) if raw_mounts else []

    # 3. 合并为总挂载列表（去重：以 Bucket+SubPath 为 key）
    seen: set[tuple[str, str]] = set()
    total_mounts: list[dict] = []
    for m in list(nb_cos_mounts) + list(env_mounts):
        key = (m.get("Bucket", ""), m.get("SubPath", ""))
        if key not in seen:
            seen.add(key)
            total_mounts.append(m)

    print(f"   ✓ 总挂载列表: {len(total_mounts)} 条（实例 {len(nb_cos_mounts)} + 环境 {len(env_mounts)}）")

    # 4. 解析 NotebookCosUri: cos://bucket/subpath/filename.ipynb
    m = re.match(r"^cos://([^/]+)(/.*)?/([^/]+\.ipynb)$", notebook_cos_uri)
    if not m:
        raise RuntimeError(f"无法解析 NotebookCosUri: {notebook_cos_uri}（期望 cos://bucket/prefix/filename.ipynb）")
    cos_bucket = m.group(1)
    cos_prefix = m.group(2) or ""       # 如 /notebooks
    filename = m.group(3)                # 如 demo.ipynb

    # 5. 匹配挂载点：Bucket 相等 且 cos_prefix 以 SubPath 开头
    matched = None
    for mount in total_mounts:
        mb = mount.get("Bucket", "")
        ms = mount.get("SubPath", "") or ""
        if mb == cos_bucket and cos_prefix.startswith(ms):
            # 选 SubPath 最长的（最精确匹配）
            if matched is None or len(ms) > len(matched.get("SubPath", "") or ""):
                matched = mount

    if matched is None:
        # 兜底：直接用 cos 路径拼在第一个可用 MountPath 下
        if total_mounts:
            matched = total_mounts[0]
        else:
            raise RuntimeError("没有可用的挂载点，无法确定 remote_notebook_path")

    mount_path = (matched.get("MountPath", "") or "").rstrip("/")
    # relative = cos_prefix 去掉 mount.SubPath 前缀
    mount_sub = (matched.get("SubPath", "") or "").rstrip("/")
    relative = cos_prefix
    if mount_sub and relative.startswith(mount_sub):
        relative = relative[len(mount_sub):]
    relative = relative.lstrip("/")

    remote_notebook_path = f"{mount_path}/{relative}/{filename}".replace("//", "/")
    print(f"   ✓ 匹配挂载: {matched.get('Bucket')}{matched.get('SubPath','')} -> {mount_path}")
    print(f"   ✓ remote_notebook_path: {remote_notebook_path}")

    return instance_url, remote_notebook_path


def _fetch_contents(session: requests.Session, base: str, remote_path: str, timeout: int) -> dict:
    """
    GET /api/contents/{path}?content=1 获取文件内容模型。

    不指定 format，让服务端按文件类型自动返回：
      - notebook → format=json，content 为 dict
      - 文本文件 → format=text，content 为 str
      - 二进制   → format=base64，content 为 base64 字符串
    """
    remote_path = remote_path.lstrip("/")
    # 对 path 每一段做 URL 编码，保留分隔符 '/'
    quoted = "/".join(requests.utils.quote(seg, safe="") for seg in remote_path.split("/"))
    url = f"{base}/api/contents/{quoted}"
    print(f"① 获取远程文件: {remote_path}")
    resp = session.get(url, params={"content": 1}, timeout=timeout)
    if resp.status_code == 404:
        raise RuntimeError(f"远程文件不存在 (404): {remote_path}")
    if resp.status_code == 400:
        reason = ""
        try:
            reason = resp.json().get("reason", "")
        except Exception:
            reason = resp.text
        raise RuntimeError(f"请求被拒绝 (400 {reason}): {remote_path}")
    resp.raise_for_status()
    return resp.json()


def _save_contents(model: dict, local_path: str) -> None:
    """根据 contents 模型的 type/format 把内容写入本地文件"""
    ctype = model.get("type")
    fmt = model.get("format")
    content = model.get("content")

    if ctype == "directory":
        raise RuntimeError(f"目标是目录而非文件，无法下载: {model.get('path')}")

    # 确保父目录存在
    parent = os.path.dirname(os.path.abspath(local_path))
    if parent:
        os.makedirs(parent, exist_ok=True)

    if fmt == "json":
        # notebook 或 json 内容：格式化写出
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    elif fmt == "text":
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content if content is not None else "")
    elif fmt == "base64":
        data = base64.b64decode(content or "")
        with open(local_path, "wb") as f:
            f.write(data)
    else:
        raise RuntimeError(f"未知的内容格式 format={fmt!r}，无法保存")

    size = model.get("size")
    size_info = f"，大小 {size} 字节" if size is not None else ""
    print(f"   ✓ 已保存 (type={ctype}, format={fmt}{size_info})")


# ---------- main ----------

def remote_get_file(
    *,
    notebook_id: str,
    local_path: str | None = None,
    timeout: int = DEFAULTS["timeout"],
) -> str:
    """
    下载 notebook_id 对应 NotebookCosUri 所指向的 .ipynb 文件到本地。

    参数:
        notebook_id : Notebook 实例 ID（如 notebook-xxx）
        local_path  : 本地保存路径（可选，不传则用远程文件名保存到当前目录）
        timeout     : HTTP 请求超时秒数，默认 300

    返回:
        本地保存路径
    """
    print(f"[STEP 1] 目标实例: {notebook_id}")

    instance_url, remote_notebook_path = _resolve_instance_info(notebook_id)
    base = f"https://{instance_url}"

    # local_path 未指定则用远程文件名
    if not local_path:
        local_path = os.path.basename(remote_notebook_path)
    print(f"[STEP 1] 本地保存路径: {local_path}")

    s = _create_session(base)
    model = _fetch_contents(s, base, remote_notebook_path, timeout)
    _save_contents(model, local_path)

    print(f"\n[STEP 2] ✅ 下载完成: {local_path}")
    return local_path


# ---------- CLI ----------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python remote_get.py <notebookId> [localPath]")
        print("示例: python remote_get.py notebook-xxx")
        print("      python remote_get.py notebook-xxx ./demo.ipynb")
        sys.exit(1)

    notebook_id = sys.argv[1]
    local_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        remote_get_file(
            notebook_id=notebook_id,
            local_path=local_path,
        )
    except Exception as e:
        print(f"❌ 远程下载失败: {e}", file=sys.stderr)
        sys.exit(1)
