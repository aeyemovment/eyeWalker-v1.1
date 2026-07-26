
# eyeWalker Mobile — Smartphone Release v0.1.0

This is the smartphone version of eyeWalker — no Ray-Bans needed to start. Your phone is the eyes.

## What's in this release

- Live camera view with VLM mock detection (trash bin, bench, pier edge, person+dog)
- Ground truth map: OSM piers/marina + Esri satellite (<3yr)
- Obstacle HUD with risk assessment and real-time avoidance guidance
- Spatial audio guidance (mock TTS → will use expo-speech)
- Split view: camera + map
- Optional NemoClaw *policy docs* only (not a tested security product; no “secured / never leaves” claim)

## Run it

```bash
cd mobile
npm install
npx expo start

# Then:
# - Press w for web
# - Scan QR with Expo Go on iOS/Android for phone
# - For native build:
#   eas build --platform android
#   eas build --platform ios
```

## How it works on phone

1. Phone camera replaces Ray-Ban camera (30fps → 0.66Hz photo for battery)
2. GPS + IMU from expo-location + expo-sensors gives 6DoF (same as glasses)
3. On-device VLM: Qwen2-VL 7B via Ollama for privacy, or Muse Spark 1.1 cloud for accuracy
4. Audio guidance via expo-speech with bearing: "trash bin 2.1m ahead, step left"

## Baltimore Harbor Demo

The default location is mocked to your 3.66mi Fells Point loop. Walk simulation moves you along the yellow route, triggers obstacles at:
- 0.8mi: trash bin
- 1.2mi: pier edge
- 2.1mi: person + dog 1.2m/s
- 2.8mi: bench blocking

Guidance: "Obstacle: trash bin 2.1m ahead, step left 0.5m"

## Next: Ray-Ban upgrade

Once mobile is validated, swap CameraView from expo-camera to Ray-Ban BLE stream — same interface.

## License

PolyForm Noncommercial 1.0.0 — open for all except commercial use.



## Safety

**This is assistive, not replacement for cane/guide dog. Always keep traditional mobility aid. This is alpha. It is a research prototype for users and developers to improve upon.**

- eyeWalker is designed to *assist* navigation, not replace primary mobility aids
- Always use your cane, guide dog, or trusted human guide alongside eyeWalker
- This is alpha research software — expect errors, false positives, missed obstacles
- Built to be improved by the community: users, visually impaired testers, and developers
- Test in safe, familiar areas first (like the Baltimore Harbor loop) before new areas
- Your feedback makes it safer for everyone

