#!/usr/bin/env python3
"""Rebuild synthetic DT training labels without absolute personal paths.

Research prototype only. synthetic_only=true. Not a medical device.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "docs" / "training" / "frames"
OUT = ROOT / "docs" / "training" / "synthetic"
EXPORTS = ROOT / "docs" / "training" / "exports"

CONDITIONS = ("day", "dusk", "night", "rain")
CLASSES = (
    ("manhole", "HIGH"),
    ("shadow_trap", "MEDIUM"),
    ("crack", "MEDIUM"),
    ("curb", "LOW"),
    ("trash_bin", "MEDIUM"),
    ("bench", "LOW"),
    ("bike", "MEDIUM"),
    ("pier_edge", "HIGH"),
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    frames = sorted(FRAMES.glob("*.jpg")) + sorted(FRAMES.glob("*.png"))
    if not frames:
        # create placeholder list so rebuild still works
        frames = [Path(f"placeholder_frame_{i:04d}.jpg") for i in range(8)]

    rng = random.Random(20260726)
    rows = []
    # wipe old absolute-path jsons
    for old in OUT.glob("*.json"):
        old.unlink()
    for old in OUT.glob("*.jsonl"):
        old.unlink()

    twin_n = 3
    for fi, frame in enumerate(frames):
        rel = f"docs/training/frames/{frame.name}" if frame.parent == FRAMES else frame.name
        for cond in CONDITIONS:
            for twin in range(twin_n):
                cls, urg = CLASSES[(fi + twin) % len(CLASSES)]
                # bearing in [-30, +30]; guidance steps AWAY
                bearing = rng.uniform(-30, 30)
                dist = round(0.7 + rng.random() * 2.5, 2)
                if bearing < -8:
                    step = "right"
                elif bearing > 8:
                    step = "left"
                else:
                    step = "side-step"
                row = {
                    "source_frame": rel,
                    "condition": cond,
                    "twin_id": twin,
                    "modulators": {"lighting": cond, "bound": [0.25, 3.0]},
                    "obstacles": [
                        {
                            "class": cls,
                            "distance_m": dist,
                            "bearing_deg": round(bearing, 1),
                            "urgency": urg,
                            "source": f"dt_{cond}_t{twin}",
                            "simulated": True,
                        }
                    ],
                    "guidance": (
                        f"SIMULATED RESEARCH CUE: {cls.upper()} {dist}m ahead "
                        f"(bearing {bearing:+.0f}°), step {step}. Keep your cane. "
                        f"Not a medical device."
                    ),
                    "dt9": {
                        "synthetic_only": True,
                        "research_prototype": True,
                        "not_medical_device": True,
                        "ritual": "all_at_once_v1.1",
                    },
                }
                rows.append(row)
                out_name = f"{Path(rel).stem}_{cond}_t{twin}.json"
                (OUT / out_name).write_text(json.dumps(row, indent=2) + "\n")

    all_path = OUT / "dt_ritual_all.jsonl"
    with all_path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")

    manifest = {
        "version": "v1.1.0",
        "n_rows": len(rows),
        "n_frames": len(frames),
        "conditions": list(CONDITIONS),
        "twins_per_condition": twin_n,
        "synthetic_only": True,
        "research_prototype": True,
        "not_medical_device": True,
        "path_policy": "repo-relative only",
        "left_right_convention": "step away from obstacle bearing (neg=left obstacle→step right)",
    }
    (OUT / "dt_ritual_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (EXPORTS / "v1_1_synthetic_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"rebuilt {len(rows)} synthetic rows → {all_path}")


if __name__ == "__main__":
    main()
