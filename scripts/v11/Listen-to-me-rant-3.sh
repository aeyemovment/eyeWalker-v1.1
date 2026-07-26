#!/usr/bin/env bash
# Local deterministic synthetic-fixture rebuild only.
# Does not discover/copy personal media, commit, tag, push, or publish.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

test -f VERSION
VERSION_VALUE="$(tr -d '[:space:]' < VERSION)"
if [[ "$VERSION_VALUE" != "1.1.9" ]]; then
  echo "VERSION must be exactly 1.1.9 for this release candidate" >&2
  exit 1
fi

python3 scripts/v11/rebuild_synthetic_frames.py
python3 scripts/v11/rebuild_synthetic_dataset.py
python3 scripts/check_public_tree.py

echo "LOCAL SYNTHETIC REBUILD COMPLETE"
echo "No personal media was discovered or copied; no Git or network mutation was performed."
echo "Review the exact diff and tests before any human-gated release action."
echo "SIMULATED RESEARCH ONLY — keep your cane or guide dog. Not a medical device."
