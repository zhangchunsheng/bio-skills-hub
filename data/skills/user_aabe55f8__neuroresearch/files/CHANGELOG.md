---
summary: neuroresearch 完整变更日志（按版本倒序）
---

# 更新说明（Change Log）

完整历史：v1.0.0 → 当前。修订细节见 commit / git log；本文件保留值得回看的版本级变更。

## v2.4.8（2026-09-03）

**许可变更：MIT → CC BY-NC-SA 4.0（非商业、署名、相同方式共享）。**

- `SKILL.md` frontmatter `license: MIT` → `license: CC BY-NC-SA 4.0`。
- 新增 `LICENSE` 文件：标准 CC BY-NC-SA 4.0 声明（可读版条款 + 法律文本/契约链接 + SPDX 标识）。
- 能力建设不受影响：NSFC 标书、生信、Prism 出图、引用核验等所有既有能力保持不变。
- 含义：他人可自由分享与改编本技能，但须**署名、非商业使用、并以相同 CC BY-NC-SA 4.0 许可分发衍生作品**。

## v2.4.7（2026-09-03）

**借鉴 Supervisor-Skills（HKUST Dial）方法论，落地 T1 四项增强，不破坏原有能力。**

- 新增 `references/idea-evaluation.md`（研究设想/假说评估框架）：移植 idea-evaluator 的评分骨架并**改写为神经科学语义**——新颖性真实检索核验 + 10 类致命缺陷早筛（含 CRITICAL 早停）+ 生命周期/能力匹配 + 五维打分（Higher/Faster/Stronger/Cheaper/Broader 神经科学语义）+ 范式突破 4 问探针 + 可行性风险 + 诚信门 + 三档裁决（Strong Accept / Accept with Revisions / Reject and Pivot）。服务于 NSFC 申报方向体检与机制假说论证；示例一律通用占位，遵循 v2.4.5 脱敏规则。
- `references/manuscript-and-submission.md` 新增 §9.5 / §9.6 / §9.7，并与 §3.2 / §9.3 联动：
  - §9.5 审稿发现严重度分级（CRITICAL/MAJOR/MINOR），神经科学示例；结论须与发现一致。
  - §9.6 禁用 AI 腔词表（含神经科学特化过度声称）+ 破折号禁令，全文自检。
  - §9.7 写作时红旗清单：证据等级 L0–L3 门控 + 12 条神经科学适配红旗（不编造机制/数值、真实 vs 计划结果分离）。
- `references/literature-review.md` 新增 Step 0（先冻结 RQs）+ §七 对抗式检索视角与生物医学证据标准（5 视角 + 证据类型权重表 + evidence-first + 六道质量门）；Step 2 加对抗式视角指针。
- `references/litsearch-protocol.md` 新增 §八（对抗式视角落到检索式）+ §九（检索时即标证据类型），与 literature-review.md §七 互链。
- `SKILL.md` 模块导航新增 idea-evaluation.md 条目；典型任务最小读取集新增「选题/开题/假说评估」；版本 2.4.6 → 2.4.7。
- **许可注意**：Supervisor-Skills 为 CC BY-NC-SA（非商业），本次仅移植其**方法论并重写成中文神经科学语义**，未逐字复制其文本。本技能现已将许可由 MIT 改为 **CC BY-NC-SA 4.0**（与新 LICENSE 文件一致），与 Supervisor-Skills 同属非商业协议，反而不再存在此前 MIT 派生自 NC 源的许可错配。

## v2.4.6（2026-08-30）

**NSFC 申请代码体系补全 + 往年中标情况分析 + 基于研究内容的自动推荐**。
- 新增 `references/nsfc-code-strategy.md`：
  - §一 补全医学科学部 **H01–H35 一级代码**全表 + 神经相关二级代码（**H09/H10/H11/H17/H28/H02/H06/H16/H20**），对齐 **2025 现行版**（精神病学已从 H09 拆分至 H10），并标注"逐年微调、以当年指南为准"。
  - §三 往年中标情况分析：**医学科学部学部层面资助率趋势**（面上 2023≈13.2% → 2024 9.04% → 2025 8.92%，青年C 11.50%→10.55%，连续垫底）+ **临床专项按代码**数据（H09/H17/H28/H10/H18/H02/H06，2023–2025）+ 明确"按代码率仅专项口径、全口径仅到学部级"的方法学局限。
  - §四 基于研究内容的**自动推荐决策矩阵**（关键词→代码表 + 机制 vs 修复轴心判定 + H09 vs H17 评审偏好差异表）+ 调用脚本说明。
