# -*- coding: utf-8 -*-
"""
pc_push.py — Protein & Cell 公众号论文推介：docx -> 草稿箱 推送器

将一篇已按 P&C 栏目结构排好版、并内嵌示意图的 Word 文档，
一键推送到微信公众号草稿箱。图片与封面均正确上传（已修复「图片丢失」bug）。

关键修复（相对早期版本）：
- 正文内图片必须用 material/add_material(type=image) 上传，返回 dict 含 'url'，
  再把 url 写进 <img src>。早期误用 media/upload?type=image（只返回 media_id、无 url），
  导致 <img> 整段丢失。
- docx 关系路径是相对路径 'media/image1.png'，不是 'word/media/...'，
  故用 basename 命中 media_files 来建 rid-> 媒体文件名映射。
- 封面(thumb_media_id)同样来自 material/add_material，取返回的 media_id。

纯标准库实现（urllib / zipfile / tempfile），不依赖 requests。

用法：
  python pc_push.py --docx ARTICLE.docx --title "标题" \
      --digest "摘要(<=120字)" --author "P&C编辑部" \
      [--old-media-id OLD_ID] [--cover COVER.jpg] [--dry-run]

环境变量：WECHAT_APP_ID / WECHAT_APP_SECRET（也可 --appid / --appsecret 传入）
"""
import os, sys, json, zipfile, tempfile, argparse, urllib.request, urllib.parse
from docx import Document
from docx.oxml.ns import qn

NAVY = '#1F3864'   # 海军蓝：小标题 / 大标题
RED  = '#B91C1C'   # 学术红：栏目标题下边框
BLACK = '#333333'  # 正文

# ---------- 极简 .env 读取（不依赖第三方库） ----------
def load_dotenv(path=None):
    """从 .env 读取键值（仅作环境变量兜底）。
    查找顺序：path(显式) -> 当前工作目录 .env -> 脚本同目录 .env。
    支持 # 注释、KEY=VALUE、值可用引号包裹。"""
    candidates = []
    if path:
        candidates.append(path)
    candidates.append(os.path.join(os.getcwd(), '.env'))
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
    for p in candidates:
        if not os.path.exists(p):
            continue
        env = {}
        try:
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k:
                        env[k] = v
        except Exception:
            return {}
        return env   # 命中第一个存在的 .env 即用
    return {}

# ---------- WeChat HTTP（纯标准库） ----------
def http_get_json(url):
    return json.loads(urllib.request.urlopen(url, timeout=30).read().decode('utf-8'))

def upload_material(token, file_path, name):
    """material/add_material?type=image -> {'media_id':..., 'url':...}"""
    boundary = '----wb' + os.urandom(8).hex()
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="media"; filename="{name}"; filelength={len(file_bytes)}\r\n'
        f'Content-Type: application/octet-stream\r\n\r\n'
    ).encode() + file_bytes + b'\r\n' + f'--{boundary}--\r\n'.encode()
    ep = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
    req = urllib.request.Request(ep, data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}, method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode('utf-8'))

def http_post_json(url, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=body,
        headers={'Content-Type': 'application/json; charset=utf-8'}, method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode('utf-8'))

def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') \
                    .replace('"', '&quot;').replace("'", '&#39;')

# ---------- 抽 docx 媒体文件 + rid 映射 ----------
def load_media(doc, docx_path):
    """返回 (media_files{basename->localpath}, rid_to_media{rid->basename})"""
    tmpdir = tempfile.mkdtemp()
    media_files = {}
    with zipfile.ZipFile(docx_path) as z:
        for name in z.namelist():
            if name.startswith('word/media/'):
                out = os.path.join(tmpdir, os.path.basename(name))
                with open(out, 'wb') as fp, z.open(name) as src:
                    fp.write(src.read())
                media_files[os.path.basename(name)] = out
    rid_to_media = {rid: os.path.basename(rel.target_ref)
                    for rid, rel in doc.part.rels.items()
                    if os.path.basename(rel.target_ref) in media_files}
    return media_files, rid_to_media

