# Patent Database Search Guide

This guide provides URLs, search syntax, and tips for searching ECG electrode manufacturing process patents across Chinese and international databases.

---

## 1. Chinese Patent Databases (中国专利数据库)

### 1.1 Google Patents (Chinese subset)

- **URL**: `https://patents.google.com`
- **Search syntax**: Advanced search with `country=CN` filter
- **Chinese search example**: 
  ```
  https://patents.google.com/?q=(心电电极)+(制作工艺)&country=CN&after=20150101&before=20251231
  ```
- **Tips**:
  - Supports both Chinese and English search terms
  - Automatically shows patent families (equivalent patents in different countries)
  - Download PDFs directly for most granted patents
  - Use `before/priority` and `after/priority` for filing date filtering
  - Use `assignee` field to filter by applicant

### 1.2 CNIPA - China National Intellectual Property Administration (国家知识产权局)

- **URL**: `https://pss-system.cponline.cnipa.gov.cn` (patent search service)
- **Alt URL**: `http://www.cnipa.gov.cn` (main portal)
- **Search syntax**: Field-specific search
  ```
  TI=(心电电极) AND AB=(制作工艺) AND PD=[20200101 TO 20251231]
  ```
  - `TI=` Title
  - `AB=` Abstract
  - `CL=` Claims
  - `PA=` Applicant (assignee)
  - `IN=` Inventor
  - `PD=` Publication Date
  - `AD=` Application Date
  - `IPC=` IPC Classification
- **Tips**:
  - Requires free registration for full-text access
  - Best source for authoritative Chinese patent status information
  - Supports CPC classification codes (CPC= field)
  - Can download full patent documents (Chinese only)

### 1.3 SooPAT (搜派网)

- **URL**: `https://www.soopat.com`
- **Search syntax**: Natural language + field filters
  ```
  心电电极 AND 制作工艺
  ```
- **Tips**:
  - Free basic search; paid advanced features
  - Good for Chinese patent family aggregation
  - Shows legal status information
  - Supports IPC code browsing

### 1.4 Zhihuiya / PatSnap (智慧芽)

- **URL**: `https://www.zhihuiya.com` (Chinese) / `https://www.patsnap.com` (English)
- **Tips**:
  - Commercial platform; requires paid subscription for full features
  - Excellent patent analytics and visualization
  - Strong patent family coverage
  - Legal status tracking
  - If the user has a subscription, this is the most feature-rich option

### 1.5 Baiten (佰腾网)

- **URL**: `https://www.baiten.cn`
- **Tips**:
  - Free basic Chinese patent search
  - Moderate coverage of international patents
  - Good for quick lookups

---

## 2. International Patent Databases (国际专利数据库)

### 2.1 Google Patents (Global)

- **URL**: `https://patents.google.com`
- **Search syntax**: Natural language with advanced filters
  ```
  https://patents.google.com/?q=(ECG+electrode)+(manufacturing+OR+fabrication)&after=20150101&before=20251231&country=US,EP,WO,JP
  ```
  - `country=` comma-separated country codes
  - `after=` / `before=` date filtering (YYYYMMDD)
  - `language=` language filter
  - `status=GRANT` or `status=APPLICATION`
  - `type=PATENT` or `type=DESIGN`
  - `assignee=` applicant filter
- **Tips**:
  - Best free resource for global patent search
  - Supports full-text search across millions of patents
  - Shows patent families and citation networks
  - PDF downloads available for most patents
  - CPC code filter: `cpc=A61B5/0408`

### 2.2 Espacenet (European Patent Office)

- **URL**: `https://worldwide.espacenet.com`
- **Search syntax**: Advanced search form
  ```
  Title: ECG electrode
  Abstract: manufacturing OR fabrication
  IPC: A61B5/0408
  ```
- **Tips**:
  - Free access to worldwide patent data
  - Excellent coverage of EP, WO, and national European patents
  - CPC classification search available
  - Machine translation available for many languages
  - Use "Smart Search" for complex Boolean queries

### 2.3 WIPO Patentscope

- **URL**: `https://patentscope.wipo.int`
- **Search syntax**: Field-specific search (CQL - Common Query Language)
  ```
  ((EN_ALLTXT:("ECG electrode")) AND (EN_ALLTXT:(manufactur* OR fabricat*)))
  ```
  - `EN_ALLTXT:` full text (English)
  - `EN_TI:` title (English)
  - `EN_AB:` abstract (English)
  - `IC:` IPC classification
  - `FP:` applicant name
  - `FD:` filing date
