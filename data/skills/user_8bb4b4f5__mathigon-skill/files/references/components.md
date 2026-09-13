# Custom Components (`x-*`)

Components are authored in `content.md` as **Pug-style indented tags** (`x-name(attrs)`), then driven from `functions.ts` by selecting and casting: `$step.$('x-name') as Type`. This reference lists the tags/attributes (for content.md) and the runtime types/methods (for functions.ts).

Source: distilled from all course content.md files + `content/shared/types.d.ts` + @mathigon/studio component sources.

## Where each component is registered

| Tag | Registered in | Runtime type |
|-----|---------------|--------------|
| `x-step` | @mathigon/studio | `Step` |
| `x-blank`, `x-blank-mc` | @mathigon/studio | (managed by framework) |
| `x-gesture`, `x-slideshow`, `x-tabbox`, `x-slider`, `x-sortable`, `x-picker`, `x-gallery`, `x-img`, `x-video`, `x-play-btn`, `x-play-toggle`, `x-gloss`, `x-bio`, `x-free-text`, `x-target`, `x-tutor`, `x-var`, `x-progress` | @mathigon/studio | see below |
| `x-select`, `x-icon` | @mathigon/boost | `Select` (re-exported by studio) |
| `x-geopad`, `x-coordinate-system`, `x-coordinate-sketch` | geometry layer (euclid/studio) | `Geopad`, `CoordinateSystem` (in `../shared/types`) |
| `x-equation`, `x-equation-system` | (framework) | `Equation`, `EquationSystem` (in `../shared/types`) |
| `x-solid`, `x-polyhedron`, `x-conic-section`, `x-scale-box`, `x-solved`, `x-buckets`, `x-binary-swipe`, `x-relation`, `x-gameplay`, `x-burst` | textbooks repo `content/shared/components/` | their impl classes |
| `x-polypad` | (framework) | `Polypad` (in `../shared/types`) |

> **If you use a course-local `<x-foo>` (from shared/components/ or ./components/), you MUST add a side-effect import** at the top of functions.ts: `import '../shared/components/solved/solved'` or `import './components/ellipse'`. The `@register('x-foo')` decorator runs on import and defines the element. Without it, the element won't upgrade.

## Media components

### `x-img`
```pug
x-img(src="images/geocentric.jpg" width=320 height=272)
x-img(src="images/x.jpg" width=320 height=160 credit="© Name" lightbox alt="desc")
```
Attrs: `src`, `width`, `height`, `alt`, `credit`, `lightbox` (click-to-zoom).

### `x-video`
```pug
x-video(src="https://static.mathigon.org/videos/weather.mp4" poster="images/weather.jpg" width=640 height=360 controls credit="© NASA")
x-video(width=200 height=200 src="images/ico.mp4" hover loop)
x-video(src="x.mp4" poster="x.jpg" width=220 height=140 audio credit="...")
```
Attrs: `src`, `poster` (defaults to src with .mp4→.jpg), `width`, `height`, `loop`, `audio` (absent = muted), `controls`, `hover` (plays on hover), `preload="no"`, `credit`. Events: `play`, `end`, `timeupdate`.

### `x-play-btn` / `x-play-toggle`
Standalone play buttons, usually inside `x-geopad`. From TS: `$play.on('play', async () => {...})`, `$play.reset()`.

### `x-gesture` — animated pointing hand
```pug
x-gesture(target="#wheel .wheel" slide="100,0")
x-gesture(target=".butterfly")
x-gesture(target=".sel" offset="0,-120" slide="-160,0")
```
Attrs: `target` (CSS selector), `slide="dx,dy"` (drag offset), `offset="dx,dy"`, `start` (auto-start bool). From TS: `Gesture` — `setTarget($el, slide?, shift?)`, `start()`, `stop()`, `startSlide($from, $to)`.

## Geometry components

### `x-geopad` — interactive geometry pad
```pug
x-geopad(width=320 height=300 style="position: relative;")
  svg(style="stroke-linecap: round; stroke-linejoin: round")
    circle.move(name="a" cx=160 cy=150 target="r d")
    circle.move.reveal(name="b" cx=250 cy=240 project="circle(a, 120)" target="r" when="compass")
    path.red(x="segment(a,b).contract(0.08)" target="r" arrows="both" hidden)
    path(name="c1" x="arc(a,b,1.99*pi)" hidden)
  x-play-btn
```
- **`circle`** attrs: `x="point(150,150)"` (geometry expr) OR `cx`/`cy`, `name`, `target`, `project="circle(a, 120)"`, `move` (draggable), `reveal`, `hidden`, classes (`.red`, `.blue`).
- **`path`** attrs: `x="segment(a,b)"` / `x="arc(a,b,1.99*pi)"` / `x="angle(a,c,b)"` / `x="polyline(...)"`, `target`, `arrows`, `fill`, `label`, classes.
- The `x=` expressions use a geometry mini-language: `point`, `segment`, `line`, `ray`, `circle`, `arc`, `sector`, `polygon`, `polyline`, `triangle`, `angle`, `distance`, `intersections`, `pi`, `round`, `sqrt`, etc.

