# pc-wechat-article · Protein & Cell 公众号论文推介排版与推送

把按《Protein & Cell》栏目结构排好版的 Word 文档，一键转成微信公众号草稿并推送（含内嵌示意图、自动设封面）。

## 一、安装

1. 解压 `pc-wechat-article-skill.zip`，得到 `pc-wechat-article/` 文件夹。
2. 把整个文件夹放到以下任一位置（二选一）：
   - 用户级：`C:\Users\DELL\.workbuddy\skills\pc-wechat-article\`
   - 工作区级：`D:\Workbuddy\.workbuddy\skills\pc-wechat-article\`
3. 安装 Python 依赖（仅需 `python-docx`，推送给微信用标准库，无需 `requests`）：
   ```
   pip install python-docx
   ```
4. 配置凭证（见第三节）。

装好后，在对话里说「P&C推文排版 / 期刊论文推介推送」即可触发；或直接在命令行调用脚本。

## 二、两种用法

### 用法 A：已有排好版的 docx（含内嵌示意图）→ 直接推
```bash
python pc_push.py --docx 文章.docx --title "标题" --digest "摘要(≤120字)"
```
- 封面默认自动取 docx **第一张内嵌图**（即"图示"示意图）；想换封面加 `--cover 封面.jpg`。
- 草稿箱已有旧稿时传 `--old-media-id 旧稿ID` 会自动先删再建。
- 改完前用 `--dry-run` 只本地解析、不联网、不动草稿箱。
- 作者字段 `--author` 默认「P&C编辑部」（≤8 字符限制）。

### 用法 B：从零按栏目生成 → 再推
1. 写一份 JSON（结构见 `references/layout_template.md` 末尾示例）。
2. 生成 docx：
   ```bash
   python build_pc_doc.py --json 文章.json --out 文章.docx
   ```
3. 再走用法 A 推送。

## 三、凭证配置（.env，密钥不进聊天）

复制 `.env.example` 为 `.env`，填入你的公众号凭证：
```ini
WECHAT_APP_ID=wx你的AppID
WECHAT_APP_SECRET=你重置后的32位AppSecret
```
脚本读取顺序：`--appid/--appsecret` 参数 > 环境变量 > 项目根 `.env`。
真实 `.env` 切勿提交/外发；已被 `.gitignore` 忽略。

### AppSecret 重置入口（2025-12 起变更）
微信已将公众号 AppSecret 管理从公众平台后台迁至「微信开发者平台」：
https://developers.weixin.qq.com/developers/product/mp/你的AppID?tab1=basicInfo
→「基础信息」→「开发密钥」→「重置」→ 管理员扫码 → 密钥仅显示一次，立即保存。

## 四、固定栏目顺序（排版规范）

今日推荐 → 文章背景 → 文章要点（研究核心与技术突破 / 关键科学发现）→ 临床转化与药物研发意义 → 图示 → 作者简介（姓名/单位/研究方向）→ 期刊简介

配色：大标题海军蓝 `#1F3864`、小节标题学术红 `#B91C1C`、正文 `#333333`。

## 五、踩坑提醒（已固化进脚本，了解即可）

1. **图片不丢**：每张内嵌图走 `material/add_material` 拿 `url` 注入 `<img>`，封面用其 `media_id`；绝不用临时素材接口。
2. **docx 关系路径是相对路径** `media/image1.png`，映射按 `basename` 命中，不按 `word/media/` 前缀过滤。
3. **中文"乱码"是微信前端 bug**：草稿箱后台把 UTF-8 误显成 `\uXXXX` 字面量，存储本身正常；以手机扫码预览为准。
4. **author 字段 ≤8 字符**，超长报 45110。

## 六、文件清单

- `SKILL.md` — 触发词与工作流
- `scripts/pc_push.py` — docx → 草稿箱推送器
- `scripts/build_pc_doc.py` — JSON → 栏目 docx 生成器
- `references/layout_template.md` — 栏目结构与样式规范、JSON 示例
- `.env.example` — 凭证模板（可共享）
- `.gitignore` — 忽略 `.env`
