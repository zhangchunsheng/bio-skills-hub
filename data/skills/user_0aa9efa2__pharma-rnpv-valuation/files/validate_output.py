#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
priced-in 输出校验脚本
=====================
校验 [ticker]_implied.json 是否符合 output_schema.json 契约。

用法:
    python validate_output.py <json_file> [--schema <schema.json>]

引擎:
    优先用 jsonschema 库(若已安装,完整 JSON Schema 语义校验);
    否则 fallback 到内置简化校验器(无外部依赖,覆盖 required/type/enum/
    minItems/maxItems/additionalProperties)。

语义检查(schema 外业务规则,返回 errors+warnings):
    - 半导体标的(asset_class=semiconductor 优先,fallback method 含"半导体")必填 baseline.s_curve [#1 v3]
    - 半导体 reality_anchor.cagr_range 须 = s_curve.adjusted_anchor(双锚一致性硬检查)
    - framework_migration 以"非迁移"开头 → warning(非迁移必须省略)[#5 v3]

退出码:
    0 = 校验通过
    1 = 校验失败(有错误)
    2 = 用法错误/文件找不到
"""
import json
import sys
import os

# 优先 jsonschema,无则用内置校验器
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 内置简化校验器(无依赖)
# ============================================================

def _type_ok(data, typ):
    """JSON Schema 类型检查(Python bool 是 int 子类,需排除)"""
    if typ == "object":
        return isinstance(data, dict)
    if typ == "array":
        return isinstance(data, list)
    if typ == "string":
        return isinstance(data, str)
    if typ == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if typ == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if typ == "boolean":
        return isinstance(data, bool)
    return True  # 未知类型不拦


def validate(data, schema, path="", errors=None):
    """递归校验 data 是否符合 schema(简化版,支持 type/required/properties/
    items/enum/minItems/maxItems/additionalProperties)。返回 errors 列表。"""
    if errors is None:
        errors = []
    if isinstance(schema, bool):
        return errors  # true/false schema 不校验

    here = path or "<root>"

    # type
    typ = schema.get("type")
    if typ and not _type_ok(data, typ):
        errors.append(f"{here}: 期望 {typ}, 实际 {type(data).__name__}")
        return errors  # 类型错则后续校验无意义

    # enum
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{here}: 值 {data!r} 不在 enum {schema['enum']} 中")

    # object
    if isinstance(data, dict):
        for req in schema.get("required", []):
            if req not in data:
                errors.append(f"{here}: 缺少必填字段 '{req}'")
        props = schema.get("properties", {})
        for k, v in data.items():
            child = f"{here}.{k}" if here != "<root>" else k
            if k in props:
                validate(v, props[k], child, errors)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{here}: 未定义字段 '{k}' (additionalProperties=false)")

    # array
    if isinstance(data, list):
        mn = schema.get("minItems")
        mx = schema.get("maxItems")
        if mn is not None and len(data) < mn:
            errors.append(f"{here}: 数组长度 {len(data)} < minItems {mn}")
        if mx is not None and len(data) > mx:
            errors.append(f"{here}: 数组长度 {len(data)} > maxItems {mx}")
        items = schema.get("items")
        if items:
            for i, item in enumerate(data):
                validate(item, items, f"{here}[{i}]", errors)

    return errors


# ============================================================
# 语义检查(schema 外业务规则)
# ============================================================

def _anchor_close(a, b, tol=1e-4):
    """两个 [low, high] 锚区间近似相等(容差对比)。
    v3 修订:原严格 list == 会因 4 位 round 误报双锚不一致(第 5 位差异即失败)。"""
    if a is None or b is None or len(a) != len(b):
        return a == b
    return all(abs(x - y) < tol for x, y in zip(a, b))


def semantic_checks(data):
    """schema 外的语义检查。返回 (errors, warnings)。

    errors(硬失败,退出码 1):
      - #1 半导体标的必须含 baseline.s_curve(Stage 4.5 强制);v3 修订
      - s_curve 双锚一致性 + conglomerate SOTP 加权校验
    warnings(打印,不失败):
      - #5 framework_migration 以"非迁移"开头(schema 要求非迁移必须省略);v3 修订
    """
    errors, warnings = [], []
    meta = data.get("metadata", {})
    baseline = data.get("baseline", {})

    # --- 行业判定:asset_class 优先(路由键),fallback method 子串(历史兼容)---
    asset_class = meta.get("asset_class")
    method = str(meta.get("method", ""))
    is_semi = (asset_class == "semiconductor" or
               (asset_class is None and ("半导体" in method or "semiconductor" in method.lower())))

    # #1: 半导体标的必须含 baseline.s_curve(Stage 4.5 强制)
    if is_semi and "s_curve" not in baseline:
        errors.append("半导体标的必须含 baseline.s_curve(Stage 4.5 强制;v3 修订 #1)")

    # #5: framework_migration 不应作"非迁移"记事本(schema:非迁移必须省略)
    fm = meta.get("framework_migration")
    if isinstance(fm, str) and "非迁移" in fm[:5]:
        warnings.append("framework_migration 以'非迁移'开头(schema 要求非迁移必须省略);v3 修订 #5")

    # #7: operation_signal.action 建议标准值(不阻断历史自由文本)
    action = data.get("operation_signal", {}).get("action", "")
    _std_actions = ("买入", "加仓", "持有", "减仓", "观察", "回避")
    if action and action not in _std_actions:
        warnings.append(f"operation_signal.action='{str(action)[:20]}' 不在标准值{_std_actions};v3 修订 #7")

    sc = baseline.get("s_curve")
    if sc is not None:
        ra = data.get("reality_anchor", {})
        segs = sc.get("segments")
        if segs:  # 非空数组,conglomerate SOTP
            # weight 规范
            total_w = sum(s.get("weight", 0) for s in segs)
            if total_w > 1.0001:
                errors.append(f"s_curve.segments: weight和={total_w:.4f}>1 (须≤1)")
            for s in segs:
                w = s.get("weight", 0)
                if w < 0:
                    errors.append(f"s_curve.segments[{s.get('segment','?')}]: weight={w}<0")
                if "adjusted_anchor" not in s:
                    errors.append(f"s_curve.segments[{s.get('segment','?')}]: 缺 adjusted_anchor")
            # 区间端点加权:[Σ(下界×w), Σ(上界×w)]
            low = sum(s["adjusted_anchor"][0] * s.get("weight", 0) for s in segs if "adjusted_anchor" in s)
            high = sum(s["adjusted_anchor"][1] * s.get("weight", 0) for s in segs if "adjusted_anchor" in s)
            weighted = [round(low, 4), round(high, 4)]
            # 整体锚 = 加权锚
            if "adjusted_anchor" in sc and not _anchor_close(sc["adjusted_anchor"], weighted):
                errors.append(
                    f"s_curve.adjusted_anchor={sc['adjusted_anchor']} != segments加权锚={weighted} "
                    f"(conglomerate整体锚须=区间端点加权[Σ下界×w, Σ上界×w])"
                )
            # 双锚:整体锚 = reality_anchor.cagr_range
            if "adjusted_anchor" in sc and "cagr_range" in ra:
                if not _anchor_close(sc["adjusted_anchor"], ra["cagr_range"]):
                    errors.append(
                        f"双锚不一致:s_curve.adjusted_anchor={sc['adjusted_anchor']} "
                        f"!= reality_anchor.cagr_range={ra['cagr_range']}"
                    )
        else:  # v1(无 segments 或空数组)
            if "adjusted_anchor" in sc and "cagr_range" in ra:
                if not _anchor_close(sc["adjusted_anchor"], ra["cagr_range"]):
                    errors.append(
                        f"双锚不一致:s_curve.adjusted_anchor={sc['adjusted_anchor']} "
                        f"!= reality_anchor.cagr_range={ra['cagr_range']} "
                        f"(s_curve.adjusted_anchor 为 source of truth,须相等)"
                    )
    return errors, warnings


# ============================================================
# 主流程
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("用法: python validate_output.py <json_file> [--schema <schema.json>]")
        sys.exit(2)

    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"[ERROR] 文件不存在: {json_path}")
        sys.exit(2)

    # schema 路径:默认同目录 output_schema.json
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_schema.json")
    if "--schema" in sys.argv:
        idx = sys.argv.index("--schema")
        if idx + 1 < len(sys.argv):
            schema_path = sys.argv[idx + 1]

    if not os.path.exists(schema_path):
        print(f"[ERROR] schema 不存在: {schema_path}")
        sys.exit(2)

    data = load_json(json_path)
    schema = load_json(schema_path)

    print(f"校验文件 : {json_path}")
    print(f"schema   : {schema_path}")
    print(f"引擎     : {'jsonschema (完整语义)' if HAS_JSONSCHEMA else '内置简化校验器 (无依赖)'}")
    print("-" * 60)

    if HAS_JSONSCHEMA:
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            loc = ".".join(str(p) for p in e.absolute_path) or "<root>"
            print(f"[FAIL] jsonschema 校验失败:")
            print(f"  路径 : {loc}")
            print(f"  错误 : {e.message}")
            sys.exit(1)
        except jsonschema.SchemaError as e:
            print(f"[ERROR] schema 本身有误: {e.message}")
            sys.exit(2)
        # schema 通过后做语义检查
        sem_errors, sem_warnings = semantic_checks(data)
        for _w in sem_warnings:
            print(f"  [WARN] {_w}")
        if sem_errors:
            print(f"[FAIL] 语义校验失败 ({len(sem_errors)} 个错误):")
            for e in sem_errors:
                print(f"  - {e}")
            sys.exit(1)
        print("[PASS] 校验通过 (jsonschema + 语义检查)")
        sys.exit(0)
    else:
        errors = validate(data, schema)
        if errors:
            print(f"[FAIL] 校验失败 ({len(errors)} 个错误):")
            for e in errors:
                print(f"  - {e}")
            print()
            print("提示: 安装 jsonschema 可获得完整语义校验: pip install jsonschema")
            sys.exit(1)
        sem_errors, sem_warnings = semantic_checks(data)
        for _w in sem_warnings:
            print(f"  [WARN] {_w}")
        if sem_errors:
            print(f"[FAIL] 语义校验失败 ({len(sem_errors)} 个错误):")
            for e in sem_errors:
                print(f"  - {e}")
            sys.exit(1)
        print("[PASS] 校验通过 (内置校验器 + 语义检查)")
        print("提示: 安装 jsonschema 可获得完整语义校验 (format/$ref 等): pip install jsonschema")
        sys.exit(0)


if __name__ == "__main__":
    main()
