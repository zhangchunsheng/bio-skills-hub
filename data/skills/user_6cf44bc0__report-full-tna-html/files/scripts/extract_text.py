# -*- coding: utf-8 -*-
"""Extract full text from a PDF with `===== PAGE N =====` separators.

Usage:
    python extract_text.py <src.pdf> <out.txt>
"""
import pymupdf, sys


def main(src, out):
    doc = pymupdf.open(src)
    chunks = []
    total_words = 0
    for pno, page in enumerate(doc, start=1):
        t = page.get_text('text')
        total_words += len(t.split())
        chunks.append('\n===== PAGE %d =====\n%s\n' % (pno, t))
    with open(out, 'w', encoding='utf-8') as f:
        f.write(''.join(chunks))
    print('pages:', doc.page_count, 'words:', total_words, '->', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
