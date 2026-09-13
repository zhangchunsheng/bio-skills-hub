#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: LKP <kunpeng.liao@abiosciences.com>
# Date:   2026-08-18
"""
Cellbin 坐标辅助工具集（合并自原 extract_cellbin_coords / read_cellbin_coordinates / fix_cellbin_matching）

提供 3 个子命令：
  extract    从 cell_segmentations.geojson 提取细胞中心坐标 → cellbin_coordinates.csv
  match      将反卷积结果（cell_id 形如 cellid_000006565-1）与坐标 CSV 合并 → cellbin_merged.csv

Usage:
    python extract_cellbin_coords.py extract --geojson <path> --output <path>
    python extract_cellbin_coords.py match --results <deconvolution_csv> --coords <coords_csv> --output <path>
"""

import argparse
import json
import os
import re
import sys

import numpy as np
import pandas as pd


# ========== 配置区域（请根据实际数据修改） ==========
USER_DATA_DIR      = "your/data/directory"          # TODO: 修改为你的数据根目录
SEGMENTED_SUBDIR   = "segmented_outputs"             # Visium HD segmented_outputs 子目录名
GEOJSON_FILENAME   = "cell_segmentations.geojson"
OUTPUT_DIR         = "."                            # 输出目录（默认当前）
# =====================================================


def cmd_extract(args):
    """从 geojson 提取细胞中心坐标"""
    geojson_path = args.geojson or os.path.join(USER_DATA_DIR, SEGMENTED_SUBDIR, GEOJSON_FILENAME)
    output_path  = args.output or os.path.join(OUTPUT_DIR, "cellbin_coordinates.csv")

    if not os.path.exists(geojson_path):
        print(f"❌ 找不到 geojson 文件: {geojson_path}")
        sys.exit(1)

    print("=== 提取 Cellbin 坐标 ===\n")
    with open(geojson_path, "r") as f:
        data = json.load(f)

    print(f"GeoJSON 类型: {data['type']}")
    print(f"Features 数量: {len(data['features'])}")

    # 兼容两种 cell_id 字段：cell_id 或 id
    cell_coords = []
    for i, feature in enumerate(data["features"]):
        props = feature["properties"]
        cell_id = props.get("cell_id", props.get("id"))
        coords = feature["geometry"]["coordinates"][0]  # 第一个环
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        cell_coords.append({
            "cell_id": cell_id,
            "x": float(np.mean(xs)),
            "y": float(np.mean(ys)),
        })
        if (i + 1) % 10000 == 0:
            print(f"  已处理 {i+1}/{len(data['features'])} 个细胞...")

    coords_df = pd.DataFrame(cell_coords)
    coords_df.to_csv(output_path, index=False)

    print(f"\n✓ 细胞坐标提取完成: {len(coords_df)} 个")
    print(f"  X 范围: {coords_df['x'].min():.2f} - {coords_df['x'].max():.2f}")
    print(f"  Y 范围: {coords_df['y'].min():.2f} - {coords_df['y'].max():.2f}")
    print(f"✓ 已保存到: {output_path}")
    print("\n前 5 个:")
    print(coords_df.head())


def cmd_match(args):
    """合并反卷积结果与真实坐标"""
    results_path = args.results
    coords_path  = args.coords
    output_path  = args.output or os.path.join(OUTPUT_DIR, "cellbin_merged.csv")

    if not os.path.exists(results_path):
        print(f"❌ 找不到反卷积结果: {results_path}")
        sys.exit(1)
    if not os.path.exists(coords_path):
        print(f"❌ 找不到坐标 CSV: {coords_path}")
        sys.exit(1)

    print("=== 合并 Cellbin 反卷积结果与坐标 ===\n")
    rctd_df  = pd.read_csv(results_path)
    coords_df = pd.read_csv(coords_path)

    print(f"反卷积结果行数: {len(rctd_df)}")
    print(f"坐标 CSV 行数: {len(coords_df)}")

    # 自动检测 cell_id 列
    cell_id_col_results = "cell_id" if "cell_id" in rctd_df.columns else rctd_df.columns[0]
    cell_id_col_coords  = "cell_id" if "cell_id" in coords_df.columns else coords_df.columns[0]
    print(f"结果 cell_id 列: {cell_id_col_results}")
    print(f"坐标 cell_id 列: {cell_id_col_coords}")

    # 从 cell_id 提取数字（兼容 cellid_000006565-1 格式）
    def extract_num(s):
        m = re.search(r"(\d+)", str(s))
        return int(m.group(1)) if m else None

    rctd_df["_cell_num"] = rctd_df[cell_id_col_results].apply(extract_num)
    coords_df["_cell_num"] = coords_df[cell_id_col_coords].apply(extract_num)

    merged_df = pd.merge(coords_df, rctd_df, on="_cell_num", how="inner", suffixes=("_coord", "_result"))
    merged_df = merged_df.drop(columns=["_cell_num"])

    merged_df.to_csv(output_path, index=False)
    print(f"\n✓ 合并完成: {len(merged_df)} 行")
    print(f"✓ 已保存到: {output_path}")
    print(f"\n列名: {merged_df.columns.tolist()}")


def main():
    parser = argparse.ArgumentParser(description="Cellbin 坐标辅助工具")
    sub = parser.add_subparsers(dest="command", required=True)

    # extract 子命令
    p_ext = sub.add_parser("extract", help="从 geojson 提取细胞坐标")
    p_ext.add_argument("--geojson", help="geojson 文件路径（默认: USER_DATA_DIR/SEGMENTED_SUBDIR/cell_segmentations.geojson）")
    p_ext.add_argument("--output",  help="输出 CSV 路径")
    p_ext.set_defaults(func=cmd_extract)

    # match 子命令
    p_mat = sub.add_parser("match", help="合并反卷积结果与坐标")
    p_mat.add_argument("--results", required=True, help="反卷积结果 CSV")
    p_mat.add_argument("--coords",  required=True, help="坐标 CSV")
    p_mat.add_argument("--output",  help="输出合并 CSV 路径")
    p_mat.set_defaults(func=cmd_match)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
