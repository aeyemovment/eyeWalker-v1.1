# eyeWalker v1.1 — Architecture (medical assistive research)

**Research prototype.** Not a medical device. Not for diagnosis or treatment.  
Assistive complement to cane / guide dog / O&M training only.

## Goal

Help developers and users explore **on-device and local-first assistive navigation** cues for people with visual impairment (including rare neurologic and ophthalmologic causes of vision loss).

## High-level flow

```
Camera (phone / optional HMD)
    → frame capture (PWA or Python)
    → perception (mock | local VLM | optional remote — privacy gated)
    → ground / obstacle cues (research labels)
    → accessibility output (speech, large HUD text) — advisory only
    → optional map / GPS trail for offline review (user consent)
```

## Main packages

| Path | Role |
|------|------|
| `docs/pwa.html` + `service-worker.js` | Installable PWA demo (MIT) |
| `eyewalker/perception/` | Frame / modality interfaces (research) |
| `eyewalker/obstacle/` · `planner/` | Hazard / path research stubs |
| `eyewalker/accessibility/` | Output surfaces |
| `eyewalker/world_model/` · `vlm/` | Optional VLM / world-model hooks |
| `eyewalker/cusp/` | Optional research overlays (synthetic / local) — not clinical |

## v1.1 ground mode (research)

- Priority toward **near-field ground** hazards (curb, crack, manhole-class labels — research taxonomy)  
- Optional **walk recording** for open training pipelines under `docs/training/` and `scripts/v11/`  
- Hybrid agentic VLM modes may include mock paths for offline development  

## Safety invariants

1. Never claim free-path guarantee  
2. Prefer fail-soft / warn when confidence is low  
3. No silent cloud upload of GPS+RGB without explicit consent design  
4. Heavy “research prototype / not a medical device” on user-facing surfaces  

## What this architecture deliberately excludes (public medical OSS)

- Law-enforcement evidence packs  
- Weapons / targeting framing  
- Classified or dual-use program packages  
- Clinical diagnostic labeling as product claims  

Those belong outside this open medical tree if pursued at all.

## Related public links

- https://github.com/aeyemovment/eyeWalker  
- https://aeyemovment.github.io/eyeWalker/pwa.html  
- https://github.com/aeyemovment/ogx-provider-eyewalker  
- https://huggingface.co/spaces/NeuroAgentAI/eyeWalker  

© 2026 NeuroAgent AI · eyeWalker v1.1.0
