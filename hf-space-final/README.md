---
title: eyeWalker v1.0 — Real-time World Vision for the Visually Impaired
emoji: 👓
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
python_version: "3.12"
short_description: Real-time world vision for visually impaired
license: other
license_name: polyform-noncommercial-1.0.0
tags:
  - accessibility
  - vision-impairment
  - assistive-technology
  - vlm
  - obstacle-avoidance
  - spatial-audio
  - neuro-ophthalmology
  - baltimore-harbor
thumbnail: https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-spaces-lg-dark.svg
pinned: false
startup_duration_timeout: 10m
---

# eyeWalker v1.0 👓🦮 — World Vision for the Visually Impaired

**From NeuroAgent AI** — for patients with rare neurologic diseases affecting vision and all other neurologic and ophthalmologic causes of visual impairment.

> Real-time world vision: VLM obstacle avoidance. **"Trash bin 2.1m ahead, step left 0.5m."** Spatial audio guidance. From harbor walks that exposed the gap.

![Logo](https://raw.githubusercontent.com/aeyemovment/eyeWalker/main/docs/neuroagent_eye_logo.png)

### Safety — Critical ⚠️
**This is assistive, not replacement for cane/guide dog. Always keep traditional mobility aid. This is alpha. It is a research prototype for users and developers to improve upon.**

### The Gap WHO Calls Out
- **2.2 billion people** globally have near or distance vision impairment [WHO](https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment)
- **1 billion** preventable or yet to be addressed
- **2 of 3** in low-income countries without glasses
- **$411B** annual productivity loss

Traditional rehab stops at cane/dog. eyeWalker adds **real-time world vision**: VLM that sees bench, pier edge, cyclist at 2 o'clock and tells you how to get around.

### Origin — Baltimore Harbor 3.66mi
Inspired by daily post-lunch harbor walks — Fells Point, Frederick Douglass-Isaac Myers Maritime Park, Harbor Point, marinas where the map stops. Car maps don't know piers, sidewalks end, benches appear, pier edges have no rails. What if glasses that record walk could also be eyes that guide it?

### How It Works
- **Input:** Meta Ray-Ban or smartphone camera 30fps → 0.66Hz, GPS+IMU
- **Brain:** Muse Spark 1.1 VLM (open-vocab) + Depth Anything V2 + SAM walkable segmentation + VIO 6DoF
- **Ground Truth:** OSM `footway|pier|path|marina` via Overpass + Esri satellite <3yr, walkable graph from non-car pathways
- **Taxonomy:** static (bench, trash bin, bollard, cone), ground hazard (curb, puddle, pier edge), dynamic (person+dog, cyclist), overhead (branch, awning)
- **Output:** Binaural spatial audio at obstacle 3D position — "Pier edge 0.8m left unguarded, keep right"

### Demo Usage
1. Upload a sidewalk/pier/harbor photo or use webcam
2. Or click **Baltimore Harbor Demo Frame**
3. See HUD overlay + Guidance: trash bin 2.1m ahead step left
4. Check JSON for full detection + safe_path

*Current Space is mock for demo stability on cpu-basic. Upgrade path: swap mock with real `@spaces.GPU` Qwen2-VL 2B or Florence-2 on ZeroGPU.*

### Architecture
```
Ray-Ban / Smartphone (RGB+GPS+IMU)
  → Perception (VIO 6DoF + Depth V2 + VLM Spark + SAM)
  → Fusion (GPS coarse + VIO fine + OSM ground truth snap)
  → Obstacle ID + Risk (class, distance, TTC, velocity, user pace)
  → Real-time Avoidance Planner (Step LEFT 0.5m, rejoin 2m)
  → Spatial Audio (binaural at obstacle 3D pos)
```

### From NeuroAgent AI — Who We Build For
- Rare neuro-immunologic: NMOSD, MOGAD, optic neuritis, autoimmune encephalitis with visual involvement
- Rare mitochondrial/genetic: LHON, OPA1 optic atrophy, Wolfram, mitochondrial optic neuropathies
- Rare neurologic: IIH, optic nerve hypoplasia, CVI, posterior cortical atrophy
- All causes: glaucoma, diabetic retinopathy, AMD, retinitis pigmentosa, stroke hemianopia, TBI vision loss
- *If your vision loss is neurologic or ophthalmologic, rare or common — eyeWalker is for you.*

### Links
- **GitHub:** https://github.com/aeyemovment/eyeWalker
- **PWA One-Tap:** https://aeyemovment.github.io/eyeWalker/
- **Architecture:** https://github.com/aeyemovment/eyeWalker/blob/main/docs/ARCHITECTURE.md
- **WHO Fact Sheet:** https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment
- **NeuroAgent AI:** https://neuroagent.ai

### License — Dual
- **Core (`eyewalker/`):** PolyForm Noncommercial 1.0.0 — open for personal/research/education/non-profit/accessibility; not for commercial selling / SaaS without separate license
- **Mobile wrapper / PWA:** MIT — enables Meta platform distribution

Commercial license: open issue `commercial-license`.

### Meta Open Source Submission
Ready for opensource.fb.com — Category: Accessibility. Includes `llama_stack_tool.json` to PR to `meta-llama/llama-stack`. See `meta_submission/` folder in GitHub repo.

**Built in Baltimore. For the world. 👓🦮**
