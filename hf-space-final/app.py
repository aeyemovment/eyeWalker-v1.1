#!/usr/bin/env python3
"""
eyeWalker v1.0 — Hugging Face Gradio Demo
Real-time world vision for visually impaired — VLM obstacle avoidance.
From NeuroAgent AI for patients with rare neurologic diseases affecting vision.

Inspired by daily post-lunch harbor walks — 3.66mi loop around Baltimore Fells Point,
Frederick Douglass-Isaac Myers Maritime Park, Harbor Point.

Safety: Assistive, not replacement for cane/guide dog. Alpha research prototype.
"""

import spaces  # MUST be before torch / CUDA imports for ZeroGPU
import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import math
from typing import List, Dict, Tuple
import torch  # preinstalled on ZeroGPU, spaces patches it

CSS = """
#col-container { max-width: 1250px; margin: 0 auto; }
.dark .gradio-container { color: var(--body-text-color); }
.safety-banner {
  background: #ffcc00; color: #000; padding: 14px 18px;
  border-radius: 12px; font-weight: 800; text-align: center;
  margin-bottom: 16px; font-size: 15px;
  border: 2px solid #000;
}
.hero-sub { color: #6b7280; font-size: 14px; margin-top: -8px; }
.who-badge { background: #fee2e2; color: #991b1b; padding: 6px 12px; border-radius: 8px; display: inline-block; font-weight: 600; font-size: 13px; }
.from-badge { background: #ede9fe; color: #5b21b6; padding: 6px 12px; border-radius: 8px; display: inline-block; font-weight: 600; font-size: 13px; margin-left: 8px; }
"""

# Baltimore Harbor reference GPS (center of 3.66mi loop)
HARBOR_LAT = 39.2813
HARBOR_LON = -76.6082

OBSTACLE_TAXONOMY = [
    {"id": "trash_bin", "label": "trash bin / trash can", "risk_base": "HIGH", "category": "static"},
    {"id": "bench", "label": "bench blocking sidewalk", "risk_base": "MEDIUM", "category": "static"},
    {"id": "pier_edge", "label": "pier edge drop-off (unguarded)", "risk_base": "HIGH", "category": "ground hazard"},
    {"id": "bollard", "label": "bollard / post", "risk_base": "MEDIUM", "category": "static"},
    {"id": "person_dog", "label": "person with dog", "risk_base": "HIGH", "category": "dynamic"},
    {"id": "cyclist", "label": "cyclist approaching", "risk_base": "HIGH", "category": "dynamic"},
    {"id": "low_branch", "label": "low-hanging branch", "risk_base": "MEDIUM", "category": "overhead"},
    {"id": "puddle", "label": "puddle / uneven pavement", "risk_base": "LOW", "category": "ground hazard"},
    {"id": "construction_cone", "label": "construction cone", "risk_base": "MEDIUM", "category": "static"},
]

RISK_COLOR = {"HIGH": (220, 38, 38), "MEDIUM": (234, 88, 12), "LOW": (34, 197, 94)}

