# 端到端 Demo：从灵感到导出 docx

> v2.0.0 新增。演示完整链路：灵感 → 大纲 → 5 章正文 → 风格校验 → 去 AI 腔 → 导出 docx。

## 场景

写作马拉松比赛（48 小时冲刺）期间，使用 novel-assistant-pro 完成《星港尽头》第 1-3 章的完整流程。

## 时间分配

| 阶段 | 时长 | 占比 |
|---|---|---|
| 灵感 → 大纲 | 30 分钟 | 5% |
| 大纲 → 记忆文件 | 15 分钟 | 2.5% |
| 续写章节 | 120 分钟 × 3 章 | 60% |
| 风格校验 + 去 AI 腔 | 30 分钟 × 3 章 | 15% |
| 导出 docx | 15 分钟 | 2.5% |
| 收尾 | 15 分钟 | 2.5% |

## Step 1：灵感 → 大纲

```text
用户："我想写一部科幻悬疑，主角是星港事故调查员，核心看点是父亲失踪真相。"

技能：
  1. 追问基本信息（5 个问题）
  2. 输出设定草案（主题/人物/世界观/前三章大纲）
  3. 用户确认

耗时：30 分钟
```

输出大纲示例：

```markdown
## 前三章大纲

### 第 1 章 黑匣子

- 钩子：黑匣子指示灯在第 47 秒停止闪烁，但林澈 5 分钟前才取出它
- 目标：林澈接手爆炸事故
- 阻力：残片来自失踪舰队（不可能存在）
- 变化：林澈意识到这件事不简单
- 反馈：林澈的内心震动（但克制）
- 钩子：她发现残片上的识别码

### 第 2 章 警告

- 钩子：林澈在档案室被内务局的人堵住
- 目标：林澈追查残片来源
- 阻力：内务局警告停止调查
- 变化：林澈意识到有人在掩盖真相
- 反馈：林澈感到被压制
- 钩子：她决定继续查

### 第 3 章 旧识别码

- 钩子：黑匣子中出现顾闻的旧识别码
- 目标：林澈找到黑匣子碎片
- 阻力：顾闻拒绝透露更多信息
- 变化：林澈首次怀疑导师
- 反馈：林澈感到背叛
- 钩子：顾闻反问：「你想知道真相吗？」
```

## Step 2：创建项目

```bash
python3 scripts/init-novel-project.py \
  --slug star-port-end \
  --title "星港尽头" \
  --type "科幻悬疑" \
  --platform "起点中文网" \
  --pov "第三人称有限视角" \
  --output-dir ~/Documents/novels/

输出：
✓ 项目创建成功：~/Documents/novels/star-port-end
  - ~/Documents/novels/star-port-end/memory/novels/star-port-end.md
  - ~/Documents/novels/star-port-end/novels/star-port-end/meta.json
  - ~/Documents/novels/star-port-end/novels/star-port-end/README.md
```

耗时：15 分钟

## Step 3：补充记忆文件

```text
用户："把刚才的设定填到记忆文件。"

技能：
  1. 读取空白的记忆文件
  2. 自动填入基本信息、风格规则、世界观硬规则、主要人物（林澈、顾闻）
  3. 填入章节概要表（第 1-3 章）
  4. 填入未解决伏笔（F001-F003）
  5. 填入时间线
```

耗时：5 分钟

## Step 4：续写第 1 章

```text
用户："续写第 1 章。"

技能（自动上下文补全）：
  1. 读 meta.json 确认当前作品
  2. 读记忆文件
  3. 列未解决伏笔（F001-F003 待埋设）
  4. 列人物（林澈、顾闻）
  5. 列硬规则
  6. 询问：≤ 3 项缺失
     → 本章目标？（自动给出：林澈接手爆炸事故）
     → 本章视角？（默认：林澈视角）
     → 特殊要求？（无）
  7. 生成第 1 章正文（2000-3000 字）
  8. 输出节拍卡 + AI 痕迹分 + 伏笔推进
  9. 询问覆盖策略 → 写入
  10. 备份 chapter-001.backup-20260909-180000.md
  11. 更新记忆文件（章节概要、未解决伏笔表新增 F001）
```

耗时：120 分钟（含 30 分钟自检修订）

## Step 5：风格校验

```bash
python3 scripts/style-dna-extract.py \
  --chapter chapter-001.md \
  --output style-dna.json

python3 scripts/style-drift-detect.py \
  --style-dna style-dna.json \
  --chapter chapter-002.md

输出：
=== 风格漂移检测（第 2 章）===
总漂移度：12/100
判定：轻微漂移（合格）
```

## Step 6：去 AI 腔扫描

```bash
python3 scripts/anti-ai-scan.py --chapter chapter-001.md --locate

输出：
=== AI 痕迹扫描（第 1 章）===
痕迹 1（破折号）：7 次 / 2000 字 → 扣 3.5 分
痕迹 2（对比结构）：2 次 → 扣 0 分
...
合计扣分：5.5
最终得分：4.5/10
判定：需改进

修改：
  - 第 3 段 L12 破折号过多
  - 第 7 段 L25 通用化总结
```

按 `references/anti-ai/rewrites.md` 改写后：

```bash
python3 scripts/anti-ai-scan.py --chapter chapter-001.md

最终得分：8.5/10
判定：人味充足
```

## Step 7：导出 docx

```bash
python3 scripts/export-to-docx.py \
  --chapter chapter-001.md \
  --output "第1章-黑匣子.docx"

输出：
✓ 已导出：第1章-黑匣子.docx
  - 字体：宋体正文、黑体标题
  - 首行缩进：2 字符
  - 行距：1.5 倍
```

## Step 8：批量导出

```bash
python3 scripts/export-to-docx.py \
  --chapter-dir ~/Documents/novels/star-port-end/novels/star-port-end/chapters/ \
  --output-dir "20 OPC 项目/10 写作马拉松/star-port-end/"

输出：
✓ 第1章-黑匣子.docx
✓ 第2章-警告.docx
✓ 第3章-旧识别码.docx

完成：3 个文件
```

## 总结

| 指标 | 数值 |
|---|---|
| 总耗时 | 6 小时 |
| 章节字数 | 2000-3000 × 3 = 6000-9000 字 |
| AI 痕迹分（最终） | 8.0+（合格） |
| 风格漂移度 | < 20（合格） |
| 节拍分 | 7.0+（合格） |
| 开篇留存分 | 28+（合格） |
| P1 伏笔推进 | F001 已埋设，F002 已埋设，F003 已埋设 |

## 关键时间节省

| 流程 | 手动 | 使用 novel-assistant-pro |
|---|---|---|
| 创建项目 | 30 分钟 | 5 分钟 |
| 续写章节 | 150 分钟（含上下文准备） | 120 分钟 |
| 风格校验 | 30 分钟（人工） | 5 分钟（自动） |
| 去 AI 腔 | 30 分钟（人工） | 10 分钟（自动） |
| 导出 docx | 15 分钟（手工排版） | 1 分钟（自动） |
| **总计** | **255 分钟** | **141 分钟** |

节省约 45% 时间，且质量更高。

## 复用建议

- 把这个 demo 保存为 `examples/end-to-end-demo.md`
- 在首次使用时引导用户走一遍
- 在写作马拉松等限时比赛中复用
