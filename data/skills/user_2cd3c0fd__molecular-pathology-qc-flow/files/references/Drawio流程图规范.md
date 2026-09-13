# Draw.io 流程图规范

作者：WangYunL  
生成器版本：1.2

## 目录

- [一、目标格式](#一目标格式)
- [二、单元格角色](#二单元格角色)
- [三、图页元数据](#三图页元数据)
- [四、样式语义](#四样式语义)
- [五、文字和分支](#五文字和分支)
- [六、布局](#六布局)
- [七、来源说明](#七来源说明)
- [八、生成和校验](#八生成和校验)
- [九、结构预览](#九结构预览)
- [十、修改已有图](#十修改已有图)
- [十一、兼容性](#十一兼容性)

## 一、目标格式

生成 UTF-8、未压缩、可编辑的 Draw.io XML：

- 根节点为 mxfile
- 图页包含 diagram、mxGraphModel 和 root
- 业务节点为 mxCell vertex
- 业务连线为 mxCell edge，并包含真实 source 和 target
- 阶段泳道和来源说明也是 mxCell，但使用 data-role 与业务节点隔离

未压缩 XML 便于审查、修改和差异比较。

## 二、单元格角色

| data-role | 用途 | 是否计入业务节点 |
| --- | --- | --- |
| business | 节点或连线 | 是 |
| stage | 阶段泳道背景 | 否 |
| metadata | 图内证据与适用范围 | 否 |

校验器会排除 stage 和 metadata，避免来源说明被误判为第二个开始节点。

## 三、图页元数据

v1.1 图页写入：

- data-schema-version
- data-generator-version
- data-technology
- data-method
- data-project
- data-qc-stage
- data-sources（压缩 JSON）
- data-measurements（压缩 JSON）

业务节点写入 data-node-type、data-stage、data-evidence-refs、可选 data-condition 和 data-terminal-result。业务连线写入 data-branch 和 data-evidence-refs。

## 四、样式语义

| 语义 | 图形 | 颜色 |
| --- | --- | --- |
| 输入或开始 | 圆角矩形 | 浅灰 |
| 处理或计算 | 圆角矩形 | 浅蓝 |
| 条件判断 | 菱形 | 浅黄 |
| 阳性或通过 | 圆角矩形 | 浅绿 |
| 阴性或普通结束 | 圆角矩形 | 浅灰 |
| 失败或无效 | 圆角矩形 | 浅红 |
| 复检或待处理 | 圆角矩形 | 浅橙 |

颜色表达流程语义，不表达医学风险等级。

## 五、文字和分支

1. 主流程从上到下，结果或失败分支放左右两侧。
2. 二元判断优先使用“是/否”，并补充直接阳性、灰区、无效等业务含义。
3. 阈值分支写完整边界，例如“否（无 Ct 或 Ct ≥ 35）”。
4. 不使用“正常/异常”代替具体结果，除非原始资料就是这样定义。
5. 允许的 HTML 换行标签会保留；字面 `<` 会转换为 Draw.io 安全实体，避免被当成标签。

## 六、布局

### 6.1 flow

- 显式 x、y、width、height 优先，适合复刻已有图。
- 缺少坐标时按开始节点和有向关系计算 level。
- 同层节点按中心、左、右交替展开。

### 6.2 swimlane

- 按 diagram.stages 生成横向阶段背景。
- 每个阶段内按全局流程层级压缩排布。
- 单独的失败或终点分支默认放到主通道侧边，避免后续连线穿过终点。
- 多个终点默认左右展开。

### 6.3 页面自适应

auto_size 为 true 时，页面宽高至少覆盖所有节点、泳道和来源说明；显式 page_width/page_height 作为最小尺寸。false 时使用固定尺寸。

## 七、来源说明

show_source_note 为 true 时，在业务流程下方增加可见说明，包含来源 ID、标题、版本、证据状态和适用范围。它不计入业务节点，也不能替代交付文档中的完整来源列表。

## 八、生成和校验

从 Skill 根目录执行：

    python -B -X utf8 scripts/generate_drawio.py --input assets/BRAF-V600E下机质控.json --output BRAF_V600E下机质控_流程图.drawio
    python -B -X utf8 scripts/validate_drawio.py BRAF_V600E下机质控_流程图.drawio

校验包括：

- XML 和 UTF-8
- 图页业务元数据
- 业务节点和连线 ID
- source、target 和 evidence_refs
- 唯一开始节点
- 判断节点出口数量、文字和 branch 唯一性
- 从开始节点可达
- 明确终点和反向终点可达性
- 无出口循环拒绝

## 九、结构预览

生成 SVG：

    python -B -X utf8 scripts/render_drawio_preview.py 输入.drawio --output 输出_结构预览.svg

生成 PNG（需要 Pillow）：

    python -B -X utf8 scripts/render_drawio_preview.py 输入.drawio --output 输出_结构预览.png

结构预览器使用 Draw.io 节点几何和样式生成近似图，用于发现节点遮挡、分支穿越、页面裁切和中文换行问题。它不实现 diagrams.net 的全部路由和字体算法，不能替代桌面端实际打开验收。

## 十、修改已有图

先解析原图节点、连线、坐标、样式和图页元数据，再生成新文件。默认不覆盖用户原文件。遇到只有 targetPoint、没有 target 的悬空线时，在新图中绑定真实终点，并在交付说明中记录结构修正。

## 十一、兼容性

校验器可读取没有 data-role 的旧版业务节点；生成器可读取 v1.0 JSON。新增正式文件统一输出 v1.1 元数据。业务 ID 不得使用 `_meta_` 或 `_stage_`，避免与来源说明和泳道单元格冲突。
