---
name: academic-radar
description: Use when a clinician, medical researcher, graduate student, or other researcher wants to install, configure, run, schedule, or maintain Academic Radar for literature monitoring across PubMed, Semantic Scholar, OpenAlex, preprint servers, arXiv, X, and RSS. 引导用户逐步完成研究方向拆解、关键词校准、模型与推送渠道配置、首次实跑及定时任务，并守住书目信息可追溯和反幻觉边界。
version: 1.0.0
author: LIN
license: MIT
metadata:
  hermes:
    tags: [academic-research, literature-monitoring, pubmed, medical-research, automation]
    related_skills: []
---

# Academic Radar 学术雷达

## Overview

Academic Radar 是面向临床医生、医学科研人员和研究生的定时文献监测工具。它从多个学术数据源抓取新内容，先由确定性代码做关键词筛选与去重，再让 LLM 只负责相关性评分和基于原摘要的总结，最后通过用户选择的渠道推送并保留可追溯存档。

这个 Skill 的职责是让 Agent 完成从安装到长期运维的完整闭环，而不是把命令丢给用户。用户只需要用自然语言描述研究方向、接收渠道和频率；Agent 负责检查环境、拆解关键词、写配置、安装依赖、建立调度并真实跑通。

## When to Use

在以下情况加载本 Skill：

- 用户要求安装、部署或试用 Academic Radar / 学术雷达；
- 用户想持续追踪某个研究领域的新论文、预印本、会议动态或指定作者；
- 用户要增加关键词、排除噪音、调整检索频率、切换推送渠道或更换评分模型；
- 用户反馈没有收到报告、重复推送、检索结果太多或太少；
- 用户怀疑报告中的论文、DOI、作者或结论不真实，需要追溯核验。

不要用它替代一次性的系统综述、诊疗决策或完整循证检索。Academic Radar 是持续监测工具，不保证穷尽所有证据，也不替代人工核查。

## Source of Truth

开始操作前按需读取仓库文件，避免在本文件里维护重复规则：

1. 首次接入、配置或排障：完整阅读 [`AGENT.md`](./AGENT.md)。
2. 设计研究关键词：必须阅读 [`keyword_template.yaml`](./keyword_template.yaml)，按六层结构展开。
3. 理解用户体验和产品边界：阅读 [`README.md`](./README.md)。
4. 只有需要理解架构决策时才读取 [`academic-radar-prd-v2.md`](./academic-radar-prd-v2.md)。

`AGENT.md` 是安装、文件修改边界、调度和反幻觉验证的详细操作手册；若与本文件的摘要存在差异，以当前代码和 `AGENT.md` 为准。

## First-Run Workflow

### 1. Preflight

先只读检查，不要立刻安装或修改配置：

- Python 是否为 3.9 或更高；
- 安装位置是否适合长期运行；
- 系统或 Agent 框架可用哪一种定时器；
- 已配置哪些 LLM provider，只报告“存在/不存在”，不得输出密钥；
- 用户可用的推送渠道及所需凭证；
- 仓库是否公开、配置文件是否可能被提交。

完成标准：明确运行目录、Python 环境、至少一个可用 LLM 方案、至少一个推送方案和唯一的调度机制。

### 2. Guide the User One Question at a Time

不要把配置表一次性扔给用户。按顺序引导：

1. 研究方向，用一两句话描述；
2. 根据 `keyword_template.yaml` 主动生成六层候选词：疾病/领域本体、药物或干预、临床试验与联合方案、机制通路、诊断与标志物、排除词；
3. 逐层让用户确认，尤其确认排除词，避免误伤；
4. 询问需要重点追踪的作者或机构；
5. 让用户选择推送渠道；
6. 根据环境中真实可用的 provider 给出模型选项，不要求用户重复提供已有密钥；
7. 根据领域出文速度推荐检索频率和时间点，让用户拍板。

关键词匹配是子串匹配且顺序敏感。不要只生成一个过宽关键词，也不要把完整论文标题当关键词。英文为主、中文为辅；修改拼写或标准名称后要告诉用户。

完成标准：用户已确认研究方向、关键词与排除词、作者/机构、推送渠道、模型、频率和时间点。

### 3. Install in a Stable Directory

典型安装命令：