**Runtime `Geopad` type (from ../shared/types):** `animateConstruction(name, duration?)`, `animatePoint(name, target, duration?)`, `switchTool('move'|'point'|'line'|'circle'|'rectangle'|'perpBisector'|'angleBisector')`, `select(obj?)`, `deselect()`, `delete()`, `redraw()`, `waitForPoint()`, `waitForPath(validate, opts)`, `waitForPaths(paths, opts)`, `showGesture(from, to?)`. Collections: `shapes`, `points`, `paths`, `polygons`, `intersections`. View groups: `$polygons`, `$paths`, `$points`, `$tools`.

### `x-coordinate-system` — graph/plot
```pug
x-coordinate-system(padding="12 12 24 120" width=640 height=320 x-axis="0,7,1" label-suffix="s,m" axis-names="time,height")
x-coordinate-system(x-axis="0,1.1,0.2" y-axis="0,10,1" crosshair-grid=1 labels="no")
```
Attrs: `width`, `height`, `x-axis="min,max,step"`, `y-axis=`, `axis-names="x,y"`, `padding="t r b l"`, `label-suffix="sx,sy"`, `labels="no"`, `crosshair-grid=1`, `crosshairs="no"`.

**Runtime `CoordinateSystem`:** `setPoints(points, initial?)`, `setSeries(...series: Point[][])`, `setFunctions(...fns)`, `drawLinePlot(points)`, `drawPoints(points)`, `$plot`, `$overlay`, `$xAxis`, `$yAxis`. Also inherited from `CoordinatePlane`: `toPlotCoords(p)`, `toViewportCoords(p)`, `plotBounds`.

### `x-solid` — 3D solid (THREE.js based)
```pug
x-solid(size="300,200" static)
x-solid(size=220 rotate="0.5")
```
Runtime `Solid` (from `../shared/components/webgl/solid`): `addMesh`, `addSolid`, `addOutlined`, `addWireframe`, `addArrow`, `addLabel`, `addCircle`, `addPoint`, `rotate`, `object`, `scene`.

### `x-polyhedron` / `x-polyhedron-slice`
```pug
x-polyhedron#poly1(size=220 shape="PentagonalPrism")
x-polyhedron-slice(:shape="poly" :opacity="opacity")   ← reactive :bind
```

### `x-conic-section`, `x-scale-box`, `x-coordinate-sketch` — specialized geometry.

## Input / control components

### `x-slider`
```pug
x-slider(steps=400 speed=0.5)
x-slider(:bind="x" steps=5 continuous)
x-slider#fern-slider(steps=8 :bind="steps")
```
Attrs: `steps` (number), `speed=0.5`, `continuous` (bool), `:bind="varName"` (two-way model binding), `no-play`, `snap`. Runtime `Slider`: `set(x)`, `play()`, `moveTo(x, duration)`, `current`, `steps`. Events: `move`, `slide-end`.

### `x-select` — segmented/tabs selector
```pug
x-select.segmented.var(:bind="type")
  div(value="cube") Cube
  div(value="sphere") Sphere

x-select.tabs(:bind="poly")
  div(value="tetrahedron") Tetrahedron
  div(value="cube") Cube
```
Variants: `.segmented`, `.tabs`, `.var(:bind="x")`. Option children carry `value=`. Runtime `Select`: `on('change', ($el) => ...)`, `$active`, `$$active`. Active option's data via `$select.$active.data.<x>`.

### `x-picker` — pick one of many
```pug
x-picker
  .item.text-center #[.t-num 4]#[.t-num 6]
  .item.text-center(data-error="inequality-error-1") #[.t-num 1]
```

### `x-equation` — inline answer input
```pug
_{x-equation.small(solution="2 π" keys="+ × π" numeric)}_
{x-equation(solution="π r^2 h" keys="+ − × ÷ π frac sup brackets" short-var hints="cylinder-volume-hint1 cylinder-volume-hint2")}
```
Attrs: `solution="..."` (correct answer in math syntax), `keys="+ − × ÷ π frac sup brackets"` (on-screen keyboard), `numeric` (bool), `short-var`, `hints="id1 id2"`. Usually wrapped inline `_{...}_`. Runtime `Equation`: `validate = (expr) => {isCorrect?, error?} | undefined`, `solution`, `hints`, `setup($step, goal)`, `focus()`, `check()`, `solve()`.

