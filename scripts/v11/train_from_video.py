#!/usr/bin/env python3
"""Extract frames from explicitly selected video into an external workspace.

Personal walk media must not be copied into the public repository. This helper
does not run a model, create ground truth, generate guidance, or write a
manifest. Its output must resolve outside the eyeWalker checkout.
"""

from __future__ import annotations

import argparse
import math
import subprocess
from numbers import Real
from pathlib import Path


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def extract_frames(
    video: Path,
    output_dir: Path,
    fps: float = 2.0,
    *,
    repository_root: Path | None = None,
) -> int:
    """Extract frames after enforcing the external-workspace boundary.

    The guard lives in this callable, not only in the CLI wrapper, so imports
    cannot bypass the public-repository containment policy.
    """
    if (
        not isinstance(fps, Real)
        or isinstance(fps, bool)
        or not math.isfinite(fps)
        or fps <= 0
        or fps > 30
    ):
        raise ValueError("fps must be greater than 0 and at most 30")

    root = (
        Path(repository_root).expanduser().resolve(strict=True)
        if repository_root is not None
        else Path(__file__).resolve().parents[2]
    )
    source_arg = Path(video).expanduser()
    output_arg = Path(output_dir).expanduser()
    if source_arg.is_symlink():
        raise ValueError("video must not be a symbolic link")
    if output_arg.is_symlink():
        raise ValueError("output directory must not be a symbolic link")

    source = source_arg.resolve(strict=True)
    output = output_arg.resolve(strict=False)
    if not source.is_file():
        raise ValueError("video must be an existing regular file")
    if _is_within(source, root) or _is_within(output, root):
        raise ValueError(
            "personal media and extracted frames must remain outside the public repository"
        )
    if output.exists() and not output.is_dir():
        raise ValueError("output path must be a directory")
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-vf",
        f"fps={fps}",
        "-q:v",
        "3",
        str(output / "frame_%06d.jpg"),
    ]
    subprocess.run(command, check=True)
    return len(list(output.glob("frame_*.jpg")))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract explicitly selected personal video outside the public repo"
    )
    parser.add_argument("--video", required=True, help="Existing local video path")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="New or empty directory outside the eyeWalker repository",
    )
    parser.add_argument("--fps", type=float, default=2.0)
    args = parser.parse_args()

    count = extract_frames(
        Path(args.video),
        Path(args.output_dir),
        fps=args.fps,
    )
    print(
        f"extracted {count} local frames to external workspace; "
        "no model, ground-truth, label, manifest, or repository write performed"
    )


if __name__ == "__main__":
    main()
