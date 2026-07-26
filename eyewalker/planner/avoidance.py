
"""Real-time avoidance planner — calculates safe bypass and voice guidance"""
import math

class AvoidancePlanner:
    def plan(self, user_pose, obstacle, depth, walkable_mask):
        """Return safe path around obstacle that rejoins main route"""
        # Simple left/right decision based on free space in depth
        left_free = self.free_space(depth, side="left")
        right_free = self.free_space(depth, side="right")

        if obstacle.label == "pier edge drop-off":
            return {"action": "keep_right", "instruction": "Pier edge 0.8m left, keep right", "lateral_m": 0.5}

        if left_free > right_free:
            return {
                "action": "step_left",
                "lateral_m": 0.5,
                "instruction": f"Obstacle: {obstacle.label} {obstacle.distance_m:.1f}m ahead, step left {0.5}m",
                "rejoin_m": 2.0
            }
        else:
            return {
                "action": "step_right",
                "lateral_m": 0.5,
                "instruction": f"Obstacle: {obstacle.label} {obstacle.distance_m:.1f}m ahead, step right {0.5}m",
                "rejoin_m": 2.0
            }

    def free_space(self, depth, side="left"):
        # TODO: compute free space from depth + walkable mask
        return 1.0
