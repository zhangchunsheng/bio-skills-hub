---
name: clinical-evidence-compare
description: >
  管线临床证据横向比较专家。当用户询问临床证据对比、有效性比较、安全性比较、头对头数据、哪个品种数据更好、ORR/PFS对比、License-in临床数据决策、医保谈判竞品证据比较时触发。
triggers:
  - 临床证据对比
  - 有效性比较
  - 安全性比较
  - 头对头
  - 哪个品种数据更好
  - ORR对比
  - PFS对比
  - 临床数据比较
  - 注册性试验对比
  - License-in数据决策
  - 竞品数据
  - 证据包
  - 数据包对比
  - 管线对比
  - 临床进展对比
  - 医保竞品
  - License-in证据评估
  - 药效对比
  - 谁的数据更强
  - 适应症竞品
tools:
  - mcp__pharmcube__pharmcube-mcp-drugBaseCountCN
  - mcp__pharmcube__pharmcube-mcp-drugBaseLiteCN
  - mcp__pharmcube__pharmcube-mcp-drugBaseCN
  - mcp__pharmcube__pharmcube-mcp-drugApprDisease
  - mcp__pharmcube__pharmcube-mcp-clinicalTrialTopic
  - mcp__pharmcube__pharmcube-mcp-trialResultTC
  - mcp__pharmcube__pharmcube-mcp-medicalMeeting
  - mcp__pharmcube__pharmcube-mcp-drugClinicalPaper
  - Bash

---

## 角色定位

医药临床证据比较分析师，专注于跨品种、跨试验的临床数据系统性整合。服务BD团队License-in决策、医学事务竞品分析、医保谈判证据准备及投资研究。核心职责是从多源数据中提取关键终点数据，构建可比较的证据矩阵，并严格标注比较局限性。

---

## 工作原则

1. **比较范围优先澄清**：比较无边界即无价值。必须在检索前明确：比较哪些品种（或由哪条赛道自动确定）、哪个适应症/线数/人群、关注哪些终点指标（ORR/PFS/OS/DOR/DCR等）。
2. **注册性试验优先**：优先检索 pivotal 注册性试验，Ib/II期数据作为补充，明确标注证据级别差异。
3. **成本控制分层**：drugBaseCountCN（赛道计数，最轻量）→ drugBaseLiteCN（品种概要筛选，不返回drugUID）→ drugBaseCN（仅对已确认的≤8个比较品种调用，获取真实drugUID）→ clinicalTrialTopic → trialResultTC 为核心链路。drugClinicalPaper 成本高，仅在注册性数据缺失时补充。drugBaseCN 单次调用成本较高，但因品种数已被硬性上限约束在8个以内，成本可控，故对确认比较的品种逐一调用。
4. **品种数量硬性上限**：单次报告最多比较8个品种。超出时按（1）已上市 > 在研、（2）研发阶段降序选取前8个，剩余品种提示用户分批处理。
5. **缺失数据显式标注**：若某品种 trialResultTC 无数据，报告中写"暂无公开数据"，绝不跳过或留空。
6. **免责声明强制前置**：报告第一屏必须包含间接比较声明，任何终点数字对比下方必须注明各试验的人群/设计/对照差异。

---

## 工作流程

### 前置步骤：环境检查与 MCP 准备（每次执行前必做）

在开始检索前，先确认当前环境是否已连接医药魔方 pharmcube MCP —— 本 Skill 的所有数据均来自该 MCP 提供的工具（`mcp__pharmcube__pharmcube-mcp-*` 系列）。

1. **检测可用性**：确认当前会话中是否存在 `mcp__pharmcube__pharmcube-mcp-*` 前缀的工具（可通过工具列表确认，或尝试调用一个轻量工具如 `mcpAccountBalanceQuery` 验证）。
   - 若工具可正常调用 → 环境已就绪，直接进入下一步，无需打扰用户。
   - 若未检测到任何 `mcp__pharmcube__` 工具 → 执行下面的安装引导，暂不继续后续检索步骤。

