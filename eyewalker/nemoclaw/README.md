# NemoClaw (optional) + Omniverse (optional)

**eyeWalker v1.1.2 medical OSS** — NeuroAgent AI.

## Honesty

| Component | Status |
|-----------|--------|
| NemoClaw | **Optional** local-first *policy docs* + `blueprint.yaml` sketch. **Not** a tested NVIDIA-managed integration. **Do not** claim “NemoClaw secured” or “data never leaves.” |
| Omniverse | **Optional stub** in `eyewalker/omniverse/` — disabled by default; returns `available: false` until you install Omniverse/Isaac yourself. |

Full NVIDIA NemoClaw lifecycle (CLI, OpenShell, versioned blueprints) is **out of scope** of this repo until implemented and tested against current NVIDIA docs.

## PWA

The browser PWA runs **without** NemoClaw or Omniverse.

## Privacy intent

Local-first *policy*: do not upload raw GPS+RGB without explicit user consent. Policy intent ≠ cryptographic guarantee.
