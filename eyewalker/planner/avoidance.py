"""Avoidance planner — simulated research cues only. Not a medical device."""

import math
import re
from numbers import Real
from typing import Any, Dict, Optional


SIMULATED_RESEARCH_LABEL = "SIMULATED RESEARCH CUE:"
SAFETY_SUFFIX = "Keep your cane or guide dog. Not a medical device."
SAFE_LABELS = {
    "bench",
    "bike",
    "bollard",
    "construction_cone",
    "crack",
    "curb",
    "curb_down",
    "curb_up",
    "low_branch",
    "manhole",
    "obstacle",
    "person",
    "pier_edge",
    "puddle",
    "shadow_trap",
    "tactile_paving",
    "trash_bin",
    "uneven_surface",
}
MIN_FREE_SPACE_DELTA = 0.05


def _safe_label(value: Any) -> str:
    normalized = re.sub(r"[^a-z0-9_]+", "_", str(value).strip().lower()).strip("_")
    return normalized if normalized in SAFE_LABELS else "obstacle"


class AvoidancePlanner:
    """
    Step *away* from obstacle bearing (user-relative).
    Convention: bearing_deg < 0 = obstacle to the user's left → step right.
                 bearing_deg > 0 = obstacle to the user's right → step left.
    """

    def plan(self, user_pose, obstacle, depth, walkable_mask) -> Dict[str, Any]:
        label = _safe_label(
            getattr(obstacle, "label", None)
            or getattr(obstacle, "class", "obstacle")
        )
        missing = object()
        raw_dist = getattr(obstacle, "distance_m", missing)
        raw_bearing = getattr(obstacle, "bearing_deg", missing)
        geometry_types_valid = all(
            isinstance(value, Real) and not isinstance(value, bool)
            for value in (raw_dist, raw_bearing)
        )
        if geometry_types_valid:
            dist = float(raw_dist)
            bearing = float(raw_bearing)
        else:
            dist = float("nan")
            bearing = float("nan")

        if (
            not math.isfinite(dist)
            or dist < 0
            or not math.isfinite(bearing)
            or abs(bearing) > 180
        ):
            return {
                "action": "hold",
                "lateral_m": 0.0,
                "instruction": (
                    f"{SIMULATED_RESEARCH_LABEL} invalid simulated obstacle "
                    f"geometry; stop and verify. {SAFETY_SUFFIX}"
                ),
                "rejoin_m": 0.0,
                "simulated": True,
                "depth_signal_used": False,
                "research_prototype": True,
                "invalid_geometry": True,
            }

        # Bearing is the safety invariant: always step away from a lateral
        # obstacle. A centered obstacle may select a side only from finite,
        # meaningfully different depth evidence; ambiguity fails closed.
        has_depth_signal = self._depth_usable(depth)

        if bearing < -8:
            step_left = False  # obstacle left → step right
        elif bearing > 8:
            step_left = True  # obstacle right → step left
        else:
            if not has_depth_signal:
                return self._hold(
                    "centered simulated obstacle has no usable side-depth evidence",
                    depth_signal_used=False,
                )
            left_free = self.free_space(depth, side="left")
            right_free = self.free_space(depth, side="right")
            scale = max(abs(left_free), abs(right_free), 1.0)
            if (
                not math.isfinite(left_free)
                or not math.isfinite(right_free)
                or abs(left_free - right_free)
                <= max(MIN_FREE_SPACE_DELTA, 0.05 * scale)
            ):
                return self._hold(
                    "centered simulated obstacle has ambiguous side-depth evidence",
                    depth_signal_used=True,
                )
            step_left = left_free > right_free

        side = "left" if step_left else "right"
        lateral = 0.4 if dist < 1.2 else 0.5
        return {
            "action": f"step_{side}",
            "lateral_m": lateral,
            "instruction": (
                f"{SIMULATED_RESEARCH_LABEL} {label.replace('_', ' ')} {dist:.1f}m ahead "
                f"(bearing {bearing:+.0f}°), step {side} {lateral:.1f}m. "
                f"{SAFETY_SUFFIX}"
            ),
            "rejoin_m": 2.0,
            # This planner currently emits research cues, even when a depth array
            # is supplied. Do not contradict the visible SIMULATED label.
            "simulated": True,
            "depth_signal_used": has_depth_signal,
            "research_prototype": True,
        }

    def _depth_usable(self, depth) -> bool:
        if depth is None:
            return False
        try:
            import numpy as np

            raw = np.asarray(depth)
            if raw.dtype.kind not in "fiu" or raw.dtype.kind == "b":
                return False
            arr = raw.astype(float, copy=False)
            return (
                arr.ndim == 2
                and arr.shape[1] >= 2
                and arr.size > 16
                and bool(np.isfinite(arr).all())
                and bool((arr > 0).all())
                and math.isfinite(float(np.std(arr)))
                and float(np.std(arr)) > 1e-3
            )
        except Exception:
            return False

    def free_space(self, depth, side: str = "left") -> float:
        """Return relative free-space score on one side; 0 if unknown."""
        if not self._depth_usable(depth):
            return 0.0
        try:
            import numpy as np

            arr = np.asarray(depth, dtype=float)
            if arr.ndim == 1:
                return float(np.nanmean(arr))
            h, w = arr.shape[:2]
            half = w // 2
            region = arr[:, :half] if side == "left" else arr[:, half:]
            # larger mean depth ≈ more free space ahead on that side
            score = float(np.mean(region))
            return score if math.isfinite(score) else 0.0
        except Exception:
            return 0.0

    def _hold(self, reason: str, *, depth_signal_used: bool) -> Dict[str, Any]:
        return {
            "action": "hold",
            "lateral_m": 0.0,
            "instruction": (
                f"{SIMULATED_RESEARCH_LABEL} {reason}; stop and verify. "
                f"{SAFETY_SUFFIX}"
            ),
            "rejoin_m": 0.0,
            "simulated": True,
            "depth_signal_used": depth_signal_used,
            "research_prototype": True,
            "ambiguous_geometry": True,
        }
