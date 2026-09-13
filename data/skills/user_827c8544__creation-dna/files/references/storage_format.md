# 存储结构规范

本文件定义创作 DNA 的完整存储结构、文件格式和命名规范。

## 目录

1. [目录结构](#目录结构)
2. [index.md 格式](#indexmd-格式)
3. [profile.md 内部结构](#profilemd-内部结构)
4. [global.md 格式](#globalmd-格式)
5. [archive/deprecated.md 格式](#archivedeprecatedmd-格式)
6. [交付计数器](#交付计数器)
7. [日期与编码规范](#日期与编码规范)

---

## 目录结构

```
.creation-dna/
+-- index.md                  # 画像索引
+-- global.md                 # 跨类型通用偏好
+-- .delivery-counter          # 交付计数器（纯整数文件）
+-- writing/
|   +-- profile.md            # 文案创作 DNA
+-- image/
|   +-- profile.md            # 图像创作 DNA
+-- video/
|   +-- profile.md            # 视频创作 DNA
+-- design/
|   +-- profile.md            # 设计创作 DNA
+-- structured/
|   +-- profile.md            # 结构化内容 DNA
+-- archive/
    +-- deprecated.md         # 已废弃偏好 + 模糊反馈记录
```

**创建规则**：
- `index.md` 在首次初始化时创建
- 各类型的 `profile.md` 在该类型首次有偏好写入时创建
- `global.md` 在首次有跨类型偏好写入时创建
- `archive/deprecated.md` 在首次有废弃偏好或模糊反馈时创建
- `.delivery-counter` 在首次初始化时创建，内容为 `0`
- 不预创建空文件

## index.md 格式

```markdown
# 创作 DNA 画像索引

> 最后更新：YYYY-MM-DD

## 画像统计

| 创作类型 | 已确认 | 待验证 | 观察候选 | 返工抗体 | 休眠 | 最后更新 |
|----------|--------|--------|---------|---------|------|---------|
| 文案 | N | N | N | N | N | YYYY-MM-DD |
| 图像 | N | N | N | N | N | YYYY-MM-DD |
| ... | ... | ... | ... | ... | ... | ... |

## 交付计数

- 累计交付次数：N
- 下次维护触发：剩余 N 次交付
```

模板文件见 `assets/index_template.md`。

## profile.md 内部结构

每个创作类型的 profile.md 遵循以下分区，标题必须严格匹配：

```markdown
# [创作类型] 创作 DNA

## 已确认偏好（高置信度，主动使用）
- [参数描述] -- 确认于 YYYY-MM-DD，引用 N 次 [used: YYYY-MM-DD]

## 待验证偏好（中置信度，谨慎使用）
- [参数描述] -- 出现于 YYYY-MM-DD，出现 N 次

## 观察候选（低置信度，仅参考）
- [参数描述] -- 首次记录于 YYYY-MM-DD

## 返工抗体（踩坑免疫，必须规避）
- [禁忌描述] -- 来源：[返工事件简述]，日期 YYYY-MM-DD

## 休眠偏好（90天以上未引用）
- [参数描述] -- 最后引用 YYYY-MM-DD

## 已废弃偏好（历史记录，不主动使用）
- [参数描述] -- 废弃于 YYYY-MM-DD，原因：[简述]

## 语义映射表（需求侧理解偏差专用）
- 用户说"[词]" -> 实际含义：[解释] -- 确认于 YYYY-MM-DD
```

**分区写入规则**：
- 每条目占一行，以 `- ` 开头
- 标注信息使用 ` -- ` 分隔（双连字符前后各一空格）
- 使用标记 `[used: YYYY-MM-DD]` 追加在条目末尾，用于追踪交付预检中的使用记录
- 同一分区内不得出现完全相同的条目（去重由工作流阶段2保证）
- 废弃的偏好不删除，移入"已废弃偏好"区并标注废弃原因

模板文件见 `assets/profile_template.md`。

## global.md 格式

```markdown
# 跨类型通用偏好

## 已确认通用偏好
- [参数描述] -- 确认于 YYYY-MM-DD，适用于 [类型列表]

## 待验证通用偏好
- [参数描述] -- 出现于 YYYY-MM-DD，适用于 [类型列表]

## 未分类偏好（待后续明确类型）
- [参数描述] -- 记录于 YYYY-MM-DD，待分类
```

## archive/deprecated.md 格式

此文件承担双重职责：

### 1. 已废弃偏好归档

```markdown
## 废弃偏好归档

### [创作类型] 废弃记录
- [参数描述] -- 废弃于 YYYY-MM-DD，原因：[简述]
- [参数描述] -- 废弃于 YYYY-MM-DD，原因：[简述]
```

### 2. 模糊反馈记录

```markdown
## 模糊反馈记录

- YYYY-MM-DD：用户反馈"[原话]"，未能具体化，未写入正式画像
- YYYY-MM-DD：用户反馈"[原话]"，未能具体化，未写入正式画像
```

### 3. 损坏事件记录

```markdown
## 文件损坏事件

- YYYY-MM-DD：[文件路径] 检测到格式损坏，已备份为 [备份文件名]，[恢复结果]
```

## 交付计数器

`.delivery-counter` 文件内容为单个非负整数，表示自上次维护以来的累计交付次数。

- 每次 AI 完成创作交付后递增 1
- 达到 10 时触发周期维护（阶段5），维护完成后重置为 0
- 用户主动触发维护时也重置为 0
- 文件格式：纯文本，仅含一个整数，无换行、无空格

## 日期与编码规范

- 所有日期使用 `YYYY-MM-DD` 格式（ISO 8601 简化版）
- 所有文件使用 UTF-8 编码
- Markdown 格式遵循 CommonMark 规范
- 文件内换行使用 LF（Unix 风格），兼容 CRLF（Windows）
- 文件名全部小写，使用连字符分隔（如 `profile.md`、`deprecated.md`）
