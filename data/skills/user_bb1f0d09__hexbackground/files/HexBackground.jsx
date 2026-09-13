import { useRef, useEffect, useCallback } from 'react';

// 黑客风格字符集：十六进制 + 片假名 + 特殊符号
const CHARS = '0123456789ABCDEFｦｧｨｩｪｫｬｭｮｯｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ<>/[]{}|\\:;*+-=';
const MATRIX_GREEN = 'rgba(0,255,65,';
const MATRIX_CYAN = 'rgba(0,220,255,';
const MATRIX_DIM = 'rgba(0,160,40,';
const MATRIX_WHITE = 'rgba(180,255,200,';
const CELL = 22;           // 紧凑网格间距
const FONT_SIZE = 13;      // 统一字号
const RIPPLE_RADIUS = 160;

/**
 * 单个字符格子 — 黑客矩阵风格
 * 固定网格位置 + 独立变换节奏 + 列联动脉冲
 */
class MatrixCell {
  constructor(ix, iy, colIndex, totalCols) {
    this.ix = ix;
    this.iy = iy;
    this.colIndex = colIndex;
    this.baseX = ix * CELL + CELL / 2;
    this.baseY = iy * CELL + CELL / 2;
    this.x = this.baseX;
    this.y = this.baseY;

    // 基础属性
    this.char = CHARS[Math.floor(Math.random() * CHARS.length)];
    this.baseAlpha = 0.04 + Math.random() * 0.08;      // 基础暗色
    this.columnPhase = (colIndex / totalCols) * Math.PI * 2;  // 列相位差

    // 变换计时
    this.changeInterval = 40 + Math.random() * 120;    // 快速变换
    this.changeTimer = Math.random() * this.changeInterval;

    // 脉冲状态
    this.pulseStrength = 0;
    this.pulseTimer = 0;

    // 涟漪
    this.currentGlow = 0;
  }

  update(dt, mouseX, mouseY, rippleRef, globalTime) {
    const dt16 = dt / 16;

    // === 列级波浪脉冲 ===
    // 每列根据全局时间产生周期性明暗波
    const wave = Math.sin(globalTime * 0.001 + this.columnPhase) * 0.5 + 0.5;
    const waveBoost = wave * 0.15;

    // === 随机字符变换 ===
    this.changeTimer -= dt;
    if (this.changeTimer <= 0) {
      this.char = CHARS[Math.floor(Math.random() * CHARS.length)];
      this.changeInterval = 30 + Math.random() * 150;
      this.changeTimer = this.changeInterval;
    }

    // === 随机脉冲：某些列偶尔整体亮起 ===
    this.pulseTimer -= dt;
    if (this.pulseTimer <= 0) {
      // 新脉冲：概率随 wave 增加
      if (Math.random() < wave * 0.04) {
        this.pulseStrength = 0.3 + Math.random() * 0.6;
        this.pulseTimer = 300 + Math.random() * 400;
      } else {
        this.pulseStrength *= 0.85;
        this.pulseTimer = 100 + Math.random() * 300;
      }
    }

    // === 涟漪位移 ===
    const dx = this.baseX - mouseX;
    const dy = this.baseY - mouseY;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < RIPPLE_RADIUS && rippleRef.strength > 0.01) {
      const force = (1 - dist / RIPPLE_RADIUS) * rippleRef.strength * 24;
      const angle = Math.atan2(dy, dx);
      const targetX = this.baseX + Math.cos(angle) * force;
      const targetY = this.baseY + Math.sin(angle) * force;

      this.x += (targetX - this.x) * 0.35 * dt16;
      this.y += (targetY - this.y) * 0.35 * dt16;

      const glow = (1 - dist / RIPPLE_RADIUS) * rippleRef.strength * 0.5;
      this.currentGlow = Math.max(this.currentGlow, glow);
    } else {
      this.x += (this.baseX - this.x) * 0.06 * dt16;
      this.y += (this.baseY - this.y) * 0.06 * dt16;
      this.currentGlow = Math.max(0, this.currentGlow - 0.015 * dt16);
    }

    // 最终合并不透明度
    this.finalAlpha = Math.min(0.7,
      this.baseAlpha + waveBoost + this.pulseStrength + this.currentGlow
    );

    // 根据亮度选择颜色
    if (this.finalAlpha > 0.4) {
      this.finalColor = MATRIX_WHITE;
    } else if (this.finalAlpha > 0.2) {
      this.finalColor = MATRIX_CYAN;
    } else if (this.finalAlpha > 0.1) {
      this.finalColor = MATRIX_GREEN;
    } else {
      this.finalColor = MATRIX_DIM;
    }
  }

  draw(ctx) {
    ctx.save();
    ctx.globalAlpha = this.finalAlpha;
    ctx.font = `${FONT_SIZE}px "Consolas", "Courier New", monospace`;
    ctx.fillStyle = this.finalColor + '1)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.char, this.x, this.y);

    // 高亮字符加发光
    if (this.finalAlpha > 0.3) {
      ctx.shadowColor = '#00FF41';
      ctx.shadowBlur = 4 + this.finalAlpha * 8;
      ctx.fillText(this.char, this.x, this.y);
    }
    ctx.restore();
  }
}

/**
 * 扫描线 — 周期性水平扫过屏幕
 */
