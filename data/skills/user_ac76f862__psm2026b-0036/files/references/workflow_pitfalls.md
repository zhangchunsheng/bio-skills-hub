# Workflow Pitfalls & Fixes — Lessons From Real Runs

## 1. ImageGen filename collision (most common failure)

**Symptom:** You asked for 8 panels but only 3–4 unique files appear, and they
don't match the intended beats.

**Cause:** ImageGen names outputs by second-resolution timestamp + a prefix
derived from the prompt. When several `DeferExecuteTool` calls fire in the same
second with similar opening words, the files overwrite each other.

**Fix:** Make every prompt start with a *different* phrase (see
`panel_prompts.md` → "Distinct opening phrases"). After generation, run
`ls comic_panels/` and confirm the count equals the number of requested panels
before assembling.

## 2. Credit / permission confirmation

Image generation consumes credits (~5–10 per image; a 2-story run ≈ 10 images).
A batch call can be rejected by a permission/quota hook. **Before a large batch,
confirm with the user once.** If rejected, stop and offer the no-regeneration
path (below).

## 3. Keep existing panels, only re-layout ("保留现有分镜，只改排版")

When the user wants a new *format* (e.g. the long vertical WeChat style) but is
happy with the current art, **do not regenerate images**. Reuse the existing
`comic_panels/*.png` and only rebuild the HTML/Word layout. This saves credits
and preserves consistency.

## 4. CJK font in Word (python-docx)

By default python-docx renders Chinese with a fallback font that may look wrong.
Force 微软雅黑 on every run by setting both the run font name **and** the
`w:rFonts` eastAsia attribute. The helper `set_cjk(run)` in
`scripts/build_comic_docx.py` does this — reuse it.

Minimal snippet:

```python
from docx.oxml.ns import qn
def set_cjk(run, font="微软雅黑"):
    run.font.name = font
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = rpr.makeelement(qn('w:rFonts'), {})
        rpr.append(rf)
    for a in ('w:ascii','w:eastAsia','w:hAnsi'):
        rf.set(qn(a), font)
```

## 5. Realistic style vs Old Master Q

The user may show a screenshot of a *realistic* health-infographic comic and ask
to match it. That requires regenerating art with `style: "realistic illustration"`
and banner images (anatomical/liver/artery illustrations). It is a separate
art-generation pass — budget extra credits and confirm before launching.

## 6. Dialogue belongs in HTML/Word, not in the art

AI image models garble Chinese text. Always keep speech bubbles blank in the
generated art and overlay dialogue via HTML `.say` boxes or Word paragraphs.
