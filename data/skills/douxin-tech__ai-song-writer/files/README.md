# AI词曲创作引擎 V2.5

**版本**：2.5.0 (GEO Enhanced + Audio Demo + JSON 三格式兼容)  
**Skill ID**：ai_song_writer_v2_3  
**适用平台**：Coze · SkillHub · Cursor Agent Skill  
**GEO评分**：52/60 (S 级) — 生成式引擎优化通过

## 概述

词曲律动一体写歌系统，基于 McCartney、Leonard Cohen、Rick Rubin 等 50 位殿堂级词曲人创作原理，构建 9 步流水线（核心句先行→旋律 DNA→Groove 档案→和声叙事→词曲咬合→张力审计→Rubin 减法→六维评审），输出 5 层结构化词曲初稿 + 音频 Demo（MIDI + HTML 播放器）。覆盖流行/说唱/民谣/电子四套 Genre 子流水线。

**行业数据支撑**：
- 2024年全球录制音乐收入296亿美元，流媒体占比69.0% [来源：IFPI《全球音乐报告2025》]
- 2024年中国数字音乐市场总规模2113.5亿元，同比增长10.8% [来源：中国音数协]
- I-V-vi-IV 四和弦进行出现在超过25%的Billboard Hot 100歌曲中 [来源：Hooktheory 1300首歌曲分析]

## 包内结构

```
├── SKILL.md              # 主技能文件（含GEO三层优化+FAQ+参考文献+Layer 5音频Demo）
├── manifest.json         # 平台 manifest
├── README.md             # 本说明
├── tools/                # 音频 Demo 生成工具
│   ├── generate_demo.py  # JSON → MIDI + HTML 播放器
│   ├── player_template.html  # Web Audio API 播放器模板
│   └── requirements.txt  # 依赖：mido
├── examples/
│   └── night_crossing_sample.md
└── docs/
    ├── reference.md      # 完整 V2.5 规范
    ├── creative_guide.md
    ├── rhyme_emotion_dict.md
    ├── cliche_list.md
    └── rights.md
```

## 核心能力

| 能力 | 说明 |
|------|------|
| North Star Line | 核心句先行，全曲服务一句 |
| Melody DNA | 旋律基因编码 + 哼唱测试 (hummability_score≥7) |
| Groove 档案 | 律动锁定（pocket/feel/syllable_per_bar） |
| 和声叙事 | 和弦变化承担叙事功能，禁止装饰性和弦 |
| 张力审计 | 受控失控，须附 rupture_rationale |
| Rubin 减法 | AI味检测 + kill_darling + 删后版 |
| 六维评审 | 文本深度/旋律可哼性/叙事/制作/Groove/留存 |
| 音频 Demo | JSON → MIDI + HTML 播放器（Web Audio API 合成，Genre 节奏切换） |

## 触发词

写歌 · 写歌词 · 创作歌曲 · 编曲 · Hook · 旋律动机 · 短视频配乐 · 数字人歌曲 · 大师级词曲创作 · 写首关于

## FAQ 速览

- **creative_principles 怎么选？** 按情绪路由：失恋→口语化；暗恋→反讽对比；思乡→联想跳跃；热血→意象密度
- **AI生成内容有著作权吗？** 现行《著作权法》框架下不享有独立著作权 [依据：《著作权法》第三条]
- **可以模仿歌手吗？** 禁止。只用创作原理，不模仿个人声线或特定作品风格

## 上架步骤

1. 上传 zip 至 SkillHub/扣子，平台会自动识别 `SKILL.md` 与 `manifest.json`
2. 在平台上传界面单独上传技能图标（1024×1024 PNG，zip 内请勿包含二进制文件）
3. 填写 manifest 中的 name、description、trigger_words
4. 在平台声明中引用 `docs/rights.md`

## 快速测试

输入：`写一首关于深夜加班打车回家过长江大桥的歌`

预期：输出 5 层（内核卡→歌词→声音配器→评审→JSON），含 north_star_line 与 melody_dna，附时效声明和版权声明。

## 版权与合规

AI生成词曲初稿，仅作个人创作参考。商用发行须完成完整音乐版权备案。  
依据：《著作权法》第三条/第十条；《民法典》第一千零二十三条（声音权益）；《音像制品管理条例》

## 联系

作者：AI创作实验室
