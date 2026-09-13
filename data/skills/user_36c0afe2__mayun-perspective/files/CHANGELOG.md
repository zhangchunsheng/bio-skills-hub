# 变更记录

## 1.0.3 · 2026-09-08

- 自动巡检构建：检测到 4 新增 / 3 修改 / 0 删除
- 变更文件：`icon.png`
- 变更文件：`mayun-perspective-public-v1.0.2.zip`
- 变更文件：`更新说明_v1.0.2.md`
- 变更文件：`马云SKILL_图标.png`
- 变更文件：`SKILL.md`
- 变更文件：`workbuddy.json`
- 变更文件：`_skillhub_meta.json`

> 本条由每日巡检脚本自动生成，描述待人工补充。

## 1.0.4 · 2026-09-10

- 自动巡检构建：检测到 0 新增 / 0 修改 / 1 删除

**人工说明（2026-09-10）**：

- 清理：`mayun-perspective-public-v1.0.2.zip`（历史打包产物误放源目录，.zip 不在 SkillHub 上传白名单）已移出至 `_待清理/mayun-perspective-public-v1.0.2_从_mayun源目录移出.zip`
- 本次为纯白名单合规修复，无功能/内容增量；版本号 +0.01 是为了确保上传时 zip 内只含合规文件
- ⚠️ 1.0.4 预检发现 SKILL.md frontmatter 缺 `displayName` 字段（CLI 拒绝），需立即修复 → 1.0.5

## 1.0.5 · 2026-09-10

- 自动巡检构建：检测到 0 新增 / 1 修改 / 0 删除
- 变更文件：`SKILL.md`

**人工说明（2026-09-10）**：

- 修复：`SKILL.md` frontmatter 补 `displayName: "马云 · 思维操作系统"` 字段（CLI 预检要求驼峰式，与已有 `display_name` 共存不冲突）
- 1.0.5 是当前可上传版本
