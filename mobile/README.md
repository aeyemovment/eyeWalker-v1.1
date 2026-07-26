# eyeWalker Mobile UI Mock v1.1.9

This directory contains a deterministic **SIMULATED RESEARCH** interface mock for accessibility-development discussion. It is not a navigation app and it does not execute a camera, GPS sensor, map provider, obstacle detector, VLM, depth model, or text-to-speech engine.

> **SIMULATED RESEARCH CUE:** Interface mock only; pause and verify. Keep your cane or guide dog. Not a medical device.

## Current implementation truth

| Surface | What executes now |
|---|---|
| Camera panel | Static React Native mock layout; no camera capture |
| Map panel | Synthetic shapes and fixed mock coordinates; no OSM, Esri, or device GPS |
| Obstacle labels | Deterministic in-memory fixtures with provenance `deterministic_mock_no_model_executed`; no model confidence is computed |
| Guidance | Locally formatted simulated text that steps away from the fixture bearing |
| Audio button | Writes the already labeled mock cue to the debug console; no TTS playback |
| NemoClaw / remote models | Not integrated, loaded, tested, or enforced here |

No empty fixture state is called “path clear.” The interface instead says that no mock obstacle was generated and tells the viewer to pause and verify.

## Development preview

```bash
cd mobile
npm install
npx expo start
```

`package.json` contains only the Expo/React Native runtime needed to render this mock. It intentionally includes no camera, location, sensor, map, audio, or speech package, and `app.json` requests no camera or location permission.

This repository does not claim a signed Android/iOS build or app-store submission. Before native testing, install dependencies and run `npx expo install --check`; review any requested dependency change rather than assuming this source-only mock is a validated binary. Web and EAS build scripts are intentionally omitted because their required packages and release configuration are not included.

Use this preview only to inspect layout, visible safety wording, mock provenance, and left/right cue formatting. Do not use it while walking or for any real-world navigation decision.

## Safety invariant

Every generated cue begins with `SIMULATED RESEARCH CUE:` and ends with the exact sentence:

`Keep your cane or guide dog. Not a medical device.`

For a fixture to the left (negative bearing), the formatter says step right. For a fixture to the right (positive bearing), it says step left. A centered fixture produces a HOLD cue unless two finite, nonnegative mock free-space scores differ by a meaningful margin.

## Future work is not current capability

Real camera capture, location permission, map data, perception models, privacy review, accessible TTS, sensor validation, and field safety testing would each require separate implementation and evidence. None is claimed by this mock.

## License

Only the exact individual mobile and static-PWA files enumerated in
[`../DUAL_LICENSE.md`](../DUAL_LICENSE.md) are licensed under the MIT terms in
[`LICENSE-MIT.txt`](LICENSE-MIT.txt), an identical local copy of
[`../LICENSE-MIT`](../LICENSE-MIT). New, renamed, or generated files default to
the repository's PolyForm Noncommercial scope unless that authoritative exact
allowlist is deliberately updated.
