#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布本地技能到 SkillHub 企业源（org）。

鉴权方式（关键，来自控制台发布请求的 DevTools 抓包）：
  企业源发布走**控制台会话 JWT**，通过 Cookie `skh_ent_token` 传递，
  而不是 `sk-ent-` API Key（API Key 对企业源注册表只读，写会 401）。

接口结构：
  POST https://api.skillhub.cn/api/v1/orgs/{org_id}/skills/{slug}/versions
  Content-Type: multipart/form-data; boundary=...
  Cookie: skh_ent_token={JWT}
  Body:
    part "payload" : JSON {version, displayName, iconUrl?, categoryIds?}
    part "files"   : 每个文件一个，name="files"，filename=相对路径，内容=文件字节

用法：
  export SKILLHUB_ENT_TOKEN="eyJ..."      # 控制台 DevTools 抓的会话 token（有时效，通常 24h）
  python publish_enterprise.py --dir . --slug wmqe-pharma-sales-data --org-id 891
  --version 1.2.0       指定版本（缺省读 SKILL.md frontmatter）
  --display-name "..."  指定展示名（缺省读 SKILL.md frontmatter）
  --get-version         只读查询当前线上版本（不发布）
  --dry-run             只构造请求并打印，不发送
  --host                自定义 host（默认 https://api.skillhub.cn）
"""
import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

DEFAULT_HOST = "https://api.skillhub.cn"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0")
EXCL_DIRS = {".git", ".idea", ".vscode", "node_modules", "__pycache__"}
EXCL_SUF = (".pyc", ".DS_Store", "Thumbs.db", ".swp")


def parse_frontmatter(path):
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    assert lines[0].strip() == "---", "SKILL.md 无 frontmatter"
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    fm = {}
    for raw in lines[1:end]:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            fm[k] = [s.strip().strip("'\"") for s in inner.split(",") if s.strip()] if inner else []
        else:
            fm[k] = v.strip("'\"")
    return fm


def collect_files(skill_dir):
    files = []
    for root, dirs, fnames in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in EXCL_DIRS]
        for fn in fnames:
            if any(fn.endswith(s) for s in EXCL_SUF):
                continue
            p = os.path.join(root, fn)
            if os.path.islink(p):
                continue
            rel = os.path.relpath(p, skill_dir).replace(os.sep, "/")
            files.append((rel, open(p, "rb").read()))
    return files


def build_body(payload_bytes, files):
    boundary = "----skillhubBoundary" + str(int(time.time() * 1000))
    body = bytearray()

    def add(name, data, filename=None, ctype="application/octet-stream"):
        body.extend(f"--{boundary}\r\n".encode())
        if filename:
            body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode())
        else:
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n'.encode())
        body.extend(f"Content-Type: {ctype}\r\n\r\n".encode())
        body.extend(data)
        body.extend(b"\r\n")

    add("payload", payload_bytes, ctype="application/json")
    for rel, data in files:
        add("files", data, filename=rel, ctype="application/octet-stream")
    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), boundary


def get_version(host, org_id, slug, token):
    url = f"{host.rstrip('/')}/api/v1/orgs/{org_id}/skills/{slug}/versions"
    req = urllib.request.Request(url, headers={
        "Cookie": f"skh_ent_token={token}",
        "Accept": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:600]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:600]


def get_icon_url(host, org_id, slug, token):
    """从技能详情取 iconUrl（对齐控制台发布请求里携带的 iconUrl 字段）。"""
    url = f"{host.rstrip('/')}/api/v1/orgs/{org_id}/skills/{slug}"
    req = urllib.request.Request(url, headers={
        "Cookie": f"skh_ent_token={token}",
        "Accept": "application/json",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.loads(resp.read().decode("utf-8", "replace"))
        return (d.get("skill") or {}).get("iconUrl")
    except Exception:
        return None


def publish(host, org_id, slug, payload, files, token):
    url = f"{host.rstrip('/')}/api/v1/orgs/{org_id}/skills/{slug}/versions"
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    body, boundary = build_body(payload_bytes, files)
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Cookie": f"skh_ent_token={token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "*/*",
        "Origin": "https://skillhub.cn",
        "Referer": "https://skillhub.cn/",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:800]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:800]
        # 平台门控：同一技能同时只能有一个待审版本
        if e.code == 409 or "审核" in body or "pending" in body.lower():
            return e.code, ("[门控] 当前有版本正在审核中，平台不允许并发待审。"
                            "需先在 SkillHub 控制台处理掉 pending 版本"
                            "（撤回 或 通过审批），再重新发布。原始返回：" + body)
        return e.code, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="技能目录（含 SKILL.md）")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--org-id", type=int, default=891)
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--version", default=None)
    ap.add_argument("--display-name", default=None)
    ap.add_argument("--icon-url", default=None, help="图标 URL（缺省自动从技能详情抓取）")
    ap.add_argument("--get-version", action="store_true", help="只读查当前线上版本")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = os.environ.get("SKILLHUB_ENT_TOKEN")
    if not token and not args.get_version and not args.dry_run:
        print("[ERROR] 需要环境变量 SKILLHUB_ENT_TOKEN（控制台会话 JWT，cookie 名 skh_ent_token）",
              file=sys.stderr)
        sys.exit(2)

    skill_md = os.path.join(args.dir, "SKILL.md")
    fm = parse_frontmatter(skill_md) if os.path.exists(skill_md) else {}
    version = args.version or fm.get("version")
    display_name = args.display_name or fm.get("displayName")
    assert version, "无法确定版本号（用 --version 或 SKILL.md frontmatter）"
    assert display_name, "无法确定 displayName（用 --display-name 或 SKILL.md frontmatter）"

    if args.get_version:
        if not token:
            print("[ERROR] --get-version 需要 SKILLHUB_ENT_TOKEN", file=sys.stderr)
            sys.exit(2)
        st, body = get_version(args.host, args.org_id, args.slug, token)
        print(f"[GET] HTTP {st}\n{body}")
        return

    files = collect_files(args.dir)
    icon_url = args.icon_url
    if not icon_url and token:
        icon_url = get_icon_url(args.host, args.org_id, args.slug, token)
    payload = {"version": str(version), "displayName": display_name}
    if icon_url:
        payload["iconUrl"] = icon_url
    print(f"[INFO] slug={args.slug} org={args.org_id} version={version} displayName={display_name}")
    if icon_url:
        print(f"[INFO] iconUrl: {icon_url[:60]}...")
    print(f"[INFO] {len(files)} files to upload")

    if args.dry_run:
        print("[DRY-RUN] would POST",
              f"{args.host}/api/v1/orgs/{args.org_id}/skills/{args.slug}/versions")
        print("[DRY-RUN] payload:", json.dumps(payload, ensure_ascii=False))
        for rel, _ in files:
            print("  file:", rel)
        return

    if not token:
        print("[ERROR] 发布需要 SKILLHUB_ENT_TOKEN", file=sys.stderr)
        sys.exit(2)
    st, body = publish(args.host, args.org_id, args.slug, payload, files, token)
    print(f"[PUBLISH] HTTP {st}\n{body}")


if __name__ == "__main__":
    main()