- 新增 `scripts/nsfc_code_recommender.py`（**仅标准库、开箱即跑**）：内置代码库/中标率/关键词映射，CLI 输入研究内容文本，输出排序推荐代码、匹配关键词、建议二级、评审偏好、竞争强度与机制/修复轴心判定；H09 vs H17 决策核心已覆盖。
- `references/proposal-nsfc.md` §1.2 修正至 2025 代码（H0910 改称"神经损伤、修复与再生"等），并指向新策略文件；示例句维持通用占位（不写死用户抉择，遵循 v2.4.5 脱敏规则）。
- `SKILL.md` 模块导航新增 `nsfc-code-strategy.md` 条目；版本 2.4.5 → 2.4.6。
- 数据来源：NSFC《2025/2026 年度项目指南》、医学科学部 2023–2025 评审工作综述、临床专项 2023–2025 资助情况公告、2024/2025 年度报告及部门决算（均已在文中标注年份与口径）。

## v2.4.5（2026-08-27）

**技能自身脱敏整改（防上传泄露用户未公开课题）**。
- `references/proposal-nsfc.md` §1.2 示例句、§2.3 案例对照表列头与建议句：原把"选 H1701 不选 H0910"的用户真实申报代码抉择写死为技能示例，改为通用占位（机制主导型/修复主导型投向、代码X），仅保留 H09/H17 等公开类目号。
- `CHANGELOG.md` v2.3.0 条目：删除"H1701 vs H0910 实操对比表"的具体代码写法，改为"申报代码抉择实操对比表"。
- `SKILL.md` 核心原则新增第 11 条「技能自身脱敏」：技能文件严禁写入用户特定、未公开的课题内容（机制假说/未发表数值/申报代码抉择/方向标识），示例一律通用占位；用户级记忆与项目交付物不随技能分发。
- 扫描确认：RAB31 / 中性粒细胞 RNA-seq / 星形胶质细胞焦亡 / LCN2-cGAS-STING / 肠脑轴 / IBD共病 等用户核心假说均未进入技能文件（仅存于用户私有记忆与交付物）。

## v2.4.4（2026-08-26）

**系统性审查整改落地（修复 v2.4.3 遗留的版本漂移 + templates 硬编码外部技能路径 + 文档断链 + selfcheck 盲区）**。
- **P1 必修**：
  - 版本号同步：`SKILL.md` version 2.4.2 → 2.4.3 → **2.4.4**（修复 v2.4.3 发布时漏改导致的 selfcheck FAIL）。
  - **templates/ 8 个模板修复硬编码路径**：全部删除 `C:\Users\DELL\.workbuddy\skills\prism-style-plot`（他人用户名 + 指向外部独立技能，破坏自包含），改为**引擎定位器**——引擎内建在本技能 `scripts/prism_theme.py`（别人只装本技能即可用，无需外部技能）；模板在技能目录内时用相对路径；复制到工作目录后回退到**用户级**（`~/.workbuddy/skills/`）与**项目级**（工作目录向上找 `.workbuddy/skills/`）两种技能安装位置；import 由 `from scripts.prism_theme` 改为 `from prism_theme`。已实测：技能目录内 + 复制到独立目录两种方式运行成功（五件套产物齐全）。
- **P2 自检加固（selfcheck.py 新增 4 类检查）**：
  - #14 templates/*.py 无硬编码路径/外部技能引用（防 P1 复发）；
  - #15 references/ + verify-README 引用的 `verify*.py` 均存在于磁盘（防断链）；
  - #16 prism-style-plot.md「最新同步至 vX.Y.Z」== `UPSTREAM_VERSION`（防标题版本漂移）；
  - C 段双源比对增加 **sha256 内容哈希**（数量/版本标记巧合一致但内容漂移时也能 WARN）。
