#!/usr/bin/env python3
"""Generate replacement 3D text in Blender and match reference model bounds."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def script_args() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects if obj.type == "MESH" for corner in obj.bound_box]
    if not points:
        raise RuntimeError("No mesh bounds available")
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return minimum, maximum


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_reference(path: Path) -> tuple[Vector, Vector]:
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    result = bounds(imported)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in imported:
        obj.select_set(True)
    bpy.ops.object.delete(use_global=False)
    return result


def center_object(obj: bpy.types.Object) -> None:
    minimum, maximum = bounds([obj])
    center = (minimum + maximum) * 0.5
    obj.location -= center
    bpy.context.view_layer.update()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--extrude", type=float, default=0.18)
    parser.add_argument("--bevel", type=float, default=0.08)
    parser.add_argument("--bevel-resolution", type=int, default=5)
    parser.add_argument("--size", type=float, default=2.0)
    parser.add_argument("--name", default="GCW_Text")
    args = parser.parse_args(script_args())

    if args.reference and not args.reference.exists():
        parser.error(f"reference not found: {args.reference}")
    if args.font and not args.font.exists():
        parser.error(f"font not found: {args.font}")
    if args.output.suffix.lower() not in {".glb", ".gltf"}:
        parser.error("--output must end with .glb or .gltf")
    if args.reference and args.reference.resolve() == args.output.resolve():
        parser.error("--output must not overwrite --reference")

    clear_scene()
    reference_bounds = import_reference(args.reference.resolve()) if args.reference else None

    bpy.ops.object.text_add(location=(0, 0, 0))
    text_obj = bpy.context.object
    text_obj.name = args.name
    curve = text_obj.data
    curve.body = args.text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = args.size
    curve.extrude = args.extrude
    curve.bevel_depth = args.bevel
    curve.bevel_resolution = args.bevel_resolution
    curve.fill_mode = "BOTH"
    if args.font:
        curve.font = bpy.data.fonts.load(str(args.font.resolve()))

    bpy.context.view_layer.objects.active = text_obj
    text_obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    mesh_obj = bpy.context.object
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    center_object(mesh_obj)

    scale_factor = 1.0
    if reference_bounds:
        reference_size = reference_bounds[1] - reference_bounds[0]
        current_bounds = bounds([mesh_obj])
        current_size = current_bounds[1] - current_bounds[0]
        reference_max = max(reference_size)
        current_max = max(current_size)
        if current_max <= 0:
            raise RuntimeError("Generated text has zero-size bounds")
        scale_factor = reference_max / current_max
        mesh_obj.scale = (scale_factor, scale_factor, scale_factor)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        center_object(mesh_obj)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj
    export_format = "GLB" if args.output.suffix.lower() == ".glb" else "GLTF_SEPARATE"
    bpy.ops.export_scene.gltf(
        filepath=str(args.output.resolve()),
        export_format=export_format,
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )

    final_min, final_max = bounds([mesh_obj])
    result = {
        "output": str(args.output.resolve()),
        "format": export_format,
        "text": args.text,
        "font": str(args.font.resolve()) if args.font else "Blender Bfont",
        "reference": str(args.reference.resolve()) if args.reference else None,
        "scaleFactor": scale_factor,
        "bounds": {"min": list(final_min), "max": list(final_max)},
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
