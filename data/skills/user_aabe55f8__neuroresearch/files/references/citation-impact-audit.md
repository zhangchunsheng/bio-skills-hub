# 他引 / 独立引用影响审计（内置，无需外部技能）

本文件提供「引用影响分析」工作流：给定目标论文，统计其被引情况、排除自引计算**独立他引数**、识别高影响力引用者，用于 NSFC 标书「工作基础 / 研究基础」与论文「相关研究进展」的可量化论证。若环境已装 `nature-academic-search` 可优先调用作加速器；否则按本自包含协议执行（仅用 WebFetch / WebSearch / 公开 REST API）。

## 一、输入
- 目标论文：DOI 或 PMID（**优先 PMID**，Europe PMC 的 `CITES:` 引用追踪最稳）；
- 目标作者名单（用于排除自引）：第一 / 通讯 / 共同作者姓名（含拼写变体）。

## 二、检索被引（多源，按可用环境降级）
| 来源 | 查询 | 说明 |
|------|------|------|
| **Europe PMC** | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=CITES:<PMID>&format=json` | 引文追踪最稳，返回引用文献列表（含作者/年/刊） |
| **OpenAlex** | `https://api.openalex.org/works?filter=cites:<openalex_id>&per_page=200` | 大规模引文 + 引用者机构/国家 |
| **Semantic Scholar** | `https://api.semanticscholar.org/graph/v1/paper/<DOI>/citations?fields=authors,year,title` | 含作者与年份 |
| **Crossref** | 链式引用（references）为主，citations 覆盖有限 | 兜底 |
| **WebSearch** | `"<title>" citations` / `Who cited "<title>"` | 兜底，补全高影响力引用者 |

> 优先 **Europe PMC + OpenAlex** 组合；两者都无结果时降级 WebSearch。每条引用记录其**来源状态**：full-text 可查 / abstract-only / metadata-only。

## 三、排除自引（独立他引）
1. 提取每条引用文献的作者列表；
2. 与目标作者名单比对，**剔除任一作者重合**的条目（自引 / 共同作者引用）；
3. 统计：
   - 总被引数（total citations）
   - **独立他引数（strict other-citations）** = 总被引 − 自引
   - 自引占比（自引 / 总被引）

## 四、高影响力引用者画像（influential citers）
对引用文献的通讯 / 第一作者做画像（**仅给线索，身份须人工核实**）：
- 是否院士 / 校长 / 院长 / 杰青 / 长江学者 / Fellow / 领域领军；
- 机构与国家分布；
- 方法：用 WebSearch 检索「<作者名> <机构> 院士 / 杰青 / Fellow」确认，**禁止 AI 直接断言头衔**。
输出「高影响力引用者清单」表：作者 | 机构 | 疑似头衔(待核) | 引用文献 | 年份。

## 五、文章级引用指标表（article-level metric table）
| 指标 | 含义 | 获取 |
|------|------|------|
| 总被引 | 全部引用数 | Europe PMC / OpenAlex |
| 独立他引 | 排除自引后计数 | 本工作流计算 |
| 自引数 / 占比 | — | 计算 |
| 高影响力引用者 | 院士 / 杰青 / Fellow 等（待核） | WebSearch 核实 |
| 引用时间分布 | 近年引用占比（持续影响力） | OpenAlex `publication_year` |

## 六、输出
- Markdown 指标表 + 高影响力引用者清单（头衔标注「待核」）；
- 可导入文献管理器的引用文献列表（RIS / BibTeX）；
- 用于标书时，以「独立他引 N 次，含 X 位杰青 / 院士团队引用」形式陈述，并注明检索日期与来源（Europe PMC / OpenAlex）。

## 七、严格禁止
- ❌ 编造引用数、虚构高影响力引用者头衔；
- ❌ 将 abstract-only 来源的引用数当作正式被引（须标注来源状态）；
- ❌ 自引计入他引；
- ❌ AI 直接断言学者头衔 / 身份（仅检索线索，由人核实）。