- **P2 文档一致性**：
  - `scripts/verify/README.md` 文件表列全 13 个验证脚本（verify3 拆分 3a/3b/3c 说明、verify6-11 覆盖、run_all 档位）并同步运行方式；
  - `references/recipes/grouped.md` 引用 `verify4_grouped_bar.py` → 实际 `verify4_twoway_posthoc.py`；
  - `references/recipes/multiple_variables.md` 引用 `verify8_multivar.py` → 实际 `verify10_deep_others.py`（run_multivar）；
  - `litsearch-protocol.md` 知识卡片代码块补闭合（修复 §七 标题被吞进代码块的渲染缺陷）；
  - `prism-style-plot.md` 标题引擎版本 v2.6.x → v2.7.4（与 UPSTREAM_VERSION 一致）。
- **P3 结构优化**：
  - `使用文档.md`「典型任务最小读取集」改为指针引用（权威源唯一化到 SKILL.md，防双份维护漂移）；
  - `experiment-design.md` 功效 n 警示去重（§2 底部红框改一行指针，权威内容保留在 §三 顶部）；
  - 10 个 `recipes/*.md` 头部注释版本号口径统一（去掉上游 v2.5.x 版本号，避免与本技能版本混淆）；
  - `prism_theme.py` 新增 `UPSTREAM_SYNCED = "2026-08-26"`（同步日期回溯）。
- **验证**：selfcheck 全绿（PASS 增加、FAIL 0）；pytest 62 例全过；verify `--quick` 10/10 通过；2 个模板独立目录端到端实测通过。

**绘图引擎重新同步（消除 v2.4.2 自检 WARN：vendored 49 → 独立 prism-style-plot 52）**。
- **整份覆盖 `scripts/prism_theme.py` 为独立 `prism-style-plot` v2.7.4**（用户确认整份同步，含画布尺寸预设一并改为 `3×5 / 5×5 / 7×5` cm）。
- **新增 3 个公开 API**：`read_excel_sheets`（单 Excel 多 sheet 解析）、`compose_panel_figure`（合并面板图）、`build_master_report`（总报告）；公开 API 49 → **52 项**。
- **`UPSTREAM_VERSION` 标记更新为 `"v2.7.4"`**（P1-1 双源漂移检测继续生效）。
- **文档同步**：`prism-style-plot.md`（v2.7.4 / 52 项）、`plotting-protocol.md`、`statistical-analysis.md`、`使用文档.md` 的画布尺寸预设统一改为 `3×5 / 5×5 / 7×5`；`verify6` 硬编码期望值断言同步修正。
- **验证**：`selfcheck.py` 35 PASS / 0 FAIL / 1 SKIP（R 依赖缺，预期）/ 0 WARN；`verify/` 全 13 脚本回归 13/13 通过，引擎零回归。

## v2.4.2（2026-08-26）

**系统性审查整改（P1/P2/P3 共 14 项优化，基于 selfcheck 增量 + 文档/护栏修订）**。
- **P1 高价值（自检加固，零逻辑改动）**：
  - **引擎双源同步断言**：`prism_theme.py` 新增 `UPSTREAM_VERSION = "v2.6.x"` 标记；`selfcheck.py` 新增 C 段——若本环境装有独立 `prism-style-plot` 技能，比对两者 `__all__` 数量与版本（WARN 不阻断，提示「需重新同步」）。
  - **§N 跨文件引用可达性**：新增 A+ 段，扫描 `references/*.md` 中 `xxx.md §N` 引用，校验目标文件存在对应标题（中文/阿拉伯数字互转归一），缺失则 WARN（重排小节不再无言失效）。
  - **API 数量双向校验**：A 段 #10 提取文档「公开 API N 项」与 `len(__all__)` 比对。
  - **绘图规则单一权威源**：`prism-style-plot.md` 新增「核心规则（权威源）」标记；`statistical-analysis.md §6.4`/`plotting-protocol.md`/`scatter-layout.md` 改为指针引用；A++ 段校验标记与指针存在。
  - **触发器护栏**：`SKILL.md` 触发段补「不触发」清单（非科研泛化提及 / 临床就医 / 泛聊天 / 纯工程）。
