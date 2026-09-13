# DESIGN.md — 论文数据造假检测器

## 架构总览

```
用户 PDF → [1.元数据提取] → [2.表格提取] → [3.检测器运行] → [4.HTML报告]
              PyMuPDF        Camelot+pdfplumber    9 detectors       内嵌数据HTML
```

四阶段 Pipeline，无状态。每个阶段可独立失败降级（如 Camelot 缺失时回退 pdfplumber-only）。

## REQ（功能需求）

| ID | 优先级 | 需求 | 验证标准 |
|----|:---:|------|---------|
| REQ-1 | P0 | 输入 PDF 路径，输出 HTML 造假嫌疑报告 | 跑已知造假论文，检测器命中 |
| REQ-2 | P1 | 9 种检测器全覆盖（GRIM 推迟到 v2.0）| 每种检测器有对应测试用例 |
| REQ-3 | P1 | 智能过滤页码/行号/文本块误报 | 纯正文论文 0 假阳性 |
| REQ-4 | P2 | 报告含风险评级 + 分布图 + 详表 | HTML 自包含、可在任意浏览器打开 |
| REQ-5 | P1 | 红旗精确定位（页码+表格+列名）+ 证据样本 | 每条 flag 含 location/evidence_text 字段，HTML 可见 |
| REQ-6 | P0 | 无有效数值表时单独标记证据不足 | `data_status="insufficient_data"`，不展示"通过检测" |

## NFR（非功能需求）

| ID | 需求 | 实现 |
|----|------|------|
| NFR-1 | pip install 友好 | 依赖检测 + 缺失提示 + 安装命令 |
| NFR-2 | 降级运行 | Camelot 缺失时回退 pdfplumber-only |
| NFR-3 | Token 预算 | L0:100, L1:600, L2:2000, hard_cap:3000 |
| NFR-4 | 不修改输入 | 只读 PDF，所有输出写入新文件 |
| NFR-5 | WorkBuddy 优先 | 保留 WorkBuddy frontmatter 扩展字段，跨平台兼容性另行处理 |

## 候选方案对比

| 决策点 | 选项 A（选用）| 选项 B | 选项 C |
|--------|:---------:|--------|--------|
| 表格提取引擎 | Camelot + pdfplumber 双引擎 | MinerU（深度学习，OOM 风险）| 仅 pdfplumber |
| 检测器位置 | 内联 detect.py | 独立 script per detector | 外部库依赖 |
| 报告格式 | 自包含 HTML | JSON + 前端渲染 | Markdown |

## ADR-001：为什么用 Camelot + pdfplumber 双引擎

**背景**：Nature/Science 论文的表格主要是无边框的（stream 模式），少数有边框（lattice 模式）。

**决策**：Camelot lattice（有边框）→ Camelot stream（无边框）→ pdfplumber（补充）。

**理由**：Camelot 表格定位更准但可能漏；pdfplumber 覆盖更全但结构差。双引擎互补。

**后果**：引入 OpenCV 依赖（Camelot 需要），增加安装复杂度。但表格检出率提升显著。

## ADR-002：为什么所有检测器内联在单文件中

**背景**：9 种检测器 ~300 行，单独拆文件会增加维护负担和 import 路径管理。

**决策**：所有检测器 + 提取 + 报告 + CLI 入口全部在一个 `scripts/detect.py` 中（~550 行）。

**理由**：skill 的定位是"单文件工具"而非"库"。内联保证了零外部依赖（除 pip 包外），任何 Python 环境直接跑。

**后果**：文件略长，但结构清晰（四阶段分段 + 注释分隔线），可读性不损失。

## SKILL vs DESIGN 边界

| 内容 | 放在 SKILL.md | 放在 DESIGN.md |
|------|:---:|:---:|
| 触发词/路由表/核心原则 | ✅ | — |
| 执行流程（4 阶段） | ✅ | — |
| 错误处理/降级策略 | ✅ | — |
| 输出文件约定 | ✅ | — |
| 功能需求（REQ/NFR） | — | ✅ |
| 候选方案对比/ADR | — | ✅ |
| 架构总览/V1.0 范围 | — | ✅ |
| 已知局限（工程级） | — | ✅ |

**原则**：SKILL.md 是给 AI 的操作手册，DESIGN.md 是给人的设计档案。操作细节进 SKILL，设计决策进 DESIGN。

## v1.1 范围

- ✅ PDF 输入 → HTML 报告
- ✅ 9 种检测器
- ✅ 双引擎表格提取 + 智能过滤
- ✅ 跨引擎重复抽取过滤，避免同一表被误判为跨表复用
- ✅ **精确定位**：每条红旗标注 Page + 表格序号 + 列名 + 证据样本
- ✅ 无有效数值表时输出"证据不足"
- ❌ Excel/CSV 输入（推迟到 v2.0）
- ❌ 批量处理（推迟到 v2.0）
- ❌ 图像取证（超出数值检测范围，不在 roadmap）

## 已知局限

| 局限 | 影响 | 缓解 |
|------|------|------|
| Nature/Science 正文以图为主 | 数值表格提取率低（可能 0 检出）| 提示用户提供 Supplementary Excel |
| 拼音匹配不区分同名 | 作者归属可能错配 | 机构限定消歧（本 skill 不涉及作者匹配）|
| Camelot 需 OpenCV | 安装复杂度增加 | 自动降级 pdfplumber-only |
| 仅检测数值数据 | 图像 PS/重复无法覆盖 | 明确边界——本 skill 不是图像取证工具 |
