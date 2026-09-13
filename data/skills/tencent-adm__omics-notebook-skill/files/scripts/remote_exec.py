#!/usr/bin/env python3
"""
远程执行 Jupyter Notebook（Python 实现）

替代 control.js + main.js，提供创建 kernel、逐个 cell 执行、回写结果的完整流程。

依赖：pip install requests websocket-client

用法 — 作为模块导入：
    from remote_exec import remote_exec
    session_url, callback_url = remote_exec(
        local_notebook_path="demo.ipynb",
        notebook_id="notebook-xxx",
        # kernel_id="xxx"  # 可选：复用已有 kernel
    )
"""

import json
import os
import re
import subprocess
import sys
import time
import uuid as uuid_mod
from pathlib import Path

import requests
from websocket import create_connection

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
    "timeout": 2400,
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


def _load_notebook(local_path: str) -> tuple[dict, list[str], str]:
    """返回 (notebook_dict, code_source_list, kernel_name)"""
    with open(local_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    kernel_name = nb.get("metadata", {}).get("kernelspec", {}).get("name", "python3")
    code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
    codes = [
        "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        for c in code_cells
    ]

    print(f"   📄 从 {local_path} 加载: {len(nb.get('cells', []))} cells, "
          f"{len(codes)} code cells, kernel={kernel_name}")
    return nb, codes, kernel_name


# ---------- steps ----------

def _upload_notebook(
    session: requests.Session,
    base: str,
    remote_path: str,
    notebook: dict,
) -> None:
    """PUT /api/contents/{path} 创建远端 notebook 文件"""
    remote_path = remote_path.lstrip("/")
    url = f"{base}/api/contents/{remote_path}"
    body = {"type": "notebook", "format": "json", "content": notebook}
    print(f"① 创建文件: {remote_path}")
    resp = session.put(url, json=body)
    resp.raise_for_status()
    print(f"   ✓ 文件已创建: {remote_path}")


def _create_kernel(
    session: requests.Session,
    base: str,
    kernel_name: str,
    kernel_id: str | None,
) -> str:
    """POST /api/kernels — 如果提供了 kernel_id 则尝试复用，否则新建"""
    if kernel_id:
        print(f"② 复用 kernel: {kernel_id}")
        return kernel_id
    print(f"② 创建 kernel: {kernel_name}")
    url = f"{base}/api/kernels"
    resp = session.post(url, json={"name": kernel_name})
    resp.raise_for_status()
    kid = resp.json()["id"]
    print(f"   ✓ kernel id: {kid}")
    return kid


def _execute_cell(
    base: str,
    kernel_id: str,
    code: str,
    cell_index: int,
    total: int,
    timeout: int,
) -> list[dict]:
    """WebSocket 连接到 kernel，执行一个 cell 的代码，返回 output 列表"""
    label = f"Cell {cell_index + 1}/{total}"
    print(f"\n--- {label} ---")
    print("③ 连接 WebSocket 执行代码...")

    ws_url = (
        base.replace("https://", "wss://")
        + f"/api/kernels/{kernel_id}/channels?token={DEFAULTS['xsrf_token']}"
    )
    ws = create_connection(
        ws_url,
        header={
            "Cookie": f"omics_session={_load_session()}; _xsrf={DEFAULTS['xsrf_token']}"
        },
        timeout=timeout,
    )
    print("   ✓ WebSocket 已连接，发送 execute_request")

    msg_id = str(uuid_mod.uuid4())
    session_id = str(uuid_mod.uuid4())

    execute_request = {
        "channel": "shell",
        "header": {
            "msg_id": msg_id,
            "session": session_id,
            "username": "",
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "msg_type": "execute_request",
            "version": "5.3",
        },
        "parent_header": {},
        "metadata": {},
        "content": {
            "code": code,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": False,
            "stop_on_error": True,
        },
        "buffers": [],
    }
    ws.send(json.dumps(execute_request))

    outputs: list[dict] = []

    try:
        while True:
            raw = ws.recv()
            msg = json.loads(raw)
            if msg.get("parent_header", {}).get("msg_id") != msg_id:
                continue

            msg_type = msg.get("msg_type")
            content = msg.get("content", {})

            if msg_type == "stream":
                text = content.get("text", "")
                print(f"   [stream:{content.get('name')}]", text.rstrip())
                outputs.append({
                    "type": "stream",
                    "name": content.get("name"),
                    "text": text,
                })
            elif msg_type == "execute_result":
                data = content.get("data", {}).get("text/plain", "")
                print("   [result]", data)
                outputs.append({"type": "result", "data": data})
            elif msg_type == "display_data":
                print("   [display_data]", list(content.get("data", {}).keys()))
                outputs.append({"type": "display", "data": content.get("data", {})})
            elif msg_type == "error":
                print(f"   [error] {content.get('ename')} {content.get('evalue')}")
                outputs.append({
                    "type": "error",
                    "ename": content.get("ename"),
                    "evalue": content.get("evalue"),
                })
            elif msg_type == "status":
                if content.get("execution_state") == "idle":
                    print("   ✓ 执行完毕 (idle)")
                    break
    finally:
        ws.close()

    return outputs


def _to_jupyter_outputs(cell_outputs: list[dict]) -> list[dict]:
    """将内部 output 格式转换为 Jupyter notebook output 格式"""
    result = []
    for o in cell_outputs:
        t = o.get("type")
        if t == "stream":
            result.append({
                "output_type": "stream",
                "name": o.get("name"),
                "text": o.get("text"),
            })
        elif t == "display":
            result.append({
                "output_type": "display_data",
                "data": o.get("data"),
            })
        elif t == "result":
            result.append({
                "output_type": "execute_result",
                "data": {"text/plain": o.get("data")},
                "execution_count": None,
            })
        elif t == "error":
            result.append({
                "output_type": "error",
                "ename": o.get("ename"),
                "evalue": o.get("evalue"),
                "traceback": [],
            })
        else:
            result.append(o)
    return result


def _writeback(
    local_path: str,
    notebook: dict,
    per_cell_outputs: list[list[dict]],
    session: requests.Session,
    base: str,
    remote_path: str,
) -> None:
    """回写：将每个 code cell 的 output 填入 notebook，写回本地 .ipynb 并同步覆盖远程实例上的对应文件"""
    output_nb = json.loads(json.dumps(notebook))  # deep copy
    code_cells = [c for c in output_nb.get("cells", []) if c.get("cell_type") == "code"]
    for i, cell in enumerate(code_cells):
        if i < len(per_cell_outputs):
            cell["execution_count"] = i + 1
            cell["outputs"] = _to_jupyter_outputs(per_cell_outputs[i])
        else:
            cell["outputs"] = []

    # 1) 写回本地
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(output_nb, f, ensure_ascii=False, indent=2)
    print(f"\n📝 本地 notebook 已更新（含执行结果）: {local_path}")

    # 2) 同步覆盖远程实例上的对应 notebook（同一路径 PUT 即为更新）
    print("📤 将执行结果回写到远程实例...")
    _upload_notebook(session, base, remote_path, output_nb)
    print(f"   ✓ 远程 notebook 已更新（含执行结果）: {remote_path.lstrip('/')}")


# ---------- 入口函数 ----------

def remote_exec(
    *,
    local_notebook_path: str,
    notebook_id: str,
    kernel_id: str | None = None,
    timeout: int = DEFAULTS["timeout"],
) -> str:
    """
    远程执行 Jupyter Notebook 并回写结果。

    参数:
        local_notebook_path  : 本地 .ipynb 文件路径
        notebook_id          : Notebook 实例 ID（如 notebook-xxx）
        kernel_id            : 可选，复用已有 kernel
        timeout              : WebSocket 整体超时秒数，默认 2400

    返回:
        set-session 链接，用于在编辑器中打开
    """
    print(f"[STEP 1] 本地文件: {local_notebook_path}")
    print(f"[STEP 1] 目标实例: {notebook_id}")

    # 通过 omics CLI 解析 instance_url 和 remote_notebook_path
    instance_url, remote_notebook_path = _resolve_instance_info(notebook_id)

    base = f"https://{instance_url}"

    print(f"[STEP 1] 远程执行目标: {base}")
    print(f"[STEP 1] 远程路径: {remote_notebook_path}")

    # 加载本地 notebook
    nb, codes, kernel_name = _load_notebook(local_notebook_path)

    # 创建 HTTP session
    s = _create_session(base)

    # 上传
    _upload_notebook(s, base, remote_notebook_path, nb)

    # 创建/复用 kernel
    kid = _create_kernel(s, base, kernel_name, kernel_id)

    # 逐个 cell 执行
    all_outputs: list[dict] = []
    per_cell_outputs: list[list[dict]] = []
    for i, code in enumerate(codes):
        cell_outputs = _execute_cell(base, kid, code, i, len(codes), timeout)
        per_cell_outputs.append(cell_outputs)
        all_outputs.extend(cell_outputs)

    # 回写（本地 + 远程实例）
    _writeback(local_notebook_path, nb, per_cell_outputs, s, base, remote_notebook_path)

    print(f"\n[STEP 2] ✅ 执行完成，收到 {len(all_outputs)} 条输出")
    print(f"[STEP 2] 📝 本地已更新: {local_notebook_path}")

    # 生成打开链接
    sid = _load_session()
    callback_url = f"https://{instance_url}/lab/tree/{remote_notebook_path.lstrip('/')}"
    session_url = (
        "https://genomics.qq.com/platform/cli/set-session"
        f"?session={requests.utils.quote(sid, safe='')}"
    )
    print(f"\n[STEP 3] 🔗 先设置 session: {session_url}")
    print(f"[STEP 3] 🔗 再打开 notebook: {callback_url}")

    return session_url, callback_url


# ---------- CLI ----------

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python remote_exec.py <notebookId> <localNotebook> [kernelId]")
        print("示例: python remote_exec.py notebook-xxx demo.ipynb")
        sys.exit(1)

    notebook_id = sys.argv[1]
    local_notebook_path = sys.argv[2]
    kernel_id = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        remote_exec(
            local_notebook_path=local_notebook_path,
            notebook_id=notebook_id,
            kernel_id=kernel_id,
        )
    except Exception as e:
        print(f"❌ 远程执行失败: {e}", file=sys.stderr)
        sys.exit(1)
