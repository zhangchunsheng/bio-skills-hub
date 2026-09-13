#!/usr/bin/env python3
"""
watermark.py — 清除 ImageGen 生成图右下角的「AI生成」水印。

原理：取水印区正上方一块同色调区块，粘贴覆盖水印区。
      ImageGen 16:9 输出实际尺寸为 1920x1072（非 1080），坐标按实际尺寸计算。

版本历史：
  v1  基础版：直接复制上方区块覆盖。
  v2  加入边缘羽化 + 可调参数，减轻可见接缝。

用法：
  python watermark.py <input.png> [output.png]
  python watermark.py <input.png> --rw 240 --rh 80 --offset 90 --feather 8
  若不指定 output，则覆盖写回 input（原地修改）。

运行环境：
  本脚本依赖 Pillow + numpy。请使用**本机已安装这两个依赖的 Python 解释器**
  （Windows 上通常是单独安装的 Python，而非应用内置运行时）。
  若报 ModuleNotFoundError，说明当前解释器缺依赖，换一个解释器或先安装依赖。
  实测：1920x1072 输入，水印区像素 (60,60,60) → 修补后 (210,190,170)，清除成功。

⚠️ 已知局限（2026-09-10 实测发现）：
  当水印落在**复杂图案区**（如花纹台面、纹理墙纸、密集陈列区）时，复制粘贴会留下
  **可见的纹理接缝**——羽化只能减轻，无法消除。此时可选：
    1. 调大 --offset，让采样块取自更同质的区域；
    2. 调大 --feather（6~12），使过渡更柔和；
    3. 若仍留痕，改用 ImageGen 对水印区做局部重绘，或直接裁掉底部若干像素。
  水印落在纯色 / 渐变 / 低频背景时，本脚本效果良好。
"""
import argparse
import sys

import numpy as np
from PIL import Image, ImageFilter

DEFAULT_RW, DEFAULT_RH = 220, 70   # 水印区宽高
DEFAULT_Y_OFFSET = 80              # 取样区相对水印区上移量
DEFAULT_FEATHER = 8                # 边缘羽化像素（仅羽化非图像边界的边）


def _feather_mask(w: int, h: int, f: int,
                  top: bool = True, left: bool = True,
                  bottom: bool = False, right: bool = False) -> Image.Image:
    """构造羽化遮罩：仅对指定的边做 0→255 渐变，其余边保持 255。"""
    m = np.full((h, w), 255, dtype=np.uint8)
    f = max(0, min(f, w // 2, h // 2))
    if f > 0:
        ramp = np.linspace(0, 255, f).astype(np.uint8)
        if top:
            m[:f, :] = np.minimum(m[:f, :], ramp[:, None])
        if bottom:
            m[-f:, :] = np.minimum(m[-f:, :], ramp[::-1][:, None])
        if left:
            m[:, :f] = np.minimum(m[:, :f], ramp[None, :])
        if right:
            m[:, -f:] = np.minimum(m[:, -f:], ramp[::-1][None, :])
    mask = Image.fromarray(m, "L")
    return mask.filter(ImageFilter.GaussianBlur(1.2)) if f > 0 else mask


def remove_watermark(src: str, dst: str | None = None,
                     rw: int = DEFAULT_RW, rh: int = DEFAULT_RH,
                     y_offset: int = DEFAULT_Y_OFFSET,
                     feather: int = DEFAULT_FEATHER) -> str:
    if dst is None:
        dst = src
    im = Image.open(src).convert("RGB")
    w, h = im.size
    # 水印区：右下角
    # 取样区：水印区正上方
    sample = (w - rw, h - rh - y_offset, w, h - y_offset)
    patch = im.crop(sample)

    if feather > 0:
        # 水印位于右下角：仅羽化「上」「左」两条内侧边，右/下为图像边界无需羽化
        mask = _feather_mask(rw, rh, feather, top=True, left=True,
                             bottom=False, right=False)
        im.paste(patch, (w - rw, h - rh), mask)
    else:
        im.paste(patch, (w - rw, h - rh))

    im.save(dst)
    return dst


def main() -> int:
    ap = argparse.ArgumentParser(description="清除 ImageGen 右下角水印")
    ap.add_argument("input", help="输入图片路径")
    ap.add_argument("output", nargs="?", default=None,
                    help="输出路径（默认原地覆盖）")
    ap.add_argument("--rw", type=int, default=DEFAULT_RW,
                    help=f"水印区宽（默认 {DEFAULT_RW}）")
    ap.add_argument("--rh", type=int, default=DEFAULT_RH,
                    help=f"水印区高（默认 {DEFAULT_RH}）")
    ap.add_argument("--offset", type=int, default=DEFAULT_Y_OFFSET,
                    help=f"采样区上移量（默认 {DEFAULT_Y_OFFSET}）")
    ap.add_argument("--feather", type=int, default=DEFAULT_FEATHER,
                    help=f"边缘羽化像素，0 关闭（默认 {DEFAULT_FEATHER}）")
    args = ap.parse_args()

    result = remove_watermark(args.input, args.output,
                              rw=args.rw, rh=args.rh,
                              y_offset=args.offset, feather=args.feather)
    print(f"watermark removed -> {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