### `x-equation-system` — multi-step worked equation
```pug
::: x-equation-system.reveal(when="blank-0" steps="π s^2 * (2 π r) / (2 π s) | π r s" hints="cone-surface-1|cone-surface-2")
| `pill(A,"green","sector")` | `=` | `pill(A,"teal","circle") × ...` |
:::
```
Attrs: `steps="step1 | step2 | ..."` (pipe-separated), `hints="h1|h2"`. Runtime `EquationSystem`: `validate = (expr, isRepeated) => ...`, `isFinal = (expr) => boolean`, `setup($step, goal)`, `solve()`.

### `x-buckets` — sort into buckets
```pug
x-buckets.independent
  .inputs
    .input(bucket="0") Winning the lottery and running out of milk.
  .buckets
    .bucket
      .title Independent
```

### `x-relation` — domain/range matching
```pug
x-relation
  .item(slot="domain" name="a") ...
  .item(slot="range") ...
```

### `x-free-text`, `x-number-grid`, `x-prime-picker` — other inputs.

## Layout / navigation components

### `x-slideshow` — stepped slideshow
```pug
::: x-slideshow
{div.inline(slot="legend")} Step 1 text...
::: x-slideshow.golden-spiral(step="auto")
```
Runtime `Slideshow`: events `next`, `back`, `next back` (either), `step` with index.

### `x-tabbox` — tabbed container (NOT `x-tabs`)
```pug
x-tabbox.full-width
  .tab
    h3 Map 1#[span.check.incorrect(when="bridge-0")]
    x-solved
    include svg/bridges-1.svg
    button.btn Clear
    button.btn.right Skip
```
Each `.tab`'s `<h3>` becomes the tab title. Runtime `Tabbox`: `makeActive(i)`.

### `x-solved` — "is this solved?" target
Pairs with `button.btn Clear` / `button.btn Skip`. Calls `enter()`/`exit()`, `$step.addHint('correct')` on solve.

## Course-local shared components (`content/shared/components/`)

| Tag | File | Purpose |
|-----|------|---------|
| `x-solved` | `solved/solved.ts` | solved/clear/skip widget |
| `x-scale-box` | `scale-box/scale-box.ts` | scalable container (template `<div><slot></slot></div>`) |
| `x-buckets` | `buckets/buckets.ts` | sort-into-buckets with Draggable + $targets |
| `x-solid` | `webgl/solid.ts` | THREE.js 3D solid |
| `x-conic-section` | `webgl/conic-section.ts` | 3D conic section |
| `x-binary-swipe` | `binary-swipe/` | binary swipe puzzle |
| `x-relation` | `relation/` | domain/range matching |
| `x-gameplay` | `gameplay/` | mini-game container |
| `Burst` (class, not a tag) | `burst.ts` | SVG burst effect — `new Burst($g, count)` |

## Authoring a NEW custom component

If you need a brand-new `<x-foo>`:

1. Create `content/<course>/components/foo.ts` (course-local) or `content/shared/components/foo/foo.ts` (reusable).
2. Use the `@register` decorator from @mathigon/boost + extend `CustomElementView`:
   ```ts
   import {CustomElementView, register} from '@mathigon/boost';

   @register('x-foo', {template: '<div><slot></slot></div>'})
   export class Foo extends CustomElementView {
     ready() { /* runs when element + children ready */ }
     // custom methods accessible after $step.$('x-foo') as Foo
   }
   ```
3. Add a **side-effect import** in every functions.ts that uses it: `import './components/foo'` or `import '../shared/components/foo/foo'`.
4. Lifecycle: `created()` runs on instantiation; `template` (if provided) is injected and `<slot>`s filled with original children; `ready()` runs after all child custom elements are ready.

> The older `@CustomElement('x-foo')` decorator is deprecated in this version (0.1.43-era) — use `@register('x-foo', {template})`.

## Reactive binding on any component/element

Vue-style attributes (parsed by boost's template system):
- `:bind="varName"` — two-way model binding (sliders, selects, inputs)
- `:html="expr"` — set innerHTML from a model expression
- `:show="cond"` — toggle visibility
- `:if="cond"` — add/remove from DOM
- `:class="..."`, `:draw="..."`, any `:foo="..."` — set attribute foo
- `@event="handler"` — bind event handler
- `${expr}` interpolation in text/attribute values

Functions called from templates (`{{ fn(x) }}`, `action:`, expressions) must be attached to `$step.model`: `$step.model.myFn = (x) => ...`.
