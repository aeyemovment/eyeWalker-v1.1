# NemoClaw + Omniverse (optional research)

**eyeWalker v1.1 medical OSS** — NeuroAgent AI.

## What this is

| Piece | Role |
|-------|------|
| **NemoClaw** | Optional **local-first** agent harness / sandbox policy (egress allowlist, sensitive routes stay local). See `blueprint.yaml`. |
| **Omniverse** | Optional **synthetic simulation** adapter (`eyewalker/omniverse/`) for offline research scenes — **not** required for the PWA. |

Neither is a medical device stack. Neither claims production crypto or classified capability.

## Honest limits

- Blueprint is **policy documentation** + optional tooling — not a warranty of security.  
- Omniverse bridge is a **stub** until you install NVIDIA Omniverse/Isaac separately.  
- Default PWA runs **without** Omniverse.  

## Quickstart (optional)

```bash
# NemoClaw — only if you use NVIDIA's harness (external install)
# follow current NVIDIA docs; do not curl | bash in production CI without review

# Omniverse stub status
python -c "from eyewalker.omniverse import OmniverseBridge; print(OmniverseBridge().status())"
```

## Privacy

Local-first: do not pair raw GPS + RGB for cloud egress without explicit user consent.  
See root `PRIVACY.md` and `SAFETY.md`.
