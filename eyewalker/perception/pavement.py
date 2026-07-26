"""
Pavement / ground-level camera modality — low, near-ground for curbs, potholes, tactile paving
v1.1 multi-camera for assistive navigation research: the most safety-critical for low-vision mobility

DT#9 synthetic research prototype. synthetic_only=true, research_prototype=true.
Safety: assistive not replacement. Always cane/guide dog. Alpha research prototype, not medical device.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class PavementFrame:
    rgb: any
    timestamp: float = 0.0
    mount: str = "cane_tip"  # cane_tip | shoe_toe | chest_low | wheelchair_front
    height_cm: float = 15.0  # 5-40cm typical
    pitch_deg: float = -35.0  # looking down-forward
    imu: Optional[any] = None

class PavementPerception:
    """
    Pavement camera — purpose-built for ground hazards:
    - curb up/down, uneven pavers, puddle depth, tactile paving, pier edge drop (sub-cm precision goal)
    - For Baltimore Harbor: 51ft gain over 3.66mi => slope + curb critical
    - For austere research (optional): off-road / debris / trip hazards in austere / disaster response
    - Optional: evidence of sidewalk block, ADA compliance checks (optional mode)
    """
    GROUND_LABELS = [
        "curb_up", "curb_down", "curb_cut_ramp", "tactile_paving",
        "uneven_pavers", "pothole", "puddle", "grate_gap",
        "pier_edge_drop", "paint_line", "sidewalk_closed",
        "cable_on_ground", "ice_patch", "sand_gravel"
    ]

    def __init__(self, mount="cane_tip", depth_model="depth_anything_v2_tiny"):
        self.mount = mount
        self.depth_model = depth_model
        self.min_range_m = 0.15
        self.max_range_m = 4.0
        self.fov_ground_m = 1.8  # width at 1m ahead

    def ingest(self, frame: PavementFrame) -> Dict:
        """
        Returns ground profile + hazards within 0.15-4m
        In prod: high-freq (60fps) + structured light / ToF + learned ground seg (SAM + SegFormer ground)
        """
        if not frame:
            return {"ground_profile": None, "hazards": [], "source": "pavement", "synthetic_only": True}

        hazards = self._detect_ground(frame)
        profile = self._profile_slope(frame)

        return {
            "ground_profile": profile,
            "hazards": hazards,
            "mount": frame.mount,
            "height_cm": frame.height_cm,
            "range_m": (self.min_range_m, self.max_range_m),
            "source": "pavement",
            "safety_critical": True,
            
            
            "synthetic_only": True,
        }

    def _detect_ground(self, frame: PavementFrame) -> List[Dict]:
        # Stub with realistic harbor examples
        return [
            {"label": "curb_up", "dist_m": 0.9, "height_cm_est": 12, "conf": 0.92, "urgency": "high", "action": "prepare_step_up"},
            {"label": "tactile_paving", "dist_m": 1.4, "conf": 0.88, "note": "signalized crossing ahead"},
        ]

    def _profile_slope(self, frame: PavementFrame) -> Dict:
        # Synthetic slope from Harbor 51ft gain
        return {
            "slope_deg": 1.8,
            "cross_slope_deg": 0.5,
            "terrain_class": "concrete_pier_with_wood_planks",
            "walkable_width_m": 1.2,
            "confidence": 0.91,
        }

    def to_costmap(self, pavement_scene):
        """
        Convert to planner add: ultra-close cost (<2m) overrides other modalities
        """
        return {
            "costmap": "pavement_close_range",
            "priority": "highest_within_2m",
            "override_risk": ["pier_edge_drop", "curb_down_unmarked"],
            "source": "pavement"
        }
