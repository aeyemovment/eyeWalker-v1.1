# Meta / Hugging Face evaluation checklist — eyeWalker v1.1.9

**Artifact status:** draft-only packaging for a simulated accessibility research interface.
**Repository:** https://github.com/aeyemovment/eyeWalker-v1.1
**Safety:** not for navigation; not a medical device; keep a cane or guide dog.

This file does not authorize or prove an email, portal submission, pull request, deployment, publication, approval, or merge. The current executable Gradio and mobile surfaces generate deterministic mock records; they do not execute a live image model, depth pipeline, map-fusion pipeline, or spatial-audio renderer.

## Historical external handles — verify before reuse

Records dated 2026-07-25 referenced these external surfaces:

- OGX documentation PR ogx-ai/ogx#6346.
- Provider repository aeyemovment/ogx-provider-eyewalker.
- Hugging Face Space NeuroAgentAI/eyeWalker, described as a static/free-tier surface.
- An older Pages path under aeyemovment.github.io/eyeWalker/.

Those are routing handles, not current-state proof in this v1.1.9 code review. Confirm the live revision, displayed claims, and provider behavior independently before citing them. Do not infer that Meta accepted or featured the project.

## Current local artifact checks

- [ ] Release candidate has one immutable commit SHA and VERSION, package metadata, PWA payload, service-worker cache, and generated manifests all equal 1.1.9.
- [ ] hf-space-final/app.py and meta_submission/app.py visibly say SIMULATED RESEARCH DEMO and not for navigation.
- [ ] Mock JSON says simulated: true, names deterministic_mock_no_model_executed, and lists no executed models.
- [ ] Every simulated movement cue starts SIMULATED RESEARCH CUE: and ends Keep your cane or guide dog. Not a medical device.
- [ ] meta_submission/llama_stack_tool.json validates as JSON and describes only the implemented mock contract.
- [ ] NemoClaw YAML remains an unloaded, unvalidated, unenforced policy sketch; Omniverse remains disabled/unavailable.
- [ ] Public-tree, privacy, synthetic-provenance, PWA-lifecycle, and left/right tests pass at the same SHA.

## Human-gated external evaluation

Before any future submission or update, a human operator must:

1. Review the exact immutable release revision and its licenses.
2. Verify the current contribution route and schema in official platform documentation.
3. Use claim-bounded copy: deterministic simulated interface now; perception, depth, VIO, map fusion, wearable integration, and audio rendering are proposed research components.
4. Test the public artifact after deployment and record the URL plus immutable revision or content digest.
5. Record any actual request, PR, email, or portal confirmation ID. A draft filename or local checklist is not a receipt.

## Safe draft description

> eyeWalker v1.1.9 is a public-source simulated accessibility-interface research project. Its current public demo produces deterministic, clearly labeled simulated obstacle records and locally derived cue text for stationary or controlled interface evaluation. It does not analyze image pixels with a live model and must not be used for navigation. Proposed future work may evaluate validated perception and accessible presentation components. It is not a medical device and is not a replacement for a cane, guide dog, orientation-and-mobility training, or a trusted human guide.

## Prohibited current claims

Do not describe the present artifact as:

- real-time obstacle detection or safe-path navigation;
- a working Muse Spark, Qwen, SAM, Depth Anything, VIO, OSM, Esri, Ray-Ban, or phone-sensor pipeline;
- measured at a stated latency, accuracy, reaction window, or geographic scale;
- producing binaural/spatial audio;
- secured by NemoClaw or guaranteed to prevent data egress;
- submitted, accepted, merged, deployed, live, approved, or featured without a current external receipt.

## Licensing and safety review

- Core scope: PolyForm Noncommercial 1.0.0; confirm the exact covered paths in DUAL_LICENSE.md.
- MIT applies only to the exact paths enumerated in `DUAL_LICENSE.md`.
- PolyForm Noncommercial is not an OSI-approved open-source license; do not claim that it is.
- Always retain the visible research-prototype, simulation, mobility-aid, and not-medical-device wording.

## Release evidence to attach before handoff

- Exact commit SHA and clean-tree result.
- Full test and CI-equivalent command results.
- Public-tree scrub result.
- Browser smoke-test result, or an explicit statement that browser runtime was unavailable.
- Independent reviewer verdict tied to the same SHA.
- Only after publication: remote branch/tag/release identifiers and live URL checks.
