# eyeWalker v1.1.9 — license scope

This document is authoritative for assigning repository paths to a license.
`LICENSE` and `LICENSE-MIT` are authoritative for the terms of their respective
licenses. This path assignment is not legal advice and makes no claim about any
platform submission or distribution requirement.

## Fail-closed path scope

Every repository path is covered by PolyForm Noncommercial 1.0.0 unless it is
explicitly included in the MIT allowlist below. A missing, renamed, generated,
or newly added path does not inherit the MIT license by proximity.

The complete currently implemented mobile wrapper and static PWA shell use the
MIT license in `LICENSE-MIT` only for these exact files:

- `LICENSE-MIT`
- `DUAL_LICENSE.md`
- `mobile/App.tsx`
- `mobile/README.md`
- `mobile/app.json`
- `mobile/package.json`
- `mobile/LICENSE-MIT.txt`
- `mobile/src/components/CameraView.tsx`
- `mobile/src/components/MapView.tsx`
- `mobile/src/components/ObstacleHUD.tsx`
- `mobile/src/hooks/useLocation.ts`
- `mobile/src/hooks/useObstacleDetection.ts`
- `mobile/src/safety.ts`
- `mobile/src/utils/avoidance.ts`
- `docs/index.html`
- `docs/pwa.html`
- `docs/service-worker.js`
- `docs/manifest.json`
- `docs/LICENSE-MIT.txt`
- `docs/icons/icon-192.png`
- `docs/icons/icon-512.png`
- `docs/icons/apple-touch-icon.png`

All other paths, including other or newly added files under `mobile/`,
`eyewalker/**`, `examples/**`, `scripts/**`,
`hf-space-final/**`, `meta_submission/**`, `docs/training/**`, other
documentation, and `docs/neuroagent_eye_logo.png`, remain in the default
PolyForm scope.

PolyForm Noncommercial is not an OSI-approved open-source license. Public
source availability must not be described as making every repository path
OSI-open-source.

## Canonical license files and marks

- `LICENSE` — PolyForm Noncommercial 1.0.0 for the default scope.
- `LICENSE-MIT` — MIT terms for only the exact allowlisted paths above. The
  identical `docs/LICENSE-MIT.txt` and `mobile/LICENSE-MIT.txt` copies keep
  that notice with the two distributable surfaces.

Neither license grants trademark rights in the NeuroAgent AI or eyeWalker
names, logos, or other source-identifying marks. This trademark reservation
does not remove the copyright permissions granted for the allowlisted files.

If this path assignment and a canonical license term appear to conflict,
obtain legal review before distribution rather than inferring rights.

## Safety is independent of license

Licensing does not validate the software for mobility, medical, clinical,
diagnostic, production, or regulatory use.

- Current movement outputs are simulated research cues, not live detections.
- Keep your cane or guide dog. Not a medical device.
- Do not use the current demo as a navigation or mobility aid.
- Expect synthetic records, false positives, false negatives, and incomplete
  interfaces.

## Attribution

Copyright (c) 2026 NeuroAgent AI / Kemar Green.

Repository: https://github.com/aeyemovment/eyeWalker-v1.1
