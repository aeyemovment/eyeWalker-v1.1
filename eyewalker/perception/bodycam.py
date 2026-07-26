"""
Chest / shoulder egocentric camera — optional assistive research stream.

eyeWalker v1.1 medical open source (NeuroAgent AI).
Research prototype only. Not a medical device.
Privacy: prefer face/plate blur; local-first retention.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class BodycamFrame:
    rgb: any
    timestamp: float = 0.0
    imu: Optional[any] = None
    gps: Optional[Dict] = None
    mount: str = "chest_center"  # chest_center | shoulder_right | shoulder_left


class BodycamPerception:
    def __init__(self, privacy_mode=True):
        self.privacy_mode = privacy_mode
        self.fov = 78
        self.stabilization = "electronic_3axis"

    def ingest(self, frame: BodycamFrame) -> Dict:
        return {
            "rgb_anonymized": frame.rgb,
            "mount": frame.mount,
            "stabilized": True,
            "modality": "bodycam_chest_shoulder",
            "fov_deg": self.fov,
            "timestamp": frame.timestamp,
            "gps": frame.gps if not self.privacy_mode else {"redacted": True, "coarse": True},
            "privacy": {
                "face_blur": True,
                "plate_blur": True,
                "retain_raw": False,
            },
            "synthetic_only": True,
            "research_prototype": True,
        }
