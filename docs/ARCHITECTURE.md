# eyeWalker v1.1 — Architecture (simulated accessibility-interface research)

**Research prototype.** Not a medical device. Not for diagnosis or treatment.  
Not a navigation or mobility aid. Keep cane / guide dog / O&M training.

## Goal

Help developers and users evaluate **deterministic simulated accessibility-interface** cue presentation for people with visual impairment (including rare neurologic and ophthalmologic causes of vision loss).

## High-level flow

```
PWA camera
    → preview and explicit-consent local recording
    → no pixel-to-cue perception path in this build

Generated abstract fixtures
    → deterministic simulated obstacle records
    → locally derived simulated HUD/text cues

Optional Python adapters
    → caller-supplied model/data interfaces or explicit-consent remote annotation
    → no validated end-to-end perception, fusion, or navigation system
```

## Main packages

| Path | Role |
|------|------|
| `docs/pwa.html` + `service-worker.js` | Installable PWA demo; these exact listed files are MIT |
| `eyewalker/perception/` | Caller-buffer interfaces and deterministic fixtures; no bundled validated detector |
| `eyewalker/obstacle/` · `planner/` | Hazard / path research stubs |
| `eyewalker/accessibility/` | Output surfaces |
| `eyewalker/world_model/` · `vlm/` | Optional VLM / world-model hooks |
| `eyewalker/cusp/` | Optional research overlays (synthetic / local) — not clinical |

## v1.1 ground mode (research)

- Priority toward **near-field ground** hazards (curb, crack, manhole-class labels — research taxonomy)
- Optional local preview/record export requires informed video-and-location
  consent; personal media extraction is external-only and is not ingested or
  trained by this repository
- Hybrid agent modes are deterministic mock paths unless an explicit,
  consented remote annotation configuration is supplied

## Safety invariants

1. Never claim free-path guarantee
2. HOLD and stop-and-verify whenever geometry, direction, or provenance is ambiguous
3. No remote transmission without explicit consent and a validated destination
4. Heavy “research prototype / not a medical device” on user-facing surfaces

## What this public research tree deliberately excludes

- Law-enforcement evidence packs
- Weapons / targeting framing
- Classified or dual-use program packages
- Clinical diagnostic labeling as product claims

Those are outside this public accessibility-interface research tree if pursued at all.

## Related public links

- https://github.com/aeyemovment/eyeWalker-v1.1
- https://aeyemovment.github.io/eyeWalker-v1.1/pwa.html
- https://github.com/aeyemovment/ogx-provider-eyewalker
- https://huggingface.co/spaces/NeuroAgentAI/eyeWalker

© 2026 NeuroAgent AI · eyeWalker v1.1.9
