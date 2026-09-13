---
name: hex-matrix-background
description: >
  React canvas-based interactive hex digit matrix background with mouse ripple effects.
  This skill should be used when the user wants to add a tech-style animated background
  to a React website, featuring a grid of morphing hexadecimal characters with cursor
  interaction that creates wave/ripple distortion effects. Trigger phrases include:
  "tech background", "matrix background", "hex background", "interactive background",
  "ripple effect background", "数字背景", "科技背景", "矩阵背景", "涟漪背景".
agent_created: true
---

# Hex Matrix Interactive Background

A React canvas component that renders a grid of hexadecimal characters with:
- Fixed-position characters that morph/transform digits in place (not falling)
- Six-color palette (cyan, magenta, gold, green, purple, orange)
- Mouse/touch ripple interaction — characters near cursor are pushed outward and glow
- Progressive decay for natural fluid movement

## When to Use

Use this whenever a user asks for a tech/sci-fi interactive background for a React website. The component is self-contained and requires no external dependencies beyond React itself.

## Usage

Copy `assets/HexBackground.jsx` into the React project's component directory, then import and render:

```jsx
import HexBackground from './components/HexBackground';

// Place as first child of root layout, before any content
<div style={{ position: 'relative', minHeight: '100vh' }}>
  <HexBackground />
  {/* ... rest of the app ... */}
</div>
```

The canvas is fixed-position, covers the full viewport, has `z-index: 0`, and `pointer-events: none` so all click interactions pass through to content below.

## Customization

Edit the constants at the top of the component:
- `CELL: 44` — grid cell size in pixels
- `RIPPLE_RADIUS: 200` — mouse interaction radius
- `HEX_CHARS` — character set to display
- `COLORS` — color palette
