#!/usr/bin/env python3
"""eyeWalker v1.1.9 deterministic accessibility-interface mock.

No image model, obstacle detector, navigation system, or audio renderer runs
here. Image bytes only seed repeatable synthetic records for UI evaluation.
"""

from __future__ import annotations

import hashlib
import math
import random
from typing import Dict, List, Tuple

import gradio as gr
from PIL import Image, ImageDraw


VERSION = "1.1.9"
SIMULATION_LABEL = "SIMULATED RESEARCH CUE:"
SAFETY_SUFFIX = "Keep your cane or guide dog. Not a medical device."
MODEL_PROVENANCE = "deterministic_mock_no_model_executed"
MAX_IMAGE_DIMENSION = 4096
MAX_IMAGE_PIXELS = 16_000_000
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

CSS = """
#col-container { max-width: 1120px; margin: 0 auto; }
.safety-banner {
  background: #ffcc00; color: #000; padding: 14px 18px;
  border-radius: 12px; font-weight: 800; text-align: center;
  margin-bottom: 16px; border: 2px solid #000;
}
"""

TAXONOMY = (
    ("trash_bin", "HIGH"),
    ("bench", "MEDIUM"),
    ("pier_edge", "HIGH"),
    ("bollard", "MEDIUM"),
    ("person_with_dog", "HIGH"),
    ("cyclist", "HIGH"),
    ("low_branch", "MEDIUM"),
    ("uneven_surface", "LOW"),
)
RISK_COLOR = {
    "HIGH": (220, 38, 38, 230),
    "MEDIUM": (234, 88, 12, 230),
    "LOW": (34, 197, 94, 230),
}


def _validated_image(image: Image.Image) -> Image.Image:
    """Reject malformed or oversized hosted inputs before pixel conversion/hash."""
    if not isinstance(image, Image.Image):
        raise ValueError("image must be a decoded Pillow image")
    width, height = image.size
    if (
        type(width) is not int
        or type(height) is not int
        or width <= 0
        or height <= 0
        or width > MAX_IMAGE_DIMENSION
        or height > MAX_IMAGE_DIMENSION
        or width * height > MAX_IMAGE_PIXELS
    ):
        raise ValueError(
            "image dimensions exceed the reviewed hosted-demo limit "
            f"({MAX_IMAGE_DIMENSION}px per side, {MAX_IMAGE_PIXELS} pixels total)"
        )
    return image


def create_demo_frame(seed: int = 0) -> Image.Image:
    """Create a synthetic harbor-style fixture; it is not captured imagery."""
    rng = random.Random(seed)
    width, height = 960, 720
    image = Image.new("RGB", (width, height), (24, 42, 65))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 250), fill=(80, 118, 152))
    draw.rectangle((0, 250, width, height), fill=(22, 56, 72))
    pier_left, pier_right = 300, 660
    draw.polygon(
        [(pier_left, 170), (pier_right, 170), (830, height), (130, height)],
        fill=(105, 83, 61),
    )
    for y in range(200, height, 55):
        draw.line((180, y, 780, y), fill=(130, 104, 77), width=2)
    box_x = rng.randint(410, 540)
    draw.rectangle((box_x, 420, box_x + 48, 510), fill=(52, 56, 60))
    draw.text((24, 24), "eyeWalker synthetic fixture", fill=(255, 244, 160))
    draw.text((24, 50), "SIMULATED RESEARCH MOCK — NOT FOR NAVIGATION", fill=(255, 255, 255))
    return image


def _seed_from_image(image: Image.Image) -> int:
    """Hash pixels only to choose repeatable mock data; this is not inference."""
    rgb = _validated_image(image).convert("RGB")
    digest = hashlib.sha256(rgb.tobytes()).digest()
    return int.from_bytes(digest[:8], "big")


def generate_mock_records(image: Image.Image) -> List[Dict]:
    """Return deterministic synthetic records with explicit provenance."""
    rng = random.Random(_seed_from_image(image))
    chosen = rng.sample(TAXONOMY, rng.randint(1, 3))
    records = []
    for class_name, base_risk in chosen:
        distance = round(rng.uniform(0.8, 5.2), 2)
        bearing = round(rng.uniform(-55, 55), 1)
        urgency = "HIGH" if distance < 1.2 else base_risk
        records.append(
            {
                "class": class_name,
                "distance_m": distance,
                "bearing_deg": bearing,
                "urgency": urgency,
                "source": "deterministic_mock",
                "simulated": True,
            }
        )
    return sorted(records, key=lambda item: item["distance_m"])


def simulated_plan(records: List[Dict]) -> Dict:
    """Derive a mock step-away cue locally; never accept model-authored movement."""
    if not records:
        return {
            "instruction": (
                f"{SIMULATION_LABEL} no simulated obstacle record is available; "
                f"HOLD and stop and verify. {SAFETY_SUFFIX}"
            ),
            "action": "hold",
            "lateral_m": 0.0,
            "simulated": True,
            "guidance_source": "local_fail_closed_no_obstacle_record",
        }

    rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    target = sorted(records, key=lambda item: (rank[item["urgency"]], item["distance_m"]))[0]
    bearing = target["bearing_deg"]
    if bearing < -8:
        side = "right"
    elif bearing > 8:
        side = "left"
    else:
        return {
            "instruction": (
                f"{SIMULATION_LABEL} simulated obstacle bearing is centered or "
                f"ambiguous; HOLD and stop and verify. {SAFETY_SUFFIX}"
            ),
            "action": "hold",
            "lateral_m": 0.0,
            "target_class": target["class"],
            "simulated": True,
            "guidance_source": "local_fail_closed_ambiguous_bearing",
        }
    lateral = 0.4 if target["distance_m"] < 1.2 else 0.5
    cue = (
        f"{SIMULATION_LABEL} {target['class'].replace('_', ' ').upper()} "
        f"{target['distance_m']:.1f}m ahead (bearing {bearing:+.0f} degrees), "
        f"step {side} {lateral:.1f}m. {SAFETY_SUFFIX}"
    )
    return {
        "instruction": cue,
        "action": f"step_{side.replace('-', '_')}",
        "lateral_m": lateral,
        "target_class": target["class"],
        "simulated": True,
        "guidance_source": "local_step_away",
    }


