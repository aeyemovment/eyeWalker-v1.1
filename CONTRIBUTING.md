# Contributing to eyeWalker

Thank you for helping make assistive navigation research safer and more useful.

## Safety-critical: report missed obstacles

If eyeWalker **missed** a real hazard (false negative) or gave **wrong** guidance:

1. **Stop walking** and use your cane / traditional aid.  
2. Open a GitHub Issue: https://github.com/aeyemovment/eyeWalker-v1.1/issues/new  
3. Title: `MISSED_OBSTACLE: <short description>`  
4. Include if possible:
   - Approximate location (city / pier / sidewalk type) — **optional**, no need for exact home address  
   - What the obstacle was (e.g. bike, curb, overhanging branch)  
   - What the app said (or that it said nothing)  
   - Device + browser  
   - Whether camera was on or demo mode  
5. Label mentally as **safety** — maintainers prioritize these over features.

**Do not** upload videos that identify bystanders without consent.

## Other contributions

- Bug fixes, accessibility improvements (ARIA, contrast, larger targets)  
- Docs and translations  
- Map/OSM walkable-graph improvements  
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
- Dual license: core PolyForm Noncommercial; mobile/PWA MIT — see `DUAL_LICENSE.md`.

## License on contributions

By contributing, you agree your contributions are dual-licensed consistently with this repository’s dual-license model unless otherwise stated.
