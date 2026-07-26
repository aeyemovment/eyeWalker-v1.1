---
title: eyeWalker v1.1.9 — Simulated Accessibility Research Demo
emoji: 👓
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
python_version: "3.12"
short_description: Deterministic mock interface for accessibility research
license: other
license_name: polyform-noncommercial-1.0.0
tags:
  - accessibility
  - vision-impairment
  - assistive-technology
  - research-prototype
pinned: false
startup_duration_timeout: 10m
---

# eyeWalker v1.1.9 — simulated accessibility research demo

eyeWalker is a simulated accessibility-interface research project from NeuroAgent AI for people with neurologic or ophthalmologic causes of visual impairment. The current demo is not a navigation or mobility aid.

> **Executable status:** this Space is a deterministic mock for interface evaluation. It does not run image inference, obstacle detection, depth estimation, VIO, map fusion, or binaural audio. It must not be used for navigation.

## What the demo does

- Accepts an uploaded image or generated harbor-style frame as a UI input.
- Uses deterministic mock data to draw a clearly marked `SIMULATED RESEARCH MOCK` overlay.
- Generates a locally derived, simulated step-away cue with truthful provenance.
- Returns JSON marked `simulated: true` and `model: deterministic_mock_no_model_executed`.
- Produces text suitable for future TTS experiments; no spatial-audio renderer is included.

Changing an image may change the deterministic mock seed. The pixels are not analyzed by a vision model.

On a hosted Space, uploaded or webcam images are transmitted to the Space host
for pixel hashing and display. Use only synthetic, non-sensitive fixtures with
no bystanders, faces, plates, documents, or precise-location clues.
Inputs are rejected above 4096 pixels on either side or 16,000,000 total pixels.

## Proposed research architecture — not implemented end to end

Future work may evaluate camera and location inputs, a validated perception model, depth/segmentation, accessible map context, and audio rendering. Those components are design goals only unless separately implemented and validated. No latency, accuracy, obstacle-completeness, navigation-safety, device-integration, or city-scale deployment claim is made here.

## Demo usage

1. Upload an image or choose the generated demo frame.
2. Inspect the simulated overlay, cue, and provenance JSON.
3. Treat every obstacle, distance, bearing, risk level, and bypass cue as synthetic test data.

## Safety

This is assistive research, not a replacement for a cane, guide dog, orientation-and-mobility training, or a trusted human guide. Always keep your traditional mobility aid. Not a medical device. Not for navigation, clinical, diagnostic, production, or regulatory use.

## Links

- Source: https://github.com/aeyemovment/eyeWalker-v1.1
- Canonical PWA: https://aeyemovment.github.io/eyeWalker-v1.1/pwa.html
- Architecture status: https://github.com/aeyemovment/eyeWalker-v1.1/blob/main/docs/ARCHITECTURE.md
- Safety: https://github.com/aeyemovment/eyeWalker-v1.1/blob/main/SAFETY.md

## Submission status

Files under `meta_submission/` are draft evaluation materials. This README does not claim that a Meta, Llama Stack, OGX, or Hugging Face submission was created, accepted, merged, deployed, or approved.

## License

- Core (`eyewalker/`): PolyForm Noncommercial 1.0.0.
- Only the exact files enumerated in `DUAL_LICENSE.md`: MIT.
