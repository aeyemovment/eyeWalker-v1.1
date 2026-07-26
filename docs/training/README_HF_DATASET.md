# eyeWalker Ground Dataset — v1.1.0-ground

**Research prototype only. Not a medical device. Not for clinical diagnosis or treatment.**

## Summary

Assistive navigation ground-hazard dataset for open-source eyeWalker.

| Field | Value |
|-------|--------|
| Version | v1.1.0-ground |
| Source | Baltimore harbor walks + optional 30-min phone video + DT synthetic |
| Task | Ground obstacle detection + spatial guidance text |
| FPS target | 2 |
| DT conditions | day / dusk / night / rain (all-at-once ritual) |
| Agent | Hybrid **Grok <> Muse Spark 1.1** (experiment modes) |

## Safety

> This is assistive, not replacement for cane/guide dog. Always keep traditional mobility aid. This is alpha. It is a research prototype for users and developers to improve upon.

From **NeuroAgent AI** — for patients with rare neurologic diseases affecting vision and all other neurologic and ophthalmologic causes of visual impairment.

## Layout

```
docs/training/
  raw/           # drop walk_YYYY-MM-DD.mp4 here
  frames/        # 2fps extracts
  synthetic/     # DT ritual JSON labels
  exports/       # manifests + VLM streams
```

## Reproduce

```bash
cd eyeWalker
# after AirDrop of 30-min video:
cp ~/Downloads/your_walk.mp4 docs/training/raw/walk_2026-07-26.mp4
./scripts/v11/train_from_video.sh docs/training/raw/walk_2026-07-26.mp4
# or full Spark Muse script:
bash scripts/v11/Listen-to-me-rant-3.sh
```

## License

Core: PolyForm Noncommercial 1.0.0 · Mobile/PWA: MIT (`LICENSE-MIT`)
