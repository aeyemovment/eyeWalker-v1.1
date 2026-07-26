#!/usr/bin/env python3
"""Deprecated compatibility entrypoint for the canonical DT rebuild.

The former implementation could emit absolute paths and overwrite labels when
JPG and PNG inputs shared a stem. Keep one deterministic, validated generator.
Research prototype only. Synthetic only. Not a medical device.
"""
from __future__ import annotations

import sys

from rebuild_synthetic_dataset import main, ritual_for_frame

__all__ = ["main", "ritual_for_frame"]


if __name__ == "__main__":
    if len(sys.argv) != 1:
        raise SystemExit(
            "custom frame/output arguments are no longer supported; run "
            "scripts/v11/rebuild_synthetic_dataset.py from the repository"
        )
    main()
