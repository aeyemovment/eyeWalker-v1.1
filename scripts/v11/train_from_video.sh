#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 /absolute/path/walk.mp4 /external/empty/output-dir" >&2
  echo "Personal media and extracted frames must stay outside the public repository." >&2
  exit 2
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec python3 "$ROOT/scripts/v11/train_from_video.py" \
  --video "$1" \
  --output-dir "$2"
