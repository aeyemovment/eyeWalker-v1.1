# Privacy — eyeWalker v1.1

**Research prototype.** Not a medical device. Local-first posture preferred.

## Local-first (NemoClaw *optional* posture)

- Prefer processing on-device or on a machine you control.
- Optional NemoClaw docs describe a **policy harness sketch**, not a certified security product and not a guarantee that data “never leaves.”
- Omniverse adapter is an optional **synthetic sim stub** (disabled by default).

## Recording (PWA)

| Behavior | Rule |
|----------|------|
| Consent | One explicit control names and covers **local video recording plus precise GPS location/trail retention and export**; REC is blocked until it is checked |
| Auto-record/location | **Off** — Start simulated session does not start REC or precise GPS |
| Revoke consent | Unchecking consent stops the GPS watch immediately, clears the live coordinate and in-memory trail, and scrubs precise GPS from **every** retained `eyewalker_vlm_*` session key before awaiting idempotent REC finalization |
| Clear retained session data | The explicit **Clear retained session data** control revokes recording/location consent, stops new local cue retention for the page lifetime, removes every discoverable `eyewalker_vlm_*` key, discards in-memory recorder chunks/references, and reports whether deletion was confirmed. Re-consenting cannot recover the cleared video |
| Pause / Start | Pause pauses the cue loop and active MediaRecorder and immediately stops precise GPS collection. Tapping **Start** or **Resume** while paused resumes that same recorder and starts a new GPS watch rather than starting a second recorder |
| REC off | Toggling REC off stops precise GPS immediately, requests a final chunk, and waits for the recorder's final `dataavailable` and `stop` events. An asynchronous recorder error or missing `stop` event resolves through a bounded timeout, cleans its listeners, marks the media **incomplete**, and does not hang or reject the UI flow |
| Stop | Explicit **Stop** ends the walk, stops GPS collection, awaits the same REC finalization promise, then releases the camera |
| Save | Save awaits any active Stop / REC-off / revoke finalization before packaging, so an immediate Stop → Save includes the final chunk; the correct MIME/extension is used. Metadata records whether final media was confirmed or incomplete |
| GPS trail | **Requires the named video-and-location consent plus an active, unpaused MediaRecorder.** Pause, REC-off, Stop, revoke, error, and Clear stop the watch. Export includes retained trail points only if consent is still checked at Save |
| localStorage | Short synthetic cue logs may be stored under `eyewalker_vlm_*`; precise GPS is written only with consent. Revocation scans all matching keys. A failed rewrite removes the affected log fail-closed. Iteration, verification, or removal failures stop the sensitive collection path and show a visible **PRIVACY WARNING** telling the user to clear browser site data. The log is not a cloud upload; export requires consent |

## Synthetic cue and accessibility bounds

- This PWA does not execute a live detector. Simulation-on and simulation-off outputs therefore retain truthful `synthetic_only` provenance.
- Camera access is preview/record-only. Synthetic cues do not inspect camera pixels.
- Every generated simulated cue begins with `SIMULATED RESEARCH CUE:` and ends with `Keep your cane or guide dog. Not a medical device.`
- The visual guidance may refresh with the 700 ms research loop, but that element is not an ARIA live region. A separate polite live region and speech synthesis share a hard minimum interval so changing synthetic distances cannot flood announcements.

## What we do not claim

- No real-time face/plate blur unless a blur pipeline is actually applied (flags may say *requested* not *applied*).
- No GenCrypt / PQC product.
- No claim that personal recording or location data is anonymized, sold, or safe to upload.

## Contact

Privacy questions: `info@neuroagentai.org`

See also: `SAFETY.md`, `eyewalker/nemoclaw/README.md`, `eyewalker/omniverse/`.