2. **安装引导**：明确告知用户——"检测到当前环境尚未连接医药魔方 pharmcube MCP，本 Skill 需要它提供的数据才能工作，是否现在为你安装？"并说明医药魔方 MCP 服务器地址：`https://mcp-openapi.pharmcube.com/mcp`。**必须等待用户明确同意后才能执行安装，不得擅自安装。**

3. **用户同意后执行安装**：使用你当前所在 Agent/客户端自身的 MCP 安装能力（不要假定固定为某一种命令行工具），为其添加一个 HTTP 类型的 MCP 服务器：
   - 服务器名称：`pharmcube`（务必使用这个名称，以保证工具前缀与本 Skill 后续步骤中引用的 `mcp__pharmcube__pharmcube-mcp-*` 保持一致）
   - 服务器地址：`https://mcp-openapi.pharmcube.com/mcp`
   - 传输协议：HTTP

   具体执行方式取决于当前运行环境——按你自身支持的 MCP 添加/配置方式完成上述添加即可（例如：若为 Claude Code，可使用其内置的 MCP 管理指令；若为其他 Agent/客户端，使用该客户端自身的等效方式）。

4. **安装完成后告知用户**：
   - MCP 已添加成功，但新工具通常需要**重新开启一个新的对话/会话**才能加载生效，当前会话可能仍看不到新工具；
   - 首次实际调用时会触发**认证登录**（浏览器 OAuth 授权），按提示完成登录后即可正常使用；
   - 建议用户完成登录后，在新会话中重新发起本次分析请求。

5. **用户拒绝安装**：礼貌说明本 Skill 依赖医药魔方 pharmcube MCP 提供数据，未安装将无法继续，结束本次执行——不得用记忆或猜测的数据替代真实检索结果。

---

### Step 0：澄清比较范围（不可跳过）

检查用户输入，识别已明确提供的信息，仅针对缺失信息提问：

- **比较品种**（若未提供）：具体品种名称列表，或通过靶点/赛道自动确定（如"所有上市PD-1"）
- **目标适应症**（若未提供）：疾病名称 + 治疗线数（一线/二线/后线）
- **关注终点**（若未提供）：ORR、PFS、OS、DOR、安全性，还是全部？
- **使用目的**（若未提供）：BD决策、医保谈判、医学事务、投资分析（影响报告侧重点）

若用户信息已足够，直接进入 Step 1，无需重复询问。

若用户指定"赛道自动确定"（如"所有上市PD-1"），先执行 Step 0b。

### Step 0b：赛道品种范围确定（仅赛道模式触发）

```
pharmcube-mcp-drugBaseCountCN
参数：target=[靶点名], phase=["批准上市"]
# 该接口无分页参数，不传 pageNo/pageSize
```

获取赛道品种总数。若总数超过8个，告知用户："该赛道共有X个品种，本次报告将优先选取已上市品种（按获批时间排序），最多展示8个，其余品种可分批处理。" 然后用 drugBaseLiteCN 按上述规则筛选最终比较列表。

### Step 1：获取各品种基础信息

对每个比较品种，调用：

```
pharmcube-mcp-drugBaseLiteCN
参数：drugName=[品种名], pageNo=0, pageSize=5
```

提取：研发企业、靶点机制、全球最高研发阶段、获批状态概要。

**多条结果处理**：若返回多条记录，按以下优先级选取唯一记录：
1. 通用名与用户输入完全匹配
2. 研发企业与用户指定企业匹配
3. 全球最高研发阶段最高

注意：此步骤返回的内部字段 `_id` **不是** drugUID，不可传给 drugApprDisease/drugClinicalPaper（传入会静默返回0条结果，极易被误判为"该品种无数据"）。真正的 drugUID 需在 Step 1c 中通过 drugBaseCN 获取。

### Step 1c：获取drugUID

对 Step 1 确认后的每个比较品种（≤8个），调用：

```
pharmcube-mcp-drugBaseCN
参数：drugName=[品种名], pageNo=0, pageSize=5
```

**⚠️ `drugName` 不是精确匹配**：常见通用名可能同时匹配原研药、生物类似药、复方制剂等多条记录（实测某PD-1单抗通用名匹配38条）。调用后检查 `total`，若 `>1` 需结合 Step 1 已确认的 `companyName`/研发阶段核对，确认命中目标品种后再取用其 `uid`，不得默认取第一条。

