# 引用格式规则（内置，无需外部技能）

本文件把 **Nature 编号制**与 **GB/T 7714-2015** 的著录规则直接写死，使本技能在**不依赖 `nature-citation` 等外部技能**的情况下也能输出合规参考文献。若环境已装 `nature-citation`，可优先调用作加速器；否则严格按本文执行。正文引用规范见 `manuscript-and-submission.md §4.1`。

> 本文的"冷门文献类型"（预印本、数据集、软件、会议、书章、电子资源）是常见漏项——投稿前务必对照目标刊《投稿须知》微调。

## 一、Nature / 神经科学顶刊编号制（顺序编码制）

- **正文**：数字序号方括号，如 `[1]`、`[1,3]`、`[1–5]`；按首次出现顺序连续编号。
- **文末列表**：依序号排列，格式统一为：

```
1. Author, A. B. & Author, C. D. Title of the paper. J. Abbrev. Name Vol, first–last pages (Year).
```

- **作者**：≤5 人列全部；>5 人列前 5 人后加 `et al.`（以目标刊稿约为准）。用 `&` 连接最后两位。
- **期刊名**：标准缩写（如 *Nat. Neurosci.*、*J. Neurosci.*、*Neuron*、*Brain*）。
- **卷/页/年**：`卷, 起始页–终止页 (年)`；有 DOI 时置于末尾 `https://doi.org/xx.xxxx/yyyy`。
- **示例**：
```
1. Hansen, D. V., Hanson, J. E. & Sheng, M. Microglia in Alzheimer's disease. J. Cell Biol. 217, 459–472 (2018).
2. Smith, J. et al. Title here. Nat. Neurosci. 25, 100–112 (2022). https://doi.org/10.1038/s41593-022-01000-0
```

### 1.1 冷门文献类型（Nature 编号制）

- **预印本**（bioRxiv / medRxiv / arXiv）：
```
3. Author, A. B. & Author, C. D. Title of the preprint. Preprint at bioRxiv https://doi.org/10.1101/xxxxxxx (2024).
```
  要点：标注 `Preprint at` + 平台 + DOI；无卷期页码。若已正式发表，**引用正式版本**并弃预印本。
- **数据集**：
```
4. Author, A. B. & Author, C. D. Title of the dataset. Zenodo https://doi.org/10.5281/zenodo.xxxxxxx (2023).
5. GEO, G. S. E. Dataset title. Gene Expression Omnibus https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE123456 (2024).
```
- **软件 / 代码**：
```
6. Author, A. B. et al. Software name v1.2.0. Zenodo/GitHub https://doi.org/10.5281/zenodo.xxxxxxx (2023).
```
- **会议论文**：
```
7. Author, A. B. & Author, C. D. Title. In Proc. Conf. Abbrev. 123–130 (Publisher, 2022).
```
- **书籍章节**：
```
8. Author, A. B. Chapter title. In Book Title (ed. Editor, E. F.) 25–48 (Publisher, 2021).
```
- **英文学位论文**：
```
9. Author, A. B. PhD thesis, University of X (2020).
```
- **网页 / 电子资源**（无 DOI 时给 URL + 访问日期）：
```
10. Organization. Page title. Website https://www.example.com (accessed 20 August 2026).
```

## 二、GB/T 7714-2015（中文期刊 / 国内学位论文）

国内中文核心、科技期刊与学位论文普遍采用。两变体：

### 2.1 顺序编码制（默认，与 Nature 编号制对应）
- **正文**：`[1]`、`[1,3]`、`[1-5]`；按出现顺序编号。
- **作者规则**：≤3 人列全部；>3 人列前 3 人后加 `, 等`（中文文献）或 `, et al.`（西文文献）。**注意与 Nature 的 ≤5 人规则不同**。
- **期刊文章**：
```
[1] 作者. 题名[J]. 刊名, 年, 卷(期): 起页-止页.
[1] 张伟, 李娜. 小胶质细胞在阿尔茨海默病中的作用[J]. 中华神经科杂志, 2023, 56(4): 389-395.
[2] 王强, 刘洋, 陈明, 等. 某细胞死亡表型在CNS损伤中的作用[J]. 中华创伤杂志, 2022, 38(9): 812-818.
```
- **专著**：`[1] 作者. 书名[M]. 出版地: 出版者, 年: 引文页码.`
- **学位论文**：`[1] 作者. 题名[D]. 保存地: 保存单位, 年.`
- **会议论文**：`[1] 作者. 题名[C]//会议名称. 出版地: 出版者, 年: 页码.`
- **专利**：`[1] 申请者. 专利题名: 专利号[P]. 公告日期或公开日期.`
- **标准**：`[1] 起草单位. 标准名称: 标准号[S]. 出版地: 出版者, 年.`
- **电子资源**：`[1] 作者. 题名[EB/OL]. (更新日期)[引用日期]. 获取和访问路径. DOI.`
- **预印本**：`[1] 作者. 题名[EB/OL]. bioRxiv, 2024[2026-08-20]. https://doi.org/10.1101/xxxxxxx.`

### 2.2 著者-出版年制（部分社科/心理/管理类刊用）
- **正文**：`(作者, 年)` 或 `(Author, Year)`，按字母序排；多作者 `(Author1 & Author2, 年)`。
- **文末列表**：按作者姓氏字母序 + 年排序：
```
张伟, 李娜. 2023. 小胶质细胞在阿尔茨海默病中的作用[J]. 中华神经科杂志, 56(4): 389-395.
```
- **注意**：仅当目标刊明确强制时才用著者-出版年制；默认用顺序编码制。投稿前务必查目标刊《投稿须知》并以期刊模板为准。

## 三、通用规则（两体系共用）

1. **一次一源**：关键结论引 primary；禁止用综述代替原始文献（二手引用）。
2. **数量**：研究论文 30–60 条、综述 80–150 条，重质不重量。
3. **标识**：正式稿每条补齐 DOI；预印本标注 bioRxiv/medRxiv 及版本/DOI。
4. **标点/排版**：序号用方括号 `[n]`；同句多文献合并（如 `[2,5]`、`[7-9]`），避免重复罗列。
5. **位置**：序号置于所支撑断言的句末标点之前，如 `…观察到小胶质细胞活化[3]。`
6. **无作者**：以题名起头（Nature 制）或以机构/刊名代替作者（GB/T 制），不得虚构作者。
7. **无年份**：中文标 `[年代不详]`；英文标 `(n.d.)`。不得凭空补年份。
8. **同一作者同年多篇**：著者-出版年制加 `a/b` 后缀（`2023a, 2023b`）；顺序编码制按不同序号处理。
9. **DOI 写法**：优先 `https://doi.org/` 前缀，不裸写 `DOI: 10.xxxx`（除非目标刊要求）。
10. **页码范围**：用短横线连接起止页，英文期刊多用 `–`（en dash），中文用 `-`。

## 四、与外技能的关系

本文件即「内置格式器」；`nature-citation` 可提速但非必需。无论是否调用外部技能，**格式必须达标**，且引用须经 `citation-verification.md` 核验真实。
