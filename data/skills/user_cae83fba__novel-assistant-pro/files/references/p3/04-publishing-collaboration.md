# P3-04 与 publishing-assistant 协同

> v3.x 路线图。完稿后自动触发排版、装帧、出版方案。

## 目标

让 novel-assistant-pro 与 publishing-assistant 形成"创作 → 出版"闭环。

## 协同链路

```text
novel-assistant-pro（创作）
  ↓ 完稿信号
  ↓
publishing-assistant（出版）
  - 自动排版
  - 自动装帧（封面设计）
  - 出版方案（实体书 / 电子书 / 连载平台）
  - 营销方案
  ↓
用户决策
```

## 协同触发

```bash
# novel-assistant-pro 完成全卷后，触发 publishing-assistant
python3 scripts/export-to-publishing.py \
  --work-id star-port-end \
  --volume 1 \
  --output publishing/star-port-end-vol1/

# 输出：
# ✓ 已导出完整创作包到 publishing/star-port-end-vol1/
#   - 全部章节（chapter-001.md ~ chapter-050.md）
#   - 完整记忆文件
#   - 人物档案
#   - 风格 DNA
#   - 时间线
#   - 伏笔回收记录
```

## publishing-assistant 接收

```text
publishing-assistant 接收到的输入：
  - 完整章节正文
  - 元数据（流派、平台、字数、读者画像）
  - 风格 DNA（指导排版与装帧）
  - 营销关键词（基于章节自动提取）

输出：
  - 排版后的 .docx / .epub / .pdf
  - 封面设计（多版本可选）
  - 简介（基于大纲自动生成）
  - 营销文案（基于钩子与爽点自动生成）
  - 出版方案（实体 / 电子 / 连载）
```

## 数据交换协议

```json
{
  "from": "novel-assistant-pro",
  "to": "publishing-assistant",
  "version": "1.0.0",
  "work": {
    "title": "星港尽头",
    "slug": "star-port-end",
    "type": "科幻悬疑",
    "platform": "起点中文网",
    "target_word_count": 200000,
    "current_word_count": 180000,
    "chapter_count": 45,
    "status": "完结"
  },
  "content": {
    "chapters_dir": "novels/star-port-end/chapters/",
    "memory_file": "memory/novels/star-port-end.md",
    "style_dna": "references/star-port-end-style-dna.json"
  },
  "preferences": {
    "format": "docx",
    "typography": "chinese-publishing-standard",
    "cover_style": "sci-fi-mystery"
  }
}
```

## 与写作马拉松工作流的衔接

```text
场景：写作马拉松（48 小时写作马拉松）完赛

novel-assistant-pro：
  1. 完成所有章节
  2. 自动打包（保留作品原稿）
  3. 调用 publishing-assistant
  4. 生成出版包

publishing-assistant：
  1. 接收创作包
  2. 自动排版
  3. 生成简介（基于大纲）
  4. 生成装帧（封面 + 标题字）
  5. 输出"参赛提交包"
```

详见 publishing-assistant 的设计文档。

## 实现阶段

| 阶段 | 内容 |
|---|---|
| 1 | 数据导出协议 + 单向集成 |
| 2 | 双向通信 + 自动触发 |
| 3 | 完整闭环（创作 → 出版 → 反馈 → 创作） |
| 4 | 跨技能生态集成 |

## 状态

**Roadmap（v3.3+）** - 等待 publishing-assistant 完成后集成。

## 相关链接

- publishing-assistant：（待创建）
- 用户级记忆：`~/.app-state/MEMORY.md`
- IMA 知识库：项目元数据共享
