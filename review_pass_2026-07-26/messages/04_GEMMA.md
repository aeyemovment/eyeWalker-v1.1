# Message for GEMMA (step 4 of 5) — adversarial / quality / claims review

**You are Gemma.** You are the **last model review before legal**.  
Prior: Codex → Fable 5 → Spark Muse.  
Next: **Legal final only** — then post if legal GO.

Be skeptical. Prefer **HOLD** over soft ship if public claims are wrong.

---

## Mission

Adversarial review of the **public eyeWalker v1.1 medical OSS** package and any proposed post/demo copy from prior agents.

Focus:

1. False or inflated claims (accuracy, clinical, partners, “production”)  
2. Safety language gaps  
3. Version confusion (HF v1.0 vs git v1.1)  
4. Synthetic data misrepresentation  
5. License / attribution mistakes  
6. Anything that looks dual-use or non-medical that leaked into public  

---

## Surfaces

- https://github.com/aeyemovment/eyeWalker-v1.1  
- https://aeyemovment.github.io/eyeWalker-v1.1/pwa.html  
- https://huggingface.co/spaces/NeuroAgentAI/eyeWalker  
- Synthetic in-repo only unless proven otherwise  
- Script origin: `Listen-to-me-rant-3.sh`

---

## Prior handoffs (operator paste)

### Codex
```
[PASTE]
```

### Fable 5
```
[PASTE]
```

### Spark Muse
```
[PASTE]
```

---

## What you must return

### A. Verdict
`PASS_TO_LEGAL` | `PASS_TO_LEGAL_WITH_REDLINES` | `HOLD_DO_NOT_POST`

### B. Blockers (must fix before legal or post)
Numbered list.

### C. Redlines
Exact phrase → replace with safer phrase (table).

### D. Scorecard (0–5)
| Dimension | Score | Note |
|-----------|-------|------|
| Safety clarity | | |
| Claim honesty | | |
| Version consistency | | |
| Synthetic data honesty | | |
| License clarity | | |
| User risk if they trust the app | | |

### E. Final public blurb (≤120 words) you would allow
If you would not allow any, say so.

### F. Questions for legal (max 8)
Only issues legal must opine on.

### G. Handoff sentence to Legal
One sentence: pass / pass with redlines / hold.

---

## Constraints

- Assume worst-case reader: patient, regulator, journalist.  
- No benefit of the doubt on clinical language.  
- Medical OSS lane only.

**Begin adversarial review now.**
