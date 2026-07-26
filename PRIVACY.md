# Privacy — eyeWalker v1.1

**From NeuroAgent AI.** Research prototype. Not a medical device.

## Local-first (NemoClaw posture)

eyeWalker is designed **local-first**:

| Data | Default behavior |
|------|------------------|
| **Camera RGB** | Processed **on-device** in the browser PWA for demo/mock HUD. Not uploaded by the default static PWA. |
| **GPS / location** | Read in-browser for on-screen coordinates only when you Start Walking and grant permission. Not uploaded by default. |
| **Microphone** | Not required for the default one-tap walk demo (speech is **output** via Web Speech API). |
| **Account login** | Not required for the public static PWA. |

## Consent for any future remote path

If a future build enables a **remote VLM / cloud endpoint**:

1. It must be **opt-in** (explicit user action).  
2. Users must be told what leaves the device (e.g. frames, coarse GPS).  
3. No silent background upload of GPS + RGB.  
4. Users can revoke permission via browser site settings.

The OGX provider package may call an optional `endpoint_url`; if unset, it stays in **research mock** mode with no network inference.

## Third parties

- GitHub Pages / Hugging Face host **static files** you request by opening the site.  
- Browser vendors handle permission prompts for camera/location.  
- We do not sell personal navigation data.

## Contact

Privacy questions: `info@neuroagentai.org`

See also: `SAFETY.md`, `eyewalker/nemoclaw/` in this repository.
