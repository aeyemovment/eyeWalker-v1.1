#!/bin/bash
set -e
echo "Setting up eyeWalker..."
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
echo "For NemoClaw harness:"
echo "curl -fsSL https://nvidia.com/nemoclaw.sh | bash"
echo "nemoclaw onboard"
echo "Done. Put your GPX in data/ and run: python examples/harbor_walk.py"
