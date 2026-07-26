"""Deterministic pavement-interface fixtures; no frame analysis is performed."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PavementFrame:
    rgb: Any
    timestamp: float = 0.0
    mount: str = "cane_tip"
    height_cm: float = 15.0
    pitch_deg: float = -35.0
    imu: Optional[Any] = None


class PavementPerception:
    """Return explicit synthetic records for interface and pipeline tests."""

    def __init__(self, mount="cane_tip", depth_model="unloaded"):
        self.mount = mount
        self.configured_depth_model = depth_model

    def ingest(self, frame: PavementFrame | None) -> Dict:
        if frame is None:
            return {
                "ground_profile": None,
                "hazards": [],
                "source": "pavement_fixture_stub",
                "input_provenance": "none",
                "fixture_generated": False,
                "rgb_analyzed": False,
                "detection_applied": False,
                "models_executed": [],
                "not_for_navigation": True,
            }

        return {
            "ground_profile": self._fixture_profile(),
            "hazards": self._fixture_hazards(),
            "mount": frame.mount,
            "height_cm_metadata": frame.height_cm,
            "source": "pavement_fixture_stub",
            "input_provenance": "caller_supplied_unknown",
            "fixture_generated": True,
            "rgb_analyzed": False,
            "detection_applied": False,
            "depth_applied": False,
            "models_executed": [],
            "not_for_navigation": True,
            "research_prototype": True,
        }

    def _fixture_hazards(self) -> List[Dict]:
        return [
            {
                "label": "curb_up",
                "distance_m": 0.9,
                "urgency": "high",
                "source": "deterministic_fixture",
                "simulated": True,
                "model_executed": False,
            },
            {
                "label": "tactile_paving",
                "distance_m": 1.4,
                "urgency": "low",
                "source": "deterministic_fixture",
                "simulated": True,
                "model_executed": False,
            },
        ]

    def _fixture_profile(self) -> Dict:
        return {
            "slope_deg": 1.8,
            "cross_slope_deg": 0.5,
            "terrain_class": "abstract_test_surface",
            "walkable_width_m": 1.2,
            "confidence": None,
            "source": "deterministic_fixture",
            "simulated": True,
            "model_executed": False,
        }

    def to_costmap(self, pavement_scene):
        """Report the unimplemented planner conversion without a priority claim."""
        return {
            "costmap": None,
            "conversion_applied": False,
            "planner_priority_assigned": False,
            "source": "pavement_fixture_stub",
            "simulated": True,
            "not_for_navigation": True,
        }
