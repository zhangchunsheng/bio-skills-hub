# -*- coding: utf-8 -*-
"""云文档链接 → 通用分析H5 全自动管线 (generic-analysis-h5 / cloud-doc mode)

用法:
    python cloud_doc_run.py "<飞书wiki/docx链接>" [--out 输出名.html]

流程:
  1) drive +export --file-extension markdown  → 官方正文 md（含 <sheet> 占位 + 图片外链）
  2) sheets +csv-get 逐个展开内嵌电子表格 → markdown 表格插回原文
  3) drive +export --file-extension pdf      → 导出 PDF，用 PyMuPDF 提取文档原图
     （按图片引用前的最近标题定位页面，排除页宽渲染图/头像小图）
  4) 图片写入 图片和附件/，md 引用改为本地相对路径 → 打包 ZIP（md + 图片和附件/ 同级）
  5) 调用 backend/generic_run.py 跑通用分析 → 输出 H5

依赖: lark-cli(已登录), python3.12+PyMuPDF, 后端报告分析系统(backend/generic_run.py)
"""
import argparse
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- 路径探测
# 跨机器友好：优先环境变量，其次自动探测，最后回退到本机已知路径。
# 换电脑时无需改代码，设 WB_NODE / WB_LARK_RUN_JS / WB_PYTHON / WB_BACKEND 即可。


def find_node() -> str:
    cands = [os.environ.get("WB_NODE"), shutil.which("node"), shutil.which("node.exe"),
             r"C:\Users\尘易顺\.workbuddy\binaries\node\versions\22.22.2\node.exe",
             r"C:\Program Files\nodejs\node.exe"]
    for p in cands:
        if p and os.path.exists(p):
            return p
    raise SystemExit("[✗] 找不到 node.exe，请设置环境变量 WB_NODE")


def find_lark_run_js() -> str:
    cands = [os.environ.get("WB_LARK_RUN_JS"),
             r"C:\Users\尘易顺\.workbuddy\binaries\node\cli-connector-packages\node_modules\@larksuite\cli\scripts\run.js"]
    for p in cands:
        if p and os.path.exists(p):
            return p
    # 在常见 WorkBuddy 安装位置递归探测 lark-cli 包
    roots = [Path.home() / ".workbuddy/binaries/node/cli-connector-packages",
             Path.home() / ".workbuddy"]
    for root in roots:
        if root.exists():
            hit = list(root.rglob("cli/scripts/run.js"))
            if hit:
                return str(hit[0])
    raise SystemExit("[✗] 找不到 lark-cli 的 run.js，请设置环境变量 WB_LARK_RUN_JS")


def find_python() -> str:
    # 优先已知装了 backend 依赖的 3.12；PATH 里的 python 可能是无依赖的 managed 版本
    cands = [os.environ.get("WB_PYTHON"),
             r"C:\Users\尘易顺\AppData\Local\Programs\Python\Python312\python.exe",
             shutil.which("python")]
    for p in cands:
        if p and os.path.exists(p):
            return p
    raise SystemExit("[✗] 找不到 python3.12（需装有 fastapi 等 backend 依赖），请设置环境变量 WB_PYTHON")


def find_backend() -> Path:
    for cand in [Path(os.environ["WB_BACKEND"]) if os.environ.get("WB_BACKEND") else None,
                 HERE.parent / "backend", Path(r"D:\Python代码源\报告分析系统\backend")]:
        if cand and (cand / "generic_run.py").exists():
            return cand
    raise SystemExit("[✗] 找不到 backend/generic_run.py，请用 --backend 指定或设置 WB_BACKEND")


NODE = find_node()
LARK_RUN_JS = find_lark_run_js()


def run_cli(args_list: list[str], desc: str = "", cwd: str = None) -> dict:
    r = subprocess.run([NODE, LARK_RUN_JS, *args_list], capture_output=True, text=True,
                       encoding="utf-8", shell=False, cwd=cwd)
    if r.returncode != 0:
        raise SystemExit(f"[✗] lark-cli {' '.join(args_list[:4])}... 失败: {r.stderr[:300]}")
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        # 导出类命令 stdout 可能混有解析日志，取最后一个 JSON 对象
        idx = r.stdout.rfind("{")
        out = json.loads(r.stdout[idx:]) if idx >= 0 else {}
    if not out.get("ok"):
        raise SystemExit(f"[✗] {desc or 'lark-cli 调用'}失败: {json.dumps(out.get('error', {}), ensure_ascii=False)[:300]}")
    return out


