---
name: mindmap-generator
description: |
  This skill should be used when users want to automatically generate a structured mind map 
  from a given topic/theme. It analyzes the topic, creates a hierarchical structure, and 
  outputs a PNG image. Triggers include: "生成导图", "帮我画思维导图", "create a mind map", 
  "自动生成结构化导图", "输入主题生成导图", and similar requests.
agent_created: true
---

# Mind Map Generator Skill

Generate structured mind maps from any topic and export as PNG images.

## Purpose

This skill transforms a given topic/theme into a well-organized hierarchical mind map. 
The AI analyzes the topic, identifies key dimensions and sub-topics, structures them logically, 
and renders them as a professional PNG image.

## When to Use

Activate this skill when users:
- Ask to generate a mind map for any topic
- Request visualization of a concept, subject, or theme
- Want to see a structured breakdown of a topic
- Need a visual overview for studying, planning, or brainstorming

**Trigger phrases**: 生成导图, 思维导图, create mind map, 结构化分析, 帮我画图

## Workflow

### Step 1: Topic Analysis

When the user provides a topic, analyze it to identify:
1. **Core concept** - The central theme
2. **Key dimensions** - Major aspects or categories (typically 3-6)
3. **Sub-topics** - Detailed points under each dimension
4. **Logical relationships** - How elements connect

### Step 2: Structure Generation

Build a hierarchical mind map structure following these principles:

```
                    [Central Topic]
                          |
    +--------+------------+------------+
    |        |            |            |
  [Dim 1] [Dim 2]      [Dim 3]      [Dim 4]
    |        |            |            |
 [Sub 1]  [Sub 1]      [Sub 1]      [Sub 1]
 [Sub 2]  [Sub 2]      [Sub 2]      [Sub 2]
```

**Guidelines**:
- 1 central node (the topic)
- 3-6 main branches (dimensions)
- 2-4 sub-nodes per branch
- Keep text concise (under 10 characters per node if possible)
- Use parallel structure within each level

### Step 3: Generate Mind Map

1. Call the `generate_mindmap.py` script with the structured data
2. The script uses Graphviz to render the mind map
3. Output is saved as `mindmap.png` in the current workspace

**Script location**: `mindmap-generator/scripts/generate_mindmap.py`

**Usage**:
```bash
python mindmap-generator/scripts/generate_mindmap.py "Central Topic" "Branch1:Sub1,Sub2" "Branch2:Sub1,Sub2" -o output.png
```

### Step 4: Deliver Result

1. Display the PNG image to the user
2. Explain the mind map structure briefly
3. Offer to refine or expand specific branches

## Script Details

### generate_mindmap.py

**Dependencies**: 
- Graphviz (system package): https://graphviz.gitlab.io/download/
- Python package: `pip install graphviz`

**Arguments**:
- `topic`: Central topic text (quoted if contains spaces)
- `branches`: Branch definitions in format `BranchName:Item1,Item2,...`
- `-o, --output`: Output file path (default: mindmap.png)
- `-c, --color-scheme`: Color theme (default: blues)

**Example**:
```bash
python mindmap-generator/scripts/generate_mindmap.py "前端开发" "基础知识:HTML,CSS,JavaScript" "框架:React,Vue,Angular" -o frontend_map.png
```

## Color Schemes

Available color schemes for mind map aesthetics:
- `blues` (default) - Professional blue tones
- `greens` - Nature/organic theme
- `warm` - Orange/red gradient
- `purple` - Creative/purple theme
- `mono` - Black and white

## Best Practices

1. **Keep branches balanced** - Try to have similar number of sub-items per branch
2. **Use parallel structure** - Items at same level should be comparable
3. **Avoid text overflow** - Short labels render better
4. **Limit depth** - 2-3 levels deep is optimal for readability

## Example

When user says: "帮我生成一个关于'时间管理'的思维导图"

Expected structure:
```
                    时间管理
                       |
    +---------+--------+--------+--------+
    |         |        |        |        |
  目标设定  优先级    工具方法   习惯养成
    |         |        |        |
  SMART原则  ABC法则  日历App   早起
  拆解任务  四象限   番茄钟    复盘
```

The generated PNG will display this as a visually appealing radial mind map.