# ---------- 封面：优先 --cover，否则取 docx 首张内嵌图 ----------
def get_cover(token, doc, docx_path, media_files, rid_to_media, cover_path=None):
    if cover_path and os.path.exists(cover_path):
        r = upload_material(token, cover_path, os.path.basename(cover_path))
        if 'media_id' not in r:
            print('  [封面] 上传失败:', r); return None
        print('  [封面] 使用 --cover ->', r['media_id'])
        return r['media_id']
    # 自动取 docx 第一张图片（即「图示」示意图）
    body = doc.element.body
    for elem in body.iterchildren():
        if elem.tag == qn('w:p'):
            blips = elem.findall('.//' + qn('a:blip'))
            if blips:
                rid = blips[0].get(qn('r:embed'))
                mf = rid_to_media.get(rid)
                if mf:
                    local = media_files.get(mf)
                    if local:
                        r = upload_material(token, local, mf)
                        if 'media_id' not in r:
                            print('  [封面] 自动抽取失败:', r); return None
                        print('  [封面] 自动取 docx 首图 ->', r['media_id'])
                        return r['media_id']
    print('  [封面] 未找到任何图片'); return None

# ---------- DOCX -> HTML ----------
def render_docx_to_html(token, doc, media_files, rid_to_media, uploaded):
    def ensure_uploaded(rid, mf):
        if rid in uploaded:
            return uploaded[rid]
        local = media_files.get(mf)
        if not local:
            uploaded[rid] = ''; return ''
        r = upload_material(token, local, mf)
        uploaded[rid] = r.get('url', '')
        if not uploaded[rid]:
            print('  [正文图] 上传无 url:', r)
        return uploaded[rid]

    def img_html_for_elem(elem):
        out = []
        for blip in elem.findall('.//' + qn('a:blip')):
            rid = blip.get(qn('r:embed'))
            if not rid:
                continue
            mf = rid_to_media.get(rid)
            if not mf:
                continue
            url = ensure_uploaded(rid, mf)
            if url:
                out.append(f'<p style="text-align:center;margin:10px 0 12px;">'
                           f'<img src="{esc(url)}" style="max-width:100%;border-radius:4px;"></p>')
        return ''.join(out)

    para_by_elem = {p._element: p for p in doc.paragraphs}

    def text_para_html(p_elem):
        p = para_by_elem.get(p_elem)
        if p is None:
            return None
        t = p.text
        if not t.strip():
            return None
        style = p.style.name if p.style else ''
        align = 'left'
        pPr = p_elem.find(qn('w:pPr'))
        if pPr is not None:
            jc = pPr.find(qn('w:jc'))
            if jc is not None and jc.get(qn('w:val')) == 'center':
                align = 'center'
        fr = p.runs[0] if p.runs else None
        fsz = (fr.font.size.pt if fr and fr.font.size else 11)
        fcol = (str(fr.font.color.rgb) if fr and fr.font.color and fr.font.color.rgb else None)
        bold = bool(fr.font.bold) if fr else False
        if fcol == 'B91C1C' and fsz >= 14 and bold:
            return f'<p style="border-bottom:2px solid {RED};padding:6px 0 4px 0;font-weight:bold;color:{RED};font-size:{fsz}px;margin:18px 0 10px;">{esc(t)}</p>'
        if fcol == '1F3864' and fsz >= 18 and bold:
            return f'<p style="text-align:center;color:{NAVY};font-size:{fsz}px;font-weight:bold;margin:20px 0 14px;">{esc(t)}</p>'
        if fcol == '1F3864' and bold and 12 <= fsz < 18:
            return f'<p style="color:{NAVY};font-size:{fsz}px;font-weight:bold;margin:8px 0 4px;">{esc(t)}</p>'
        if style == 'List Number':
            return f'<p style="margin:4px 0 4px 24px;color:{BLACK};font-size:{fsz}px;line-height:1.8;">{esc(t)}</p>'
        if style == 'List Bullet':
            return f'<p style="margin:4px 0 4px 24px;color:{BLACK};font-size:{fsz}px;line-height:1.7;">• {esc(t)}</p>'
        return f'<p style="color:{BLACK};font-size:{fsz}px;text-indent:22px;line-height:1.8;margin:6px 0;">{esc(t)}</p>'

    def table_html(tbl_elem):
        # 表格：逐单元格渲染文字 + 内嵌图（用于作者简介左图右文等）
        parts = []
        for row in tbl_elem.findall(qn('w:tr')):
            for cell in row.findall(qn('w:tc')):
                # 图片
                ih = img_html_for_elem(cell)
                if ih:
                    parts.append(ih)
                for cp in cell.findall(qn('w:p')):
                    th = text_para_html(cp)
                    if th:
                        parts.append(th)
        return ''.join(parts)

    parts = []
    for elem in doc.element.body.iterchildren():
        if elem.tag == qn('w:p'):
            ih = img_html_for_elem(elem)
            if ih:
                parts.append(ih); continue
            th = text_para_html(elem)
            if th:
                parts.append(th)
        elif elem.tag == qn('w:tbl'):
            th = table_html(elem)
            if th:
                parts.append(th)
        # w:sectPr 忽略
    return ('<section style="font-family:Microsoft YaHei, PingFang SC, Helvetica, Arial, sans-serif;'
            f'color:{BLACK};max-width:677px;margin:0 auto;padding:0 8px;">'
            + ''.join(parts) + '</section>')

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description='P&C 公众号 docx -> 草稿箱 推送器')
    ap.add_argument('--docx', required=True, help='已排版的 docx 路径')
    ap.add_argument('--title', required=True, help='推文标题（<=32字）')
    ap.add_argument('--digest', default='', help='摘要（<=120字，留空自动取首段正文）')
    ap.add_argument('--author', default='P&C编辑部', help='作者（<=8字）')
    ap.add_argument('--old-media-id', default='', help='可选：推送前删除的旧草稿 media_id')
    ap.add_argument('--cover', default='', help='可选：封面图路径；缺省自动取 docx 首张图')
    ap.add_argument('--appid', default='', help='公众号 AppID（或环境变量 WECHAT_APP_ID）')
    ap.add_argument('--appsecret', default='', help='公众号 AppSecret（或环境变量 WECHAT_APP_SECRET）')
    ap.add_argument('--dry-run', action='store_true', help='只解析+渲染，不调用微信接口')
    args = ap.parse_args()

    if not os.path.exists(args.docx):
        print('ERROR: docx 不存在:', args.docx); sys.exit(1)

    doc = Document(args.docx)
    media_files, rid_to_media = load_media(doc, args.docx)
    print(f'[解析] 段落={len(doc.paragraphs)} 表格={len(doc.tables)} '
          f'媒体文件={len(media_files)} 图片关系={len(rid_to_media)}')

    # dry-run：本地验证，不联网
    if args.dry_run:
        uploaded = {}
        # 不真正上传，仅统计
        cnt_imgs = 0
        for elem in doc.element.body.iterchildren():
            if elem.tag == qn('w:p'):
                cnt_imgs += len(elem.findall('.//' + qn('a:blip')))
        print(f'[dry-run] 预计内嵌图片数={cnt_imgs}（联网上传后注入 <img>）')
        print(f'[dry-run] 标题="{args.title}" 作者="{args.author}"')
        print('[dry-run] 完成，未调用微信接口。')
        return

    dotenv = load_dotenv()
    APP_ID = args.appid or os.environ.get('WECHAT_APP_ID') or dotenv.get('WECHAT_APP_ID', '')
    APP_SECRET = args.appsecret or os.environ.get('WECHAT_APP_SECRET') or dotenv.get('WECHAT_APP_SECRET', '')
    if not APP_ID or not APP_SECRET:
        print('ERROR: 缺少 WECHAT_APP_ID / WECHAT_APP_SECRET（可放环境变量、.env 或 --appid/--appsecret）'); sys.exit(1)

    token = http_get_json(
        f'https://api.weixin.qq.com/cgi-bin/token?{urllib.parse.urlencode({"grant_type":"client_credential","appid":APP_ID,"secret":APP_SECRET})}'
    )['access_token']

    # 封面
    thumb_mid = get_cover(token, doc, args.docx, media_files, rid_to_media,
                          cover_path=args.cover or None)
    if not thumb_mid:
        print('封面上传失败，终止'); sys.exit(1)

    # 正文 HTML
    uploaded = {}
    html = render_docx_to_html(token, doc, media_files, rid_to_media, uploaded)
    print(f'[渲染] HTML 长度={len(html)} <img> 数={html.count("<img")}')

    # 摘要：留空则取第一段非标题正文
    digest = args.digest
    if not digest:
        for p in doc.paragraphs:
            t = p.text.strip()
            if t and len(t) > 10:
                digest = t[:110]; break

    # 删除旧草稿
    if args.old_media_id:
        try:
            dr = http_post_json(f'https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}',
                                {'media_id': args.old_media_id})
            print('[删除旧稿]', dr)
        except Exception as e:
            print('[删除旧稿警告]', e)

    # 新建草稿
    article = {
        'title': args.title,
        'author': args.author,
        'digest': digest,
        'content': html,
        'content_source_url': '',
        'need_open_comment': 0,
        'only_fans_can_comment': 0,
        'thumb_media_id': thumb_mid,
    }
    add_resp = http_post_json(f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}',
                              {'articles': [article]})
    print('[新建草稿]', add_resp)
    print('NEW_MEDIA_ID =', add_resp.get('media_id'))

if __name__ == '__main__':
    main()