- **P2 中等价值**：
  - **R 模板定位澄清**：`statistical-analysis.md §四` 顶部加醒目定位（Python 优先，R 仅备选）。
  - **交付物统一路径**：`SKILL.md` 核心原则新增第 9 条（`deliverables/<项目名>/`、`_tmp/`）+ `academic-word-template.md §十` 同步。
  - **项目级记忆**：`SKILL.md` 核心原则新增第 10 条（`deliverables/<项目名>/PROJECT.md` 跨会话连续性）。
  - **R 脚本自检块**：D 段用 `bioinfo_rna_seq.R` demo 端到端跑通（缺 R/Bioconductor 包则 SKIP，与引擎测试同策略）。
  - **recipes/templates 纳入自检**：A 段 #11/#12 静态校验 templates 导入名、recipes 调用的 `prism_*` 函数均在 `__all__` 中。
  - **导航表瘦身**：`SKILL.md` 模块导航改为「任务/触发 → 文件」两列，压缩约 30 行。
- **P3 润色**：
  - **适用范围声明**：`SKILL.md` 新增「适用范围」小节（不覆盖临床注册/流行病学建模/非神经通用生信/非科研医疗咨询）。
  - **功效 n 告诫前置**：`experiment-design.md §三` 开头加「常见 n ≠ 功效 n」红框。
  - **小细节**：`experiment-report.md` 元数据 YAML 版本号改占位（`<当前版本>`）；`domain-lexicon.md` 神经科学专科列表 `Brain` 去重。
- **结果**：`selfcheck.py` 0 FAIL（35 PASS / 1 SKIP / 1 WARN）；唯一 WARN 为 vendored(49) ≠ 独立 prism-style-plot(52)，提示需重新同步引擎。

## v2.4.1（2026-08-25）

**同步 prism-style-plot 引擎至 v2.6.x（修用户「已更新请优化对应功能」）**。
- **引擎同步**：`scripts/prism_theme.py` 从 prism-style-plot 最新版覆盖（无 neuro 独有代码，仅注释差异）；公开 API 48→**49 项**，新增 `read_table`（v2.6.0：读 CSV/Excel 自动拆组 + 自动返回 y 轴标签默认）。
- **三处新能力落地 neuroresearch**：① `read_table` 文件来源自动设 ylabel（长格式=数值列表头，宽格式回退 None）；② `format_legend(..., test=...)` 不传 `stat_method` 时由 test 名自动推导方法文字（2 组 t 检验不再误写 ANOVA）；③ `add_pairwise_brackets(..., ytick_step=...)` 小图可显式设 y 轴刻度步长。
- **环境脚本合并**：`scripts/ensure_env.py` 合并 prism 标记缓存（秒回、不随技能上传串味）+ neuro 原 Windows `--copies` 兜底（防受管理 Python 上 venv 卡 launcher 重定向）。
- **测试补齐**：新增 `tests/test_read_table.py`（8 例，专测上述新能力）；并修正 `test_prism_stats.py`/`test_read_table.py` 写死的 `C:\Users\DELL\...` 路径为 `__file__` 相对推导（跨机器/跨用户名可移植，且正确指向 neuroresearch 自身 vendored 引擎）。pytest 54→**62 例**全过；verify 快速档 10/10 通过。
- **文档同步**：`references/prism-style-plot.md`（v2.6.x、49 API、62 测试例、新能力说明 + Phase 0 自动 ylabel 约定）、`SKILL.md` 导航（v2.5→v2.6.x）、`使用文档.md`（引擎版本/API 数/测试例数）一并更新。

## v2.4.0（2026-08-24）

