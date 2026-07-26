# Privacy — eyeWalker v1.1

**Research prototype.** Not a medical device. Local-first posture preferred.

## Local-first (NemoClaw *optional* posture)

- Prefer processing on-device or on a machine you control.
- Optional NemoClaw docs describe a **policy harness sketch**, not a certified security product and not a guarantee that data “never leaves.”
- Omniverse adapter is an optional **synthetic sim stub** (disabled by default).

## Recording (PWA)

| Behavior | Rule |
|----------|------|
| Consent | REC and Save of recorded media require an **checked consent** box |
| Auto-record | **Off** — Start walk does **not** start REC |
| Revoke consent | Unchecking consent **stops** active REC |
| Pause | Pauses cue loop; resumes capture if REC was paused |
| Stop | Explicit **Stop** ends walk, stops REC, releases camera |
| Save | Finalizes active REC (stop + flush) before download; uses correct MIME/extension |
| GPS trail | **Requires recording consent.** Geolocation watch and trail append only while consent is checked; unchecking consent clears the trail and stops the watch. Export includes GPS only if consent still checked at Save |
| localStorage | Short VLM/sim cue log may be stored locally for the session; clearable by browser; not a cloud upload. Export of VLM log requires consent |

## What we do not claim

- No real-time face/plate blur unless a blur pipeline is actually applied (flags may say *requested* not *applied*).
- No GenCrypt / PQC product.
- No sale of personal navigation data.

## Contact

Privacy questions: `info@neuroagentai.org`

See also: `SAFETY.md`, `eyewalker/nemoclaw/README.md`, `eyewalker/omniverse/`.