def fetch_export(url: str, ext: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = run_cli(["drive", "+export", "--url", url,
                   "--file-extension", ext, "--output-dir", ".",
                   "--overwrite", "--as", "user"], f"导出 {ext}", cwd=str(out_dir))
    return Path(out_dir) / Path(out["data"]["saved_path"]).name


# ---------------------------------------------------------------- sheet 展开
def fetch_sheet_csv(token: str, sid: str) -> str:
    out = run_cli(["sheets", "+csv-get", "--spreadsheet-token", token,
                   "--sheet-id", sid, "--max-chars", "60000", "--as", "user"], f"读表 {sid}")
    return out["data"].get("annotated_csv", "")


def csv_to_md(raw: str) -> str:
    lines = [re.sub(r"^\[row=\d+\] ", "", ln) for ln in raw.split("\n")]
    rows = list(csv.reader(io.StringIO("\n".join(lines))))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    header, body_start = rows[0], 1
    if len(rows) > 1:
        r0, r1 = rows[0], rows[1]
        blanks0 = sum(1 for c in r0 if not c.strip())
        blanks1 = sum(1 for c in r1 if not c.strip())
        if blanks0 >= 2 and blanks1 < blanks0:
            filled, last = [], ""
            for c in r0:
                if c.strip():
                    last = c.strip()
                filled.append(last)
            header = [(f"{a}-{b.strip()}" if b.strip() and a and a != b.strip() else (b.strip() or a))
                      for a, b in zip(filled, r1)]
            body_start = 2
    header = [h.strip().replace("|", "/").replace("\n", " ") or f"列{i+1}" for i, h in enumerate(header)]
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * width]
    for r in rows[body_start:]:
        cells = [c.strip().replace("|", "/").replace("\n", "<br>") for c in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def expand_sheets(content: str) -> str:
    refs = re.findall(r'<sheet sheet-id="([^"]+)" token="([^"]+)"></sheet>', content)
    if not refs:
        return content, 0
    counter = [0]

    def repl(m):
        counter[0] += 1
        sid, token = m.group(1), m.group(2)
        print(f"  [补表 {counter[0]}/{len(refs)}] {sid} ...", flush=True)
        try:
            md = csv_to_md(fetch_sheet_csv(token, sid))
        except Exception as e:
            print(f"    ⚠ 读取失败: {e}")
            return f"\n> (表格 {sid} 读取失败)\n"
        return f"\n**【数据表 {counter[0]}】**\n\n{md}\n"

    content = re.sub(r'<sheet sheet-id="([^"]+)" token="([^"]+)"></sheet>', repl, content)
    return content, len(refs)


# ---------------------------------------------------------------- PDF 图片提取
def extract_doc_images(pdf_path: Path, md_content: str, out_dir: Path) -> int:
    """按 md 图片引用的锚标题定位 PDF 页面，提取文档原图。
    排除: 页宽渲染图(宽>=1400)、头像/图标小图(宽高<=100)。"""
    import fitz  # PyMuPDF
    doc = fitz.open(str(pdf_path))
    pages_text = [p.get_text() for p in doc]

    # 每个图片引用向上找最近的标题作为锚
    anchors = []
    lines = md_content.split("\n")
    last_title = ""
    img_pat = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
    for ln in lines:
        t = re.match(r"^#{1,6}\s+(.+)$", ln.strip())
        if t:
            last_title = t.group(1).strip().replace("\\", "").strip()
        if img_pat.search(ln):
            anchors.append((last_title, img_pat.search(ln).group(1)[:20]))

    # 收集每页候选图（非头像、非页宽渲染）
    candidates = []  # (page_no, path)
    for pno, text in enumerate(pages_text):
        imgs = doc[pno].get_images(full=True)
        for idx, img in enumerate(imgs):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n > 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            if pix.width <= 100 and pix.height <= 100:
                continue
            if pix.width >= 1400:
                continue
            tmp = out_dir / f"_cand_p{pno+1}_{idx}.png"
            pix.save(str(tmp))
            candidates.append((pno + 1, tmp))

    if not candidates:
        print("  ⚠ PDF 中未提取到候选文档图片")
        return 0

    # 锚标题定位：图片引用前标题文本出现在哪些页 → 取该页候选图
    picked, used_pages = [], set()
    for anchor, _ in anchors:
        if not anchor:
            continue
        # 归一化标题用于匹配（去掉 markdown 转义）
        norm = re.sub(r"\\", "", anchor)
        for pno, txt in enumerate(pages_text, 1):
            if pno in used_pages:
                continue
            if norm[:12] in re.sub(r"\s+", "", txt.replace(" ", "")) or \
               re.sub(r"\s+", "", norm[:12]) in re.sub(r"\s+", "", txt):
                page_cands = [c for c in candidates if c[0] == pno]
                if page_cands:
                    picked.extend(page_cands)
                    used_pages.add(pno)
                    break

    if len(picked) < len(anchors):
        # 兜底：锚定位不足，按出现顺序补齐（跳过已用页）
        for c in candidates:
            if c[0] not in used_pages and len(picked) < len(anchors):
                picked.append(c)
                used_pages.add(c[0])

    # 按 md 引用顺序重命名 image.png / image 1.png / ...
    names = []
    for i, (pno, tmp) in enumerate(picked[: len(anchors) or 999]):
        stem = "image.png" if i == 0 else f"image {i}.png"
        dest = out_dir / stem
        shutil.move(str(tmp), str(dest))
        names.append(stem)
    for p in out_dir.glob("_cand_*.png"):
        p.unlink(missing_ok=True)
    return len(names)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="云文档链接 → 通用分析H5 全自动")
    ap.add_argument("url", help="飞书 wiki/docx 链接")
    ap.add_argument("--out", help="输出 HTML 文件名")
    ap.add_argument("--backend", default="", help="报告分析系统 backend 目录(默认自动探测)")
    ap.add_argument("--model", default="",
                    help="覆盖分析模型(默认 backend/.env 的 DEFAULT_MODEL)；会透传给 generic_run.py 并参与多模态检测")
    ap.add_argument("--no-ai", action="store_true",
                    help="只做导出/补表/提图/打包并建记录，AI 分析由 WorkBuddy 会话内模型完成(不花外部API费用)")
    args = ap.parse_args()

    work = Path(tempfile.mkdtemp(prefix="clouddoc_"))  # 系统临时目录，不在 skill 目录留垃圾
    print(f"[1/5] 导出官方 markdown ...")
    md_file = fetch_export(args.url, "markdown", work)
    content = md_file.read_text(encoding="utf-8")

    print("[2/5] 展开内嵌电子表格 ...")
    content, n_sheets = expand_sheets(content)

    print("[3/5] 导出 PDF 提取文档原图 ...")
    img_dir = work / "图片和附件"
    img_dir.mkdir(exist_ok=True)
    pdf_file = fetch_export(args.url, "pdf", work)
    n_imgs = extract_doc_images(pdf_file, content, img_dir)
    print(f"      图片提取: {n_imgs} 张")

    # 图片外链 → 本地路径（按出现顺序）
    img_names = sorted([f for f in os.listdir(img_dir) if f.startswith("image")],
                       key=lambda f: (0, 0) if f == "image.png" else (1, int(re.search(r"\d+", f).group())))
    if img_names:
        it = iter(img_names)

        def repl_img(m):
            name = next(it, None)
            return f"![{m.group(1)}](图片和附件/{name})" if name else m.group(0)

        content = re.sub(r"!\[([^\]]*)\]\([^)]+\)", repl_img, content)

    # 清理
    content = re.sub(r"&amp;", "&", content)
    content = re.sub(r"&lt;", "<", content)
    content = re.sub(r"&gt;", ">", content)
    content = re.sub(r"&nbsp;", " ", content)
    content = re.sub(r"<title>(.*?)</title>", r"# \1\n", content, flags=re.S)
    content = re.sub(r"<sheet[^>]*></sheet>", "", content)
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    stem = md_file.stem
    full_md = work / f"{stem}-完整.md"
    full_md.write_text(content, encoding="utf-8")

    print("[4/5] 打包 ZIP ...")
    zp = work / f"{stem}-完整.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(full_md, full_md.name)
        for f in img_names:
            z.write(img_dir / f, f"图片和附件/{f}")
    print(f"      ZIP: {zp} ({os.path.getsize(zp)} bytes), 数据表 {n_sheets} 张, 图片 {n_imgs} 张")

    # 定位 backend
    backend = Path(args.backend) if args.backend else find_backend()
    generic_run = backend / "generic_run.py"
    py312 = find_python()

    if args.no_ai:
        # 只建记录，不跑外部 AI；分析交给 WorkBuddy 会话内模型
        cmd = [py312, str(generic_run), "--upload-only", str(zp)]
        r = subprocess.run(cmd, cwd=str(backend))
        if r.returncode != 0:
            raise SystemExit("[✗] 建记录失败，详见上方日志")
        print("\n[✓] 准备完成（--no-ai）：请在 WorkBuddy 会话内让助手读 zip 完成 10 维度分析，"
              "再执行 generic_run.py --id <分析ID> --h5-only 出 H5")
        print("    ⚠ 分析前先做多模态自检：Read 一张「图片和附件/」的图，能描述出内容 → 会话模型是多模态，继续；"
              "Read 失败/看不到图 → 先让用户切换到多模态模型再继续。")
        return

    cmd = [py312, str(generic_run), str(zp)]
    if args.out:
        # 相对当前工作目录解析为绝对路径（不要落在 skill 目录）
        cmd += ["--out", str(Path(args.out).resolve())]
    if args.model:
        cmd += ["--model", args.model]
    print(f"[5/5] 运行通用分析 (约3-5分钟；开始前自动检测模型是否多模态) ...")
    r = subprocess.run(cmd, cwd=str(backend))
    if r.returncode != 0:
        raise SystemExit("[✗] 分析未通过，详见上方日志（常见原因：模型不支持多模态，"
                         "按 generic_run 的提示换多模态模型后重试）")
    print("\n[✓] 完成")


if __name__ == "__main__":
    main()