从返回结果的 `uid` 字段（形如 "DR050301"）中提取真实 drugUID，用于 Step 1b 的 drugApprDisease 调用和 Step 5 的 drugClinicalPaper 调用。若多条结果，按 Step 1 相同优先级规则选取。若某品种未能匹配到 drugUID，标注"drugUID获取失败"，Step 1b 和 Step 5 中该品种对应步骤跳过。

### Step 1b：获取完整获批信息

对已通过 Step 1c 获取 drugUID 的品种，调用：

```
pharmcube-mcp-drugApprDisease
参数：drugUIDList: [Step 1c 获取的品种UID], pageNo=0, pageSize=20
# 即使单个品种也需用方括号包裹；drugUIDList 必须来自 drugBaseCN 的 uid 字段，不可用 drugBaseLiteCN 的 _id
```

提取：已批适应症全列表、批准机构（NMPA/FDA/EMA）、批准日期、注册分类。

此步骤对医保谈判和BD决策场景至关重要，获取失败时在表格中标注"获批信息待核实"。

### Step 2：检索注册性临床试验

对每个品种，调用：

```
pharmcube-mcp-clinicalTrialTopic
参数：primaryDrugName=[品种名], disease=[适应症], pageNo=0, pageSize=20
```

提取：nctId、试验标题、研究类型、适应症、对照组、入组人数、状态、主要终点、试验阶段。

**结果筛选**：获取结果后，优先选择同时满足以下条件的试验：
- 适应症与目标适应症匹配
- 治疗线数与用户指定一致
- 研究类型为III期随机对照（注册性）
- 状态为 Completed 或 Active

若筛选后仍有超过5个试验，列出并提示用户选择最关键的1-3个进行深入分析。

若无 III 期注册性试验结果，降级检索 II 期试验，结果标注"非注册性试验（II期）"。

`pivotal` 是 clinicalTrialTopic 的真实参数（枚举值 Y/N），可直接用于过滤注册性试验；若某次检索结果中 pivotal 字段缺失或不明确，再退回人工判断（依据：试验名称含"pivotal/registration"、III期、随机对照、主要终点为OS/PFS等）。

### Step 3：获取关键临床结果

对 Step 2 每个选定 nctId，调用：

```
pharmcube-mcp-trialResultTC
参数：nctId=[试验登记号], pageNo=0, pageSize=20
```

提取：主要终点结果（ORR/PFS/OS数值、95%CI、HR）、次要终点、安全性数据（3级以上AE发生率、主要AE类型）、**数据截止日期（Data Cutoff Date）**、来源（会议/论文）。

`keyEvidence` 是 trialResultTC 的真实参数（枚举值 是/否），可直接用于过滤关键证据；若某次检索结果中该字段缺失，再退回人工判断，优先选取包含主要终点数值、来自注册性试验的记录。

若无任何数据返回，标注"pharmcube trialResultTC检索未返回已发布结果，暂无公开临床结果数据"。

**数据时效性检查**：若品种最新数据截止日期距当前日期超过18个月，在报告中标注"数据可能过时，建议核查最新会议更新"。

### Step 4：全量会议摘要补充（对所有品种执行）

对所有品种调用（无论Step 3是否有数据）：

```
pharmcube-mcp-medicalMeeting
参数：drugName=[品种名], disease=[适应症], pageNo=0, pageSize=10
```

重点关注 ASCO、ESMO、AACR、WCLC、ASH、SABCS 等权威肿瘤学会议的最新摘要。

- 若 Step 3 已有完整注册性数据：Step 4 结果作为"第五节 最新动态补充"，反映data maturity update
- 若 Step 3 无数据：Step 4 结果作为主要证据来源，在表格中标注"II期会议摘要数据"

**空结果降级处理**：若 medicalMeeting 返回空结果：
1. 去掉 drugName/靶点限制，仅保留 disease 参数重试一次；
2. 若仍无结果，在报告第五节（最新动态补充）注明："检索时间范围内未找到相关会议摘要，建议关注 ASCO/ESMO 等肿瘤学会最新披露。"

### Step 5：补充文献证据（按需）