class MockVLMBrain:
    """Mock VLM brain — simulates Muse Spark 1.1 + Depth + SAM output for Baltimore Harbor."""

    def __init__(self):
        self.step = 0
        self.route_progress = 0.0

    def detect(self, image: Image.Image) -> List[Dict]:
        """Detect obstacles in frame (mock, route-aware)."""
        w, h = image.size if image else (1080, 1920)
        # Deterministic pseudo-random based on step to avoid flicker hell
        rnd = random.Random(self.step * 7919)
        num_obs = rnd.randint(1, 4)
        chosen = rnd.sample(OBSTACLE_TAXONOMY, num_obs)

        results = []
        for i, obs in enumerate(chosen):
            # Distance logic: pier edge is closest in harbor sections
            if obs["id"] == "pier_edge" and self.route_progress > 0.3:
                dist = rnd.uniform(0.6, 1.4)
            else:
                dist = rnd.uniform(1.0, 5.5)
            angle = rnd.uniform(-60, 60) + (math.sin(self.step * 0.05 + i) * 15)
            # Dynamic velocity
            vel = 0.0
            if obs["category"] == "dynamic":
                vel = rnd.uniform(0.8, 2.2)
            # Confidence
            conf = rnd.uniform(0.82, 0.98)

            # Urgency bump if close
            urgency = obs["risk_base"]
            if dist < 1.2:
                urgency = "HIGH"
            elif dist < 2.5 and urgency == "LOW":
                urgency = "MEDIUM"

            results.append({
                "class": obs["id"],
                "label": obs["label"],
                "distance_m": round(dist, 2),
                "bearing_deg": round(angle, 1),
                "category": obs["category"],
                "urgency": urgency,
                "confidence": round(conf, 3),
                "velocity_ms": round(vel, 2) if vel else 0.0,
                "is_moving": obs["category"] == "dynamic"
            })
        self.step += 1
        self.route_progress = (self.route_progress + 0.007) % 1.0
        return sorted(results, key=lambda x: x["distance_m"])

    def plan_avoidance(self, obstacles: List[Dict]) -> Dict:
        """Generate avoidance guidance from highest-risk obstacle."""
        if not obstacles:
            return {
                "instruction": "Path clear. Continue straight 5 meters.",
                "direction": "STRAIGHT",
                "lateral_m": 0.0,
                "distance_m": 5.0,
                "rejoin_m": 0.0,
                "duration_s": 4
            }
        high = [o for o in obstacles if o["urgency"] == "HIGH"]
        target = high[0] if high else obstacles[0]

        bearing = target["bearing_deg"]
        # Simple rule: if obstacle is left of center, go right, else left.
        # If it's dead center, pick side with more clearance (random for demo)
        if abs(bearing) < 10:
            direction = random.choice(["LEFT", "RIGHT"])
        elif bearing < 0:
            direction = "RIGHT"
        else:
            direction = "LEFT"

        lateral = round(random.uniform(0.4, 0.8), 2)
        rejoin = round(random.uniform(1.5, 3.0), 1)

        instr_templates = {
            "trash_bin": f"Trash bin {target['distance_m']:.1f}m ahead, center. Step {direction.lower()} {lateral}m, then straight.",
            "bench": f"Bench blocking full sidewalk at {target['distance_m']:.0f}m. Go {direction.lower()} around, {lateral}m, rejoin in {rejoin}m.",
            "pier_edge": f"Pier edge {target['distance_m']:.1f}m {direction.lower()}, unguarded drop. Keep {direction.lower()}, slow.",
            "person_dog": f"Person with dog approaching {target['velocity_ms']:.1f} m/s from {bearing:.0f}°, {target['distance_m']:.1f}m. Hold {direction.lower()}, wait.",
            "cyclist": f"Cyclist {target['distance_m']:.1f}m at {bearing:.0f}°, {target['velocity_ms']:.1f} m/s. Step {direction.lower()} {lateral}m, hold.",
            "low_branch": f"Low branch {target['distance_m']:.1f}m ahead, overhead. Duck slightly, step {direction.lower()} {lateral}m.",
            "bollard": f"Bollard {target['distance_m']:.1f}m ahead. Step {direction.lower()} {lateral}m.",
            "puddle": f"Uneven pavement / puddle {target['distance_m']:.1f}m. Step {direction.lower()} {lateral}m.",
            "construction_cone": f"Construction cone {target['distance_m']:.1f}m. Go {direction.lower()} {lateral}m, rejoin {rejoin}m."
        }
        instruction = instr_templates.get(target["class"], f"{target['label']} {target['distance_m']:.1f}m ahead. Step {direction.lower()} {lateral}m.")

        return {
            "instruction": instruction,
            "direction": direction,
            "lateral_m": lateral,
            "distance_m": target["distance_m"],
            "rejoin_m": rejoin,
            "duration_s": 2,
            "target_class": target["class"]
        }


brain = MockVLMBrain()