def draw_mock_overlay(image: Image.Image, records: List[Dict], plan: Dict) -> Image.Image:
    """Draw synthetic markers; marker positions are not image detections."""
    base = image.convert("RGB")
    width, height = base.size
    overlay = base.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rectangle((0, 0, width, 62), fill=(0, 0, 0, 215))
    draw.text((16, 12), "SIMULATED RESEARCH MOCK — MARKERS ARE SYNTHETIC", fill=(255, 235, 80, 255))
    draw.text((16, 36), "NO LIVE DETECTOR — NOT FOR NAVIGATION", fill=(255, 255, 255, 255))

    center_x, center_y = width // 2, int(height * 0.53)
    for index, record in enumerate(records):
        angle = math.radians(record["bearing_deg"])
        x = int(center_x + math.sin(angle) * width * 0.33)
        y = int(center_y + min(record["distance_m"] / 6.0, 1.0) * height * 0.25)
        color = RISK_COLOR[record["urgency"]]
        size = 15
        draw.line((x - size, y - size, x + size, y + size), fill=color, width=4)
        draw.line((x - size, y + size, x + size, y - size), fill=color, width=4)
        draw.text(
            (max(4, x - 70), min(height - 70, y + 20)),
            f"MOCK {index + 1}: {record['class']} {record['distance_m']:.1f}m",
            fill=color,
        )

    draw.rectangle((0, height - 108, width, height), fill=(0, 0, 0, 220))
    cue_detail = plan["instruction"].removesuffix(SAFETY_SUFFIX).strip()
    if len(cue_detail) > 125:
        cue_detail = cue_detail[:122] + "..."
    draw.text((14, height - 88), cue_detail, fill=(120, 255, 175, 255))
    draw.text((14, height - 56), SAFETY_SUFFIX, fill=(255, 235, 80, 255))
    draw.text((14, height - 28), MODEL_PROVENANCE, fill=(220, 220, 220, 255))
    return overlay


def process_image(image: Image.Image) -> Tuple[Image.Image, Dict, str, str]:
    """Run the deterministic mock and return truthful UI/provenance fields."""
    source_image = _validated_image(image if image is not None else create_demo_frame())
    records = generate_mock_records(source_image)
    plan = simulated_plan(records)
    overlay = draw_mock_overlay(source_image, records, plan)
    risk_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    risk = min(
        (item["urgency"] for item in records),
        key=lambda value: risk_rank[value],
        default="LOW",
    )
    payload = {
        "version": VERSION,
        "simulated_obstacles": records,
        "simulated_plan": plan,
        "simulated_cue": plan["instruction"],
        "simulated_risk_level": risk,
        "provenance": {
            "simulated": True,
            "model": MODEL_PROVENANCE,
            "models_executed": [],
            "image_processing": "pixel_hash_for_repeatable_mock_seed_only",
            "not_for_navigation": True,
        },
        "safety": SAFETY_SUFFIX,
    }
    status = f"SIMULATED {risk} — {len(records)} mock records — no model executed"
    return overlay, payload, plan["instruction"], status


with gr.Blocks(
    title=f"eyeWalker v{VERSION} — Simulated Accessibility Research Demo",
    theme=gr.themes.Citrus(),
    css=CSS,
) as demo:
    gr.HTML(
        '<div class="safety-banner">'
        'SIMULATED RESEARCH ONLY — NOT FOR NAVIGATION. '
        'Keep your cane or guide dog. Not a medical device.'
        "</div>"
    )
    with gr.Column(elem_id="col-container"):
        gr.Markdown(
            f"""
            # eyeWalker v{VERSION} — simulated accessibility-interface mock

            This demo hashes image pixels only to select repeatable synthetic records.
            It performs no image inference, obstacle detection, distance estimation,
            map fusion, sensor fusion, or audio rendering.

            **Hosted-demo privacy:** an uploaded or webcam still is sent to the
            Space host for pixel hashing and display. Use only synthetic,
            non-sensitive images with no bystanders, faces, plates, documents,
            or precise-location clues.
            """
        )
        with gr.Row():
            input_image = gr.Image(
                label="Display/seed image — pixels are not analyzed by a model",
                sources=["upload", "webcam"],
                type="pil",
                height=430,
            )
            overlay_output = gr.Image(
                label="Synthetic marker overlay — not detections",
                height=430,
            )
        with gr.Row():
            demo_button = gr.Button("Load synthetic fixture")
            run_button = gr.Button("Generate repeatable mock records", variant="primary")
        status_output = gr.Textbox(label="Mock status", interactive=False)
        cue_output = gr.Textbox(
            label="Simulated research cue text — no audio is rendered",
            lines=3,
            interactive=False,
        )
        json_output = gr.JSON(label="Synthetic records and provenance")
        gr.Markdown(
            """
            Proposed future components such as validated perception, depth, map
            context, wearable integration, and audio rendering are not implemented
            end to end here. Draft submission materials do not prove an external
            submission, deployment, acceptance, or approval.
            """
        )

        demo_button.click(fn=create_demo_frame, outputs=input_image)
        run_button.click(
            fn=process_image,
            inputs=input_image,
            outputs=[overlay_output, json_output, cue_output, status_output],
        )


if __name__ == "__main__":
    demo.launch()
