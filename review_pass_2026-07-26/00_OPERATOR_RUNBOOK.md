# Review pass runbook — eyeWalker v1.1 medical OSS  
**Date:** 2026-07-26  
**Operator:** Kemar (manual handoff — paste each message yourself)  
**Script basis:** `Listen-to-me-rant-3.sh` (v1.1.0-ground Spark Muse prep + Grok DT ritual)

---

## Order (do not skip)

| Step | Reviewer | Message file | Drop response in |
|------|----------|--------------|------------------|
| **1** | **Codex** | `messages/01_CODEX.md` | `outbox/01_codex_response.md` |
| **2** | **Fable 5** | `messages/02_FABLE5.md` | `outbox/02_fable5_response.md` |
| **3** | **Spark Muse** | `messages/03_SPARK_MUSE.md` | `outbox/03_spark_muse_response.md` |
| **4** | **Gemma** | `messages/04_GEMMA.md` | `outbox/04_gemma_response.md` |
| **5** | **Legal (final)** | `messages/05_LEGAL_FINAL.md` | `outbox/05_legal_response.md` |
| **POST** | Only if legal = **GO** | — | Public post / HF / social |

**Gate:** After Gemma, **stop**. Run **legal once**. **No posting** until legal returns **GO** (or GO with redlines applied).

---

## What is being reviewed

| Surface | URL / path |
|---------|------------|
| Public repo | https://github.com/aeyemovment/eyeWalker-v1.1 |
| Tag/release | `v1.1.0` |
| PWA (Pages) | https://aeyemovment.github.io/eyeWalker-v1.1/pwa.html |
| Landing | https://aeyemovment.github.io/eyeWalker-v1.1/ |
| HF Space (still v1.0 card) | https://huggingface.co/spaces/NeuroAgentAI/eyeWalker |
| Synthetic data (git, not HF Dataset yet) | `docs/training/synthetic/` (~360 DT rows) |
| Script | `context/Listen-to-me-rant-3.sh` |
| HazyEyes / dual-use | **PRIVATE** — not in this medical OSS package |

---

## How to pass messages (manual)

1. Open step N message file.  
2. Copy **entire** contents into that model/agent chat.  
3. Attach or paste links + `context/` files if the tool allows.  
4. Save their full reply into the matching `outbox/` file.  
5. Only then open step N+1 (include prior outbox summaries if helpful).  
6. After Gemma outbox exists → send **05_LEGAL_FINAL** only.  
7. If legal GO → post using `checklists/POST_CHECKLIST.md`.

---

## Hard constraints for every reviewer

- Medical / assistive **only** (NeuroAgent AI eyeWalker v1.1).  
- **Not** a medical device; no FDA / diagnostic / treatment claims.  
- Keep cane / guide dog language.  
- **No** HazyEyes R military/DARPA/NASA/SpaceX strategy pack in public copy.  
- Synthetic data tagged research-only.  
- Dual license: PolyForm NC core + MIT PWA.

---

## Package layout

```
review_pass_2026-07-26/
  00_OPERATOR_RUNBOOK.md          ← you are here
  messages/                       ← paste these in order
  context/                        ← script + safety + README snapshot
  checklists/                     ← review + post checklists
  outbox/                         ← paste agent replies here
```

Local path:  
`/Users/lesharicotsverts/eyeWalker-v1.1-oss/review_pass_2026-07-26/`
