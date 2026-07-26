"""
Multi-camera fusion for eyeWalker v1.1 — HMD / body / pavement only.

Medical assistive research (NeuroAgent AI). Not a medical device.
No aerial / drone / elevated surveillance modality in the public medical OSS tree.

Fusion strategy (research):
- Prefer closest reliable cue: pavement (near) > HMD/body
- Optional research overlays (CUSP) must not override safety-critical drop/curb labels
- Privacy flags are *requests* only unless a real CV pipeline is attached
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class MultiCamFrameBundle:
    hmd: Optional[Dict] = None
    bodycam: Optional[Dict] = None
    pavement: Optional[Dict] = None
    timestamp: float = 0.0
    gps: Optional[Dict] = None


class MultiCamFusion:
    def __init__(self, use_cusp=True, privacy_mode=True):
        self.use_cusp = use_cusp
        self.privacy_mode = privacy_mode
        self.priorities = ["pavement", "hmd", "bodycam"]

    def fuse(self, bundle: MultiCamFrameBundle, cusp_ctx: Optional[Dict] = None, osm_graph=None) -> Dict:
        scene = {
            "timestamp": bundle.timestamp,
            "gps": bundle.gps,
            "modalities_present": [
                k
                for k, v in {
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
            "privacy": {
                "face_blur_requested": bool(self.privacy_mode),
                "face_blur_applied": False,
                "plate_blur_requested": bool(self.privacy_mode),
                "plate_blur_applied": False,
                "mode": self.privacy_mode,
                "note": "Redaction flags are requests only until CV blur is implemented.",
            },
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

        if cusp_ctx and self.use_cusp:
            scene = self._apply_cusp_guidance(scene, cusp_ctx)

        scene = self._enforce_safety_overrides(scene)

        if self.privacy_mode:
            scene["privacy_enforced"] = {
                "face_blur_requested": True,
                "face_blur_applied": False,
                "plate_blur_requested": True,
                "plate_blur_applied": False,
                "aggregate_only_requested": True,
                "note": "Not a security product; no silent claim of performed blur.",
            }

        return scene

    def _apply_cusp_guidance(self, scene: Dict, cusp: Dict) -> Dict:
        """Optional research overlay — modulators bounded; never overrides safety-critical."""
        for h in scene.get("hazards_fused", []):
            if "pier_edge" in h.get("label", "") or "curb_down" in h.get("label", ""):
                h["severity"] = "high"
                h["safety_override"] = True
            elif isinstance(cusp, dict) and "severity_mod" in cusp:
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
