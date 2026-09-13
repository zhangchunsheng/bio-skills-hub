# Visual HTML Manual Design System

## Contents

1. Document architecture
2. Component selection
3. Visual language
4. Screenshot system
5. Responsive and print behavior
6. Quality gates

## 1. Document architecture

Use this default order, removing only chapters that do not apply:

1. Cover and scope
2. Executive route/category map
3. One detailed chapter per route or implementation type
4. Source preparation and input standards
5. One detailed playbook per scenario
6. End-to-end integration or workflow wiring
7. Test and acceptance
8. Maintenance, update, rollback, and troubleshooting
9. Screenshot index and reusable forms

The sidebar must mirror the actual hierarchy. Do not add a parent and only the first child; either list all same-level children or intentionally list none.

## 2. Component selection

Choose the smallest component that makes the relationship obvious.

| Information relationship | Component | Class/pattern |
|---|---|---|
| 2–4 parallel choices | Cards | `.summary-grid`, `.route-grid` |
| Ordered action sequence | Step cards | `.steps`, `.step-card` |
| Linear data movement | Flow | `.flow`, `.flow-node`, `.flow-arrow` |
| Conditional choice | Decision rows | `.decision-flow`, `.decision-row` |
| Roles or systems acting in parallel | Swimlanes | `.lanes`, `.lane` |
| Risk, rule, success, warning | Callout | `.callout`, `.good`, `.warn`, `.danger` |
| Exact field-by-field comparison | Table | `.table-wrap` |
| UI operation evidence | Screenshot | `.shot` |
| Small measurable targets | KPI cards | `.kpi-grid` |

Prefer visuals when three or more items interact or a sequence has three or more steps. Keep explanatory text close to the visual; do not make the reader decode an unlabeled diagram.

### Scenario playbook anatomy

Every substantial scenario should contain:

- Trigger and goal
- Required input and owner
- Route/knowledge-source choice
- Explicit numbered procedure
- A flow diagram whose nodes are real actions
- Key settings or decision points
- Expected output and acceptance check
- Failure/rollback path
- One or more screenshots if the action occurs in a UI

## 3. Visual language

### Tokens

- Navy `#0b2848`: headings, primary structure, table headers
- Blue `#155eef`: actions, step numbers, links, active state
- Cyan `#0e7490`: secondary route or data source
- Ink `#172033`: body copy
- Muted `#5d6b82`: captions and supporting text
- Line `#dce3ec`: borders and dividers
- Soft `#f4f7fb`: low-emphasis panels
- Green `#087a55`: success or recommended
- Amber `#a15c00`: caution or preparation
- Red `#b42318`: stop, risk, or failure

Use color semantically and consistently. Do not introduce decorative gradients beyond the cover/sidebar unless a new brand requires it.

### Typography and density

- Prefer Microsoft YaHei/PingFang SC/Noto Sans CJK SC for Chinese.
- Body: about 15px and 1.7–1.8 line-height.
- Keep line lengths comfortable through a centered document width around 1160px.
- Do not fill every area. Use whitespace to group ideas, but make scenario chapters operationally complete.
- Avoid more than six cards in one undifferentiated grid; group them or add subheadings.

### Flow wording

Each node should begin with a verb or a concrete system state:

- Good: `选择目标知识库`, `上传源文件`, `检查解析结果`, `发布工作流`
- Weak: `知识准备`, `系统处理`, `后续操作`, `完成`

Put a small note under a node when a parameter, owner, or output is important.

## 4. Screenshot system

Store images beside the HTML in a predictable directory:

```text
manual.html
manual-images/
  S01.png
  S02.png
  source-link/
    01-upload-source.png
```

Rules:

- Name by operational order, not capture time.
- Use meaningful `alt` text describing the relevant UI region.
- State screenshot scope and redaction needs in the placeholder.
- Use `data-src` for optional screenshots so a missing file leaves a designed placeholder.
- Let `.shot-img` use the common sizing rules; never add per-image width/height hacks.
- Keep captions focused on what to verify after the click, not merely what the picture shows.
- Verify both landscape and portrait screenshots in the same frame.

## 5. Responsive and print behavior

Desktop:

- Sticky 260–300px sidebar
- Centered document canvas
- Multi-column cards where useful

Narrow screen:

- Sidebar becomes a compact top block
- Navigation may collapse or become horizontally scrollable
- Grids become one column
- Flows become vertical and arrows rotate conceptually downward
- Content remains fully readable without horizontal page scrolling

Print/PDF:

- Hide sidebar, controls, and lightbox
- Use A4 margins
- Make the cover a full first page
- Avoid breaking cards, figures, and tables internally where practical
- Remove interactive hover effects and excessive shadows
- Preserve background colors with `print-color-adjust`

## 6. Quality gates

### Structural

- Exactly one `h1`
- Unique section IDs
- Every `nav[href^="#"]` resolves
- Navigation labels and headings use consistent numbering
- No sample/TODO copy remains

### Content

- The implementation/category map appears before detailed scenarios
- Each route and major scenario has explicit executable steps
- Parameters are qualified as verified values or recommended starting points
- Acceptance criteria and maintenance ownership are present

### Media and interaction

- Every image has alt text
- Every expected missing image has a visible placeholder
- Existing images load through relative paths
- Click, Enter, Space, backdrop click, close button, and Escape work in the lightbox
- Focus returns to the invoking image after close

### Visual

- Inspect at approximately 1440px and 390px viewport widths
- Inspect one landscape and one portrait screenshot
- Check sidebar completeness and active/hover states
- Check print preview for clipped flows, oversized screenshots, and blank pages
- Confirm no horizontal overflow except intentionally scrollable tables/flows
