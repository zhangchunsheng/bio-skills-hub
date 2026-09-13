# -*- coding: utf-8 -*-
"""
判别 PDF 的「涂黑脱敏」是视觉脱敏（可恢复）还是真脱敏（不可恢复）。

原理：
  - 视觉脱敏：PDF 上画了黑色填充矩形盖住文字，但文字层完好 -> 可恢复、应翻译
  - 真脱敏：文字层里的字符已被替换成 ■ / ● 等占位字形 -> 不可恢复
  - 混合：正文可恢复、但图片/图形内部的文字在文件层面已被删除（需逐处判断）

用法：
  python check_redaction.py <pdf> [--pages 1-10] [--samples 15]

输出：黑框数、被覆盖 span 数、■ 字形 span 数、可恢复样本，以及最终判别结论。
"""
import sys
import argparse

import pymupdf


def black_boxes(page):
    """页面上的近黑色填充矩形（面积 >3x3pt）。"""
    out = []
    for d in page.get_drawings():
        f = d.get('fill')
        if f is None:
            continue
        if max(f) < 0.15:
            r = pymupdf.Rect(d['rect'])
            if r.width > 3 and r.height > 3:
                out.append(r)
    return out


def page_nums(spec, total):
    if not spec:
        return list(range(1, total + 1))
    res = []
    for seg in spec.split(','):
        seg = seg.strip()
        if '-' in seg:
            a, b = seg.split('-', 1)
            res.extend(range(int(a), int(b) + 1))
        else:
            res.append(int(seg))
    return [p for p in res if 1 <= p <= total]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--pages', default='', help='如 1-10,20,35；默认全文档')
    ap.add_argument('--samples', type=int, default=15)
    ap.add_argument('--cover', type=float, default=0.6, help='判定被覆盖的相交面积占比阈值')
    args = ap.parse_args()

    doc = pymupdf.open(args.pdf)
    pages = page_nums(args.pages, doc.page_count)

    total_boxes = 0
    spans_under = 0
    glyph_placeholder = 0
    normal_spans = 0
    samples = []

    for pno in pages:
        page = doc[pno - 1]
        boxes = black_boxes(page)
        total_boxes += len(boxes)

        for b in page.get_text('dict')['blocks']:
            if b['type'] != 0:
                continue
            for line in b.get('lines', []):
                for s in line['spans']:
                    txt = s['text']
                    if any(ch in txt for ch in ('■', '●', '█', '▇')):
                        glyph_placeholder += 1
                        continue
                    if not txt.strip():
                        continue
                    normal_spans += 1
                    sr = pymupdf.Rect(s['bbox'])
                    sr_area = max(sr.get_area(), 1e-6)
                    for box in boxes:
                        inter = sr & box
                        if not inter.is_empty and inter.get_area() > args.cover * sr_area:
                            spans_under += 1
                            if len(samples) < args.samples:
                                samples.append((pno, txt[:70].replace('\n', ' ')))
                            break

    print('扫描页数            :', len(pages))
    print('黑框（近黑填充矩形）:', total_boxes)
    print('文本 span 总数      :', normal_spans)
    print('被黑框覆盖的 span   :', spans_under)
    print('■/● 占位字形 span   :', glyph_placeholder)

    print('\n--- 可恢复样本（黑框下的真实文字）---')
    for pno, t in samples:
        print(f'  p{pno}: {t}')
    if not samples:
        print('  （无）')

    print('\n--- 判别结论 ---')
    if glyph_placeholder == 0 and spans_under > 0:
        print('【视觉脱敏 → 可恢复】：黑框只是盖在完整文字层之上，无占位字形。')
        print('  处理原则：用不带脱敏逻辑的提取器拿到完整文本，被覆盖内容照常翻译写入译文。')
        print('  ⚠ 不要用「脱敏感知提取器」把覆盖文本替换成 ■ —— 那是自我阉割。')
    elif glyph_placeholder > 0 and spans_under == 0:
        print('【真脱敏 → 不可恢复】：文字层已被占位字形替换。')
        print('  处理原则：占位处保留 ■ 并在术语清单注明「原文此处已脱敏」。')
    elif glyph_placeholder > 0 and spans_under > 0:
        print('【混合脱敏】：部分占位替换、部分仅视觉覆盖，需逐处判断。')
    else:
        print('【未发现脱敏痕迹】：无黑框或未被覆盖文本，按普通 PDF 处理。')


if __name__ == '__main__':
    main()