```bash
git clone https://github.com/banxia-O/Academic-Radar.git ~/academic-radar
cd ~/academic-radar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

VPS 服务可安装到 `/opt/academic-radar/`；临时验收才使用临时目录。不要把长期任务放进会被自动清理的目录。

完成标准：虚拟环境可用，依赖安装成功，`python -m py_compile radar_main.py` 不报错。

### 4. Configure Without Leaking Secrets

主要只编辑 `academic_radar_config.yaml`：

- `topics`、`research_focus`、`authors`、`exclude`；
- `schedule` 和 `timezone`；
- 数据源开关、RSS、输出条数；
- LLM 与推送渠道配置。

当前程序不会展开 `${ENV_VAR}`，密钥需要按 `AGENT.md` 描述配置。配置后至少执行：

```bash
chmod 600 academic_radar_config.yaml
```

不要把真实密钥提交到公开仓库。写入前检查部署目录的 Git 状态，写入后再次检查 diff 中是否出现凭证；必要时使用独立部署副本，不在开发仓库里保存生产配置。

完成标准：配置文件权限受限、无凭证进入待提交 diff、LLM 最小请求和推送渠道均单独验证成功。

### 5. Run a Real Smoke Test

在项目虚拟环境中执行：

```bash
cd ~/academic-radar
.venv/bin/python radar_main.py
```

不能仅以进程退出码判断成功。检查日志和最新存档，确认：

- 至少一个已启用数据源真实返回或给出可解释的空结果；
- 关键词筛选、LLM 评分、DOI 验证、去重和存档阶段按顺序完成；
- 推送渠道返回成功；
- 最新 `data/radar/*.json` 中的条目具有可追溯来源；
- 标题、作者、DOI 来自抓取结果，没有由 LLM 补写。

无新增论文可以是正常结果，但 API、鉴权或推送错误不能伪装成“今日无新增”。

完成标准：一次真实执行完成，并能指出日志、存档和送达结果的位置。

### 6. Install Exactly One Scheduler

根据 `AGENT.md` 的频率映射选择系统 cron 或 Agent 自带调度器，二者不要并用。使用虚拟环境的 Python 绝对路径和项目绝对路径。

安装后立即：

- 列出定时任务，确认没有重复项；
- 手动触发一次同一执行命令；
- 核对时区、下次运行时间和日志路径；
- 确认失败时有可见告警，不静默吞错。

完成标准：定时任务已真实注册、手动触发成功、下一次运行时间正确且不存在重复调度。

## Routine Operations

日常维护优先修改 `academic_radar_config.yaml`：

- 增加关键词、排除词、作者或机构；
- 调整数据源、RSS、输出上限和去重窗口；
- 更改频率；
- 更换模型或推送渠道。

仅当时间点、monthly、twice_daily、every_4_hours 等 cron 形态发生变化时重装调度。改完配置后至少执行一次针对性验证，不要只说“已修改”。

代码修改边界、常见请求映射和详细排障顺序见 `AGENT.md`。除非用户明确要求开发新功能，否则不要改 `fetchers/`、`models.py`、DOI 验证、去重算法或主流水线顺序。

## Anti-Hallucination Boundary

始终保持以下约束：

- LLM 只输出相关性评分和基于原摘要的总结；
- LLM 不生成或改写标题、作者、DOI、期刊等书目信息；
- 总结不得加入摘要中没有的数据和结论；
- 不使用通用网页搜索去“补全”缺失书目信息；
- 用户质疑某条论文时，优先检查存档中的 `fetch_sources`、`abstract_source` 和 DOI 验证信息，再查原始来源；
- 若书目信息不一致，停止推送并回退可疑改动，不做未经验证的热修复。

## Common Pitfalls

1. **把 Skill 当脚本说明书。** Agent 必须主动完成用户引导、配置、实跑和调度，不应让用户自己照 README 敲完所有命令。
2. **一次问完所有配置。** 用户通常只能先说研究方向；Agent 应逐层展开和确认。
3. **只看 stdout 有“Done”。** 必须核对真实数据源、存档和推送送达。
4. **明文密钥进入 Git。** 配置文件当前需要本地密钥，公开仓库尤其要检查 diff 和文件权限。
5. **cron 与 Agent 调度器重复。** 会造成重复抓取、重复推送和状态竞争。
6. **为了丰富报告让 LLM 补背景。** 这会破坏可追溯设计并制造幽灵引用。
7. **把无新增和抓取失败混为一谈。** 先检查各数据源统计与错误日志。

## Verification Checklist

- [ ] 根目录、README、AGENT.md、配置和入口脚本均来自同一仓库版本
- [ ] Python 版本、虚拟环境和依赖通过
- [ ] 用户逐步确认了六层关键词与排除词
- [ ] LLM 与推送渠道分别烟测成功
- [ ] 配置文件权限受限且 Git diff 不含凭证
- [ ] `radar_main.py` 完成一次真实执行
- [ ] 最新存档中的条目可追溯到原始数据源
- [ ] 只安装了一个调度器且已手动触发验证
- [ ] 告知用户下一次运行时间、报告去向和后续自然语言维护方式
