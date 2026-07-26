#!/bin/bash
set -e
# eyeWalker git bootstrap — commits to your git
# Usage: ./scripts/commit_to_git.sh [remote_url]

REMOTE=${1:-""}

if [ ! -d .git ]; then
  git init
  echo "Initialized new git repo"
fi

git add .
git commit -m "feat: eyeWalker v0.1.0 - world vision for the impaired

- Real-time VLM world model with Muse Spark 1.1
- Ground truth layer: OSM piers/marina + Esri <3yr satellite
- Obstacle identification & risk assessment (static/dynamic/ground/overhead)
- Real-time avoidance planner with spatial audio guidance
- Meta Ray-Ban 6DoF perception via VIO
- NemoClaw secure harness included
- Baltimore Harbor 3.66mi prototype
- License: PolyForm Noncommercial 1.0.0 (open except commercial)

Mission: one day provide world vision for the impaired."

if [ -n "$REMOTE" ]; then
  git remote add origin $REMOTE || git remote set-url origin $REMOTE
  git branch -M main
  git push -u origin main
  echo "Pushed to $REMOTE"
else
  echo "Local commit done. To push, run:"
  echo "  git remote add origin YOUR_GITHUB_URL"
  echo "  git push -u origin main"
fi
