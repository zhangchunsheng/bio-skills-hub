# 上架前检查清单

- `SKILL.md` 存在，且 YAML frontmatter 包含 `name`、`description`、`version`、`category`、`platforms`、`tags`。
- `references/api-mapping.md` 存在，并说明 API 基础地址、API Key 规则和意图映射。
- `references/medical-keywords.json` 是合法 JSON。
- `assets/icon.png` 存在，尺寸为 512x512。
- 未创建 `agents/openai.yaml`。
- Skill 明确说明不新增 API，只复用世舶科技全行业招投标数据 API。
- Skill 明确说明需配置 `BBIAO_API_KEY`，并使用指定 API Key 获取链接。
