"""
Chest / shoulder egocentric camera — optional assistive research stream.

eyeWalker v1.1 medical OSS (NeuroAgent AI).
Research prototype only. Not a medical device.
Privacy: blur/redaction are *requests* unless a real CV pipeline is wired.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class BodycamFrame:
    rgb: Any
    timestamp: float = 0.0
    imu: Optional[Any] = None
    gps: Optional[Dict] = None
    mount: str = "chest_center"  # chest_center | shoulder_right | shoulder_left


class BodycamPerception:
    def __init__(self, privacy_mode: bool = True):
        self.privacy_mode = privacy_mode
        self.fov = 78
        self.stabilization = "electronic_3axis"

    def ingest(self, frame: BodycamFrame) -> Dict:
        # IMPORTANT: no silent claim of performed blur. Raw buffer is unchanged
        # unless a real redaction backend is attached later.
        return {
            "rgb": frame.rgb,
            "rgb_redaction_status": "not_applied",
            "rgb_redaction_requested": bool(self.privacy_mode),
            "mount": frame.mount,
            "stabilized": True,
            "modality": "bodycam_chest_shoulder",
            "fov_deg": self.fov,
            "timestamp": frame.timestamp,
            "gps": (
                {"coarse": True, "precise_redacted": True}
                if self.privacy_mode and frame.gps
                else frame.gps
            ),
            "privacy": {
                "face_blur_requested": True,
                "face_blur_applied": False,
                "plate_blur_requested": True,
                "plate_blur_applied": False,
                "retain_raw_default": False,
                "note": "Redaction flags are requests only until CV blur is implemented.",
            },
            "synthetic_only": True,
            "research_prototype": True,
        }
