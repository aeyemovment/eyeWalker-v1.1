#!/usr/bin/env bash
# eyeWalker v1.1.0-ground — Spark Muse prep FIXED + Grok DT ritual all-at-once
# Run from anywhere. Research prototype only — not a medical device.
set -euo pipefail

ROOT="${EYEWALKER_ROOT:-$HOME/eyeWalker}"
cd "$ROOT"
echo "v1.1.0-ground" > VERSION

mkdir -p docs/training/raw docs/training/frames docs/training/synthetic docs/training/exports

# Copy any checklist / training webp from Downloads
for f in \
  "$HOME/Downloads/eyewalker_v1_1_0_ground_checklist.webp" \
  "$HOME/Downloads/eye_walker_github_banner.webp"
do
  [[ -f "$f" ]] && cp -f "$f" docs/training/ || true
done

# If user dropped a 30-min walk video in Downloads, stage it
WALK_VID=""
for cand in \
  "$HOME/Downloads"/walk*.mp4 \
  "$HOME/Downloads"/walk*.mov \
  "$HOME/Downloads"/Walk*.mp4 \
  "$HOME/Downloads"/*harbor*walk*.mp4 \
  "$HOME/Downloads"/*Harbor*.mp4 \
  "$ROOT/docs/training/raw"/walk*.mp4 \
  "$ROOT/docs/training/raw"/walk*.mov \
  "$ROOT/docs/training/raw"/walk*.webm
do
  if [[ -f "$cand" ]]; then WALK_VID="$cand"; break; fi
done

if [[ -n "$WALK_VID" ]]; then
  echo "Using walk video: $WALK_VID"
  cp -f "$WALK_VID" docs/training/raw/
  ./scripts/v11/train_from_video.sh "docs/training/raw/$(basename "$WALK_VID")"
else
  echo "NOTE: 30-min walk video not found on disk yet."
  echo "v1.0 PWA never MediaRecorder-saved (live feed only)."
  echo "Drop video to docs/training/raw/walk_YYYY-MM-DD.mp4 then re-run."
  ./scripts/v11/train_from_video.sh
fi

# Ensure PWA v1.1 is in docs/ (written by Grok finish pass)
test -f docs/pwa.html

git add VERSION docs/training eyewalker/vlm scripts/v11 docs/pwa.html docs/index.html \
  docs/manifest.json docs/service-worker.js 2>/dev/null || true
git add -A

git status -sb
git commit -m "feat: v1.1.0-ground — REC fix, hybrid Grok<>Muse Spark VLM, DT ritual all-at-once, ground obstacles" || echo "nothing to commit?"

# push if authenticated
if gh auth status &>/dev/null; then
  git push origin main || true
  git tag -f v1.1.0-ground
  git push origin v1.1.0-ground -f || true
else
  echo "gh not authed — commit local only"
fi

echo ""
echo "DONE v1.1.0-ground"
echo "  PWA: docs/pwa.html (REC saves webm + GPS)"
echo "  Train: docs/training/"
echo "  Hybrid: eyewalker/vlm/hybrid_agent.py"
echo "  SAFETY: assistive research prototype — not medical device — keep cane"