**绘图引擎升级：重新整合独立技能 prism-style-plot v2.5.x（2663→4772 行，公开 API 48 项）**。
- **引擎替换**：`scripts/prism_theme.py` 同步为独立技能最新版（旧版不随发布包提供，仅保留在本地开发历史）。**完全向后兼容**（get_figsize/p_to_stars/format_p/mean_sem/mean_sd/oneway_anova_tukey/ttest_two_groups 等旧 API 与返回结构不变，selfcheck 断言无需改动，已实测）。
- **新增图型**：`prism_grouped_bars`（Grouped 分组柱）、`prism_spaghetti`（重复测量意大利面条图，默认 wide 画板）、`prism_nested_bars`（Nested 嵌套柱，单元级防假重复）、`prism_pie`/`prism_donut`（占比）、`prism_pairplot`/`prism_facet_boxplot`（多变量）。
- **新增统计**：`mann_whitney_u`/`wilcoxon_signed_rank`（非参数两组）；`oneway_anova_tukey` 支持 `var_equal`（assumed/welch/auto，Levene 自动切换）+ `posthoc`（games_howell/dunnett_t3/welch_t）；`build_stats_report` 新增 `twoway_rm`（重复测量 two-way，GG 球形性校正 + 简单效应 Sidak）、`nested`、`add_cox`（Cox HR + PH 检验，需 lifelines）。
- **新增交付**：`recommend_figsize`/`recommend_shape`（表类型→形态三级推荐，重复测量一律 wide）、`common_point_size`/`auto_dot_alpha`（点大小/透明度自适应）、`format_legend`（图注生成，n 支持 list）、`write_report` HTML 总览、`emit_run_script`（图/脚本/报告五件套同前缀）、`save_figure` 默认 `pad_inches=0.04`。
- **新增资产**：`references/recipes/`（10 类图型完整模板）、`references/scatter-layout.md`（散点布局实现细节）、`tests/test_prism_stats.py`（pytest 54 例）、`scripts/verify/`（run_all.py 回归 13 项）、`templates/`（8 个表型模板）。
- **文档同步**：`prism-style-plot.md` 重写为新引擎入口（API 速查 48 项 + 图型模板速查）；`statistical-analysis.md` 4.B.2/4.B.8 补引擎封装（Welch/Dunnett T3 内置，scikit-posthocs 仅剩非参数 Dunn's 兜底）；使用文档模块数 17→18（+scatter-layout.md）+ 结构图（recipes/verify/tests/templates）；SKILL.md 导航补图型模板条目。

## v2.3.0（2026-08-24）

**深度审查整改（P0 事实错误/断链 + P1 能力缺口，基于 3 路并行审查）**。
- **proposal-nsfc.md**：① 修正学科代码表硬错误（H09 神经系统、H10 精神卫生与心理健康、H11 医学免疫学、H17 创伤/烧伤/整形、H02 循环系统；以当年指南为准）；② 经费科目由旧"5 大科目"改为现行三大类（设备费/业务费/劳务费）+ 间接费，注明青年 C 类包干制；③ 删除不存在的 `scripts/build_pathway.py`/`build_doc.py` 引用（改指 `prism-style-plot.md §五` / `academic-word-template.md`）；④ 新增 §1.3 科学问题属性（A/B/C/D 四选一必填）；⑤ 检查清单新增限项自检；⑥ 年度计划注明青年 3 年；⑦ 文件命名统一课题缩写占位（脱敏）。
- **statistical-analysis.md**：① 修正 scipy `ttest_ind` 默认值注释（默认 equal_var=True，Welch 需显式）；② 决策树补配对/嵌套分支；③ 新增 §三 异常值检测与处理（Grubbs/1.5×IQR/稳健 z + 处理决策，防"删点不交代"）；④ 新增可执行模板 4.B.6 嵌套聚合防假重复、4.B.7 Cox 回归（lifelines）、4.B.8 非参数事后 Dunn's / Games-Howell + 效应量（Cohen's d/η²/ε²）；⑤ 版本号与形态预设（cm）同步。
- **绘图一致性**：prism-style-plot.md/plotting-protocol.md/statistical-analysis.md/使用文档.md 的 figsize 数值统一为引擎 cm 实现（tall 4×6 / square 6×6 / wide 8×6）；prism_xy_fit 文档收敛为仅 4pl/linear；experiment-report.md 断链引用"离群值检测"改为真实小节。
- **domain-lexicon.md**：补脑挫伤/脑震荡/DAI、bulk RNA-seq/差异表达词条、Journal of Neurotrauma 与中文核心期刊。
- **脚本**：bioinfo_rna_seq.R 依赖守卫补 ragg；ensure_env.py Windows 创建 venv 加 `--copies` 兜底+失败提示；plot_demo.py 移除未使用的 lifelines 依赖；prism_theme.py jitter/beeswarm 默认 seed=42（可复现）。
- **selfcheck.py**：新增内容级断言（references 引用 scripts 存在性、prism-style-plot API 表 vs 实现 def），防文档-实现漂移漏网。

