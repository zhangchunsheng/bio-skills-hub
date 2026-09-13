# ASCO / ESMO / CSCO / AACR / WCLC 会议摘要检索策略

## ASCO（美国临床肿瘤学会）

### 基本信息

- **会议库 URL**：`meetinglibrary.asco.org`
- **年会时间**：每年 5-6 月（芝加哥）
- **摘要发布**：年会前约 2-4 周在线发布
- **覆盖范围**：通常可检索近 5-10 年年会摘要

### WebSearch 查询模板

```
site:meetinglibrary.asco.org <关键词> <年份>
```

示例：
- `site:meetinglibrary.asco.org HER2 breast cancer 2024`
- `site:meetinglibrary.asco.org KEYNOTE lung cancer 2023`
- `site:meetinglibrary.asco.org CAR-T lymphoma 2024`

### 专场类型

| 专场 | 说明 |
|------|------|
| Plenary Session | 全体大会（最重要研究） |
| Oral Abstract Session | 口头报告 |
| Poster Session | 壁报展示 |
| Clinical Science Symposium | 临床科学研讨会 |
| Education Session | 教育专场 |

### 结果解析

1. 从 WebSearch 结果中提取：标题、作者、摘要编号、专场类型、年份
2. 用 WebFetch 抓取摘要页面全文（典型 URL 格式：`https://meetinglibrary.asco.org/record/<id>/abstract`）
3. 从页面中提取摘要正文：Background、Methods、Results、Conclusion
4. 标注专场类型和摘要编号

### 搜索技巧

- 按药物名称搜索：`site:meetinglibrary.asco.org pembrolizumab 2024`
- 按试验名称搜索：`site:meetinglibrary.asco.org KEYNOTE-671 2024`
- 按癌种搜索：`site:meetinglibrary.asco.org "non-small cell lung cancer" 2024`
- 按专场类型搜索：`site:meetinglibrary.asco.org "plenary session" 2024`

---

## ESMO（欧洲肿瘤内科学会）

### 基本信息

- **官网**：`esmo.org`
- **年会时间**：每年 10 月（欧洲城市轮换）
- **摘要发布**：年会前约 1-2 周在线发布，发表在 Annals of Oncology 增刊
- **覆盖范围**：通常可检索近 5 年年会摘要

### WebSearch 查询模板

```
site:esmo.org <关键词> <年份> congress abstract
```

或通过期刊搜索：
```
annalsofoncology.org ESMO congress <年份> supplement <关键词>
```

示例：
- `site:esmo.org CAR-T lymphoma 2023 congress`
- `site:esmo.org breast cancer 2024 congress abstract`
- `annalsofoncology.org ESMO 2024 congress pembrolizumab`

### 摘要编号前缀含义

| 前缀 | 含义 |
|------|------|
| LBA | Late-Breaking Abstract（最新突破性摘要） |
| O | Oral Presentation（口头报告） |
| P | Poster（壁报） |
| MO | Mini Oral（小型口头报告） |
| TiP | Trial in Progress（进行中试验） |

### 结果解析

1. 从 WebSearch 结果中提取：标题、作者、摘要编号（注意前缀）、专场类型
2. 用 WebFetch 抓取 ESMO 官网页面或 Annals of Oncology 摘要页面
3. 提取摘要正文
4. 标注摘要编号前缀含义（LBA / O / P / MO / TiP）

### 搜索技巧

- 按药物搜索：`site:esmo.org osimertinib 2024 congress`
- 按 LBA 搜索：`site:esmo.org LBA 2024 congress`
- 按癌种搜索：`site:esmo.org "gastric cancer" 2024 congress abstract`

---

## CSCO（中国临床肿瘤学会）

### 基本信息

- **官网**：`csco.org.cn`
- **年会时间**：每年 9 月（中国城市轮换）
- **摘要来源**：CSCO 年会、CSCO 专题研讨会
- **语言**：中文为主，部分有英文摘要
- **覆盖范围**：摘要通常分散在医学媒体、期刊增刊、官网

### WebSearch 查询模板

```
CSCO 年会 <年份> <关键词> 摘要
```

或：
```
CSCO <年份> <关键词> 进展
```

示例：
- `CSCO 年会 2024 胃癌 靶向治疗 摘要`
- `CSCO 年会 2024 免疫治疗 肺癌 进展`
- `CSCO 2024 乳腺癌 指南更新`
- `CSCO 年会 2023 结直肠癌 新进展`

### 结果来源

CSCO 摘要搜索结果可能来自以下渠道：

| 来源 | 说明 |
|------|------|
| CSCO 官网 | csco.org.cn，可能有年会专题页面 |
| 丁香园 | dxy.cn，医学媒体常报道 CSCO 要点 |
| 肿瘤资讯 | 各医学媒体平台 |
| 期刊增刊 | 《临床肿瘤学杂志》等可能收录 CSCO 摘要 |
| 医学界 | 医学专业媒体报道 |

### 结果解析

1. 从 WebSearch 结果中筛选最权威的来源（优先 CSCO 官网、专业医学媒体）
2. 用 WebFetch 抓取页面内容
3. 提取：标题、讲者、专场信息、研究要点
4. 注意区分：指南更新、研究进展、专家解读

### 搜索技巧

