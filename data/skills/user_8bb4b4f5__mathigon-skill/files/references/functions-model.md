# `functions.ts` Interactive Model

How interactivity is wired into Mathigon courses. Source: distilled from real course `functions.ts` files + `content/shared/types.d.ts` + @mathigon/studio's `step.ts`.

## The export-per-section contract

```ts
// content/<course>/functions.ts
export function <camelCasedId>($step: Step) {
  // runs ONCE, the first time the step with > id: <kebab-id> is revealed
}
```

- `toCamelCase("my-step-2")` → `myStep2`. Keep the `> id:` and the function name in sync.
- Parameter conventionally `$step` (graph-theory uses `$section` — same `Step` type).
- Most steps have **no** function (pure content). Add one only for custom JS.
- Async is allowed: `export async function sphereMaps($step: Step) { await loadD3(); ... }`.
- A noop exists for courses with no interactivity: `export function noop() {}`.

## File skeleton (always start with this)

```ts
// =============================================================================
// <Course Name>
// (c) Mathigon
// =============================================================================


import {/* core utils */} from '@mathigon/core';
import {/* math */} from '@mathigon/fermat';
import {/* geometry */} from '@mathigon/euclid';
import {$, $N, animate, /* views */} from '@mathigon/boost';
import {Step, Slider, Select, /* components */} from '@mathigon/studio';

import {Geopad, EquationSystem} from '../shared/types';
import {RED, BLUE} from '../shared/constants';
import {Burst} from '../shared/components/burst';

import {MyLocalThing} from './components/my-local-thing';

// side-effect: register custom elements used in this course's content.md
import '../shared/components/solved/solved';
import './components/ellipse';

// -----------------------------------------------------------------------------
// <Section grouping comment, mirrors > section: in content.md>

export function myStep($step: Step) {
  // ...
}
```

## The `Step` API — what you actually call

### Selection (inherited from ElementView — `$step` is queryable)
```ts
$step.$('.ball')              // first match → ElementView (or subclass)
$step.$$('circle')            // all matches → ElementView[]
$step.$('x-geopad') as Geopad // cast to component type
$step.$blanks[i].on('valid', cb)  // react to blank answers
```
Free functions `$('sel', $parent?)`, `$$(sel, $parent?)`, `$N(tag, attrs, $parent)` come from `@mathigon/boost` (see libraries.md).

### Scoring & goals (the core lifecycle)
```ts
$step.score('compass');              // fulfil a goal declared in > goals:
$step.score('circle-' + i);          // dynamic goal name
$step.onScore('blank-0', cb);        // fire when goal(s) achieved
$step.onScore('blank-0 blank-1', cb);// space-separated = ALL required (idiomatic)
$step.addHint('correct');            // random praise from shared hints.yaml
$step.addHint('myHintKey');          // key resolved from course hints.yaml
```
**Goal names** passed to `score()` must match tokens in the section's `> goals:`. Blanks auto-generate `blank-0, blank-1, …` (don't score them yourself — listen). `x-equation-system` rows auto-generate `eqn-0, …`.

### Properties
```ts
$step.model            // Observable — reactive model bound to template ($step.model.x = 5)
$step.isReady          // bool, step finished initialising
$step.isPageLoaded     // bool, false during resume/restore (guard confetti etc.)
$step.prev             // previous Step (sibling)
$step.$blanks          // x-blank views array
```
Because Step extends ElementView, you can also call `$step.addClass(...)`, `$step.on(...)`, etc. directly.

### What does NOT exist (don't reach for these)
`$step.solve(...)`, `$step.scoreGoal(...)`, `$step.score([...])` (score takes ONE string), `$step.data` (use per-element `.data`), `$step.enter/exit/reveal` (those are child ElementView methods). `$step.score(['a','b'][i])` is just JS indexing then a single-string score call.

## The reactive `$step.model`

`$step.model` is an `Observable`. Patterns:

```ts
// 1. Write a value — template bindings ({{x}}, ${x}, :bind="x") update
$step.model.day = 0;
$step.model.h = 5;

// 2. Attach a function the template can call (action: links, expressions)
$step.model.toWord = toWord;
$step.model.increment = (n: number) => { $step.model.b += 1; };

// 3. Watch — auto-tracks which properties are accessed in the body, re-runs on their change
$step.model.watch((state: any) => {
  $circle.removeChildren();
  for (const i of list(state.n1)) { $N('path', {...}, $circle); }
});

// 4. Assign many at once
$step.model.assign({b: 2, r: 3});
$step.model.set = (b, r) => $step.model.assign({b, r});
```
`watch` is efficient: first run records which properties were read; subsequent runs fire only when *those* change.

