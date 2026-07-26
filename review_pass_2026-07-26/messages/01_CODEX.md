# Message for CODEX (step 1 of 5) — engineering / ship review

**You are Codex.** You are first in a sequential review chain.  
After you: Fable 5 → Spark Muse → Gemma → Legal (final before post).  
Operator will paste your reply into an outbox and hand forward manually.

---

## Mission

Review **eyeWalker v1.1 medical open-source** ship state driven by `Listen-to-me-rant-3.sh` (v1.1.0-ground: REC fix, hybrid VLM hooks, DT synthetic ritual, train pipeline).

**Scope:** engineering correctness, repo hygiene, PWA/Pages, synthetic data layout, risks that would break users or CI.  
**Out of scope:** marketing polish (later agents), full legal opinion (step 5).

---

## Canonical surfaces

- Repo: https://github.com/aeyemovment/eyeWalker-v1.1  
- Release: https://github.com/aeyemovment/eyeWalker-v1.1/releases/tag/v1.1.0  
- PWA: https://aeyemovment.github.io/eyeWalker-v1.1/pwa.html  
- Landing: https://aeyemovment.github.io/eyeWalker-v1.1/  
- HF Space (still titled v1.0): https://huggingface.co/spaces/NeuroAgentAI/eyeWalker  
- Script: `Listen-to-me-rant-3.sh` (attached / in package `context/`)

---

## Script intent (what it was supposed to do)

1. Set VERSION / stage `docs/training/{raw,frames,synthetic,exports}`  
2. Optionally ingest walk video → `train_from_video.sh`  
3. Ensure `docs/pwa.html`  
4. Commit/push + tag `v1.1.0-ground` if `gh` auth  
5. Echo PWA/train/hybrid/SAFETY reminders  

**Later operator pass** also created clean medical public repo `eyeWalker-v1.1` (NeuroAgent only; HazyEyes dual-use kept private).

---

## What you must return (structured)

### A. Verdict
`SHIP` | `SHIP_WITH_FIXES` | `HOLD`

### B. Engineering findings
Table: severity (blocker/high/med/low) · finding · file/path · fix

### C. Script review
- Broken paths / assumptions (`EYEWALKER_ROOT=$HOME/eyeWalker` vs new repo path)  
- Missing video handling  
- Unsafe `git push -f` / tag force  
- Medical OSS vs old HazyEyes assumptions  

### D. PWA / Pages
Confirm or flag: index, pwa, manifest, SW, icons, HTTPS installability

### E. Synthetic data
- Present in git under `docs/training/synthetic/`?  
- Fit for public? PII? path leaks (absolute local paths in JSON)?  
- Ready for HF Dataset or not  

### F. Top 5 fixes before Fable 5 sees copy

### G. One paragraph handoff to Fable 5
What Codex already checked so Fable 5 does not re-do eng deep dive.

---

## Constraints

- Not a medical device; flag any clinical-sounding claims in code/UI strings.  
- Do not invent HF Dataset existence (synthetic is in git; not confirmed as HF Dataset).  
- Prefer concrete paths and commands.

**Begin review now.**
