# 数据分析&汇报小助手

**把一张业务表，变成有判断、有依据、能汇报的经营简报。**

面向运营、销售、产品及业务负责人。提供一张 Excel／CSV 和汇报目标，由 AI 找重点、查依据、组织结论与行动建议，适合周报、月报、活动复盘和阶段经营汇报。

> **第一次使用：** 把文件交给能够读取文件并运行本地 Python 的 AI 工具，然后说“请用 sheet-to-report 分析这份表，面向业务负责人做月度复盘，先生成 HTML”。用户不需要编写代码或配置 JSON。

[在线看完整案例](https://majichuan.github.io/sheet-to-report/) · [三步开始](https://github.com/majichuan/sheet-to-report/blob/main/QUICKSTART.zh-CN.md) · [常见问题](https://github.com/majichuan/sheet-to-report/blob/main/FAQ.md) · [安装与环境](https://github.com/majichuan/sheet-to-report/blob/main/INSTALL.md)

> **English summary:** Turn a structured Excel or CSV table into an evidence-traceable business review with actionable insights, an offline HTML report, an editable PPT, and optional SlideViber refinement. Chinese-first in v0.2.

**[在线查看完整案例展示](https://majichuan.github.io/sheet-to-report/)** · [GitHub 源码与安装说明](https://github.com/majichuan/sheet-to-report)

## 你能拿到什么

| 产物 | 适合怎么用 |
| --- | --- |
| **HTML 分析简报** | 看整体表现、重点判断、图表与行动；通过导航和证据链接查看依据，单文件可离线阅读 |
| **标准汇报 PPT** | 用可编辑的汇报页讲清概况、结论、支撑依据与下一步，页面指引让听众跟上主线 |
| **SlideViber 美化 PPT（可选）** | 沿用标准稿内容，进一步设计演示构图；另存美化版，保留标准稿和完整信息 |

## 哪些时候最适合用

已经有一张业务表，却不确定**先看什么、变化如何解释、下一步做什么**。

可用于销售业绩与区域贡献、渠道增长与效率、用户活跃与分层、电商交易与商品结构等复盘。需要相应的时间、对象和指标字段；内容表现、项目进展等任务可先确认方案，再按实际数据进行通用分析。

## 四个核心优势

- **抓重点：** 围绕业务问题选择有价值的变化、机会与风险，把发现组织成清楚的汇报主线。
- **追依据：** 数字按明确口径计算，必要时在表内继续比较、细分与补查；证据不足就说明限制。
- **落行动：** 建议指向具体人群、渠道、商品或环节，写清做法、验证信号与边界。
- **三版同源：** 图表按结论和数据匹配，HTML与两版PPT共享分析依据，美化不改数字或漏掉内容。

## 怎么开始

把文件交给支持本地脚本执行的 AI 工具，例如这样说：

> 请用 sheet-to-report 分析这份 Excel，面向业务负责人做月度复盘。说明整体表现、主要变化、机会风险和下一步建议。先生成 HTML，再生成标准 PPT；PPT 请先给我两页真实风格小样。

可以选择**直接分析**，或**先确认分析方案**。生成PPT前，未指定风格时先看真实小样；明确让AI代选时，默认“清晰商务”。

标准稿完成后，可选择继续使用 [SlideViber](https://github.com/tf71991/slideviber-skill) 美化。是否安装、是否继续由你决定；不安装也能使用HTML和标准PPT。

遇到环境、工作表、指标口径或平台模型错误时，先看[常见问题](https://github.com/majichuan/sheet-to-report/blob/main/FAQ.md)。后续阶段失败时应保留已经通过的产物。

## 使用前了解

支持**一张结构清晰的 Excel／CSV**。AI工具须能读取文件、运行Python并组织分析；PPT另有依赖，详见[安装与使用说明](https://github.com/majichuan/sheet-to-report/blob/main/INSTALL.md)。不承诺所有AI工具或系统都兼容，不用于高风险决策。

**不绑定任何案例。** 每次分析你的当前数据；如需试用，可用内置脚本在本地生成轻量业务模拟样例，不会套用预设结论。多表联合、数据库接入和后台定时运行不属于当前版本。