class ScanLine {
  constructor(canvasH) {
    this.y = -100;
    this.speed = 0.03 + Math.random() * 0.08; // px/ms
    this.alpha = 0;
    this.maxAlpha = 0.06 + Math.random() * 0.04;
    this.canvasH = canvasH;
    this.phase = Math.random() * Math.PI * 2;
  }

  update(dt, globalTime) {
    this.y += this.speed * dt;
    if (this.y > this.canvasH + 100) {
      this.y = -100;
      this.speed = 0.03 + Math.random() * 0.08;
    }
    // 扫描线的 alpha 在中间最亮
    const normalized = this.y / this.canvasH;
    const pulse = Math.sin(globalTime * 0.002 + this.phase) * 0.5 + 0.5;
    this.alpha = this.maxAlpha * (1 - Math.abs(normalized * 2 - 1)) * 0.5 * (0.5 + pulse * 0.5);
  }

  draw(ctx, canvasW) {
    if (this.alpha < 0.005) return;
    ctx.save();
    ctx.globalAlpha = this.alpha;
    ctx.fillStyle = '#00FF41';
    ctx.fillRect(0, this.y, canvasW, 1);
    // 扫描线上下轻微渐变
    const grad = ctx.createLinearGradient(0, this.y - 8, 0, this.y + 8);
    grad.addColorStop(0, 'transparent');
    grad.addColorStop(0.5, 'rgba(0,255,65,0.03)');
    grad.addColorStop(1, 'transparent');
    ctx.fillStyle = grad;
    ctx.fillRect(0, this.y - 8, canvasW, 16);
    ctx.restore();
  }
}

export default function HexBackground() {
  const canvasRef = useRef(null);
  const cellsRef = useRef([]);
  const scanLinesRef = useRef([]);
  const animationIdRef = useRef(null);
  const resizeObserverRef = useRef(null);
  const mouseRef = useRef({ x: -500, y: -500 });
  const prevMouseRef = useRef({ x: -500, y: -500 });
  const rippleRef = useRef({ strength: 0 });
  const lastTimeRef = useRef(0);
  const globalTimeRef = useRef(0);

  const initGrid = useCallback((w, h) => {
    const cols = Math.ceil(w / CELL) + 1;
    const rows = Math.ceil(h / CELL) + 1;
    const cells = [];
    for (let ix = 0; ix < cols; ix++) {
      for (let iy = 0; iy < rows; iy++) {
        cells.push(new MatrixCell(ix, iy, ix, cols));
      }
    }
    cellsRef.current = cells;

    // 扫描线：3-5条
    const scanCount = 3 + Math.floor(Math.random() * 3);
    const lines = [];
    for (let i = 0; i < scanCount; i++) {
      lines.push(new ScanLine(h));
    }
    scanLinesRef.current = lines;
  }, []);

  const animate = useCallback((timestamp) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dt = lastTimeRef.current ? timestamp - lastTimeRef.current : 16;
    lastTimeRef.current = timestamp;
    globalTimeRef.current = timestamp;

    // 涟漪衰减
    rippleRef.current.strength *= 0.93;
    if (rippleRef.current.strength < 0.001) rippleRef.current.strength = 0;

    // 鼠标速度 → 涟漪
    const dx = mouseRef.current.x - prevMouseRef.current.x;
    const dy = mouseRef.current.y - prevMouseRef.current.y;
    const speed = Math.sqrt(dx * dx + dy * dy);
    if (speed > 2) {
      rippleRef.current.strength = Math.min(1, rippleRef.current.strength + speed * 0.01);
    }
    prevMouseRef.current.x = mouseRef.current.x;
    prevMouseRef.current.y = mouseRef.current.y;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 绘制扫描线（在字符下面）
    for (const line of scanLinesRef.current) {
      line.update(dt, globalTimeRef.current);
      line.draw(ctx, canvas.width);
    }

    // 绘制字符网格
    const mx = mouseRef.current.x;
    const my = mouseRef.current.y;
    const ripple = rippleRef.current;
    const gt = globalTimeRef.current;

    for (const cell of cellsRef.current) {
      cell.update(dt, mx, my, ripple, gt);
      cell.draw(ctx);
    }

    animationIdRef.current = requestAnimationFrame(animate);
  }, []);

  useEffect(() => {
    const handleMouse = (e) => {
      mouseRef.current.x = e.clientX;
      mouseRef.current.y = e.clientY;
    };

    window.addEventListener('mousemove', handleMouse, { passive: true });
    window.addEventListener('touchmove', (e) => {
      const t = e.touches[0];
      if (t) { mouseRef.current.x = t.clientX; mouseRef.current.y = t.clientY; }
    }, { passive: true });

    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initGrid(canvas.width, canvas.height);
    };

    handleResize();
    resizeObserverRef.current = new ResizeObserver(handleResize);
    resizeObserverRef.current.observe(document.body);
    animationIdRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('mousemove', handleMouse);
      if (animationIdRef.current) cancelAnimationFrame(animationIdRef.current);
      if (resizeObserverRef.current) resizeObserverRef.current.disconnect();
    };
  }, [initGrid, animate]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed', top: 0, left: 0,
        width: '100%', height: '100%',
        zIndex: 0, pointerEvents: 'none',
      }}
      aria-hidden="true"
    />
  );
}
