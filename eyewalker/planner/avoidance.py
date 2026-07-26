"""Avoidance planner — research advisory only. Not a medical device."""

from typing import Any, Dict, Optional


class AvoidancePlanner:
    """
    Step *away* from obstacle bearing (user-relative).
    Convention: bearing_deg < 0 = obstacle to the user's left → step right.
                 bearing_deg > 0 = obstacle to the user's right → step left.
    """

    def plan(self, user_pose, obstacle, depth, walkable_mask) -> Dict[str, Any]:
        label = getattr(obstacle, "label", None) or getattr(obstacle, "class", "obstacle")
        dist = float(getattr(obstacle, "distance_m", 2.0))
        bearing = float(getattr(obstacle, "bearing_deg", 0.0))

        # Prefer free-space if depth provides real signal; else use bearing (step away)
        left_free = self.free_space(depth, side="left")
        right_free = self.free_space(depth, side="right")
        has_depth_signal = self._depth_usable(depth)

        if has_depth_signal:
            step_left = left_free > right_free
        else:
            # step AWAY from obstacle
            if bearing < -8:
                step_left = False  # obstacle left → step right
            elif bearing > 8:
                step_left = True  # obstacle right → step left
            else:
                step_left = left_free >= right_free

        side = "left" if step_left else "right"
        lateral = 0.4 if dist < 1.2 else 0.5
        return {
            "action": f"step_{side}",
            "lateral_m": lateral,
            "instruction": (
                f"SIMULATED RESEARCH CUE: {label} {dist:.1f}m ahead "
                f"(bearing {bearing:+.0f}°), step {side} {lateral:.1f}m. "
                f"Keep your cane. Not a medical device."
            ),
            "rejoin_m": 2.0,
            "simulated": not has_depth_signal,
            "research_prototype": True,
        }

    def _depth_usable(self, depth) -> bool:
        if depth is None:
            return False
        try:
            import numpy as np

            arr = np.asarray(depth)
            return arr.size > 16 and float(np.nanstd(arr)) > 1e-3
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
            return float(np.nanmean(region))
        except Exception:
            return 0.0
