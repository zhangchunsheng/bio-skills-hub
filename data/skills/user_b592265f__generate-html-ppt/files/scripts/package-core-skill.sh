#!/usr/bin/env bash
# Build the lightweight Codex skill archive. Demo and gallery assets stay in
# the repository for GitHub documentation, but are deliberately not shipped.
set -euo pipefail

skill_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_path="${1:-$skill_root/dist/generate-html-ppt-core.tar.gz}"

if [[ -e "$output_path" ]]; then
  echo "Refusing to overwrite existing archive: $output_path" >&2
  exit 1
fi

mkdir -p "$(dirname "$output_path")"

tar -czf "$output_path" \
  --exclude='.DS_Store' \
  --exclude='scripts/__pycache__' \
  --exclude='resources/screenshot-backgrounds' \
  -C "$skill_root" \
  SKILL.md LICENSE README.md README_en.md designs references resources scripts

du -h "$output_path"
echo "Created core skill archive: $output_path"
