# Llama Stack / OGX contribution — LIVE

> **Status:** Opened against OGX (Llama Stack successor).  
> **Provider repo:** https://github.com/aeyemovment/ogx-provider-eyewalker  
> **Docs PR:** https://github.com/ogx-ai/ogx/pull/6346  
> **Note:** `meta-llama/llama-stack` redirects to `ogx-ai/ogx`. External tools are listed as out-of-tree providers.

---

# Llama Stack PR draft — eyeWalker v1.0

**Target repo:** https://github.com/meta-llama/llama-stack  
**Source tool JSON:** `meta_submission/llama_stack_tool.json`  
**Upstream project:** https://github.com/aeyemovment/eyeWalker  
**Author:** NeuroAgent AI · contact: info@neuroagent.ai / kemar@hazyeyesai.com  

---

## PR title

```
feat: add eyeWalker perception.navigation tool (assistive research prototype)
```

---

## PR description (paste into GitHub)

### Summary

This PR proposes **eyeWalker** as a **perception.navigation** tool for Llama Stack: a research prototype that turns RGB + GPS/IMU context into **obstacle lists + bypass guidance + spatial-audio-style text cues** for people with vision impairment.

It is **assistive only** — not a cane/guide-dog replacement, **not a medical device**, and **not for clinical diagnosis or treatment**.

Built by **NeuroAgent AI** for people living with **rare neurologic diseases affecting vision** (e.g. NMOSD, MOGAD, LHON, CVI) and **all other neurologic and ophthalmologic causes of visual impairment**.

### Links

| Resource | URL |
|----------|-----|
| Source repo | https://github.com/aeyemovment/eyeWalker |
| GitHub Pages PWA | https://aeyemovment.github.io/eyeWalker/ |
| HF Space (static demo) | https://huggingface.co/spaces/NeuroAgentAI/eyeWalker |
| Static host | https://neuroagentai-eyewalker.static.hf.space/ |
| Tool manifest | `meta_submission/llama_stack_tool.json` in the source repo |
| Safety | https://github.com/aeyemovment/eyeWalker/blob/main/SAFETY.md |

### Motivation

- WHO estimates **~2.2B** people with vision impairment globally; navigation disability remains high even after rehab that stops at cane/guide dog.
- Everyday harbor/pier/sidewalk paths are poorly represented in car-centric maps (OSM `footway` / `pier` / marinas).
- open tool surface on Llama Stack lets accessibility and agent developers experiment with **claim-bounded**, **open**, **research-prototype** navigation guidance.

### What this tool is / is not

**Is:**
- Open research prototype for developers and accessibility experimentation  
- Dual-licensed: **PolyForm Noncommercial** (core) + **MIT** (mobile/PWA surfaces)  
- Designed to emit structured obstacles + short guidance strings suitable for TTS/spatial audio  

**Is not:**
- A medical device or diagnostic product  
- A substitute for orientation & mobility training, cane, or guide dog  
- Production navigation safety certification  

### Tool contract (high level)

From `llama_stack_tool.json` (`version: 1.0.0`, `type: perception.navigation`):

**Inputs (conceptual):** RGB frame, GPS lat/lon, IMU accel/gyro, optional user speed  
**Outputs (conceptual):** obstacles[], safe_path, guidance_audio string, risk_level  

**Example guidance string:**  
`"Trash bin 2.1m ahead, center. Step left 0.5m."`

### Suggested tree layout in this repo

Maintainers: please adjust paths to match current Llama Stack conventions if different.

```text
# illustrative — match upstream layout
tools/eyewalker/   # or docs/external_tools/eyewalker/
  manifest.json    # copy of meta_submission/llama_stack_tool.json
  README.md         # short tool README + safety block
```

Registry-style entry (if applicable):

```json
{
  "name": "eyeWalker",
  "description": "Assistive research prototype: VLM-oriented obstacle cues + guidance text for vision impairment navigation (not a medical device).",
  "category": "perception.navigation",
  "author": "NeuroAgent AI",
  "license": "PolyForm Noncommercial + MIT (mobile)",
  "url": "https://github.com/aeyemovment/eyeWalker",
  "tags": ["accessibility", "vision-impairment", "research-prototype", "spatial-audio"]
}
```

### Safety (required in tool docs)

> This is assistive, not replacement for cane/guide dog. Always keep traditional mobility aid. This is alpha. It is a research prototype for users and developers to improve upon. **Not a medical device. Not for clinical diagnosis or treatment.**

### Testing notes for reviewers

1. Read `SAFETY.md` and dual-license notes in the source repo.  
2. Exercise the **static PWA** demos (Pages / HF) for UX only — current HF free tier hosts **static**, not full Gradio GPU inference.  
3. Treat live VLM path as **prototype / mock-capable** unless a GPU runtime is provisioned.  
4. Confirm guidance strings remain **advisory** (no hard guarantees of obstacle completeness).

### Checklist

- [x] Public source repository with v1.0 tag/version  
- [x] Explicit research-prototype / not-medical-device language  
- [x] Dual license documented (PolyForm core + MIT mobile)  
- [x] Tool JSON v1.0.0 with inputs/outputs/examples  
- [ ] Maintainer path/registry placement (this PR)  
- [ ] CI / schema validation per Llama Stack contribution guide  

### Contact

NeuroAgent AI · https://github.com/aeyemovment/eyeWalker  
Issues: GitHub Issues on the source repo  

Thank you for reviewing accessibility-oriented research tooling for the Llama Stack ecosystem.

---

## Commit message (if opening PR from a fork)

```
feat: add eyeWalker perception.navigation tool

Assistive research prototype for vision-impairment navigation cues
(VLM-oriented obstacles + guidance text). Not a medical device.

Source: https://github.com/aeyemovment/eyeWalker
Author: NeuroAgent AI
```

## Branch name suggestion

```
feat/eyewalker-perception-navigation-tool
```