- 按讲者搜索：`CSCO 年会 2024 <讲者姓名> <癌种>`
- 按专场搜索：`CSCO 年会 2024 <专场名称> 摘要`
- 按药物搜索：`CSCO 年会 2024 <药物名称> 进展`
- 按癌种 + 治疗搜索：`CSCO 年会 2024 肺癌 免疫治疗 进展`

---

## AACR（美国癌症研究协会）

### 基本信息

- **官网**：`aacr.org`
- **年会时间**：每年 4 月（美国城市轮换）
- **摘要发布**：年会前约 1-2 周在线发布
- **覆盖范围**：基础与转化研究为主，也有早期临床试验数据
- **特点**：新药 I 期数据、耐药机制、临床前研究常在 AACR 首次报告

### WebSearch 查询模板

```
site:aacr.org <关键词> <年份>
```

或：
```
AACR <年份> <关键词> clinical trial results
```

示例：
- `site:aacr.org KRAS G12D inhibitor 2025`
- `AACR 2026 <药物代号> phase I results`
- `AACR <年份> <靶点> clinical data abstract`

### 专场类型

| 专场 | 说明 |
|------|------|
| Plenary Session | 全体大会 |
| Major Symposium | 专题研讨会 |
| Minisymposium | 小型研讨会（含口头报告） |
| Poster Session | 壁报展示 |
| Clinical Trials Mini Symposium | 临床试验小型研讨会 |

### 结果解析

1. 从 WebSearch 结果中提取：标题、作者、摘要编号、专场类型
2. 用 WebFetch 抓取 AACR 官网页面或 Cancer Research 期刊摘要
3. 提取摘要正文
4. 注意区分临床数据和临床前/转化研究

---

## WCLC（世界肺癌大会）

### 基本信息

- **官网**：`iaslc.org`（国际肺癌研究协会主办）
- **年会时间**：每年 9 月（全球城市轮换）
- **摘要发布**：年会前约 1-2 周在线发布
- **覆盖范围**：专攻肺癌领域，NSCLC / SCLC / 胸膜间皮瘤等
- **特点**：肺癌靶向治疗、免疫治疗最新数据的重要发布平台

### WebSearch 查询模板

```
WCLC <年份> <关键词> abstract results
```

或：
```
WCLC <年份> <药物代号> <瘤种> phase
```

示例：
- `WCLC 2025 EGFR inhibitor osimertinib results`
- `WCLC 2026 KRAS G12D NSCLC clinical data`
- `WCLC <年份> <试验代号> results`

### 专场类型

| 专场 | 说明 |
|------|------|
| Plenary Session | 全体大会 |
| Oral Abstract Session | 口头报告 |
| Mini Oral | 小型口头报告 |
| Poster Session | 壁报展示 |
| Presidential Symposium | 主席研讨会（最重要研究） |

### 结果解析

1. 从 WebSearch 结果中提取：标题、作者、摘要编号、专场类型
2. 用 WebFetch 抓取 IASLC 官网或 Journal of Thoracic Oncology 摘要页面
3. 提取摘要正文
4. 注意 Presidential Symposium 和 Plenary Session 的研究通常最重要

---

## 多会议综合检索策略

当用户要求检索多个会议时：

1. **按会议逐一搜索**：先 ASCO → ESMO → CSCO → AACR → WCLC，每个会议独立搜索
2. **结果分组展示**：按会议分组，每组内按专场 / 摘要编号排序
3. **跨会议去重**：同一试验可能在多个会议都有报告，注意标注「同一研究在 X 会议也有报告」
4. **时间线整合**：如果用户需要追踪某试验的进展时间线，按时间排序整合各会议数据
5. **药物代号逐一搜索**：对于药物/靶点专题检索，根据已找到的药物列表逐一搜索每个药物代号在各会议的数据

---

## 会议年份对照表

| 会议 | 2024 | 2025 | 2026 | 常规时间 |
|------|------|------|------|----------|
| ASCO GI | 1月（旧金山） | 1月（旧金山） | 1月（旧金山） | 每年 1 月 |
| AACR | 4月5-10日（圣地亚哥） | 4月25-30日（芝加哥） | 4月25-30日（华盛顿） | 每年 4 月 |
| ASCO | 5月31日-6月4日（芝加哥） | 5月30日-6月3日（芝加哥） | 5月29日-6月2日（芝加哥） | 每年 5-6 月 |
| ESMO GI | 6月（慕尼黑） | 7月（柏林） | 7月（待定） | 每年 6-7 月 |
| WCLC | 9月7-10日（圣地亚哥） | 10月（待定） | 9月（待定） | 每年 9 月 |
| CSCO | 9月（厦门） | 9月（待定） | 9月（待定） | 每年 9 月 |
| ESMO | 10月18-22日（巴塞罗那） | 10月17-21日（柏林） | 10月（待定） | 每年 10 月 |

**注意**：
- 当前年份的会议可能尚未举行或摘要尚未公开
- 如用户询问的年份会议尚未举行，提示该年份会议尚未召开
- 摘要通常在会议前 1-4 周在线发布
- LBA（最新突破性摘要）可能在会议期间才公开
- 当检索日期接近某会议结束日期（2个月内），必须专门搜索该会议最新数据
