# 临床 ASR 术语错误率评测

- 唯一标识：`digital-health-clinical-asr-eval`
- 显示名称：临床 ASR 术语错误率评测
- 能力摘要：对带临床扩展字段的 NeMo 清单调用指定 ASR 服务并计算 WER、CER、KER、SER，生成按实体类别、IPA 来源、噪声和术语分层的五段式排行榜；只允许合成音频，不应用于真实患者数据或临床决策。

## 案例素材

1. 语音团队拿到合成药名音频清单后先披露将发送至外部 ASR 服务的音频与参考文本，确认所用 NIM 和 function ID，再运行离线转写与 KER 评测。
2. 总体 WER 很低但某些药名仍错误，按 `entity_category` 和逐术语 KER 找到高风险词；不因平均 WER 好看就忽略临床关键术语遗漏。
3. `merriam-webster` 发音行表现好而 `magpie_g2p` 行表现差时，判定为 SSML 发音覆盖问题并回到数据构建阶段补充发音，而不是直接花 GPU 做模型微调。