## ElementView methods (the `$`/`$$`/`$N` results)

### Animation (the most-used)
```ts
$el.enter('draw-reverse', 1500, 1000);   // effect, durationMs, delayMs — returns {promise}
$el.exit();                              // hide (often bare)
$el.exit('pop');
await $img.exit('fade', 200).promise;    // await the animation
$el.effect('pulse-down');                // named CSS effect
$el.animate({transform: ['scale(1)', 'scale(.4)']}, 600);  // [from,to] or target
$el.animate({fill: GREEN}, 600);
```
Effects: `fade`, `pop`, `descend`, `ascend`, `draw`, `draw-reverse`, `slide`, `slide-down/up`, `reveal`, `reveal-left/right`.

### Visibility & classes
```ts
$el.hide(); $el.show(); $el.toggle(show?);
$el.addClass('c'); $el.removeClass('c'); $el.toggleClass('c'); $el.setClass('hidden', cond);
$el.hasClass('active');
```

### CSS & attributes
```ts
$el.css('transform', `translate(${x}px, ${y}px)`);
$el.css({transform: 'rotate(23.5deg)'});
$el.setAttr('cy', newY);   $el.attr('cx');        // setAttr vs attr getter
$el.text = '...';          $el.textStr = n;       // rendered text vs coerced
$el.remove(); $el.removeChildren();
```

### SVG geometry helpers (SVGView)
```ts
$path.setLine(p1, p2);          $circle.setCenter(point);
$el.translate(x, y);            $el.setTransform(translate?, rotate?, scale?);
$path.points = [...];           // parse/build the `d` attribute
$svg.drawPath(euclidShape, attrs);  // create <path> child from a euclid shape
```

### Tree & events
```ts
$el.children / .next / .prev / .parent / .parents('x-step') / .id
$el.data.type          // typed data-* attrs (camelCased): data-type → .data.type
$el.on('click', fn);   $el.one('play', async () => {...});
$el.on('next back', fn);  // space-separated events
```

## Gestures & dragging

### `slide($el, fns)` — drag/swipe (from @mathigon/boost)
```ts
slide($wheel, {
  move(posn, start, last) {
    p = clamp(p + (posn.x - last.x) / 314, 0.01, 1);
    redraw();
    if (p > 0.95 && !done) $step.score('unroll');
  },
  end() { /* ... */ },
  accessible: true   // keyboard-accessible
});
```
Callbacks: `down(p)`, `start(p)`, `move(p, start, last)`, `end(last, start)`, `click(p)`. Auto-handles SVG/canvas coordinate conversion.

### `hover($el, {enter, exit})` — hover/focus
```ts
hover($c, {
  enter() { $step.score('hover'); /* ... */ },
  exit() { /* ... */ }
});
```

### `Draggable` — drag-and-drop with targets (from @mathigon/studio/boost)
```ts
const drag = new Draggable($card, {
  $parent: $svg, $targets: $buckets, useTransform: true, resetOnMiss: true, withinBounds: false
});
drag.on('move', (e) => { posn.x = e.posn.x; redraw(); });
drag.on('enter-target', ({$target}) => $target.addClass('active'));
drag.on('end', ({$target}) => { if ($target) score(); });
drag.setPosition(x, y);  drag.resetPosition();
drag.disabled = true;
```
Events: `start`, `move {posn}`, `end {$target?}`, `click`, `enter-target {$target}`, `exit-target {$target}`.

### `Gesture` — animated pointing hand (`<x-gesture>`)
```ts
const $gesture = $N('x-gesture', {}, $step) as Gesture;
$gesture.setTarget($handle, slide, shift);   // slide/shift optional offset
setTimeout(() => $gesture.start(), 1000);
$gesture.startSlide($from, $to);
$svg.on('click pointerdown', () => $gesture.stop());
```
Or just author `<x-gesture target=".sel" slide="100,0">` in content.md.

## Animation loops — `animate` (from @mathigon/boost)
```ts
const anim = animate((p, dt) => {       // p ∈ [0,1] over duration; dt = ms since last frame
  $path.points = points.slice(0, p * 401);
}, 5000);
await anim.promise;     // awaitable
anim.cancel();          // stop
```
Easing: `ease('sine-out', p)`, `ease('exp-out', p)`. Types: `quad/cubic/quart/quint/circ/sine/exp/back/elastic/swing/spring/bounce` + `-in`/`-out`. Timing: `wait(ms)` → Promise, `delay(fn, ms)`.

