#!/usr/bin/env python3
"""Extract 2fps frames from a walk video and build v1.1 training pack.

If no video is supplied, seeds from docs/training/raw stills + demo.gif.

  python3 scripts/v11/train_from_video.py --video docs/training/raw/walk.mp4
  python3 scripts/v11/train_from_video.py --seed-only
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

import sys
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parent))
from dt_ritual_all_at_once import ritual_for_frame  # type: ignore


def extract_frames(video: Path, out_dir: Path, fps: float = 2.0) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    # clear old extracted
    for p in out_dir.glob("frame_*.jpg"):
        p.unlink()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-vf",
        f"fps={fps}",
        "-q:v",
        "3",
        str(out_dir / "frame_%06d.jpg"),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return len(list(out_dir.glob("frame_*.jpg")))


def gif_to_frames(gif: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(gif),
        "-vf",
        "fps=2",
        "-q:v",
        "4",
        str(out_dir / "gif_%04d.jpg"),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return 0
    return len(list(out_dir.glob("gif_*.jpg")))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="", help="Path to 30-min walk video")
    ap.add_argument("--seed-only", action="store_true")
    ap.add_argument("--fps", type=float, default=2.0)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    frames = root / "docs/training/frames"
    raw = root / "docs/training/raw"
    synthetic = root / "docs/training/synthetic"
    exports = root / "docs/training/exports"
    for d in (frames, raw, synthetic, exports):
        d.mkdir(parents=True, exist_ok=True)

    n_frames = 0
    video_path = Path(args.video) if args.video else None
    if video_path and video_path.exists() and not args.seed_only:
        n_frames = extract_frames(video_path, frames, fps=args.fps)
        print(f"extracted {n_frames} frames @ {args.fps}fps from {video_path}")
    else:
        # seed stills
        for src in raw.glob("*.jpg"):
            dest = frames / src.name
            if not dest.exists():
                shutil.copy2(src, dest)
                n_frames += 1
        gif = raw / "demo_seed.gif"
        if gif.exists():
            n_frames += gif_to_frames(gif, frames)
        print(f"seed-only / no video: {n_frames} frames prepared (drop 30min video into docs/training/raw/)")

    # DT ritual all-at-once on frames
    all_rows = []
    for p in sorted(frames.glob("*.jpg"))[:500]:
        all_rows.extend(ritual_for_frame(p, synthetic))

    # Hybrid agent smoke on first frame bytes
    import sys

    sys.path.insert(0, str(root))
    from eyewalker.vlm.hybrid_agent import HybridVLMAgent, HybridConfig

    agent = HybridVLMAgent(HybridConfig(mode="hybrid", ground_mode=True))
    sample = frames.glob("*.jpg")
    first = next(sample, None)
    fb = first.read_bytes() if first else b"seed"
    vlm = agent.infer(frame_bytes=fb, gps={"lat": 39.2815, "lon": -76.5930}, note="v1.1 train")

    pack = {
        "version": "v1.1.0-ground",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "video": str(video_path) if video_path else None,
        "frames": len(list(frames.glob("*.jpg"))),
        "synthetic_dt_rows": len(all_rows),
        "fps_target": args.fps,
        "hybrid_sample": vlm,
        "pwa_fix": "v1.0 had getUserMedia only — no MediaRecorder; v1.1 adds REC webm+GPS",
        "agentic_flow": "grok<>muse-spark hybrid (experiment modes: hybrid|spark_only|grok_only|mock)",
        "dt9": {
            "synthetic_only": True,
            "research_prototype": True,
            "not_medical_device": True,
            "disclaimer": "Assistive research prototype. Not replacement for cane/guide dog.",
        },
    }
    (exports / "v1_1_ground_manifest.json").write_text(json.dumps(pack, indent=2) + "\n")
    (root / "docs/training/dataset_card.json").write_text(
        json.dumps(
            {
                "pretty_name": "eyeWalker Baltimore Harbor Ground v1.1",
                "version": "v1.1.0-ground",
                "task": "assistive_ground_obstacle_navigation",
                "language": ["en"],
                "license": "PolyForm-Noncommercial-1.0.0 / MIT mobile",
                "source": "harbor walks + optional 30min phone video + DT synthetic",
                "annotations": "DT ritual all-at-once (day/dusk/night/rain)",
                "not_medical_device": True,
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps({k: pack[k] for k in pack if k != "hybrid_sample"}, indent=2))
    print("sample guidance:", vlm.get("guidance"))


if __name__ == "__main__":
    main()
