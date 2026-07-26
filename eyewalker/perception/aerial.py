"""
Aerial camera modality — optional drone / elevated / top-down view for assistive research.

eyeWalker v1.1 medical open source (NeuroAgent AI).

Research prototype only. Not a medical device. Not for clinical use.
Assistive complement to cane / guide dog — not a replacement.
Local-first privacy: aggregate / anonymize when possible; no face ID.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class AerialFrame:
    rgb: any
    timestamp: float
    altitude_m: float  # typical hobby drone 10–120 m
    gimbal_pitch_deg: float  # -90 = nadir
    gps: Optional[Dict] = None
    platform: str = "drone"  # drone | balloon | cctv_tower | fixed_elevated
    sensor: str = "eo_day"  # eo_day | ir_thermal | nvg | multispectral | fused_eo_ir
    gimbal_model: str = "generic"
    intrinsics: Optional[Dict] = None
    extrinsics: Optional[Dict] = None

    def is_nadir(self):
        return self.gimbal_pitch_deg < -75

    def is_high_alt(self):
        return self.altitude_m > 300


class AerialPerception:
    """Optional elevated view for path context (research / mock)."""

    def __init__(self, mode="urban", platform="drone"):
        self.mode = mode
        self.platform = platform
        self.horizon_m = 200 if platform == "drone" else 500
        self.min_altitude_m = 10
        self.max_altitude_m = 120 if platform == "drone" else 300
        self.fov_deg = 84
        self.gimbal_model = "generic"

    def ingest(self, frame: Optional[AerialFrame]) -> Dict:
        if not frame:
            return {
                "walkable": None,
                "far_hazards": [],
                "source": "aerial",
                "platform": self.platform,
                "synthetic_only": True,
                "research_prototype": True,
            }

        far_hazards = self._detect_from_topdown(frame)
        return {
            "walkable": {
                "type": "aerial_occupancy",
                "resolution_m": 0.5,
                "size": (400, 400),
            },
            "far_hazards": far_hazards,
            "pose": {
                "alt_m": frame.altitude_m,
                "gps": frame.gps,
                "nadir": frame.is_nadir(),
                "platform": frame.platform,
                "sensor": frame.sensor,
                "gimbal": frame.gimbal_model,
            },
            "horizon_m": self.horizon_m,
            "source": "aerial",
            "platform": frame.platform,
            "privacy": {"anonymized": True, "no_face_id": True, "retain": "local-first"},
            "synthetic_only": True,
            "research_prototype": True,
        }

    def _detect_from_topdown(self, frame: AerialFrame) -> List[Dict]:
        # Mock research detections for development without live aerial hardware
        return [
            {
                "label": "path_edge",
                "range_m": 30,
                "severity": "high",
                "note": "water or drop edge from top-down (research mock)",
            },
            {
                "label": "path_obstruction",
                "range_m": 45,
                "severity": "med",
                "sensor": frame.sensor,
            },
        ]

    def to_birdseye_for_planner(self, aerial_scene, osm_graph):
        return {
            "costmap_add": None,
            "rejoin_hint": "prefer_marked_walkway",
            "source": "aerial",
        }
