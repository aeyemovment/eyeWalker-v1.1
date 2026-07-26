#!/bin/bash
set -e
echo "Setting up eyeWalker..."
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
echo "NemoClaw integration is not implemented or tested in this repository."
echo "For optional evaluation, consult current official NVIDIA documentation at https://docs.nvidia.com/"
echo "and review any external installation steps manually before running them."
echo "Done. Run the deterministic no-input mock with: python examples/harbor_walk.py"
