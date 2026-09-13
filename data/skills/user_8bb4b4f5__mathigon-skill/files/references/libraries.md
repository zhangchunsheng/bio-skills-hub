# @mathigon/* Library API (quick reference)

Pinned versions in this repo: `@mathigon/core@1.1.19`, `@mathigon/fermat@1.1.20`, `@mathigon/euclid@1.2.0`, `@mathigon/boost@1.2.27`, `@mathigon/hilbert@1.1.20`, `@mathigon/studio@0.1.43`. Source: TypeScript source on GitHub (mathigon/*.js), cross-checked against actual usage in this repo.

**Corrections to common assumptions** (verified, not in docs): no `spread` in core; no `Polynomial`/`smoothstep`/`Transform` class; `Matrix`/`Random`/`Regression` are **namespace exports** (`Random.uniform`, `Matrix.product`), not classes; transforms are a `TransformMatrix = [[a,b,c],[d,e,f]]` type.

---

## @mathigon/boost — DOM, events, animations (MOST used)

### Selection & creation
```ts
import {$, $$, $N, ElementView, SVGView, SVGParentView, CanvasView, InputView} from '@mathigon/boost';

$('.btn')                    // first match → typed view (HTMLView/SVGView/etc by tag)
$$('.btn', $parent)          // all matches → array
$N('circle', {cx: 50, r: 20, class: 'dot'}, $svg)  // create + append
$N('g', {}, $svg)            // returns ElementView (cast to SVGView for svg nodes)
$N('x-gesture', {}, $step) as Gesture   // create a custom element instance
$body / $html                // pre-wrapped document.body / documentElement
```

### ElementView (the type $step and all $ results share) — key methods
```ts
// classes
$el.addClass('c') / .removeClass('c') / .toggleClass('c') / .setClass('c', cond) / .hasClass('c')
// content
$el.html / .text  (get|set)        $el.textStr = val
// attributes
$el.attr('cx')                      // getter
$el.setAttr('cy', y) / .removeAttr('x') / .attributes
$el.data.type                       // data-* attrs camelCased (data-type → .data.type)
// css / transform
$el.css('top', '10px') / .css({...})
$el.transform / .transformMatrix / .scale
$el.translate(x, y) / .setTransform(posn?, angle=0, scale=1)
// visibility
$el.show() / .hide() / .toggle(show?)
// tree
$el.children / .next / .prev / .parent / .parents('x-step') / .id / .index()
$el.append($c) / .prepend($c) / .insertBefore($x) / .insertAfter($x)
$el.copy() / .detach() / .remove() / .removeChildren()
// dimensions
$el.bounds / .boundsRect / .boxCenter / .width / .height / .isInViewport
// events
$el.on('click pointerdown', fn) / .one('play', fn) / .off('click', fn) / .trigger('x')
$el.onKey('ArrowUp', fn) / .onKey('AllArrows', fn, {up: true})
```

### SVGView specifics (for `<path>`, `<circle>`, etc.)
```ts
$path.setLine(p1, p2)               // set x1/y1/x2/y2 or d
$circle.setCenter(point)
$rect.setRect(rectangleEuclid)
$path.points = [...]                // parse/build the `d` attribute
$path.getPointAt(t)                 // t ∈ [0,1]
$path.strokeLength
$svg.drawPath(euclidShape, attrs?)  // SVGParentView: create <path> child from a euclid shape
$path.draw(euclidShape, options?)   // render a euclid shape to this path's d
```

### Animations
```ts
import {animate, ease, transition, enter, exit} from '@mathigon/boost';

const anim = animate((p, dt) => {...}, durationMs);   // p ∈ [0,1]; dt ms since last frame
await anim.promise;  anim.cancel();
// without duration: callback receives ms-since-start instead of p

ease('sine-out', p)                  // easing; types below
ease('exp-out', p)
// types: quad cubic quart quint circ sine exp back elastic swing spring bounce
//        + -in / -out suffix (e.g. 'cubic-in-out')

$el.enter('pop', 500, 100)           // effect, duration, delay → {promise}
$el.exit('fade', 500)
$el.effect('pulse-down')
$el.animate({transform: ['scale(1)','scale(.4)']}, 600)   // [from,to]
$el.animate({fill: GREEN}, 600)
// enter/exit effects: fade pop descend ascend draw draw-reverse slide slide-down/up reveal reveal-left/right
```

### Gestures & events
```ts
import {slide, hover, pointerOver, pointerPosition, svgPointerPosn, Draggable} from '@mathigon/boost';

slide($el, {
  down(p) {}, start(p) {}, move(p, start, last) {}, end(last, start) {}, click(p) {},
  accessible: true   // keyboard support
});

hover($el, {enter() {}, exit() {}, delay: 0, exitDelay: 0});

new Draggable($el, {$parent, $targets, useTransform, resetOnMiss, withinBounds, snap, margin, bounds})
// events: start, move {posn}, end {$target?}, click, enter-target {$target}, exit-target {$target}
// methods: setPosition(x,y), resetPosition(duration=250), addTarget, .position, .disabled
```

### Observable models (the `$step.model` engine)
```ts
import {observe, batch} from '@mathigon/boost';
// $step.model is already an Observable. Patterns:
$step.model.x = 5;                          // write → template updates
$step.model.watch(() => {...});             // auto-tracks accessed props, re-runs on their change
$step.model.assign({a, b});
$step.model.myFn = (x) => x + 1;            // expose to templates
```

### Browser utilities
```ts
import {Browser} from '@mathigon/boost';
Browser.isMobile / .isTouch / .isChrome / .width / .height / .theme / .localStorage
Browser.ready(fn) / .onResize(fn) / .redraw()
import {loadScript, loadImage} from '@mathigon/boost';
import {post} from '@mathigon/boost';       // form-encoded POST with CSRF header
```

### Web components
```ts
import {CustomElementView, register} from '@mathigon/boost';

@register('x-foo', {template: '<div><slot></slot></div>'})
export class Foo extends CustomElementView {
  created() {}   // on instantiation
  ready() {}     // after children ready
}
// Note: old @CustomElement('x-foo') decorator is deprecated — use @register.
```

---

## @mathigon/euclid — 2D geometry (heavily used)

```ts
import {Point, Line, Ray, Segment, Circle, Arc, Sector, Angle, Polygon, Polyline, Triangle, Rectangle, Ellipse, Bounds, TransformMatrix, intersections, ORIGIN, TWO_PI, rad, toDeg, toRad} from '@mathigon/euclid';
```

### Point (most used)
```ts
new Point(x, y)
p.length / .unitVector / .array
p.add(q) / .subtract(q) / .scale(s) / .shift(x, y) / .translate(q)   // q = Point
p.rotate(angle, c=ORIGIN) / .reflect(line) / .transform(matrix)
p.angle(c=ORIGIN) / .distance(q)  / .equals(q)
p.round(inc=1) / .clamp(bounds) / .changeCoordinates(from, to)
Point.distance(a, b) / .interpolate(a, b, t=0.5) / .interpolateList(points, t)
Point.fromPolar(angle, r=1) / .average(...ps) / .dot(a, b) / .random(bounds)
ORIGIN  // = new Point(0,0)
```

### Lines
```ts
new Line(p1, p2)        // infinite
new Ray(p1, p2)         // half-line
new Segment(p1, p2)     // finite — adds .contract(ratio), bounded project/contains
l.length / .midpoint / .slope / .angle / .perpendicularVector
l.parallel(p) / .perpendicular(p) / .perpendicularBisector / .project(p)
```

### Circle / Arc / Sector / Angle
```ts
new Circle(c=ORIGIN, r=1)
c.circumference / .area / .arc / .tangentAt(t) / .project(p) / .at(t) / .contains(p)

new Arc(c, start, angle)        a.circle / .radius / .end / .startAngle / .minor / .major / .contract(p)
new Sector(...)                 pie slice; extends Arc

new Angle(a, b, c)              // angle at vertex b between rays to a and c
a.rad / .deg / .isRight / .bisector / .sup / .arc
a.shape(filled=true, radius?, round?)   // → drawable Sector/Arc/Polygon
Angle.fromDegrees(v) / .fromRadians(v) / .equals(a,b)

toDeg(rad) / toRad(deg)
```

### Polygon family
```ts
new Polygon(...points)          .points / .circumference / .area / .centroid / .edges / .radius
  .contains(p) / .centerAt(o) / .interpolate
  Polygon.regular(n, r=1) / .convexHull(...points) / .collision(p1,p2)
new Polyline(...)               // open chain; .length
new Triangle(...)               // adds .circumcircle / .incircle / .orthocenter
```

### Rectangle / Ellipse / Bounds
```ts
new Rectangle(p, w=1, h=w)      .polygon / .center / .edges / .contains / .collision / .aroundPoints(points)
new Ellipse(c, a, b, angle=0)   .f1 / .f2 / .intersect(line) / .fromFoci(f1,f2,stringLength)
new Bounds(xMin, xMax, yMin, yMax)   .contains(p) / .resize / .extend
```

### Intersections & transforms
```ts
intersections(...elements)      // → Point[] among any lines/rays/segments/circles/arcs
TransformMatrix = [[a,b,c],[d,e,f]]   // 2×3 affine; pass to shape.transform(m)
```

### Drawing helpers
```ts
import {drawSVG, drawCanvas} from '@mathigon/euclid';
drawSVG(euclidShape, {arrows, mark, round, size, fill, box, cornerRadius})  // → SVG path d string
// $svg.drawPath(shape, attrs) and $path.draw(shape) from boost use these internally
```

---

## @mathigon/core — utilities

```ts
import {Obj, isOneOf, run, wait, delay, cache, throttle, uid, safeToJSON,
        list, tabulate, tabulate2D, last, total, repeat, repeat2D, flatten, unique, sortBy, chunk, cumulative, rotate, intersect, difference, loop,
        toCamelCase, toTitleCase, words, stringDistance,
        EventTarget, Color, Cache} from '@mathigon/core';
```

Most-used:
```ts
list(5)              // [0,1,2,3,4]   (list(2,5) → [2,3,4,5])
list(10, 0, -2)      // [10,8,6,4,2]
tabulate(fn, n)      // [fn(0),...,fn(n-1)]
tabulate2D(fn, w, h) // 2D array
last(arr, i=0)       // nth-from-end
total(arr)           // sum
wait(ms)             // → Promise<void>
delay(fn, ms=0)      // setTimeout (sync when 0)
cache(fn)            // memoise by args.join('--')
Color.rainbow(n) / .mix(a,b,p) / .gradient(colors, n) / .shades(c, n)
toCamelCase('my-step-2')  // 'myStep2'  ← this is what links content.md ids to functions.ts
words(str)           // trim + split on whitespace (used for space-separated class/event lists)
```

---

## @mathigon/fermat — math & statistics

```ts
import {clamp, lerp, round, roundTo, numberFormat, toWord, toOrdinal, parseNumber,
        nearlyEquals, isBetween, sign, mod, gcd, lcm, isPrime, primeFactorisation, goldbach,
        factorial, binomial, permutations, subsets,
        Vector, Complex, XNumber,
        Matrix, Random, Regression, statistics} from '@mathigon/fermat';
```

### Arithmetic (most used)
```ts
clamp(x, min, max)              lerp(a, b, t=0.5)
round(n, precision=0)           roundTo(n, increment=1)
numberFormat(n, places=0)       // thousand separators + k/m/b suffix
toWord(n)                       // spell out in English
toOrdinal(n)                    // 1st, 2nd...
nearlyEquals(a, b, t=1e-6)      isBetween(v, a, b)
```

### Random (namespace) — for stochastic interactives
```ts
Random.integer(a, b?)           // int in [a,b) or [0,a)
Random.shuffle(arr)
Random.find(arr)                // random element
Random.weighted(weights)        // index sampled by weights
Random.smart(n, id)             // avoids immediate repeats
// distributions: Random.uniform(a=0,b=1), .normal(m=0,v=1), .exponential(rate), .bernoulli, .binomial, .poisson, ...
```

### Number theory / combinatorics
```ts
gcd(...ns) / lcm(...ns)         isPrime(n) / primeFactorisation(n) / listPrimes(100) / goldbach(x)
factorial(n) / binomial(n, k)   permutations(arr) / subsets(arr, length=0)
```

### Linear algebra
```ts
new Vector(...nums)             // extends Array; .magnitude / .unitVector / .scale(q)
Vector.dot(a,b) / .cross(a,b)   // cross is 3D only
Matrix.identity(n) / .product / .transpose / .determinant / .inverse / .rotation(angle)
```

### Regression (namespace)
```ts
Regression.linear(data, throughOrigin=false)   // → [intercept, gradient]
Regression.polynomial(data, order=2)           // → coefficients[]
Regression.bestPolynomial(data, threshold=0.85, maxOrder=8)
```

### XNumber (fractions + units)
```ts
new XNumber(...) / XNumber.fromString('3π') / XNumber.fromString('1/2')
// supports fractions (num/den) and units (%, π); used by equation checking
```

---

## @mathigon/hilbert — expression parsing (rarely needed directly)

```ts
import {Expression, ExprElement} from '@mathigon/hilbert';

const expr = Expression.parse('3^n');
Expression.numEquals(expr1, expr2)   // numeric equality (samples random values, not a CAS)

// on a parsed expr:
expr.evaluate(vars?)    // → number  (vars = {name: number | Interval | fn})
expr.substitute(vars?)
expr.variables          // string[] of free variable names
expr.functions          // string[] of function names called
expr.toString() / .toMathML()

// ExprElement is the abstract AST base; subclasses ExprNumber, ExprIdentifier, ExprOperator, ExprFunction, ExprString
```

Use case: custom validation in `x-equation`/`x-equation-system` `.validate` callbacks (see functions-model.md).

---

## @mathigon/studio — course framework

```ts
import {Step, Slideshow, Select, Slider, PlayBtn, PlayToggle, Tabbox, Gesture, Draggable, confetti} from '@mathigon/studio';
```

- **`Step`** — the step element view; full API in functions-model.md.
- **`Slideshow`** — events `next`/`back`/`step` with index.
- **`Select`** — `on('change', ($el)=>...)`, `$active`, `$select.$active.data.<x>`.
- **`Slider`** — `set(x)`, `moveTo(x,dur)`, `current`, `steps`, event `move`.
- **`PlayBtn`** — `on('play', cb)`, `reset()`.
- **`Tabbox`** — `makeActive(i)`.
- **`Gesture`** — `setTarget($el, slide?, shift?)`, `start()`, `stop()`, `startSlide($from, $to)`.
- **`Draggable`** — re-exported from boost; see boost section.
- **`confetti()`** — celebration animation; guard with `if ($step.isPageLoaded) confetti();`.

The `Step` lifecycle code (`frontend/components/step/step.ts`):
```ts
show() {
  // ... fires the matching function the first time the step is revealed:
  StepFunctions?.[toCamelCase(this.id)]?.(this);
}
```
This is the mechanism that connects `> id: my-step` in content.md to `export function myStep($step)` in functions.ts.
