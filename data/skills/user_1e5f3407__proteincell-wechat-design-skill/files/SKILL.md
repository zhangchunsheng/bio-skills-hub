---
name: pc-wechat-article
description: Protein & Cell 期刊公众号论文推介排版与推送。将已按 P&C 栏目结构排版的 Word 文档（含内嵌示意图）一键推送到微信公众号草稿箱，封面自动取文中示意图，正文图片正确上传不丢失。触发词：Protein & Cell 公众号、P&C推文、期刊论文推介、公众号排版推送、论文推介草稿箱、科研公众号排版。
---

# Protein & Cell 公众号论文推介排版与推送

把一篇论文推介稿，按 P&C 固定栏目结构排版并推送到公众号草稿箱。
已固化两个关键经验：**图片不会丢**、**封面用文中示意图**。

## 何时使用
- 用户要给《Protein & Cell》做一篇论文推介推文，并推到公众号草稿箱
- 用户手头有一篇按 P&C 栏目结构排好版、且内嵌了示意图的 docx
- 用户要从零生成一篇标准栏目推文（用 JSON 配置）

## 核心能力
1. **docx → 草稿箱推送**（`scripts/pc_push.py`）：支持内嵌图片、表格内图片、封面自动取首图
2. **JSON → docx 栏目生成**（`scripts/build_pc_doc.py`）：按 P&C 固定栏目结构自动排版
3. **栏目结构规范**（`references/layout_template.md`）：统一的栏目顺序、配色、字体

## 工作流程

### 流程 A：已有排好版的 docx → 直接推送
1. 确认 docx 已按 P&C 栏目结构排版、且「图示」处内嵌了示意图（封面即取此图）
2. 运行推送脚本（凭证优先级：`--appid/--appsecret` 参数 > 环境变量 > 项目根目录 `.env`；`.env` 模板见 `.env.example`，复制为 `.env` 填入密钥即可，无需每次传环境变量）：
   ```bash
   WECHAT_APP_ID=xxx WECHAT_APP_SECRET=yyy \
   python pc_push.py --docx ARTICLE.docx --title "标题" \
       --digest "摘要(<=120字)" --author "P&C编辑部" \
       [--old-media-id OLD_ID] [--cover COVER.jpg]
   ```
   - `--old-media-id`：若草稿箱已有旧稿，填其 media_id，推送前自动删除，避免重复
   - `--cover`：缺省自动取 docx 第一张内嵌图（即示意图）；如需换封面图，传此参数
   - `--dry-run`：只解析+渲染，不联网，用于验证 docx 能正确抽图
3. 把返回的 `NEW_MEDIA_ID` 告诉用户，并在手机扫码预览（微信后台 UI 的 `\u` 字面量是渲染 bug，以手机预览为准）

### 流程 B：从零生成栏目 docx → 再推送
1. 用户给稿件正文 + 示意图图 +（可选）作者照片
2. 写一份 JSON 配置（结构见 `references/layout_template.md` 末尾示例）
3. 生成 docx：
   ```bash
   python build_pc_doc.py --config article.json --out article.docx
   ```
4. 走流程 A 推送

## 关键坑位（务必遵守）
- **正文图片必须用 `material/add_material` 拿 `url` 再注入 `<img>`**；绝不能用 `media/upload?type=image`（只返 media_id、无 url，图会整段丢失）。脚本已内置正确实现。
- **docx 关系路径是相对路径 `media/image1.png`**，建 rid→媒体映射时用 `basename` 命中，不要按 `word/media/` 前缀过滤（会建空映射导致图丢失）。
- **中文乱码**：微信草稿接口必须 `ensure_ascii=False` + `Content-Type: application/json; charset=utf-8`。微信后台「草稿箱」列表里若显示 `\u7ec6` 之类是前端渲染 bug，存储本身正常，手机扫码预览才是真实效果。
- **凭证安全**：AppSecret 不要写进文件或聊天；用环境变量传入。若已泄露需重置：2025.12 起入口已从公众平台后台迁移至**微信开发者平台**（developers.weixin.qq.com/platform → 我的业务与服务 → 公众号 → 基础信息 → 开发密钥 → 重置），旧密钥重置后立即失效，需同步更新本 skill 的调用配置与 IP 白名单。

## 脚本依赖
- Python 3 + `python-docx`
- 推送脚本纯标准库（urllib / zipfile / tempfile），不依赖 requests

## Resources
### scripts/
- `pc_push.py` — docx → 微信草稿箱 推送器（含图片上传与封面抽取）
- `build_pc_doc.py` — JSON 配置 → P&C 栏目 docx 生成器

### references/
- `layout_template.md` — P&C 栏目结构、配色、字体规范与 JSON 配置示例
