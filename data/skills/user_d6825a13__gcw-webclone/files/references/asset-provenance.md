# Asset provenance

Use an asset manifest for asset-heavy, offline, or maintained work. Each entry records source URL, deterministic local path, purpose, license/attribution, content type, and SHA-256 checksum. Only download in-scope assets whose reuse is permitted.

Generate an initial draft from inventory without overwriting existing work:

```text
python <skill-root>/scripts/generate_asset_manifest.py <workspace>/.gcw/evidence/site-inventory.json --out <workspace>/.gcw/asset-manifest.json
```

The generator combines network resources with route-surface images, videos, scripts, and stylesheets; classifies known static types and extensions; deduplicates URLs; proposes hashed local paths; and records unsupported or sensitive resources under `excluded`. This is discovery evidence, not a reuse decision. Review every entry, remove out-of-scope assets, fill purpose/license/attribution, and change `reviewStatus` from `pending` to `confirmed` only when downloading is authorized.

Run `scripts/download_assets.py` with a concurrency limit. It rejects generated drafts that are not confirmed. Existing checksum-matching files are skipped; `--refresh` is explicit. The downloader rejects traversal paths, credential-bearing URLs, content-type mismatches, and checksum mismatches. Never package target-site assets inside the GCW skill.
