# Contributing to eyeWalker

Thank you for helping make simulated accessibility-interface research safer and more useful.

## Report simulated-interface defects

The current build does not analyze camera pixels with a live detector and must
not be used while walking or for real-hazard testing. If its deterministic mock
interface displays a malformed, contradictory, unlabeled, or wrong-direction
simulated cue during stationary or controlled evaluation:

1. End the simulated session; do not act on the cue.
2. Open a GitHub Issue: https://github.com/aeyemovment/eyeWalker-v1.1/issues/new
3. Title: `SIMULATED_CUE_BUG: <short description>`
4. Include if possible:
   - The synthetic fixture or deterministic mock record used
   - The exact simulated cue text
   - Device + browser
   - Whether simulation was on or off
5. Do not include real location data, bystander media, or personal walk recordings.

**Do not** upload videos that identify bystanders without consent.

## Other contributions

- Bug fixes, accessibility improvements (ARIA, contrast, larger targets)
- Docs and translations
- Offline map-adapter truthfulness and test improvements
- OGX provider improvements: https://github.com/aeyemovment/ogx-provider-eyewalker

## Development

```bash
git clone https://github.com/aeyemovment/eyeWalker-v1.1.git
cd eyeWalker-v1.1
# PWA lives in docs/ — served via GitHub Pages from /docs
# Open docs/pwa.html locally or use: python3 -m http.server -d docs 8080
```

## Code of conduct expectations

- Claim-safe language only (research prototype; not a medical device).
- Never remove the safety banner from the PWA.
- Path-scoped license: PolyForm Noncommercial by default; only exact files in
  the `DUAL_LICENSE.md` allowlist use MIT.

## License on contributions

`DUAL_LICENSE.md` controls the license assignment for each contributed path.
New files default to PolyForm Noncommercial unless that exact path is added to
the authoritative MIT allowlist through an explicit reviewed change.
