#!/usr/bin/env bash
# eyeWalker — safe, help-only local git status helper
# Does NOT auto-stage, force-tag, or publish.
# Explicit paths only after human review.
set -euo pipefail

echo "eyeWalker safe git helper"
echo "This script does NOT run: git add -A / git add . / force-push / force-tag."
echo ""
echo "Recommended flow:"
echo "  1) git status"
echo "  2) git add <explicit paths>   # never git add -A in release prep"
echo "  3) git commit -m '...' "
echo "  4) Human review before push"
echo "  5) git push origin main"
echo "  6) Immutable tag only: git tag vX.Y.Z && git push origin vX.Y.Z"
echo "     (never move an existing public tag)"
echo ""
echo "Optional NemoClaw / Omniverse: docs only — not a security product."
echo "Research prototype — not a medical device. Keep cane / guide dog."
exit 0