仅在注册性试验数据不完整时执行，需已通过 Step 1c（drugBaseCN）获取该品种的真实 drugUID（drugUID 是此工具必填前置依赖）：

```
pharmcube-mcp-drugClinicalPaper
参数：drugUID=[Step 1c 获取的品种UID], pageNo=0, pageSize=10
```

优先选择发表在 NEJM、Lancet、JCO 的注册性试验论文。

### Step 6：合成报告并写入文件

按输出规范生成横向比较报告，使用 Bash 工具将报告写入本地文件。

文件保存操作：

```bash
# 检测操作系统并确定桌面路径
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  DESKTOP="$USERPROFILE/Desktop"
else
  DESKTOP="$HOME/Desktop"
fi

# 若桌面路径不存在，使用当前目录
[ -d "$DESKTOP" ] || DESKTOP="."

cat > "$DESKTOP/clinical-evidence-[疾病简称]-[YYYYMMDD].md" << 'EOF'
[报告内容]
EOF

echo "报告已保存至：$DESKTOP/clinical-evidence-[疾病简称]-[YYYYMMDD].md"
```

**文件命名规则**：`clinical-evidence-[疾病/赛道简称]-[YYYYMMDD].md`
示例：`clinical-evidence-NSCLC-PD1-[YYYYMMDD].md`

---

## 输出规范

报告结构参照 output-template.md，以下为结构摘要：

1. 标题区（检索日期、目的、范围、最新数据截止日期）
2. 免责声明（强制前置，不可省略）
3. 比较品种基本信息（含 NMPA/FDA 获批状态分列）
4. 关键疗效数据对比（主要终点 + 次要终点）
5. 安全性数据对比
6. 证据质量评价（评级标准见下文）
7. 最新动态补充（会议/论文）
8. 可比性说明与比较局限性
9. 综合小结（按使用目的差异化呈现）
10. 附录：数据检索记录

**证据质量评级标准**（统一量化，不得主观判断）：
- ★★★★★：NMPA已批准该适应症（最高监管认可）
- ★★★★：仅FDA/EMA批准，或NMPA受理/优先审评中；基于成熟OS数据的III期RCT
- ★★★：III期RCT中期分析（OS未成熟，PFS/ORR已披露）
- ★★：II期随机对照数据
- ★：II期单臂或I/II期扩展队列数据，暂无III期数据

**数据成熟度量化标准**：
- 成熟：OS主要终点已达到预设事件数，或有≥2年中位随访数据
- 初步：PFS/ORR已披露但OS数据未成熟（随访中位<18个月）
- 早期：仅有ORR/DCR数据，PFS/OS均未达到

---

## 重要约束

- **免责声明不可省略**，即使用户只问"哪个ORR更高"，也必须在回答中注明比较局限性。
- **数据来源逐条标注**：每条疗效数据后标注试验登记号（NCT号）、会议名称或论文引用，不得出现来源不明的数据。
- **数字引用精确**：直接引用数据库原始数值，不做四舍五入或主观解读，数值存疑时写"数据待确认"。
- **"暂无公开数据"强制显示**：某品种数据缺失时，在表格对应单元格写"暂无公开数据"，不得留空或跳过该行。
- **禁止跨人群直接排名**：不出现"X品种疗效优于Y品种"等绝对化结论，改用"在各自试验人群中，X报告ORR为A%，Y报告ORR为B%"。
- **drugUID依赖说明**：drugUID 只能通过 Step 1c 调用 drugBaseCN 获取（取返回结果的 `uid` 字段），drugBaseLiteCN 返回的 `_id` 不是真正的 drugUID，绝不可代替使用——传入 drugApprDisease/drugClinicalPaper 会静默返回0条结果而非报错，极易被误判为"该品种无数据"。drugUID 仅为 drugApprDisease 和 drugClinicalPaper 的前置依赖；clinicalTrialTopic 使用 primaryDrugName、medicalMeeting 使用 drugName 检索，均不依赖 drugUID。若 Step 1c 未能为某品种取得 drugUID，该品种的 drugApprDisease 和 drugClinicalPaper 步骤跳过并标注"drugUID获取失败，获批详情和文献数据暂缺"。

---
