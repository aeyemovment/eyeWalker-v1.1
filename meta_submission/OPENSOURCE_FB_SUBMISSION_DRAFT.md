# Meta Open Source Portal draft — eyeWalker v1.0

**Portal:** https://opensource.fb.com (or current Meta open-source project submission flow)  
**Category:** **Accessibility**  
**Project:** eyeWalker  
**Org / builder:** NeuroAgent AI  
**Source:** https://github.com/aeyemovment/eyeWalker  

---

## Submission form fields (paste-ready)

### Project name
```
eyeWalker
```

### One-line tagline (≤120 chars)
```
Assistive research prototype: world-vision cues for navigation with vision impairment — not a medical device.
```

### Short description (elevator, ~300–500 chars)
```
eyeWalker is an open research prototype for assistive navigation. It explores real-time obstacle cues and short guidance phrases (e.g. “trash bin 2.1m ahead, step left 0.5m”) from camera + location context. Built by NeuroAgent AI for people with rare neurologic diseases affecting vision and all other neurologic/ophthalmologic causes of visual impairment. Assistive only—not a cane/guide dog replacement and not a medical device.
```

### Long description / About the project

```
eyeWalker v1.0 is an open-source research prototype for assistive outdoor/indoor path cues for people with vision impairment.

Origin: daily post-lunch harbor walks in Baltimore (~3.66 mi). Sidewalks, piers, and marinas are poorly covered by car maps; benches, bins, and unguarded pier edges create practical navigation friction. eyeWalker explores whether open world models + maps + spatial-audio-style guidance can help as a *complement* to traditional mobility tools.

Who we build for (NeuroAgent AI):
- Rare neuro-immunologic disease with visual involvement (e.g. NMOSD, MOGAD, optic neuritis)
- Rare mitochondrial/genetic optic neuropathies (e.g. LHON)
- Cortical and other neurologic causes (e.g. CVI)
- Broader neurologic and ophthalmologic causes of visual impairment (glaucoma, DR, AMD, hemianopia, TBI-related vision loss, and others)

What the stack explores:
- Perception from smartphone or Meta Ray-Ban-class RGB + GPS/IMU context
- Obstacle taxonomy (static, ground hazard, dynamic, overhead) as a research interface
- Short guidance strings suitable for TTS / spatial audio experimentation
- Dual license: PolyForm Noncommercial for core research code; MIT for mobile/PWA surfaces to ease open distribution

Safety (required):
This is assistive, not replacement for cane/guide dog. Always keep traditional mobility aid. This is alpha. It is a research prototype for users and developers to improve upon. Not a medical device. Not for clinical diagnosis or treatment.

Public demos:
- GitHub Pages PWA: https://aeyemovment.github.io/eyeWalker/
- Hugging Face Space (static free tier): https://huggingface.co/spaces/NeuroAgentAI/eyeWalker
- Source + Meta pack: https://github.com/aeyemovment/eyeWalker (meta_submission/)
```

### Category
```
Accessibility
```

### Secondary tags / topics (if multi-select)
```
Accessibility, Computer Vision, Mobile, Open Source AI, Assistive Technology, Research Prototype
```

### Primary language(s)
```
Python, TypeScript/JavaScript (PWA/mobile), Markdown
```

### License
```
Dual license:
- PolyForm Noncommercial 1.0.0 — core (eyewalker/, research stack)
- MIT — mobile/ and PWA docs (docs/pwa.html, docs/index.html)
See DUAL_LICENSE.md and LICENSE / LICENSE-MIT in the repository.
```

### Repository URL
```
https://github.com/aeyemovment/eyeWalker
```

### Homepage / demo URLs
```
https://aeyemovment.github.io/eyeWalker/
https://aeyemovment.github.io/eyeWalker/pwa.html
https://huggingface.co/spaces/NeuroAgentAI/eyeWalker
https://neuroagentai-eyewalker.static.hf.space/
```

### Documentation URLs
```
https://github.com/aeyemovment/eyeWalker/blob/main/README.md
https://github.com/aeyemovment/eyeWalker/blob/main/SAFETY.md
https://github.com/aeyemovment/eyeWalker/blob/main/docs/ARCHITECTURE.md
https://github.com/aeyemovment/eyeWalker/tree/main/meta_submission
```

### Contact email
```
info@neuroagent.ai
```

### Maintainer / GitHub org or user
```
aeyemovment (GitHub) · NeuroAgentAI (Hugging Face)
```

### Why Meta / Ray-Ban relevance (optional free-text)

```
eyeWalker is designed around wearable + phone camera contexts (including Meta Ray-Ban-class capture paths in the research architecture). We publish open interfaces and a MIT-licensed PWA surface so Meta open-source, accessibility, and Llama Stack tool ecosystems can evaluate and extend assistive navigation research without clinical claims.
```

### Safety / ethics statement (if asked)

```
eyeWalker is a research prototype. It must never be marketed as a medical device or as a replacement for cane, guide dog, or certified orientation & mobility training. All public surfaces carry assistive-only disclaimers. Outputs are advisory; false negatives/positives are expected. Suitable for developer experimentation and controlled user testing with traditional mobility aids retained at all times.
```

### Logo / media
```
https://raw.githubusercontent.com/aeyemovment/eyeWalker/main/docs/neuroagent_eye_logo.png
https://raw.githubusercontent.com/aeyemovment/eyeWalker/main/docs/demo.gif
https://raw.githubusercontent.com/aeyemovment/eyeWalker/main/docs/eye_walker_github_banner.webp
```

---

## Cover email / note (if portal asks for a short message)

**Subject:** eyeWalker v1.0 — Accessibility research prototype (NeuroAgent AI)

```
Hello Meta Open Source team,

Please find eyeWalker v1.0, an open research prototype for assistive navigation cues for people with vision impairment, submitted under Accessibility.

• Source: https://github.com/aeyemovment/eyeWalker
• PWA demo: https://aeyemovment.github.io/eyeWalker/pwa.html
• HF Space (static): https://huggingface.co/spaces/NeuroAgentAI/eyeWalker
• Dual license: PolyForm Noncommercial (core) + MIT (mobile/PWA)
• Safety: assistive only; not a medical device; not a cane/guide dog replacement

Built by NeuroAgent AI for rare neurologic diseases affecting vision and all other neurologic and ophthalmologic causes of visual impairment.

We also prepared a Llama Stack tool manifest for a separate contribution PR (perception.navigation).

Thank you for considering accessibility-oriented research software.
— NeuroAgent AI / Kemar Green
```

---

## Manual steps remaining (operator)

1. Open Meta open-source project submission form (opensource.fb.com or linked “submit a project” flow).  
2. Paste fields above; attach logo/demo if upload slots exist.  
3. Confirm category **Accessibility**.  
4. Keep claims bounded: research prototype / assistive / not medical device.  
5. After submit, file the Llama Stack PR using `LLAMA_STACK_PR_DRAFT.md`.  
6. Log portal confirmation ID in `meta_submission/META_SUBMISSION_CHECKLIST.md`.