## v2.2.3（2026-08-24）

**其余模块对齐公开科研 skill 最佳实践（借鉴 SciWrite / K-Dense-AI claude-scientific-skills / qinyan-academic-skills）**。
- `manuscript-and-submission.md` 新增「§九 五段式编辑审计与声明-证据匹配（anti-overclaim）」：① SciWrite 式五段审计清单（Clarity/Voice/Structure/Consistency/Integrity）；② 声明-证据匹配矩阵（claim→证据类型→强度→支撑文献→是否过度）；③ 过度声称红名单（"首次证明/揭示机制/治疗潜力"等降级规则）；④ NSFC 标书特化（立项依据/创新点/可行性绑定预实验证据）。
- `bioinformatics.md` 新增「§十 进阶可执行流水线」：scVI 概率批次校正（scanpy+scvi-tools）、PyDESeq2 差异表达（Python 端）、arboreto GRN 推断、cellxgene Census 公共数据整合，均含脚本骨架+标准参数+managed venv 安装约定。
- `plotting-protocol.md` 新增「Phase 5 期刊 preflight 检查表」（分辨率/色彩空间/字体/线宽/面板标注/尺寸/格式/图注自足 9 项门禁）+「Phase 6 机制通路图/Graphical Abstract 协议」（工具选择+内容规范+课题示例）。
- `prism-style-plot.md` 新增「§五 机制通路图生成协议」（matplotlib 可复现框-箭头骨架，复用 prism_theme 主题）。
- SKILL.md 模块导航：生信/写作/Prism 绘图触发词与描述同步；版本号 → 2.2.3。使用文档.md 模块速查表与文件结构注释同步。

## v2.2.2（2026-08-24）

**文献检索与引用校验能力对齐业界最佳实践（借鉴 nature-ref-verifier / nature-academic-search / nature-citation）**。
- `citation-verification.md` 升级：① 新增「DOI 可解析性先行检查」（最便宜先查，捕获最常见错误）；② 新增**三级严重度分级 + 错误类型目录**（🔴 Critical：作者顺序/漏第5+作者/页码差≥5/文章号字母误判 T/7·l/1·O/0/标题核心词/DOI 张冠李戴；🟡 Warning：卷年≠DOI年/Early Access 漂移/缺期号/页码差≤4；🟢 Info：大小写/缩写/标点）；③ 新增**置信度评估**（Verified / Check suggested / Needs fix / Unverifiable）；④ 新增 **Zotero 写回修正协议**（pyzotero Web 模式、本地只读 501 限制、BibTeX Patch + 更新指令清单）；⑤ 新增「**为主张补引用（claim→reference）**」逆向能力（文本分段、保守评级、证据来源状态标注）。
- 新增 `references/citation-impact-audit.md`：**他引 / 独立引用统计**（排除自引）、高影响力引用者画像、文章级引用指标表，直接服务 NSFC 标书「工作基础」量化论证。
- SKILL.md 模块导航：引用核验协议补充触发词；新增「他引/引用影响审计」条目；NSFC 最小读取集联动该文件。
- 使用文档.md：模块速查表与文件结构（16→17）同步登记 `citation-impact-audit.md`。

## v2.2.1（2026-08-20）

**引用格式默认 numbered（顺序编码制）固化为全局规则，补齐实验设计模块缺口**。
- 根因：`citation-formatting.md` / `manuscript-and-submission.md` 等已写"默认顺序编码制"，但**实验设计模块 `experiment-design.md` 通篇无引用格式约束**，且 SKILL.md 核心原则未提引用格式默认值——导致写实验设计/方案时引用格式可能不统一（混用作者-年制）。
- SKILL.md 核心原则第 1 条：补"引用格式默认顺序编码制（numbered，[1]/[1,3]/[1-5]），作者-年制仅刊方强制时例外"。
- `experiment-design.md`：核心原则新增「### 5. 引用格式（默认顺序编码制）」；实验方案模板新增「## 8. 参考文献（[n] 顺序编码制）」。

