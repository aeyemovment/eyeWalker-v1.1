# eyeWalker v1.1.9 (release-candidate hardening)

- Enforce locally derived step-away guidance after every remote/model response; preserve truthful fallback provenance
- Make REC finalization await the final recorder events; revoke consent clears GPS state and retained precise-location logs
- Remove remaining dual-use and unsupported privacy/security claims from the tracked public tree
- Make the synthetic rebuild collision-safe, ownership-scoped, deterministic, and one-to-one under CI
- Replace NemoClaw guarantees with an explicit unenforced policy sketch; retain Omniverse as a disabled synthetic-only stub
- Add executable hybrid, privacy/AgentAPI, recorder-lifecycle, and adversarial synthetic regression tests
- Remove legacy non-synthetic media from the release tip. Existing commits and immutable tags were not rewritten and may still retain those historical objects; this is not a historical-purge claim. Any history remediation requires a separate human/legal decision.

# eyeWalker v1.1.8 (safety and privacy honesty)

- Canonical PWA only at `docs/pwa.html` (no root duplicate); hybrid L/R step-away + SIMULATED labels
- Remove aerial dual-use perception module; honest multicam/bodycam redaction (`requested` / not applied)
- Public tree free of unsafe ship scripts; `commit_to_git.sh` non-publishing; safe prep script
- REC: consent revocable (stops capture + clears GPS trail/watch), Stop bound, finalize before Save, MIME ext
- All version surfaces **1.1.8**; CI covers duplicate-PWA, recorder wiring, privacy scrub, script safety, aerial ban
- NemoClaw/Omniverse: optional stubs only — no “secured / never leaves” marketing
- Immutable tag **v1.1.8** (do not move v1.1.1–v1.1.7)

# eyeWalker v1.1.2 (PWA and privacy fixes)

- Remove root `pwa.html` duplicate; canonical is `docs/pwa.html` only
- Fix `hybrid_agent` left/right (step away) + SIMULATED labels
- Remove unsafe ship scripts from public tree
- Honest bodycam redaction fields (`requested`/`not_applied`)
- REC: consent revocable, Stop bound, finalize before Save, MIME extension, GPS trail requires consent
- NemoClaw/Omniverse claims de-hyped to optional/stub
- Stronger CI; immutable tag **v1.1.2** (do not move v1.1.1)

# eyeWalker v1.1 — accessibility-interface research source (2026-07-26)

## v1.1.1 (public research hardening)

- Simulated cues explicitly labeled; simulation can be toggled off
- Left/right: step **away** from obstacle bearing (PWA + planner tests)
- Scrub dual-use / private-path / fake-crypto presentation from the public tree
- Safe local prep script (no `git add -A`, no force tags, no auto-publish)
- REC requires consent; pause resumes; save respects consent
- Synthetic dataset rebuilt (no absolute home paths) + GitHub Actions CI
- Optional NemoClaw + Omniverse research stubs (honest, non-warranty)

# eyeWalker v1.1.0 — accessibility-interface research source (2026-07-26)

## Positioning

Public repo is **eyeWalker v1.1** by **NeuroAgent AI** — simulated accessibility-interface research for visual impairment / rare neuro-ophthalmic vision loss.

**Not** a dual-use program pack. **Not** a medical device.

## User-facing

- PWA walk experience with safety banner
- Optional **REC** (MediaRecorder) for local research export; personal media remains outside the public repository
- Ground-priority research cues
- Links: GitHub, GitHub Pages PWA, OGX provider, HF Space

## Engineering

- Hybrid VLM hooks (mock / spark / optional grok paths for research)
- Train helpers under `scripts/v11/`
- Fail-closed dual-license scope: PolyForm NC by default; MIT only for exact paths in `DUAL_LICENSE.md`

## Safety / claims

- Assistive only; keep cane / guide dog
- No FDA / clinical / diagnostic claims
- Local-first privacy defaults

## From v1.0

- v1.0 established public PWA + dual license + assistive framing
- v1.1 added a simulated cue/REC research interface; current claims are bounded by this changelog's v1.1.9 section
