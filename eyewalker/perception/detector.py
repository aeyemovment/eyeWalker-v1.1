
"""Adapter for caller-supplied depth/VLM implementations.

This module loads no model, performs no remote call, and makes no accuracy or
navigation-safety claim. Callers own model validation, the explicit score
threshold, and provenance.
"""
import math
from numbers import Real

OBSTACLE_PROMPTS = [
    "trash can blocking path",
    "bench blocking sidewalk",
    "bollard",
    "construction cone",
    "low branch at head height",
    "curb up",
    "puddle",
    "uneven pavers",
    "person walking",
    "dog",
    "cyclist approaching",
    "pier edge drop-off"
]

def detect_obstacles(rgb, depth_model, vlm_model, *, caller_score_threshold):
    if (
        not isinstance(caller_score_threshold, Real)
        or isinstance(caller_score_threshold, bool)
        or not math.isfinite(caller_score_threshold)
        or not 0.0 <= caller_score_threshold <= 1.0
    ):
        raise ValueError("caller_score_threshold must be a finite real in [0, 1]")
    depth = depth_model(rgb)
    detections = vlm_model.open_vocab_detect(
        rgb,
        OBSTACLE_PROMPTS,
        conf=float(caller_score_threshold),
    )
    # Attach distance from depth
    for d in detections:
        d.distance = float(depth[d.cy, d.cx])
    return detections, depth