- **Tips**:
  - Free access; covers PCT/WO applications extensively
  - Best for international (PCT) patent applications
  - Supports cross-lingual search
  - Can search in Chinese, English, and other languages simultaneously

### 2.4 USPTO Patent Full-Text and Image Database (PatFT)

- **URL**: `https://patft.uspto.gov` (granted patents)
- **URL**: `https://appft.uspto.gov` (published applications)
- **Search syntax**: Field-specific search
  ```
  ABST/(ECG AND electrode AND (manufactur$ OR fabricat$)) AND IC/A61B5/0408
  ```
  - `ABST/` Abstract
  - `TTL/` Title
  - `SPEC/` Specification (full text)
  - `CLM/` Claims
  - `AN/` Assignee name
  - `IN/` Inventor name
  - `ISD/` Issue date (granted)
  - `APD/` Application date
  - `IC/` IPC classification
  - `CPC/` CPC classification
  - `$` truncation symbol (equivalent to `*` in other systems)
- **Tips**:
  - Free; authoritative for US patents
  - USPTO's Patent Public Search (PPUBS) is the newer interface: `https://ppubs.uspto.gov`
  - Patent images available in TIFF format

### 2.5 European Patent Register

- **URL**: `https://register.epo.org`
- **Tips**:
  - Shows legal/procedural status of EP applications
  - Useful for checking if a European patent is still in force
  - Free access

---

## 3. Supplementary Patent Search Resources (补充资源)

### 3.1 Free Patent Search Aggregators

| Platform | URL | Notes |
|---|---|---|
| FreePatentsOnline | `https://www.freepatentsonline.com` | Good for US patents |
| SumoBrain | `https://www.sumobrain.com` | Global search |
| Lens.org | `https://www.lens.org` | Scholarly + patent search |
| EPO Open Patent Services | `https://developers.epo.org` | API access for bulk queries |

### 3.2 Non-Patent Literature (for novelty assessment)

| Resource | URL | Notes |
|---|---|---|
| Google Scholar | `https://scholar.google.com` | Academic papers on electrode manufacturing |
| PubMed | `https://pubmed.ncbi.nlm.nih.gov` | Biomedical literature |
| IEEE Xplore | `https://ieeexplore.ieee.org` | Engineering/electronics literature |
| CNKI | `https://www.cnki.net` | Chinese academic papers |

### 3.3 Patent Classification Browsing

| Resource | URL | Notes |
|---|---|---|
| WIPO IPC | `https://www.wipo.int/classifications/ipc/` | Official IPC hierarchy |
| CPC Scheme | `https://www.uspto.gov/web/patents/classification/` | CPC classification scheme |
| Espacenet CPC | `https://worldwide.espacenet.com/classification` | Browse CPC in Espacenet |

---

## 4. Search Strategy Tips (搜索策略提示)

### 4.1 General Tips

1. **Start broad, then narrow**: Begin with broad keyword searches, then add classification filters and date ranges to narrow results.
2. **Check patent families**: A single invention may have equivalent patents in multiple countries. Use patent family data to avoid counting the same invention multiple times.
3. **Citation analysis**: Forward citations (who cites this patent) and backward citations (what this patent cites) reveal technology flow and related patents.
4. **Legal status check**: Always verify the legal status of key patents. A withdrawn or lapsed patent has different implications than a granted one.
5. **Full-text review**: Abstracts may not reveal manufacturing process details. Read claims and specification for accurate process information.

### 4.2 ECG Electrode-Specific Tips

1. **Cross-reference with non-ECG electrode patents**: EEG electrodes, TENS electrodes, and defibrillator electrodes share manufacturing processes. Search these categories too.
2. **Material patents**: Some key innovations are in electrode materials (e.g., Ag/AgCl formulation, hydrogel composition). Search material-specific patents separately.
3. **Process vs. product patents**: Distinguish between patents on the electrode product itself and patents on the manufacturing process. Both are relevant for innovation analysis.
4. **Chinese vs. international**: Chinese patents tend to focus on process improvements; international patents often cover fundamental electrode designs. Search both for complete coverage.

### 4.3 Database-Specific Notes

- **Google Patents**: Best starting point for free, comprehensive searches. Always use this first.
- **CNIPA**: Essential for authoritative Chinese patent status. Use this to verify any Chinese patent's legal status.
- **Espacenet**: Best for European and PCT patents. Use for international patent family lookup.
- **WIPO Patentscope**: Best for PCT applications. Use to find international filing stage patents.
- **USPTO**: Best for US-specific patents. Use the Patent Public Search (PPUBS) for modern interface.