## v2.2.0（2026-08-20）

**新增自检脚本 + 补齐冷门场景文档，消除版本/文档漂移**。
- 新增 `scripts/selfcheck.py`：A 部分一致性检查（SKILL.md version vs CHANGELOG 最新、导航表/速查表/结构图引用的 references 与磁盘一致、无孤儿 reference/脚本、模块数一致）+ B 部分引擎冒烟回归（p_to_stars / format_p / mean_sem 纯函数断言 + 5 类图端到端）。零第三方依赖、秒退、只读；退出码 0=全绿。用法见 python-runtime.md §七。
- 自检上线即抓到一处历史漂移：使用文档.md 模块速查表 `citation-verification.md` 漏写 `references/` 前缀，已修复。
- 充实 `citation-formatting.md`：补预印本/数据集/软件/会议/书章/电子资源等冷门类型（Nature 编号制 + GB/T 7714 双体系）、GB/T ≤3 人作者规则、无作者/无年份/同年多篇处理、DOI 与页码范围规范。
- 充实 `academic-word-template.md`：补封面/摘要关键词/目录、python-docx 兜底代码骨架（中文字体 ascii/eastAsia 分设）、三线表画法（1.5pt/0.75pt）、图片分辨率与单双栏尺寸、单位/数字/缩写规范。
- 充实 `python-runtime.md`：补 ensure_env.py 环境引导用法、常见报错排查表（EBADENGINE/权限/编码/中文方块）、pip 镜像源、版本锁定与可复现、改动后自检流程。

## v2.1.0（2026-08-20）

**新增 P0 两类核心 reference，填补项目书与实验报告空白**。
- 新增 `references/proposal-nsfc.md`（~30 KB）：覆盖 H 学科代码选择决策框架（申报代码抉择实操对比表，示例用通用占位、不写死具体二级代码）、NSFC 8 节详版模板（立项依据 4 段漏斗式 / 研究内容 / 方案 / 创新 / 可行性 / 年度计划 / 5 大科目经费预算 / 双盲评审策略 / 写作铁律）、自检清单（10 项硬扣分 + 24h 提交前检查）。
- 新增 `references/experiment-report.md`（~20 KB）：5 类团队内部文档（Standard Lab Report / Weekly Report / Monthly Progress / Failure Log / Data Handover），含元数据 YAML、README 模板、8 件套数据归档规范、写报告硬规范（真实性 / 完整性 / 复现性红线）。
- SKILL.md 顶部新增"高风险产出边界"声明（IACUC / 经费金额 / DOI / 临床数据等 AI 不允许越权生成的 7 类硬红线，仅生成草稿+占位）。
- SKILL.md 导航表新增两条模块（NSFC 项目书 / 实验报告），典型任务最小读取集同步扩展。

## v2.0.10（2026-08-20）

**R/ggplot2 绘图引擎移除，R 定位调整为生信分析**。
- 删除 `scripts/prism_theme.R` / `prism_demo.R`：与 Python 引擎功能重复且无优势，绘图统一走 `prism_theme.py`。
- 新增 `scripts/bioinfo_rna_seq.R`（RNA-seq 差异表达 DESeq2 + GO/KEGG/GSEA 富集完整模板，含依赖守卫与合成 demo 端到端验证，RStudio 中 `demo=FALSE` 接入真实数据）。
- `bioinformatics.md` 运行环境更新：用户本机已装 R / RStudio。
- 绘图引擎 v2.0.40：KM 生存曲线 y 轴顶端刻度 1.0 贴轴顶带标签；≥3 组时左上角标注两两 log-rank 比较显著性（`show_pairwise=True`，未校正，报告注明）。

## v2.0.9（2026-08-20）

**新增 R/ggplot2 绘图引擎 `scripts/prism_theme.R`**——对齐 Python 版 API 与规范：`prism_theme()`（L 形轴/0.75 pt 线宽）、`prism_boxplot()`（箱线图+镜像均衡抖动散点）、`prism_bars()`（单因子/两因子分组柱+误差线+散点）、`add_pairwise_brackets()`（显著性括号按 x 跨度自动分层）、`p_to_stars()` / `format_p()` / `format_legend()`（p 值格式铁律）、`balanced_jitter()`、`ttest_two_groups()` / `oneway_anova_tukey()`（统计封装）、`prism_save()`（PNG+PDF）。附 `scripts/prism_demo.R` 一键验证。R 用户可在 RStudio 直接 `source("scripts/prism_theme.R")` 调用。

