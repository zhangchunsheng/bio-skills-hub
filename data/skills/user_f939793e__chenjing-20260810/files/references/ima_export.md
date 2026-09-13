# IMA 笔记导出参考（ima_export.md）

本文件为 Medical SCI Journal Selection Expert 的 **Step 9 — Export to IMA Notes** 提供
可直接执行的命令模板与边界处理。目标：把完整的选刊分析报告（Section 1–5）推送到用户的
IMA 个人笔记，便于长期保存与检索。

## 前置条件

- IMA 连接器（`ima-mcp`）需已连接。若未连接，跳到「降级处理」写入本地文件，不要静默丢弃结果。
- 写入内容 (`content`) 必须为**合法 UTF-8** 的 Markdown；非 UTF-8 会在 IMA 产生不可逆乱码。
- 本地图片（`file:///`、`/Users/...`、`C:\...`）**不支持**，写入前必须移除并主动告知用户。
  网络图（`http(s)://`）可保留。

## 笔记标题约定

```
【SCI选刊】<稿件简称，≤40字> - YYYY-MM-DD
```

- 稿件简称：用中文精炼标签，或取英文标题前 ~6 个词。
- 日期用选刊当天的本地日期（格式 `YYYY-MM-DD`）。

## 笔记正文模板（Markdown）

将 Section 1–5 的完整分析原样放入 `content`。建议正文结尾追加 provenance 脚注：

```markdown
---

## 数据来源与核实状态
- 生成时间：<YYYY-MM-DD HH:MM>
- IF / JCR 分区 / 审稿实证指标：已联网核实 或 含 estimate（需核实）
- 工具：Medical SCI Journal Selection Expert
```

## 执行命令

IMA 笔记写入使用 `import_doc`，`content_format` 固定为 `1`（Markdown）。

```bash
# 新建到默认（未分类）位置
ima_api "openapi/note/v1/import_doc" '{
  "content_format": 1,
  "content": "<完整 Markdown 报告，含标题与脚注>"
}'

# 新建到指定笔记本（用户指定 folder_id 时）
ima_api "openapi/note/v1/import_doc" '{
  "content_format": 1,
  "content": "<完整 Markdown 报告>",
  "folder_id": "<目标 notebook 的 folder_id>"
}'
```

> **注意**：JSON 中的 `content` 必须是合法 JSON 字符串（换行用 `\n`，引号需转义）。
> 若报告过长导致 JSON 难以手工拼接，先把它写成本地 `.md` 文件，再用脚本读取并调用
> `ima_api`（见「降级处理」中的本地文件方案，可复用同一文件二次推送）。

## 成功处理

`import_doc` 返回 `note_id`。向用户汇报：
- 已创建笔记标题（如 `【SCI选刊】…… - 2026-08-10`）
- 笔记 `note_id`（便于后续 `append_doc` 追加或 `get_doc_content` 读取）
- 提醒：笔记已保存在 IMA，可在 IMA 客户端查看。

## 降级处理（IMA 不可用 / 出错）

出现以下任一情况 → **不推送 IMA**，改为本地保存并明确告知用户：

- `ima-mcp` 连接器未连接 / 鉴权失败（错误码 `20004`）
- 限频（错误码 `20002`）→ 可等待后重试一次
- 参数或其他服务端错误

本地保存命令（在工作目录生成 Markdown 文件）：

```bash
# 将完整报告写入本地文件
cat > "sci_journal_selection_<YYYYMMDD-HHMM>.md" <<'EOF'
<完整 Markdown 报告>
EOF
```

然后告知用户：「IMA 笔记推送失败（原因：……），报告已保存到本地
`sci_journal_selection_<YYYYMMDD-HHMM>.md`，连接 IMA 后可重试。」

## 边界情况

| 情况 | 处理 |
| ---- | ---- |
| 内容超大小限制（错误码 `100009`） | 拆分为多次 `append_doc` 写入：先 `import_doc` 创建笔记拿到 `note_id`，再用 `append_doc` 追加剩余部分 |
| 限频（错误码 `20002`） | 等待后重试一次；仍失败则降级本地保存 |
| 含本地图片引用 | 写入前移除图片引用并提醒用户 |
| 用户未指定笔记本 | 使用默认（未分类）位置，不传 `folder_id` |
| 用户说「不要发 IMA」 | 跳过 Step 9，仅输出分析报告 |

## 隐私提醒

笔记属于用户隐私。仅在用户明确需要（本 Skill 的 Step 9 默认行为）时写入；不要在群聊
等场景主动展示笔记正文，仅可展示标题与摘要。
