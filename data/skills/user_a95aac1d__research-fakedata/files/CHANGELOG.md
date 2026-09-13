# Changelog

## [1.1.3] - 2026-07-06

### Fixed
- SKILL.md 文件结构表补充遗漏的 `tests/test_detect.py`
- SKILL.md JSON schema 中 `flags[].type` 注释修正为实际返回类型名
- README 删除不相关的"同名作者混淆"限制
- `.consistency.yml` 添加占位意图注释

## [1.1.2] - 2026-07-06

### Fixed
- 修复末位数字检测：不再把固定小数格式补出的尾随 0 当成真实末位数字，降低误报。
- 无有效数值表时新增"证据不足"状态，不再展示"未发现异常/通过全部检测器"。
- 依赖缺失提示改用真实 pip 包名，例如 `PyMuPDF (fitz)` 映射为 `pymupdf`。
- 跨表检测跳过同页同数值矩阵的重复抽取，避免 Camelot/pdfplumber 抓到同一表后互相报警。
- 统一脚本、HTML 和文档中的"9 种检测器，GRIM v2.0"表述。

### Added
- 新增 `tests/test_detect.py`，覆盖末位数字、证据不足、依赖提示、跨引擎重复过滤和 9 种检测器基本行为。

## [1.1.0] - 2026-06-23

### Added
- 🔑 **精确定位**：每个红旗标注 `📍 Page X, 表格 Y, 列「Z」`，人工可直接翻到 PDF 对应位置验证
- 📊 **证据样本**：每个红旗显示前 5-8 行原始数值，不需重新提取即可快速目检
- 跨表检测器也支持定位（`跨表 — Page 3 表格 1 vs Page 5 表格 2`）
- HTML 红旗列表中新增定位行和证据行样式
- README 新增「WorkBuddy 中使用」章节，说明首次运行自动检测依赖的流程

### Changed
- 检测器数量从 10 调整为 9（GRIM 因需 NLP 提取样本量 n，推迟到 v2.0）
- 有效表格数在 HTML 报告和终端输出保持一致（修复 card 显示原始表格数的 bug）
- 全文档「10 种」→「9 种」批量同步（SKILL / README / DESIGN / CHANGELOG）
- pip install 命令补全遗漏的 pandas 和 opencv-python

### Fixed
- Camelot stream 去重逻辑：增加首格值比对，避免同页不同内容的同形表格被误合并
- 跨表检测器：新增匹配单元格证据（前 5 个匹配位置的坐标和值）

## [1.0.0] - 2026-06-23

### Added
- 首次发布
- 10 种统计检测器：末位卡方、固定差值、固定倍数、等差/等比数列、小数位重复、取整异常、GRIM、本福特、重复列、跨表相同
- PDF 元数据提取（标题/DOI/PMID/作者）
- 双引擎表格提取（Camelot lattice + stream + pdfplumber）
- 智能文本过滤（排除 Camelot 误抓的正文段落）
- 页码/行号/序列号自动排除（减少等差/等比误报）
- HTML 报告（风险等级、统计卡片、红旗列表、检测器分布图、免责声明）
- 输出格式规范（风险阈值表、JSON schema、HTML 占位符映射）
- pip install 友好：依赖检测 + 缺失提示
- 已验证：王平 Nature (PMID 39567688) 和陈佺 Nature Cancer (PMID 38291304) 的已知造假模式均可检出
