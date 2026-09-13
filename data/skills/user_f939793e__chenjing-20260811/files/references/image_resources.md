# Clinical Image Resource Module

Provide teaching images for the disease, scaled to Level (Level 1: typical signs/imaging;
Level 2: add pathology; Level 3: add mechanism/molecular figures). Every image MUST be
verified reachable and license-checked before inclusion — never embed an image whose source or
rights are unknown.

## Preferred open sources (verify link + license)
- **PubMed Central (PMC)** — open-access article figures (check article license, usually CC/BY or CC/BY-NC).
- **CDC / WHO** — public-health and clinical images, mostly public domain or CC.
- **Open-access journals** — NEJM, Lancet, JAMA, BMJ, Frontiers, etc. (respect CC license & attribution).
- **NIH / NCI Visuals Online**, **Openi**, **Wikimedia Commons** (verify license tag).

## Per-image metadata (always include)
For each image emit:
```
名称 (Name): <descriptive title>
临床意义 (Clinical significance): <what it teaches>
来源 (Source): <URL + article/publisher>
版权信息 (Copyright/License): <e.g., CC BY 4.0 / Public Domain / © publisher — used under fair use for education>
```
- If license is unclear or non-commercial-only and the use is educational, label it explicitly and
  note "for educational use; obtain permission for redistribution".

## Image categories to cover
- 典型体征图片 (typical physical signs)
- 影像 (imaging: X-ray / CT / MRI / US)
- 病理 (pathology: gross / microscopy / IHC)
- 分子机制图 (mechanism / pathway / biomarker figures) — Level 3

## Note on embedding in IMA
IMA note import supports Markdown but NOT local image files. For IMA sync, use **network image
URLs only** (https://…). Strip any local `file:///` or `/Users/...` references and tell the user.