def draw_hud(image: Image.Image, obstacles: List[Dict], plan: Dict) -> Image.Image:
    """Draw HUD overlay with obstacle markers and guidance."""
    if image is None:
        image = create_demo_frame()

    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")
    w, h = image.size
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")

    # Center crosshair (user heading)
    cx, cy = w // 2, int(h * 0.55)
    cross_col = (0, 255, 0, 220)
    draw.line([(cx - 28, cy), (cx + 28, cy)], fill=cross_col, width=2)
    draw.line([(cx, cy - 28), (cx, cy + 28)], fill=cross_col, width=2)
    # FOV guides
    draw.line([(cx, cy), (cx - w//3, h)], fill=(100, 255, 100, 80), width=1)
    draw.line([(cx, cy), (cx + w//3, h)], fill=(100, 255, 100, 80), width=1)

    for obs in obstacles:
        angle_rad = math.radians(obs["bearing_deg"])
        # Map polar to screen: 60deg FOV = 0.6*w, distance 0-6m = 0.4*h
        max_disp = 6.0
        dist_norm = min(obs["distance_m"] / max_disp, 1.0)
        # Further = closer to center horizon, nearer = lower
        depth_y = cy + (1.0 - dist_norm) * 0.5 * (h - cy) + dist_norm * 0.3 * h * 0.2
        lateral_x = math.sin(angle_rad) * dist_norm * w * 0.45
        ox = int(cx + lateral_x)
        oy = int(depth_y)

        rgba = RISK_COLOR.get(obs["urgency"], (200, 200, 200)) + (230,)
        s = 18 if obs["urgency"] == "HIGH" else 14
        # X marker
        draw.line([(ox - s, oy - s), (ox + s, oy + s)], fill=rgba, width=3)
        draw.line([(ox - s, oy + s), (ox + s, oy - s)], fill=rgba, width=3)
        # Glow dot
        draw.ellipse([(ox - 4, oy - 4), (ox + 4, oy + 4)], fill=rgba)

        label = f"{obs['class'][:12]} {obs['distance_m']:.1f}m {obs['urgency']}"
        # Text background
        tb = draw.textbbox((ox + 10, oy - 10), label)
        draw.rectangle([(tb[0]-4, tb[1]-2), (tb[2]+4, tb[3]+2)], fill=(0,0,0,180))
        draw.text((ox + 10, oy - 10), label, fill=rgba)

    # Bottom banner guidance
    banner_h = 82
    draw.rectangle([(0, h - banner_h), (w, h)], fill=(0, 0, 0, 200))
    guid_text = plan.get("instruction", "Path clear")
    # Word wrap manually for PIL
    draw.text((18, h - 68), f"GUIDANCE: {guid_text}", fill=(0, 255, 130, 255))
    risk = "HIGH" if any(o["urgency"] == "HIGH" for o in obstacles) else "MEDIUM" if obstacles else "LOW"
    draw.text((18, h - 32), f"Risk: {risk} | Obstacles: {len(obstacles)} | GPS {HARBOR_LAT:.4f},{HARBOR_LON:.4f} | Step {brain.step}", fill=(200,200,200,200))

    return overlay


def create_demo_frame(seed: int = 0) -> Image.Image:
    """Generate synthetic Baltimore Harbor demo frame with pier texture."""
    rnd = random.Random(seed)
    w, h = 960, 1280
    img = Image.new("RGB", (w, h), (18, 32, 48))
    draw = ImageDraw.Draw(img)

    # Sky - gradient
    for y in range(int(h*0.38)):
        t = y / (h*0.38)
        c = int(24 + t*40)
        draw.line([(0, y), (w, y)], fill=(c, c+10, c+30))
    # Water
    for y in range(int(h*0.58), h):
        t = (y - h*0.58) / (h*0.42)
        c = int(10 + t*8)
        draw.line([(0, y), (w, y)], fill=(c, c+15, c+25))

    # Pier planks - vertical
    pier_w = 360
    pier_x0 = w//2 - pier_w//2
    pier_x1 = w//2 + pier_w//2
    draw.rectangle([(pier_x0, int(h*0.2)), (pier_x1, h)], fill=(88, 72, 58))
    for x in range(pier_x0, pier_x1, 36):
        draw.line([(x, int(h*0.2)), (x, h)], fill=(72, 58, 46), width=1)
    for y in range(int(h*0.2), h, 48):
        draw.line([(pier_x0, y), (pier_x1, y)], fill=(110, 92, 76), width=1)

    # Small harbor details
    # Bench
    bx = w//2 + rnd.randint(-80, 80)
    by = int(h*0.55)
    draw.rectangle([(bx-40, by-8), (bx+40, by+4)], fill=(120, 100, 80))
    # Trash bin
    tx = w//2 + rnd.randint(20, 120)
    ty = int(h*0.68)
    draw.rectangle([(tx-14, ty-20), (tx+14, ty)], fill=(50, 50, 55))

    # Text overlay title
    draw.text((24, 28), "eyeWalker Demo — Baltimore Harbor 3.66mi", fill=(250, 220, 80))
    draw.text((24, 52), "Fells Point → Maritime Park → Harbor Point (where maps fail)", fill=(180, 180, 120))
    draw.text((24, 78), f"Frame #{seed} — Mock VLM: Muse Spark 1.1 + Depth Anything V2 + SAM", fill=(130, 150, 180))

    return img


@spaces.GPU(duration=30)
def process_image(image: Image.Image) -> Tuple[Image.Image, Dict, str, str]:
    """
    Process a frame: detect obstacles, plan avoidance, generate spatial audio text.
    Runs on ZeroGPU — one GPU per request, free for creator, visitors use quota.

    Args:
        image: input RGB frame from Ray-Ban glasses or phone camera

    Returns:
        hud image, detection JSON, audio guidance text, risk summary
    """
    if image is None:
        image = create_demo_frame(brain.step)

    obstacles = brain.detect(image)
    plan = brain.plan_avoidance(obstacles)
    hud = draw_hud(image, obstacles, plan)

    # Build JSON
    output_json = {
        "timestamp": datetime.now().isoformat(),
        "gps": {
            "lat": HARBOR_LAT + brain.step * 0.00001,
            "lon": HARBOR_LON,
            "source": "Baltimore Harbor Loop 3.66mi",
            "freshness": "mock"
        },
        "obstacles": obstacles,
        "safe_path": plan,
        "guidance_audio": plan["instruction"],
        "risk_level": "HIGH" if any(o["urgency"] == "HIGH" for o in obstacles) else "MEDIUM" if obstacles else "LOW",
        "model": "mock Muse Spark 1.1 + DepthAnythingV2 + SAM (replace with Real on ZeroGPU)",
        "safety": "Assistive only, not replacement for cane/guide dog. Alpha research prototype."
    }

    audio_text = plan["instruction"]
    risk_summary = f"Risk {output_json['risk_level']} — {len(obstacles)} obstacles — Next: {plan['direction']} {plan['lateral_m']}m"

    return hud, output_json, audio_text, risk_summary


def load_demo(seed: int = 0) -> Image.Image:
    """Load a synthetic Baltimore Harbor demo frame."""
    return create_demo_frame(seed=brain.step)


with gr.Blocks(title="eyeWalker v1.0 — World Vision for Impaired", theme=gr.themes.Citrus(), css=CSS) as demo:
    gr.HTML('<div class="safety-banner">⚠️ SAFETY: This is assistive, not replacement for cane/guide dog. Always keep traditional mobility aid. This is alpha. It is a research prototype for users and developers to improve upon.</div>')

    with gr.Column(elem_id="col-container"):
        gr.Markdown(f"""
        # 👓 eyeWalker v1.0 — Real-time World Vision for the Visually Impaired
        <span class="who-badge">WHO: 2.2B with vision impairment</span> <span class="from-badge">Built by NeuroAgent AI — for rare neuro diseases affecting vision</span>

        **One-tap PWA for the world.** Real-time VLM obstacle avoidance: *"Trash bin 2.1m ahead, step left 0.5m"* + spatial audio + NemoClaw secured.

        **Origin:** Inspired by daily post-lunch harbor walks — 3.66mi loop around Baltimore's Fells Point, Frederick Douglass-Isaac Myers Maritime Park, Harbor Point where car maps fail. **Mission:** One day provide full world vision for the impaired.

        From **NeuroAgent AI** — built from lived experience of NMOSD, MOGAD, LHON, optic neuritis, IIH, CVI, glaucoma, RP, AMD, diabetic retinopathy, hemianopia, TBI — **and all neurologic/ophthalmologic causes.**

        <div class="hero-sub">

        - **Input:** Meta Ray-Ban / phone camera 30fps → 0.66Hz, GPS+IMU
        - **Brain:** Muse Spark 1.1 VLM open-vocab + Depth Anything V2 + SAM + VIO
        - **Ground Truth:** OSM footway/pier/marina + Esri satellite <3yr
        - **Output:** Binaural spatial audio guidance at obstacle 3D position
        - **Taxonomy:** trash bins, benches, pier edges (unguarded), bollards, person+dog, cyclists, low branches, puddles, cones
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=6):
                gr.Markdown("### 📹 Input — Ray-Ban / Phone Camera")
                input_image = gr.Image(label="Upload or use camera (webcam)", sources=["upload", "webcam"], type="pil", height=520)
                with gr.Row():
                    demo_btn = gr.Button("🎬 Load Baltimore Harbor Demo Frame", variant="secondary")
                    random_btn = gr.Button("🎲 Random Harbor Frame", variant="secondary")
                gr.Markdown("*Tip: Upload a sidewalk/pier photo. Model is mock now — swap to Qwen2-VL / Florence-2 on ZeroGPU for real detection.*")

            with gr.Column(scale=6):
                gr.Markdown("### 🎯 Output — HUD + Avoidance Guidance")
                hud_output = gr.Image(label="HUD overlay — crosshair is heading, X are obstacles", height=520)
                risk_text = gr.Textbox(label="Risk summary", lines=1)

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🔊 Spatial Audio Guidance (TTS ready)")
                audio_guidance = gr.Textbox(label="Binaural guidance text — plug to expo-speech / Web Audio binaural", lines=3, placeholder='"Trash bin 2.1m ahead, step LEFT 0.5m, then straight 2m"')
                gr.Markdown("🗺️ **Baltimore Harbor Graph:** OSM Overpass `footway|pier|path|marina` + Esri <3yr. 70% of harbor is off-street — we build our own walkable graph. GPS coarse + VIO fine + OSM snap.")

        with gr.Accordion("📊 Detection JSON — Detailed VLM Output", open=False):
            json_output = gr.JSON(label="Full output: GPS, obstacles (class/distance/bearing/urgency/velocity), safe_path, model info")

        with gr.Accordion("🛡️ Safety, License & Architecture", open=False):
            gr.Markdown("""
            **Safety — Critical:** Assistive only, not replacement for cane/guide dog. Always keep traditional mobility aid. Alpha research prototype for users and developers to improve upon. Test in safe familiar areas first (Baltimore Harbor loop) before new areas.

            **License:** PolyForm Noncommercial 1.0.0 for core (`eyewalker/`) — free for personal/research/education/non-profit/accessibility testing; **not allowed** without commercial license: selling, SaaS hosting for money, use in commercial product. Mobile PWA wrapper MIT. Contact via GitHub Issues `commercial-license`.

            **Architecture:**
            ```
            Ray-Ban / Smartphone (RGB+GPS+IMU) → Perception (VIO 6DoF + Depth V2 + VLM Spark + SAM walkable) → Fusion (GPS coarse + VIO fine + OSM ground truth) → Obstacle ID + Risk (class+distance+TTC+velocity) → Real-time Avoidance Planner ("Step LEFT 0.5m, rejoin 2m") → Spatial Audio (binaural at obstacle 3D pos)
            ```

            **Ground Truth Problem:** Google/OSM car-mode snaps to Boston St and breaks — 70% of harbor off-street. Solution: OSM Overpass custom filter + Esri World Imagery + vector tile cache for offline.

            **NemoClaw Harness:** Local-first, allowlist only: *.openstreetmap.org, overpass-api.de, server.arcgisonline.com, integrate.api.nvidia.com. No cloud logs/telemetry. Raw GPS+RGB never leaves sandbox without consent.

            **Why From NeuroAgent AI:**
            - Rare neuro: NMOSD, MOGAD, optic neuritis, autoimmune encephalitis visual, LHON, OPA1, Wolfram, mitochondrial optic neuropathies, IIH, optic nerve hypoplasia, CVI, PCA
            - All causes: glaucoma, diabetic retinopathy, AMD, RP, hemianopia, TBI
            - WHO: 2.2B impaired, 1B preventable, 2/3 low-income no glasses, $411B productivity loss
            - We built for us, open for 2.2B.

            **Links:**
            - GitHub: `aeyemovment/eyeWalker`
            - PWA: https://aeyemovment.github.io/eyeWalker/
            - WHO: https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment
            - Deployment: GitHub Pages PWA + HF Space demo
            """)

        with gr.Accordion("🚀 Next Steps — For Users / Devs / Meta Submission", open=False):
            gr.Markdown("""
            **For Users (non-technical):** One-tap PWA → Start Walking → Listen "Trash bin 2.1m ahead, step left..." → Repeat button. Report missed obstacles → GitHub Issues.

            **For Developers:** `git clone https://github.com/aeyemovment/eyeWalker.git` → `examples/harbor_walk.py --gpx data/harbor_3.66mi.gpx --satellite esri --mode obstacle-avoidance` → Add your city ground truth, improve VLM prompts, port to Ray-Ban native SDK.

            **For Meta Open Source (Accessibility):** This Space is the HF demo for `meta_submission/README_HF.md`. Ready to submit to opensource.fb.com category Accessibility. Llama Stack tool JSON in `meta_submission/llama_stack_tool.json`. See `META_SUBMISSION_CHECKLIST.md`.

            **PWA Deploy:** GitHub Action `deploy-pwa.yml` → copies `docs/` + one-tap artifact to `_site` → Pages. Safety banner yellow top, hero, iframe pwa.html with camera+geo.

            **Model Upgrade Path:** Current mock → Real:
            - ZeroGPU: `Qwen/Qwen2-VL-2B-Instruct` or `microsoft/Florence-2-large` for open-vocab detection + Depth Anything V2 small + `briaai/RMBG-1.4` style walkable seg. Use `@spaces.GPU(duration=30)` for VLM call.
            - Or Inference Providers (zero VRAM): via `hf_inference` or Cerebras for VLM.

            **Bio:** Built in Baltimore (Fells Point harbor walks), for the world. 2.2B needs world vision.
            """)

        gr.Markdown("""
        ---
        **Built in Baltimore. For the world. 👓🦮** From NeuroAgent AI — for rare neurologic diseases affecting vision and all other neurologic and ophthalmologic causes.

        *Synthetic demo — research prototype true, compliance_ref="Addendum_5_...", version v1.0, no real sends unless approved. Not for clinical/diagnostic/production/regulatory use.*
        """)

        # Actions
        demo_btn.click(fn=load_demo, outputs=[input_image])
        random_btn.click(fn=lambda: create_demo_frame(seed=random.randint(0, 9999)), outputs=[input_image])
        input_image.change(fn=process_image, inputs=[input_image], outputs=[hud_output, json_output, audio_guidance, risk_text])

        # Also generate initial demo on load
        demo.load(fn=lambda: create_demo_frame(seed=0), outputs=[input_image])

if __name__ == "__main__":
    demo.launch(mcp_server=True, ssr_mode=False)
