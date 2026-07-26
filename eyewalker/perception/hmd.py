"""
HMD / smart glasses modality — egocentric primary for assistive navigation research.

eyeWalker v1.1 medical open source (NeuroAgent AI).
Devices (research targets): phone, Ray-Ban Meta–class, Quest-class, HoloLens-class.
Not a medical device. Assistive only — keep cane / guide dog.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class HMDFrame:
    rgb: any
    imu: any
    gps: Optional[Dict] = None
    timestamp: float = 0.0
    device: str = "phone"  # phone | rayban_meta | quest3 | hololens2
    pose_6dof: Optional[Dict] = None
    is_bodycam: bool = False


class HMDPerception:
    """Egocentric stream for obstacle / path cues (research / mock)."""

    def __init__(self, primary="phone", enable_bodycam=False):
        self.primary = primary
        self.enable_bodycam = enable_bodycam
        self.vio = None

    def on_hmd_frame(self, frame: HMDFrame) -> Dict:
        if frame.is_bodycam:
            return self._process_bodycam(frame)
        return self._process_hmd(frame)

    def _process_hmd(self, frame: HMDFrame) -> Dict:
        return {
            "modality": "hmd",
            "device": frame.device,
            "timestamp": frame.timestamp,
            "gps": frame.gps,
            "pose_6dof": frame.pose_6dof,
            "privacy": {
                "face_blur_requested": True,
                "face_blur_applied": False,
                "local_first": True,
                "note": "Redaction flags are requests only until CV blur is implemented.",
            },
            "synthetic_only": True,
            "research_prototype": True,
        }

    def _process_bodycam(self, frame: HMDFrame) -> Dict:
        return {
            "modality": "bodycam",
            "device": frame.device,
            "timestamp": frame.timestamp,
            "privacy": {
                "face_blur_requested": True,
                "face_blur_applied": False,
                "plate_blur_requested": True,
                "plate_blur_applied": False,
                "note": "Redaction flags are requests only until CV blur is implemented.",
            },
            "synthetic_only": True,
            "research_prototype": True,
        }
