#!/usr/bin/env python3
"""Grok DT ritual — ALL AT ONCE — for eyeWalker v1.1 ground training.

Generates synthetic day/dusk/night/rain digital-twin frame descriptors + obstacle
labels from seed frames. Does NOT claim real clinical training.

Usage:
  python3 scripts/v11/dt_ritual_all_at_once.py
  python3 scripts/v11/dt_ritual_all_at_once.py --frames-dir docs/training/frames
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

CONDITIONS = ("day", "dusk", "night", "rain")
SURFACE = ("manhole", "shadow_trap", "crack", "curb", "wet_reflect")


def ritual_for_frame(path: Path, out_dir: Path) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b"seed"
    h = hashlib.sha256(raw).hexdigest()
    rows = []
    for ci, cond in enumerate(CONDITIONS):
        # 3 synthetic DT twins per condition (12 total per real frame)
        for twin in range(3):
            seed = h[ci * 8 : (ci + 1) * 8] + f"{twin}"
            n_obs = 1 + (int(seed[0], 16) % 3)
            obstacles = []
            for j in range(n_obs):
                cls = SURFACE[(int(seed[j + 1], 16) + j) % len(SURFACE)]
                obstacles.append(
                    {
                        "class": cls,
                        "distance_m": round(0.5 + (int(seed[j + 2], 16) % 30) / 10.0, 2),
                        "bearing_deg": -30 + (int(seed[j + 3], 16) % 60),
                        "urgency": "HIGH" if cls in ("manhole", "pier_edge") else "MEDIUM",
                        "source": f"dt_{cond}_t{twin}",
                    }
                )
            row = {
                "source_frame": str(path),
                "condition": cond,
                "twin_id": twin,
                "modulators": {"lighting": cond, "bound": [0.25, 3.0]},
                "obstacles": obstacles,
                "guidance": (
                    f"{obstacles[0]['class'].replace('_',' ').upper()} "
                    f"{obstacles[0]['distance_m']}m ahead — DT {cond}. Keep your cane."
                ),
                "dt9": {
                    "synthetic_only": True,
                    "research_prototype": True,
                    "not_medical_device": True,
                    "ritual": "all_at_once",
                },
            }
            rows.append(row)
            out_path = out_dir / f"{path.stem}_{cond}_t{twin}.json"
            out_path.write_text(json.dumps(row, indent=2) + "\n")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames-dir", default="docs/training/frames")
    ap.add_argument("--raw-dir", default="docs/training/raw")
    ap.add_argument("--out-dir", default="docs/training/synthetic")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    frames = root / args.frames_dir
    raw = root / args.raw_dir
    out = root / args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    seeds = list(frames.glob("*.jpg")) + list(frames.glob("*.png"))
    seeds += list(raw.glob("*.jpg")) + list(raw.glob("*.png"))
    if not seeds:
        # synthetic placeholder seed
        dummy = raw / "_dt_seed_placeholder.txt"
        dummy.write_text("eyeWalker DT seed — no real frames yet\n")
        seeds = [dummy]

    all_rows = []
    for p in seeds[:200]:
        all_rows.extend(ritual_for_frame(p, out))

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version": "v1.1.0-ground",
        "ritual": "grok_dt_all_at_once",
        "conditions": list(CONDITIONS),
        "seed_count": len(seeds),
        "synthetic_rows": len(all_rows),
        "note": "Synthetic DT labels for research; not clinical training data.",
        "dt9": {"synthetic_only": True, "research_prototype": True, "not_medical_device": True},
    }
    (out / "dt_ritual_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (out / "dt_ritual_all.jsonl").write_text("\n".join(json.dumps(r) for r in all_rows) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
