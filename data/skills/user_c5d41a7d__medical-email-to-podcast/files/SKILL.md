---
name: "medical-email-to-podcast"
description: "医学邮件转播客"
---

# 医学邮件转播客

## 适用场景
> 把医学通讯邮件自动转成 5 分钟音频简报，通勤时直接听。
- 自动读取医学通讯邮件并提取文章链接，不再手动逐条看。

## 功能说明
> 把医学通讯邮件自动转成 5 分钟音频简报，通勤时直接听。

## 这个 Skill 能帮你做什么
- 自动读取医学通讯邮件并提取文章链接，不再手动逐条看。
- 自动补充链接上下文后生成口语化播客脚本，再转成音频。
- 音频会直接发送到 Signal，早上拿起手机就能听。

## 需要的工具/依赖
| 类型 | 工具/能力 | 用途 | 说明 |
|---|---|---|---|
| 外部 | `email` | 读取并解析邮件 | 可替换外部集成 |
| 内置 | `web_fetch` | 拉取链接正文补充上下文 | 内置能力 |
| 外部 | `elevenlabs` | 文本转语音 | 可替换外部集成 |
| 内置 | `ffmpeg` | 合并音频分片 | 内置能力 |
| 内置 | `signal` | 发送最终音频 | 内置能力 |

## 快速体验版（先跑一轮）
先只做单封邮件演示：

```text
你是我的 AI 自动化助手。
请帮我做“医学邮件转播客”的预演版：
1. 读取最近一封医学通讯邮件，提取标题与链接。
2. 抓取每个链接的正文要点并整合。
3. 写一版 5 分钟口语化脚本（家庭医学语境）。
4. 本轮只输出脚本，不生成音频、不发送消息。
```

## 稳定自动版（可长期运行）
### 1) 邮件识别配置

```text
Set up email forwarding from medical newsletter to agent's Gmail.
Configure auto-detection during heartbeats for newsletters matching:
- Sender: doctors@bcnews.com
- Subject contains: "Newsflash"
```

### 2) 安装 Skills

```bash
npx molthub@latest install email
npx molthub@latest install web_fetch
npx molthub@latest install elevenlabs
npx molthub@latest install ffmpeg
npx molthub@latest install signal
```

### 3) 处理脚本：`skills/email-podcast/index.js`

```javascript
// Parse email → extract stories → research URLs → write script → TTS → deliver
async function processMedicalEmail(email) {
  const stories = parseStories(email.body);
  const enriched = await Promise.all(
    stories.map(s => web_fetch(s.url).then(enhanceStory))
  );
  const script = writePodcastScript(enriched, "family_medicine");
  const audio = await generateTTS(script); // chunk if > 4000 chars
  await signal.sendAudio({ to: human.phone, audio });
}
```

### 4) 执行提示词（自动版）

```text
你是我的 AI 自动化助手，请执行“Medical Email to Podcast”。
请使用 Skills：email、web_fetch、elevenlabs、ffmpeg、signal。

当收到医学通讯邮件时按顺序执行：
1. 解析邮件正文，提取新闻标题和 URL。
2. 对每个 URL 抓取全文并补充背景。
3. 写一版 5 分钟播客脚本（专业但口语化，面向家庭医学）。
4. 使用 ElevenLabs 生成语音；若文本超过 4000 字符，分片后用 ffmpeg 合并。
5. 通过 Signal 发送音频文件。
6. 记录到 memory/medical-podcasts/YYYY-MM-DD.md。
```

### 5) 调度配置

```json
{
  "schedule": "0 6 * * *",
  "task": "check_medical_emails",
  "action": "process_and_deliver_podcast"
}
```

## 落地配置建议

- 先把“医学邮件转播客”拆成一次性试跑和长期自动化两种模式。
- 先定义输入材料、目标平台和输出规格，再批量处理。
- 建议保留运行日志、输入样例和最终输出，方便后续复盘和交付验收。

## 验收口径

- 能用真实或模拟数据完整跑通一次。
- 输出结果结构清晰，包含下一步动作或明确结论。
- 输出内容能直接发布或进入人工审核。

## 注意事项

- 正式接入账号、数据源或自动操作前，先确认权限边界。
- 对外发布前必须保留人工审核点。
- 高风险动作建议默认只生成建议或草稿，不直接执行。

## 质量等级

- 难度：进阶
- 风险：中
- 自动化程度：可定时
- 适用对象：团队

## 成功标准
- Newsletter processed within 1 hour of receipt
- Audio length: 5-7 minutes
- Human listens within 24 hours
- 人工步骤应尽量减少，并保留必要审核点
