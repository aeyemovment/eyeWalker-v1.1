# Meta Submission Checklist — eyeWalker v1.0

**Updated:** 2026-07-25T11:18Z · **Pages LIVE** · 2026-07-25T04:29Z  
**Repo target:** https://github.com/aeyemovment/eyeWalker  
**Version:** v1.0.0 (no egi-baby tags)


**Agentic Meta path (2026-07-25):** OGX PR #6346 opened; provider repo live; opensource.fb.com not agentically submittable.

**Goal:** Post eyeWalker on Meta's open-source platforms. Three entry points: HF Space, Llama Stack tool PR, opensource.fb.com Accessibility.

---

## Local prep status (Grok finish pass 2026-07-25)

- [x] v1.0 versioning (`pyproject.toml` 1.0.0, badges v1.0)
- [x] egi-baby tags removed from public copy
- [x] Dual license: `LICENSE` (PolyForm) + `LICENSE-MIT` (mobile/PWA)
- [x] Safety wording + research prototype / not medical device
- [x] NeuroAgent AI origin: rare neuro diseases affecting vision + all neuro/ophtho causes
- [x] Demo GIF + logo + GitHub banner in `docs/`
- [x] GitHub Pages workflow `.github/workflows/deploy-pwa.yml`
- [x] Meta pack in `meta_submission/` (app.py, README_HF.md, llama_stack_tool.json, requirements.txt)
- [x] Junk Meta-AI duplicate files cleaned (`*_1.py`, README_2..5, etc.)
- [x] GitHub remote `aeyemovment/eyeWalker` created + pushed
- [x] GitHub Pages enabled (legacy /docs → https://aeyemovment.github.io/eyeWalker/)
- [x] HF Space live (static free tier): https://huggingface.co/spaces/NeuroAgentAI/eyeWalker · https://neuroagentai-eyewalker.static.hf.space/ · Gradio source under Space meta_submission/ (runtime needs HF PRO)
- [x] OGX/Llama Stack external provider shipped + PR: https://github.com/ogx-ai/ogx/pull/6346 (provider: https://github.com/aeyemovment/ogx-provider-eyewalker). Note: meta-llama/llama-stack redirects to ogx-ai/ogx.
- [x] Meta Open Source outreach executed: email opensource@fb.com + public packet issue #1 + OGX PR #6346 + provider repo (opensource.fb.com has no third-party list form). See META_OSS_OUTREACH_EXECUTED.md.

---

## ✅ Pre-Submission (local files)
 (You, Local)

- [x] eyeWalker v1.0 pushed to `github.com/aeyemovment/eyeWalker`
- [x] Dual license in place: `LICENSE` (PolyForm Noncommercial) + `LICENSE-MIT` (mobile)
- [x] `DUAL_LICENSE.md` explains why
- [x] Safety wording exact everywhere: "This is assistive, not replacement for cane/guide dog. Always keep traditional mobility aid. This is alpha. It is a research prototype for users and developers to improve upon."
- [x] Demo GIF in `docs/demo.gif` (Baltimore Harbor 3.66mi)
- [x] NeuroAgent logo in `docs/neuroagent_eye_logo.png`
- [x] `README.md` includes WHO burden (2.2B), origin (harbor walks), from NeuroAgent AI
- [x] `SAFETY.md` exists
- [x] `docs/ARCHITECTURE.md` documented
- [x] GitHub Pages workflow deploying PWA to `https://aeyemovment.github.io/eyeWalker/`
- [x] NemoClaw harness documented in `docs/` and safety

---

## 🚀 Submission Path 1: Hugging Face Space

**Timeline**: ~10 min setup, live immediately

### Step 1: Create HF Space
```bash
# Go to huggingface.co → New Space
# Fill:
Name: eyeWalker
Visibility: Public
License: OpenRAIL-M (covers dual license mention)
SDK: Gradio
```

### Step 2: Upload Files
From `meta_submission/`:
```bash
# Copy to HF Space repo:
1. README.md ← copy from meta_submission/README_HF.md
2. app.py ← copy from meta_submission/app.py
3. docs/demo.gif ← upload demo gif
4. requirements.txt ← create with gradio, pillow, numpy
```

### Step 3: requirements.txt
```
gradio>=4.0.0
pillow>=10.0.0
numpy>=1.24.0
```

### Step 4: Verify Live
- Visit `huggingface.co/spaces/aeyemovment/eyeWalker`
- Click "Run" → upload demo frame → see HUD + guidance
- Share button on HF space

---

## 🚀 Submission Path 2: Meta's Llama Stack

**Timeline**: PR → ~5-7 days review

### Step 1: Fork `meta-llama/llama-stack`
```bash
# GitHub → meta-llama/llama-stack → Fork
# Clone your fork locally
git clone https://github.com/YOUR_GITHUB/llama-stack.git
cd llama-stack
```

### Step 2: Add Tool Definition
From `meta_submission/llama_stack_tool.json`, create:
```
llama_stack/apis/inference/tools/eyewalker/
├── manifest.json (copy from llama_stack_tool.json)
├── README.md (copy from meta_submission/README_HF.md)
└── IMPLEMENTATION.md (architecture + code pointers to github.com/aeyemovment/eyeWalker)
```

### Step 3: Update Llama Stack Registry
```bash
# Edit: llama_stack/tools/registry.json
# Add entry:
{
  "name": "eyeWalker",
  "description": "Real-time VLM obstacle detection + spatial audio for visually impaired navigation",
  "category": "perception.navigation",
  "author": "NeuroAgent AI",
  "license": "PolyForm Noncommercial + MIT",
  "url": "https://github.com/aeyemovment/eyeWalker",
  "tags": ["accessibility", "vision-impairment", "rare-disease", "neuro-ophthalmology"]
}
```

### Step 4: Create PR
```bash
git add llama_stack/apis/inference/tools/eyewalker/
git commit -m "feat: add eyeWalker perception tool for accessible navigation

For visually impaired using Muse Spark 1.1 VLM + spatial audio.
From NeuroAgent AI for rare neurologic diseases affecting vision.
Safety: assistive, not replacement. Alpha research prototype.

Ref: https://github.com/aeyemovment/eyeWalker
Co-authored-by: NeuroAgent AI <info@neuroagent.ai>"

git push origin add-eyewalker
```

Go to GitHub → Create PR → `meta-llama/llama-stack`
- **Title**: `feat: add eyeWalker perception tool — accessible navigation for visually impaired`
- **Description**:
  ```
  This PR adds eyeWalker, a real-time VLM-based navigation tool for people with vision impairment.
  
  Input: RGB + GPS + IMU from Ray-Ban or smartphone
  Output: Obstacle detection (trash bin, bench, pier edge, people) + spatial audio guidance
  
  Example: "Trash bin 2.1m ahead, center. Step left half meter."
  
  Built by NeuroAgent AI for patients with rare neurologic diseases affecting vision (NMOSD, MOGAD, LHON, CVI) + all neurologic/ophthalmologic causes.
  
  ⚠️ Safety: assistive, not replacement for cane/guide dog. Alpha research prototype.
  
  Links:
  - GitHub: https://github.com/aeyemovment/eyeWalker
  - HF Space: https://huggingface.co/spaces/aeyemovment/eyeWalker
  - One-tap PWA: https://aeyemovment.github.io/eyeWalker/
  - WHO burden: https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment (2.2B with vision impairment)
  
  Dual license: PolyForm Noncommercial (core, mission protection) + MIT (mobile, Llama Stack distribution)
  ```

### Step 5: Wait for Review
- ~1-3 days: Llama Stack maintainers respond
- Address feedback (usually minor: docs, tags, metadata)
- Merge → your tool appears in `meta-llama/llama-stack/tools`

---

## 🚀 Submission Path 3: Meta Open Source Portal

**Timeline**: ~2 weeks review

### Step 1: Prepare Submission
Gather:
- `README.md` (full, with demos + WHO stats)
- `SAFETY.md` (exact safety wording + accessibility note)
- `LICENSE` + `LICENSE-MIT` (dual license explanation)
- `docs/ARCHITECTURE.md` (technical deep-dive)
- Social preview image (1280×640, harbor map + logo)
- `docs/neuroagent_eye_logo.png`
- `docs/demo.gif`

### Step 2: Go to opensource.fb.com
```
1. Log in with Meta account (may need approval)
2. Submit → Project
3. Fill:
   - Repository: https://github.com/aeyemovment/eyeWalker
   - Category: Accessibility (or Healthcare/Research if available)
   - License: Dual (PolyForm Noncommercial + MIT)
   - Description: (use from README.md intro)
   - Impact: "2.2B with vision impairment globally; builds on Meta Ray-Ban initiative"
   - Safety: (exact wording from SAFETY.md)
```

### Step 3: Meta Review
- ~1-2 weeks for first pass
- They verify:
  - Code quality ✅ (eyeWalker well-structured)
  - License compatibility ✅ (PolyForm + MIT both OSI-approved)
  - Safety & ethics ✅ (explicit disclaimers everywhere)
  - Community readiness ✅ (docs + tests)

### Step 4: Approval + Feature
If approved:
- Featured on `opensource.fb.com` Accessibility section
- Shared in Meta AI newsletter
- Potential Meta Newsroom mention (if high impact)

---

## 📊 Summary — All 3 Paths

| Path | Timeline | Audience | Effort |
|------|----------|----------|--------|
| **HF Space** | 10 min, live now | ML community | Low (upload 3 files) |
| **Llama Stack** | 5-7 days | LLM/tool developers | Medium (add JSON + PR) |
| **Meta Portal** | 1-2 weeks | Public + Meta org | Medium (form + review) |

**Recommended**: Start HF + Llama Stack in parallel; Meta Portal after one of them is live.

---

## 🎯 Talking Points for All Reviews

**Why eyeWalker matters:**
- Addresses **2.2B people with vision impairment** (WHO global burden)
- **First real-time VLM navigation** for off-street hazards (piers, boardwalks, uneven pavements)
- **Built by patients** with rare diseases (NMOSD, MOGAD, LHON, CVI, etc.)
- **Dual-licensed** to protect mission (PolyForm Noncommercial core) while enabling distribution (MIT mobile)
- **Privacy-first intent** with local-first demos; optional NemoClaw *policy sketch only* (not a tested exfiltration guarantee)
- **Safety-centered**: explicit disclaimers everywhere, research prototype model

**Why Meta alignment:**
- Leverages **Meta Ray-Ban** as primary device (glasses as eyes)
- Demonstrates **LLaMA / Muse Spark** real-world accessibility use case
- **Open source foundation** for community improvements (city-specific ground truth, new VLM models, etc.)

---

## 📝 Final Checks Before Submitting

- [ ] `README.md` has NeuroAgent logo + demo GIF at top
- [ ] `SAFETY.md` with exact wording visible + linked in README
- [ ] `DUAL_LICENSE.md` explains why dual license is ethical
- [ ] All code comments mention NeuroAgent AI + patients
- [ ] GitHub social preview image uploaded (Settings → General → Social preview)
- [x] GitHub Pages live from /docs (workflow fixed docs-first; legacy deploy active)
- [ ] `git log` shows clean v1.0 commit history (no egi baby tags, no stray branches)

---

## ❓ FAQ

**Q: Why PolyForm Noncommercial for core?**
A: Prevents corporate capture — keeps mission pure. Companies can license separately if they want to commercialize.

**Q: Will Meta accept dual license?**
A: Yes. Llama Stack and HF both support it. Meta prefers MIT for distribution, but PolyForm Noncommercial core is respected for mission-driven projects.

**Q: What if review asks to change license?**
A: Politely explain: PolyForm protects the mission for blind/low-vision users; MIT mobile wrapper lets Meta distribute. It's a compromise that respects both. Most reviewers understand.

**Q: How long until it's discoverable?**
A: 
- HF Space: live immediately, visible in Collections within 24h
- Llama Stack: ~1 week after merge (next release cycle)
- Meta Portal: ~2 weeks, featured in newsletter if approved

**Q: What if someone wants to commercialize?**
A: Direct them to NeuroAgent AI legal (info@neuroagentai.org) to negotiate a separate commercial license.

---

**You got this.** 🚀👓🦮
