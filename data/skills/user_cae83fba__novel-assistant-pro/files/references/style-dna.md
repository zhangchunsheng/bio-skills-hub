# 风格 DNA（Style DNA）

> v2.0.0 新增模块。把"开篇 1000 字的文风"提取为可量化、可校验、可复现的"风格指纹"。

## 风格 DNA 是什么

风格 DNA 是一份**机器可读的文风基线**，包含：

- 句长分布
- 词频统计
- 修辞密度
- 对话比例
- 信息密度
- 禁用表达扫描结果

后续每章写完后，自动与 DNA 比对，输出**漂移度**，确保长篇文风稳定。

## 提取流程

```text
开篇 1000 字（或第 1 章完整正文）
  ↓
scripts/style-dna-extract.py
  ↓
references/{slug}-style-dna.json
  ↓
作为后续章节的基线
```

## JSON 结构

```json
{
  "novel_slug": "star-port-end",
  "extracted_at": "2026-09-09T18:00:00Z",
  "source": "chapter-001.md",
  "stats": {
    "avg_sentence_length": 18.5,
    "sentence_length_distribution": {
      "short_0_10": 0.35,
      "medium_11_25": 0.50,
      "long_26_plus": 0.15
    },
    "top_50_words": ["林澈", "黑匣子", "星港", "内务局", "顾闻", ...],
    "rhetoric_density": {
      "metaphor": 0.04,
      "irony": 0.02,
      "parallelism": 0.01,
      "antithesis": 0.005
    },
    "dialogue_ratio": 0.22,
    "info_density": 0.65,
    "forbidden_expressions_found": []
  },
  "samples": {
    "good_sentence": "证据不会消失，只会被人放错地方。",
    "good_paragraph": "黑匣子的指示灯在第 47 秒停止了闪烁。林澈的手指停在记录仪上。她见过太多巧合，但这次巧合的形状太过规整。"
  }
}
```

## 漂移度计算

```text
漂移度 = 0.4 * 句长漂移
       + 0.3 * 词频漂移（Top50 重合率）
       + 0.2 * 修辞密度漂移
       + 0.1 * 对话比例漂移
```

| 漂移度 | 含义 | 处理 |
|---|---|---|
| < 10 | 完全一致 | 无需调整 |
| 10-20 | 轻微漂移 | 合格 |
| 20-40 | 中度漂移 | 标注段落 + 改写建议 |
| > 40 | 严重漂移 | 必须改写 |

## 提取命令

```bash
# 提取风格 DNA
python3 scripts/style-dna-extract.py \
  --memory memory/novels/{slug}.md \
  --chapter chapter-001.md \
  --output references/{slug}-style-dna.json

# 校验当前章节
python3 scripts/style-drift-detect.py \
  --style-dna references/{slug}-style-dna.json \
  --chapter chapter-008.md \
  --output reports/drift-008.md

# 批量校验最近 10 章
python3 scripts/style-drift-detect.py \
  --style-dna references/{slug}-style-dna.json \
  --chapter-range 1-10 \
  --output reports/drift-summary.md
```

## 风格 DNA 的限制

- 基于统计，对文学性强的风格判定有限
- 短章节（< 500 字）统计不准确
- 对话比例需结合上下文判断（不能仅按句数）
- 修辞密度是粗略估算（基于标点模式）

## 风格 DNA 的更新

何时应重新提取 DNA：

1. 故事进入新阶段（如进入新卷）
2. 视角人物更换
3. 平台调性切换（如从微信公众号改为起点中文网）
4. 重大风格调整（如从悬疑转为史诗）

每次重新提取前必须备份旧 DNA。
