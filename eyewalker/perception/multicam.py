"""
Multi-camera fusion for eyeWalker v1.1 — optional aerial <> HMD <> body <> pavement.

Medical assistive research (NeuroAgent AI). Not a medical device.

Fusion strategy (research):
- Prefer closest reliable cue: pavement (near) > HMD/body > aerial (context)
- Optional research overlays (CUSP) must not override safety-critical drop/curb labels
- Privacy: anonymize by default; local-first
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class MultiCamFrameBundle:
    aerial: Optional[Dict] = None
    hmd: Optional[Dict] = None
    bodycam: Optional[Dict] = None
    pavement: Optional[Dict] = None
    timestamp: float = 0.0
    gps: Optional[Dict] = None


class MultiCamFusion:
    def __init__(self, use_cusp=True, privacy_mode=True):
        self.use_cusp = use_cusp
        self.privacy_mode = privacy_mode
        self.priorities = ["pavement", "hmd", "bodycam", "aerial"]

    def fuse(self, bundle: MultiCamFrameBundle, cusp_ctx: Optional[Dict] = None, osm_graph=None) -> Dict:
        scene = {
            "timestamp": bundle.timestamp,
            "gps": bundle.gps,
            "modalities_present": [
                k
                for k, v in {
                    "aerial": bundle.aerial,
                    "hmd": bundle.hmd,
                    "bodycam": bundle.bodycam,
                    "pavement": bundle.pavement,
                }.items()
                if v
            ],
            "layers": {},
            "hazards_fused": [],
            "walkable_fused": None,
            "cusp": cusp_ctx,
            "privacy": {"anonymized": True, "no_face_id": True, "mode": self.privacy_mode},
            "synthetic_only": True,
            "research_prototype": True,
        }

        if bundle.pavement:
            scene["layers"]["pavement"] = bundle.pavement
            scene["hazards_fused"].extend(bundle.pavement.get("hazards", []))
            scene["walkable_fused"] = bundle.pavement.get("ground_profile")

        if bundle.hmd:
            scene["layers"]["hmd"] = bundle.hmd

        if bundle.bodycam:
            scene["layers"]["bodycam"] = bundle.bodycam

        if bundle.aerial:
            scene["layers"]["aerial"] = bundle.aerial
            scene["hazards_fused"].extend(bundle.aerial.get("far_hazards", []))

        if cusp_ctx and self.use_cusp:
            scene = self._apply_cusp_guidance(scene, cusp_ctx)

        scene = self._enforce_safety_overrides(scene)

        if self.privacy_mode:
            scene["privacy_enforced"] = {
                "face_blur": True,
                "plate_blur": True,
                "aggregate_only": True,
            }

        return scene

    def _apply_cusp_guidance(self, scene: Dict, cusp: Dict) -> Dict:
        """Optional research overlay — modulators bounded; never overrides safety-critical."""
        for h in scene.get("hazards_fused", []):
            if "pier_edge" in h.get("label", "") or "curb_down" in h.get("label", ""):
                h["severity"] = "high"
                h["safety_override"] = True
            elif isinstance(cusp, dict) and "severity_mod" in cusp:
                # keep advisory only
                h["research_mod_note"] = "cusp_mod_applied_research_only"
        return scene

    def _enforce_safety_overrides(self, scene: Dict) -> Dict:
        for h in scene.get("hazards_fused", []):
            lab = h.get("label", "")
            if any(x in lab for x in ("pier_edge", "curb_down", "drop", "open_water")):
                h["severity"] = "high"
                h["safety_override"] = True
        return scene

    def to_planner_input(self, scene: Dict) -> Dict:
        return {
            "hazards": scene.get("hazards_fused", []),
            "walkable": scene.get("walkable_fused"),
            "modalities": scene.get("modalities_present", []),
            "gps": scene.get("gps"),
            "synthetic_only": True,
        }
