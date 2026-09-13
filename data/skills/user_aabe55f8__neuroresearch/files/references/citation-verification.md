# 引用核验自包含协议（内置，无需外部技能）

本文件使本技能在**不依赖 `nature-ref-verifier` 等外部技能**的情况下，也能逐条核验引用的真实性、为主张补引用、并将修正写回 Zotero。若环境已安装 `nature-ref-verifier` / `nature-citation`，可优先调用作加速器；否则严格按本协议执行。**核验是硬性红线：禁止任何编造的 PMID/DOI/作者/卷期流入正式稿。**

## 一、核验表（先建表，再逐条查）

| 序号 | 文中引用文本 | 期望 作者/年/刊/卷/页 | DOI | PMID | 状态 |
|------|--------------|----------------------|-----|------|------|
| [1] | Author YYYY Journal | Author, YYYY, J Name, 12(3), 100-110 | 10.xxxx/yyyy | 35140389 | ✅/⚠️/❌ |

- **状态**：✅ 一致 / ⚠️ 待核（信息不全需补） / ❌ 可疑（编造、卷期错、页码偏差、张冠李戴）。
- 抽验范围：**随机抽查 3–5 条 + 全部「关键支撑」文献**（支撑核心结论、被反复引用的）。
- 修正后**复验至 0 条 ❌** 方可投稿。

## 二、字段核对（逐条）

对每一条，确认以下字段与源一致：
1. 作者（拼写、顺序、人数；超 5 人是否用 et al. 合理）
2. 年份（与卷期匹配；DOI 注册年 vs 发表年）
3. 期刊名（缩写/全称一致，非编造刊名）
4. 卷(期) 与页码（卷年冲突、页码越界是常见编造痕迹）
5. 标题（与数据库记录一致）
6. DOI / PMID 可解析且指向同一文献

## 三、直接用数据库核验（无外部技能时的标准做法）

### Step 0（最便宜、最先做）：DOI 可解析性检查
对每条有 DOI 的文献先请求 `https://api.crossref.org/works/<DOI>`：
- **404 → DOI 本身错误**（高度疑似错号）；
- **200 → 比对返回记录的标题/作者/卷期页**，不一致即「DOI 张冠李戴」。

单次请求即可发现实践中最常见的一类错误（批量核查中占比可达 7/9）。**务必先做此步，再展开逐字段核对。**

### PubMed E-utilities（最可靠）
```text
# 用 PMID 拉元数据，比对作者/年/刊/卷/页
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<PMID>&retmode=json

# 用关键词反查是否存在该文（验证「文中引用」是否真实）
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<Author>+<Title关键词>+<Journal>
```
> 要点：PMID 必须在 PubMed 可查且记录与文中一致。查不到 = 极可能编造。

### Europe PMC REST
```text
# 按 PMID
https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:<PMID>&format=json
# 按 DOI
https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<doi>&format=json
```

### Crossref（按 DOI 校验元数据）
```text
https://api.crossref.org/works/<doi>
```

> 中文文献：Crossref 常缺失，降级到 CNKI/万方（WebSearch / 带登录态检索）核对标题+作者+年份。
> 用 WebFetch 直接请求上述 URL 即可拿到结构化记录用于比对。

## 四、三级严重度分级 + 错误类型目录

逐条执行字段级对比，按严重程度分为三级（借鉴 `nature-ref-verifier` 的实战经验）：

### 🔴 Critical（必须修正）
| 检查项 | 说明 | 典型表现 |
|--------|------|---------|
| 作者姓名/顺序不一致 | 第一作者不同、顺序颠倒、完全编造 | 作者拼写/顺序错误 |
| 作者漏人 | 条目作者数少于出版方记录（常见于 5+ 作者只录前 3–4 人） | 漏第 5+ 作者 |
| 页码差异 ≥5 | 页码完全不匹配 | 1309-1319 → 1444-1449 |
| 文章号字母误判 | 文章号含字母被写成形近数字（T/7、l/1、O/0） | 101880T 误作 1018807 |
| 标题核心词不一致 | 非大小写/标点差异 | 核心词被替换 |
| DOI 指向不同论文 | DOI 存在但标题/作者不对应 | 10.1109/4.482157 → 10.1109/4.482187 |
| DOI 张冠李戴 | DOI 可解析但解析到另一篇论文 | 比对标题作者即可发现 |

