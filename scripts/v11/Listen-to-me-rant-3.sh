#!/usr/bin/env bash
# eyeWalker v1.1 — SAFE local training prep (medical OSS)
# Does NOT auto-commit, force-tag, or publish.
# Research prototype only — not a medical device.
set -euo pipefail

# Prefer the medical OSS checkout; override with EYEWALKER_ROOT
ROOT="${EYEWALKER_ROOT:-$HOME/eyeWalker-v1.1-oss}"
if [[ ! -d "$ROOT" ]]; then
  ROOT="${EYEWALKER_ROOT:-$HOME/eyeWalker}"
fi
cd "$ROOT"
echo "eyeWalker local prep in: $ROOT"
# Do not clobber VERSION — release version is owned by human + CI surfaces.
if [[ ! -f VERSION ]]; then
  echo "1.1.8" > VERSION
fi
echo "VERSION=$(tr -d '[:space:]' < VERSION)"

mkdir -p docs/training/raw docs/training/frames docs/training/synthetic docs/training/exports

for f in \
  "$HOME/Downloads/eyewalker_v1_1_0_ground_checklist.webp" \
  "$HOME/Downloads/eye_walker_github_banner.webp"
do
  [[ -f "$f" ]] && cp -f "$f" docs/training/ || true
done

WALK_VID=""
for cand in \
  "$HOME/Downloads"/walk*.mp4 \
  "$HOME/Downloads"/walk*.mov \
  "$HOME/Downloads"/Walk*.mp4 \
  "$ROOT/docs/training/raw"/walk*.mp4 \
  "$ROOT/docs/training/raw"/walk*.mov \
  "$ROOT/docs/training/raw"/walk*.webm
do
  if [[ -f "$cand" ]]; then WALK_VID="$cand"; break; fi
done

if [[ -n "$WALK_VID" ]]; then
  echo "Using walk video: $WALK_VID"
  cp -f "$WALK_VID" "docs/training/raw/$(basename "$WALK_VID")"
  if [[ -x ./scripts/v11/train_from_video.sh ]]; then
    ./scripts/v11/train_from_video.sh "docs/training/raw/$(basename "$WALK_VID")"
  else
    echo "train_from_video.sh missing — staged video only"
  fi
else
  echo "NOTE: no walk video found. Staging empty train layout."
  echo "Drop video to docs/training/raw/walk_YYYY-MM-DD.mp4 then re-run."
  if [[ -x ./scripts/v11/train_from_video.sh ]]; then
    ./scripts/v11/train_from_video.sh || true
  fi
fi

# Rebuild synthetic DT labels (no absolute user paths)
if [[ -x ./scripts/v11/rebuild_synthetic_dataset.py ]]; then
  python3 ./scripts/v11/rebuild_synthetic_dataset.py
elif [[ -f ./scripts/v11/rebuild_synthetic_dataset.py ]]; then
  python3 ./scripts/v11/rebuild_synthetic_dataset.py
fi

test -f docs/pwa.html && echo "PWA present: docs/pwa.html"

echo ""
echo "SAFE PREP DONE (no git commit/push)."
echo "  Review: git status"
echo "  Commit only explicit paths after human review."
echo "  Publish only after Codex re-review + legal GO."
echo "  SAFETY: assistive research prototype — not medical device — keep cane"
