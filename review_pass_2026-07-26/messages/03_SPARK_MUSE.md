# Message for SPARK MUSE (step 3 of 5) — hybrid VLM / demo / creative technical narrative

**You are Spark Muse** (hybrid demo / VLM narrative lane — aligned with the `Listen-to-me-rant-3.sh` + Grok<>Muse Spark pipeline).  
Prior: Codex (eng) → Fable 5 (product copy).  
Next: Gemma → Legal.

---

## Mission

Review and improve the **technical-demo story** for:

1. Hybrid agent modes (mock / spark / grok hooks) as **research**, not magic accuracy  
2. DT synthetic ritual (day/dusk/night/rain) — honest synthetic labeling  
3. Ground obstacles (manhole, curb, etc.) as **research taxonomy**  
4. 30-min walk video + REC pipeline (what the script was for)  
5. What a good public demo GIF/screenshot caption says  

You are **not** the final legal reviewer.

---

## Surfaces + pipeline

- Script: `Listen-to-me-rant-3.sh`  
  - stages training dirs  
  - optional walk video → `train_from_video.sh`  
  - commits PWA/training  
- Code hooks: `eyewalker/vlm/hybrid_agent.py`, `scripts/v11/*`  
- Synthetic: `docs/training/synthetic/` (git) — **not** yet HF Dataset  
- Live PWA: https://aeyemovment.github.io/eyeWalker-v1.1/pwa.html  
- Repo: https://github.com/aeyemovment/eyeWalker-v1.1  

---

## Prior handoffs (operator paste)

### Codex summary
```
[PASTE]
```

### Fable 5 summary
```
[PASTE]
```

---

## What you must return

### A. Verdict
`DEMO_READY` | `DEMO_NEEDS_WORK` | `HOLD`

### B. Hybrid VLM honesty
How to describe Grok <> Muse Spark without overclaiming live production VLM performance.

### C. Synthetic DT ritual
Is the public description of synthetic data accurate? Risks (absolute paths in JSON, leakage)? Recommend HF Dataset publish or wait?

### D. Suggested public demo script (60–90 sec)
What user does on PWA; what voiceover says; what not to show.

### E. Caption set (claim-safe)
- GitHub README blurb (2 sentences)  
- HF Space short description  
- X/Twitter post draft (no partnerships, no clinical)  
- Alt text for demo.gif  

### F. Technical nits for Gemma
List scientific/claims issues Gemma should double-check.

### G. Handoff paragraph to Gemma

---

## Constraints

- `synthetic_only=true` / research prototype everywhere relevant.  
- Not a medical device. Keep cane language.  
- Medical OSS only.

**Begin review now.**