### 🟡 Warning（建议核对）
| 检查项 | 说明 |
|--------|------|
| 卷年 ≠ DOI 年 | 卷归属年份与 DOI 编号年不一致 |
| Early Access 元数据漂移 | IEEE 等 Early Access 转正式出版后卷/期/页/年会变化，**以 CrossRef 现值为准** |
| 作者中间名缺失/多余 | 一般不影响检索 |
| 期号缺失 | 有卷无期 |
| 页码偏差 ≤4 | 细微差异 |

### 🟢 Info（仅供参考）
| 检查项 | 说明 |
|--------|------|
| 标题大小写不同 | Title Case vs Sentence case |
| 期刊名缩写 vs 全称 | 如 IEEE Trans. AES vs 全称 |
| 标点/连接词差异 | and vs & |

## 五、置信度评估

每条文献最终给出一个综合置信度：
| 等级 | 含义 |
|------|------|
| ✅ **Verified** | 多源一致，无需修改 |
| ⚠️ **Check suggested** | 存在 🟡 级差异，需人工判断 |
| ❌ **Needs fix** | 存在 🔴 级差异，必须更正 |
| ❓ **Unverifiable** | 所有来源均无法查到（内部报告、老旧学位论文等） |

## 六、单条核验模板（写入核验表备注）

```
[序号] 文中(Author YYYY Journal) → PMID/DOI=xxx
       → 标题✓? 作者✓? 卷期✓? 页码✓? → ✅/❌
```

## 七、Zotero 写回修正协议

核验出 ❌/⚠️ 后，可批量修正 Zotero 库（2026 实测要点）：
- **Zotero 7 本地 HTTP API（localhost:23119）只读**——写操作返回 501；修正写操作首选 **pyzotero Web 模式**（需 userID + API key，全功能 CRUD，自带 429 退避）；
- 无 key 时可用本地 `/connector/saveItems` 端点**新增**条目（不能改已有条目）；
- 直接改 `zotero.sqlite` 仅在 Zotero 关闭后可行，且需手工维护多表关联与版本号，**仅作最后手段**；
- 修正前先确认条目在库：按标题检索为空则说明该条另有来源（如文献管理 CSV），Zotero 侧无需修正。

**输出物**：除 Markdown 核验报告外，一并生成
1. **BibTeX Patch**：修正后的 `.bib` 文件内容片段；
2. **Zotero 更新指令清单**：逐条列出「条目 → 字段 → 正确值」，供 pyzotero 批量执行。

## 八、附：为主张补引用（claim→reference）

本技能除「核验已有引用」外，还支持**给定一段主张/文字，找支撑文献**（逆向能力，参考 `nature-citation`）：
1. 将文本拆为可引用片段（每句 / 每论断一个 segment）；
2. 为每个 segment 构造检索式（MeSH/关键词，见 `litsearch-protocol.md`），优先 PubMed / Europe PMC / CNKI；
3. **保守评级**：仅当文献摘要或出版页确实支持该论断时才引用；**标题相关 ≠ 真实支撑**，绝不因标题相近而强行引用；
4. 标注证据来源状态：**full-text / abstract-only / metadata-only**——abstract-only 不能支撑亚组/统计细节，须在文中披露；
5. 默认导出可被文献管理器直接导入的格式（RIS / EndNote / Zotero RDF / BibTeX）。

> 与「核验」互补：核验保证已有引用真实；补引用保证论点有据。两者共同构成引用可信度闭环。

## 九、交付要求

- 正式稿每条引用必须**真实可查**，正式版补齐 DOI；预印本标注 bioRxiv/medRxiv 及版本/DOI。
- 与外部技能的关系：本文件即「内置核验器」；若调用 `nature-ref-verifier` / `nature-citation` 可提速，但**不可因其不可用而跳过核验**。
