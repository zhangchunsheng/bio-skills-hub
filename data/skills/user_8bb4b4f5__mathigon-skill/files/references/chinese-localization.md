# 中文（cn）课程编写规范

为面向中国学生的课程（如 `content/<course>/` 直接用中文撰写）必须遵守的规范。全部规则均来自真实构建/运行验证。

## 1. section 必须用显式英文 `> section:`（最关键）

**中文 H2 标题无法被 slugify 成有效的 URL slug。** 如果一个 section 只写了 `## 中文标题` 而没有 `> section:` 指令，构建时该 section 会丢失，首页只剩第一个 section，其余全部 404。

**正确做法**：每个 section 都加显式英文 slug：
```markdown
## 构造梯形

> id: build-trapezoid
> section: build-trapezoid        ← 必须有，用英文 kebab-case
> goals: place-u
```

`> id:` 也保持英文（因为它要 camelCase 匹配 functions.ts 的导出函数名，中文无法作函数名）。只有 `## 标题`、正文、填空选项、hints 用中文。

## 2. backtick 内严禁中文

` `...` ` 是 AsciiMath 数学表达式，**遇到中文字符会报 "Unknown symbol" 构建错误**：
```
! [WARNING] Maths parsing error in "1/2 × (两平行边之和)": Unknown symbol "两"
```

错误做法：`` `1/2 × (两平行边之和) × 高` ``
正确做法：把公式和中文分开——
```markdown
梯形面积公式为：__二分之一__ ×（两底之和）× 高，即：
```
数学符号（`1/2`、`×`、`a^2`、`π`）可以放 backtick 里，但中文文字必须放 backtick 外。

## 3. 标点与排版（避免乱码）

- **所有格/缩写的撇号用弯引号 `'`（U+2019），绝不用 ASCII `'`**。ASCII 撇号在标题/meta 里会变成 `&#39;` 乱码。中文里一般不需要撇号（用"的"），但引用英文人名时注意（如"毕达哥拉斯'定理"——不过中文通常写"毕达哥拉斯的定理"）。
- 中文标点：用中文逗号 `，`、句号 `。`、顿号 `、`、括号 `（）`、冒号 `：`。
- 破折号：中文用 `——`（两个 em dash）或 `——`，不要用 `--`。
- 数学符号直接用 Unicode：`° × ÷ − π θ √ ∞ ≈ ≠ ≤ ≥ ∠`。

## 4. 术语对照（参照 translations/cn 既有译法）

| 英文 | 中文（Mathigon 既有译法） |
|------|-------------------------|
| Pythagoras' theorem | 勾股定理 / 毕达哥拉斯定理 |
| right angle | 直角 |
| right-angled triangle | 直角三角形 |
| hypotenuse | 斜边 |
| trapezium / trapezoid | 梯形 |
| triangle | 三角形 |
| polygon | 多边形 |
| proof | 证明 |
| theorem | 定理 |
| area | 面积 |
| angle | 角 |
| parallel | 平行 |
| sequence | 序列 |
| function | 函数 |

## 5. gloss/bio 链接保持英文 key

`[勾股定理](gloss:pythagoras-theorem)` —— 显示文字用中文，但括号里的 `gloss:`/`bio:` key 保持**英文原 key**（指向 `content/shared/glossary.yaml` 和 `bios.yaml` 的英文条目）。中文翻译在 `translations/cn/shared/` 下，由 GitLocalize 流程处理，不要在 content 里手改。

## 6. 填空选项用中文

填空选项应翻译成中文（学生在页面看到的）：
```markdown
这是一个 [[直角三角形|等边三角形|锐角三角形]]。
答案是 [[90]]°。
```
第一个选项是正确答案（会被打乱显示）。数学答案仍用 backtick 数学：`[[`1/2 ab`|`ab`]]`。

## 7. hints.yaml 用中文

```yaml
drag-hint: 试着拖动橙色点 U，让它在底边上移动。
```
这是学生看到的提示文字，必须中文。

## 8. 参照真实中文课程

写中文课程前，先读 `translations/cn/` 下的既有翻译（如 `translations/cn/euclidean-geometry/content.md`、`translations/cn/circles/content.md`），学习术语、句式、标点规范。它们的 `> id:`/`> section:`/`> goals:` 保持英文，正文全中文。

## 9. 构建与验证

```bash
npm run assets 2>&1 | grep -i "error\|warning.*cn\|Maths parsing"
# 重点看: "Maths parsing error"（说明中文混进了 backtick）
#          "Missing glossary/bios keys"（说明 gloss/bio key 写错）
npm run server
# 访问首页确认所有 section 都出现 (curl http://localhost:5000/ | grep garfield)
# 再逐个 section 验证中文渲染
```