## Driving built-in components

### Select (`<x-select>`)
```ts
const $select = $step.$('x-select') as Select;
$select.on('change', ($el) => {
  const i = $select.$active.data.value;   // active option's data
  if (i === 3) $step.score('area-circle');
});
```

### Slider (`<x-slider>`)
```ts
const $slider = $step.$('x-slider') as Slider;
$slider.on('move', (value: number) => { redraw(value); });
$slider.set(0);  $slider.moveTo(5, 1000);   $slider.current;  $slider.steps;
```

### PlayBtn (`<x-play-btn>`)
```ts
const $play = $step.$('x-play-btn') as PlayBtn;
$play.one('play', async () => {
  await animate((p) => {...}, 5000).promise;
  $play.reset();
  $step.score('play');
});
```

### Slideshow (`<x-slideshow>`)
```ts
const $slideshow = $step.$('x-slideshow') as Slideshow;
$slideshow.on('next', async (x: number) => { /* x = slide index */ });
$slideshow.on('back', async (x: number) => { /* ... */ });
```

### Video (`<x-video>`)
```ts
$step.$('x-video')!.one('play', () => $step.score('video'));
$step.$('x-video')!.on('end', () => $step.score('video'));
```

## Where types come from

| Type | Source |
|------|--------|
| `Step` | `@mathigon/studio` |
| `Slider`, `Select`, `Slideshow`, `PlayBtn`, `Tabbox`, `Gesture`, `Draggable`, `confetti` | `@mathigon/studio` |
| `Geopad`, `Equation`, `EquationSystem`, `CoordinateSystem`, `Polypad`, 3D types | `../shared/types` (a .d.ts — type-only) |
| `Solid`, `Burst`, `ConicSection`, course-local components | their impl files under `../shared/components/` or `./components/` |
| `Point`, `Line`, `Circle`, `Polygon`, etc. | `@mathigon/euclid` |
| `$`, `$$`, `$N`, `ElementView`, `SVGView`, `animate`, `slide`, `hover` | `@mathigon/boost` |
| `list`, `tabulate`, `wait`, `delay`, `Color`, `Obj` | `@mathigon/core` |
| `Random`, `clamp`, `lerp`, `round`, `numberFormat` | `@mathigon/fermat` |
| `Expression`, `ExprElement` | `@mathigon/hilbert` |

## Equation validation (x-equation-system)

```ts
const $system = $step.$('x-equation-system') as EquationSystem;
$system.isFinal = (expr) => !expr.variables.includes('s') && expr.functions.includes('sqrt');
$system.validate = (expr, isRepeated) => {
  if (isRepeated && expr.variables.includes('s')) return {error: 'cone-surface-2'};
  return undefined;   // undefined = no error
};
// or for x-equation:
const $eq = $step.$('x-equation') as Equation;
$eq.validate = (expr: ExprElement) => {
  if (Expression.numEquals(expr, close)) return {error: 'pay-it-forward-close'};
  return undefined;
};
```

## Geopad animation (x-geopad)

```ts
const $geopad = $step.$('x-geopad') as Geopad;
await $geopad.animateConstruction('c1');          // animate drawing the path named c1
$geopad.animatePoint('b', new Point(240, 140));   // move point b to a target
$geopad.$('.earth')!.insertBefore($geopad.$('.shadow')!);
$geopad.$paths.insertAfter($geopad.$('.obelisk')!);
$geopad.showGesture(from, to);                    // show a gesture hint
const point = await $geopad.waitForPoint();        // wait for user to place a point
await $geopad.waitForPath((path) => /* validate */, {onCorrect, onIncorrect, maxErrors});
```

## hints.yaml

Course-local `hints.yaml` holds strings keyed by what you pass to `$step.addHint`:
```yaml
crossWater: Careful – you are not allowed to enter the water.
mapError: You can't use this colour here.
```
`$step.addHint('correct')` / `'incorrect'` draw from the shared `content/shared/hints.yaml` (randomized praise/retry arrays).

## Tips

- `confetti()` (from @mathigon/studio) fires the celebration — guard with `if ($step.isPageLoaded) confetti();`.
- For "do X after N tries": use a counter in a closure + `$step.isReady`/`setTimeout`.
- Reach the previous step: `if ($step.prev) $step.prev.addClass('complete');`.
- Match a content.md `> id:` to its function by camelCasing — verify with a grep before assuming one exists.