> 注：该引擎于 v2.0.10 移除。

## v2.0.8（2026-08-20）

**集成 prism-style-plot 引擎 + 冗余清理**。
- 内建 `scripts/prism_theme.py`（2636 行引擎：`apply_prism_theme` / `prism_boxplot` / `prism_bars` / `prism_violin` / `prism_survival` / `add_pairwise_brackets` / `build_stats_report` / `set_nice_ylim` 等）。
- 内建 `scripts/ensure_env.py` 环境引导（跨平台、幂等）。
- `prism-style-plot.md` 成为推荐绘图入口；`plotting-protocol.md` 降级为纯 matplotlib 兜底（246→96 行）。
- 删除冗余 `statistics-guide.md`（独有规则并入 `statistical-analysis.md`）。
- 跨文件去重：`balanced_jitter` / p 值铁律 / LW=0.75 统一单一权威源。
- `statistical-analysis.md` 398→327 行；修复 `neuro-research-optimized` 旧名引用；压缩图标。

## v2.0.7（2026-08-18）

**紧凑 Y 轴收尾**：bracket 布局与留白改以数据跨度 `span` 为基准，顶部留白从 ~45% 降到 **≤26%×跨度**。三道保险：bracket 紧凑（`y_base = y_max + 0.03*span`、`H_LAYER = 0.05*span`、竖线 0.015*span、星号 0.018*span va=bottom）；步长三阶段选择（50/20/10/5/2/1 优先 4–9 刻度+取整损失≤20%）；程序化验证项「顶部留白比 ≤ 0.26」。

## v2.0.6（2026-08-18）

默认线宽 0.5 → **0.75 pt**——印刷/投影下更清晰，仍属 Nature 系可接受的细线。

## v2.0.5（2026-08-18）

线条粗细统一默认 0.5 pt：所有线条（柱/箱描边、errorbar、bracket、折线、散点描边）统一 `LW = 0.5`。三个演示脚本（`plot_demo.py` / `plot_demo_grouped.py` / `plot_demo_line.py`）同步 `LW=0.5` 并验证 PASS（errorbar 与柱描边一致）。用户明确指定线宽时以其为准。

## v2.0.4（2026-08-18）

p 值下溢边界（`p=<1e-300`）+ Grouped 连线图（重复测量）模板验证（MixedLM **对比矩阵 f_test**，patsy 对 `Treatment(reference=...)` 系数名不支持字符串约束）。新增 `plot_demo_line.py`：线性混合效应模型（subject 随机截距），个体点按 subject 固定横向偏移 + 镜像均衡，均值±SEM 折线，图例置图外右侧。

## v2.0.3（2026-08-18）

修复显著性星号分级逻辑 bug（`**`/`***`/`****` 永不触发）；`FTestAnovaPower` 返回总样本量注释修正；章节重排。

## v2.0.2（2026-08-18）

- **`balanced_jitter` 镜像均衡抖动**固化为全局强制规则（左右点数均衡、组色+黑描边）。
- python-runtime 标准前导修复（`importlib.util` + Agg 后端）。
- 维护审查后：修复标准前导缺失、统一字号规范（轴标题 12–14pt / 刻度 10–12pt）、删除硬编码本机路径、Word 交付补 python-docx 兜底、导航表/版本号全面对齐、压缩图标至 86 KB。

## v2.0.1（2026-08-18）

Grouped 分组柱状图三条强制规则（25% 柱间距 / 柱内 uniform 均匀抖动 / errorbar 线宽与柱描边一致）。

## v2.0.0（2026-08-18）

**自包含重建**：内嵌 `litsearch` / `citation-verification` / `citation-formatting` / `plotting` / `python-runtime` 五份协议；Python-first 运行环境，无外部硬依赖。

## v1.0.0（2026-08-17）

首版 skillhub 发布（7 阶段全流程）。
