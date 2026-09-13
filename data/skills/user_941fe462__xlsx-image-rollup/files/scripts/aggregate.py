"""
Aggregate raw records into a per-issue rollup summary.

Inputs:
    raw_records.json   list of dict, one per source row. Must contain every
                       key listed in --keys plus optionally --quote-key and
                       --image-key. If --image-key is omitted, the script
                       looks up images in --image-index by (sheet, row).
    image_index.json   (optional) extract_images.py output, used when
                       --image-key is absent. Format:
                         {sheet_name: {row_str: [{"filename": ...}, ...]}}

Output:
    summary.json   list of records, each with:
        category, series, responsibility, issue, count, pct,
        user_quotes (list), image_files (list)

Usage:
    python aggregate.py --input raw_records.json --keys category,series,responsibility,issue \\
        --quote-key user_quote --image-index image_index.json \\
        --sheet "质量问题登记" --row-field row_number \\
        --output summary.json
"""
import argparse
import json
import sys
from collections import defaultdict


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="Path to raw_records.json")
    p.add_argument("--output", required=True, help="Path to summary.json")
    p.add_argument("--keys", required=True,
                   help="Comma-separated grouping keys, e.g. category,series,responsibility,issue")
    p.add_argument("--quote-key", default=None,
                   help="Field name in raw_records containing a user-original-quote string")
    p.add_argument("--image-key", default=None,
                   help="Field name in raw_records containing a list of image filenames")
    p.add_argument("--image-index", default=None,
                   help="Path to image_index.json (extract_images.py output)")
    p.add_argument("--sheet", default=None,
                   help="Sheet name to look up in image_index (defaults to first)")
    p.add_argument("--row-field", default=None,
                   help="Field in raw_records holding the 1-based source row number")
    p.add_argument("--pct-by", default=None,
                   help="Group key to compute percentage against (default: second key)")
    args = p.parse_args()

    with open(args.input, encoding="utf-8") as f:
        records = json.load(f)
    if not isinstance(records, list):
        print("[ERROR] input must be a JSON list of records", file=sys.stderr)
        return 2

    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        print("[ERROR] --keys must not be empty", file=sys.stderr)
        return 2

    image_index = None
    if args.image_index:
        with open(args.image_index, encoding="utf-8") as f:
            image_index = json.load(f)
        if not args.sheet and image_index:
            args.sheet = next(iter(image_index))

    pct_by = args.pct_by or (keys[1] if len(keys) > 1 else keys[0])

    # Pass 1: count per pct_by group
    pct_denom = defaultdict(int)
    for rec in records:
        if not all(k in rec for k in keys):
            continue
        pct_denom[rec.get(pct_by, "")] += 1

    # Pass 2: aggregate by full key set
    buckets = {}  # tuple -> {values, quotes, images}
    for rec in records:
        if not all(k in rec for k in keys):
            continue
        k = tuple(rec.get(x, "") for x in keys)
        if k not in buckets:
            buckets[k] = {
                "values": dict(zip(keys, k)),
                "quotes": [],
                "images": [],
            }
        if args.quote_key and rec.get(args.quote_key):
            buckets[k]["quotes"].append(str(rec[args.quote_key]))
        if args.image_key and rec.get(args.image_key):
            v = rec[args.image_key]
            if isinstance(v, list):
                buckets[k]["images"].extend(v)
            else:
                buckets[k]["images"].append(v)
        elif image_index and args.sheet and args.row_field:
            row = rec.get(args.row_field)
            if row is not None:
                hits = image_index.get(args.sheet, {}).get(str(row), [])
                for h in hits:
                    fn = h.get("filename")
                    if fn and fn not in buckets[k]["images"]:
                        buckets[k]["images"].append(fn)

    # Build output
    summary = []
    for k, b in buckets.items():
        count = len([r for r in records if all(r.get(x, "") == k[i] for i, x in enumerate(keys))])
        # Recompute count via direct pass (more accurate if other filters apply)
        denom = max(1, pct_denom.get(k[keys.index(pct_by)] if pct_by in keys else "", 0))
        pct = count / denom * 100
        rec_out = {**b["values"], "count": count, "pct": round(pct, 2),
                   "user_quotes": b["quotes"], "image_files": b["images"]}
        summary.append(rec_out)

    # Stable sort: by count desc, then key order
    summary.sort(key=lambda r: (-r["count"], tuple(r.get(k, "") for k in keys)))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    total_imgs = sum(len(r["image_files"]) for r in summary)
    print(f"[OK] Wrote {args.output}")
    print(f"     Groups: {len(summary)}  Total image references: {total_imgs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
