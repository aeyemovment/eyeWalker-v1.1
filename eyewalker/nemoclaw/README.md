
# NemoClaw Harness for eyeWalker

NVIDIA NemoClaw is a secure agent harness — it sandboxes OpenClaw agents with policy-enforced network, filesystem, and inference routing.

Why we include it:
- **Privacy**: Ray-Ban GPS + camera are sensitive. NemoClaw enforces local-first routing — inference happens on-device via Ollama/Qwen2-VL unless you opt into cloud Nemotron.
- **Safety**: Egress allowlist — only map tiles (Esri, MapTiler, OSM) and inference endpoints. No trackers.
- **Reproducibility**: Blueprint is versioned and digest-verified.

## Install

```bash
curl -fsSL https://nvidia.com/nemoclaw.sh | bash
nemoclaw onboard
nemoclaw eyewalker connect
openclaw tui
```

## Policies
- `privacy.yaml` — blocks raw location+video exfiltration
- Presets `pypi`, `npm` for dependencies

## Use with eyeWalker

Inside sandbox:
```bash
cd /sandbox/eyeWalker
pip install -e .
python examples/harbor_walk.py --mode secure
```

See https://docs.nvidia.com/nemoclaw/
