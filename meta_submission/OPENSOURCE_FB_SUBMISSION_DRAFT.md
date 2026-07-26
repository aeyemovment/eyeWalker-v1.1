# Meta source-availability evaluation draft — eyeWalker v1.1.9

**Status:** draft-only operator copy. It is not a portal submission, email receipt, approval, listing, or publication record.

## Project name

eyeWalker

## Category

Accessibility research

## One-line description

Deterministic simulated interface for evaluating accessibility-cue presentation; not a medical device and not for navigation.

## Claim-bounded description

eyeWalker is a public-source accessibility-interface research project from NeuroAgent AI for people with neurologic or ophthalmologic causes of visual impairment. The current public code demonstrates a user interface with deterministic mock obstacle records and locally derived simulated cue text. It does not execute a live image model, obstacle detector, depth pipeline, VIO, map fusion, phone or wearable sensor pipeline, or spatial-audio renderer and must not be used for navigation.

The interface is intended for software and accessibility-interface research only. Proposed future work may evaluate validated perception and accessible guidance components, but those components are not part of the current executable demo.

Every simulated movement output must begin SIMULATED RESEARCH CUE: and end Keep your cane or guide dog. Not a medical device.

## Safety and ethics

eyeWalker must not be marketed or used as a medical device, a navigation system, or a replacement for a cane, guide dog, certified orientation-and-mobility training, or a trusted human guide. Current records are synthetic and may be wrong or incomplete. No controlled-user-testing, clinical, diagnostic, production, regulatory, latency, accuracy, or obstacle-completeness claim is made.

## Implemented now

- Deterministic mock overlay and JSON output.
- Simulated obstacle records with explicit provenance.
- Local step-away text for interface testing.
- PWA recorder/consent research surface.

## Proposed only

- Validated camera perception and distance estimation.
- Walkable-region or map-context fusion.
- Phone or wearable sensor integration.
- TTS or binaural/spatial-audio rendering.
- Real-world navigation evaluation.

## Repository and demo links

- Source: https://github.com/aeyemovment/eyeWalker-v1.1
- Canonical PWA: https://aeyemovment.github.io/eyeWalker-v1.1/pwa.html
- Safety: https://github.com/aeyemovment/eyeWalker-v1.1/blob/main/SAFETY.md
- Architecture status: https://github.com/aeyemovment/eyeWalker-v1.1/blob/main/docs/ARCHITECTURE.md

## Licensing

- PolyForm Noncommercial 1.0.0 for the documented core scope.
- MIT only for the exact paths enumerated in `DUAL_LICENSE.md`.
- See DUAL_LICENSE.md for exact boundaries. Do not call PolyForm Noncommercial OSI-approved.

## Human-gated steps

1. Verify the current official Meta submission route.
2. Review the exact immutable eyeWalker revision and public claims.
3. Test any deployed artifact and record its immutable source revision or digest.
4. Submit only the claim-bounded description above.
5. Save the actual portal, email, issue, or PR confirmation identifier.

Until those steps produce evidence, report this lane as draft-only.
