"""Caller-record aggregation stub for HMD, body, and pavement interfaces."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class MultiCamFrameBundle:
    hmd: Optional[Dict] = None
    bodycam: Optional[Dict] = None
    pavement: Optional[Dict] = None
    timestamp: float = 0.0
    gps: Optional[Dict] = None


class MultiCamFusion:
    """Aggregate caller records without claiming validated sensor fusion."""

    def __init__(self, use_cusp=True, privacy_mode=True):
        self.use_cusp = use_cusp
        self.privacy_mode = privacy_mode

    def fuse(
        self,
        bundle: MultiCamFrameBundle,
        cusp_ctx: Optional[Dict] = None,
        osm_graph=None,
    ) -> Dict:
        layers = {
            key: deepcopy(value)
            for key, value in {
                "hmd": bundle.hmd,
                "bodycam": bundle.bodycam,
                "pavement": bundle.pavement,
            }.items()
            if value
        }
        hazards = deepcopy((bundle.pavement or {}).get("hazards", []))
        profile = deepcopy((bundle.pavement or {}).get("ground_profile"))
        scene = {
            "timestamp": bundle.timestamp,
            "gps": deepcopy(bundle.gps),
            "modalities_present": list(layers),
            "layers": layers,
            "hazards_aggregated": hazards,
            "walkable_record": profile,
            "cusp_record": deepcopy(cusp_ctx),
            "input_provenance": "caller_supplied_unknown",
            "record_aggregation_applied": bool(layers),
            "validated_sensor_fusion": False,
            "rgb_analyzed": False,
            "models_executed": [],
            "synthetic_status": "unknown",
            "not_for_navigation": True,
            "research_prototype": True,
            "privacy": {
                "face_blur_requested": bool(self.privacy_mode),
                "face_blur_applied": False,
                "plate_blur_requested": bool(self.privacy_mode),
                "plate_blur_applied": False,
                "note": "Policy requests only; no redaction or aggregation privacy guarantee.",
            },
        }

        if cusp_ctx and self.use_cusp:
            for hazard in scene["hazards_aggregated"]:
                hazard["research_annotation_present"] = True
                hazard["cusp_override_applied"] = False

        if self.privacy_mode:
            scene["privacy_requests"] = {
                "face_blur_requested": True,
                "face_blur_applied": False,
                "plate_blur_requested": True,
                "plate_blur_applied": False,
                "aggregate_only_requested": True,
                "aggregate_only_applied": False,
                "note": "Requests only; no redaction or privacy-preserving aggregation is performed.",
            }
        return scene

    def to_planner_input(self, scene: Dict) -> Dict:
        """Expose records for interface testing, never as validated planner data."""
        return {
            "hazards": deepcopy(scene.get("hazards_aggregated", [])),
            "walkable": deepcopy(scene.get("walkable_record")),
            "modalities": list(scene.get("modalities_present", [])),
            "gps": deepcopy(scene.get("gps")),
            "input_provenance": scene.get("input_provenance", "unknown"),
            "validated_sensor_fusion": False,
            "suitable_for_navigation": False,
        }
