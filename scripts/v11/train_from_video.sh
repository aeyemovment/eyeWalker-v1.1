#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
VIDEO="${1:-}"
if [[ -n "$VIDEO" && -f "$VIDEO" ]]; then
  python3 scripts/v11/train_from_video.py --video "$VIDEO"
else
  echo "No video arg or missing file — running seed-only train (drop 30min walk into docs/training/raw/)"
  python3 scripts/v11/train_from_video.py --seed-only
fi
python3 scripts/v11/dt_ritual_all_at_once.py
python3 -c "from eyewalker.vlm.hybrid_agent import demo_once; import json; print(json.dumps(demo_once('hybrid'), indent=2))"
echo "OK v1.1 train pack → docs/training/"
