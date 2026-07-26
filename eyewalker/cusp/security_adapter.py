"""
SecurityLayer + GenCrypt wrapper for CUSP — ensures local-first privacy for assistive research

DT#9 synthetic research prototype. synthetic_only=true

Responsibility:
- Encrypt GPS/RGB blobs before any optional AgentAPI :8780 loopback
- Enforce privacy.yaml: no face ID, plate blur, aggregate-only crowd, no raw RGB exfiltration
- BPD mode: evidence integrity hash chain, redact by default, opt-in only tags
- ERIS mode: allow coarse GPS + anonymized thumbnails for remote situational awareness, but with GenCrypt

Implementation: mock AES-GCM placeholder + policy check
"""

from typing import Dict, Optional
import hashlib
import os

class CUSPSecurityAdapter:
    def __init__(self, bpd_mode=False, eris_mode=False):
        self.bpd_mode = bpd_mode
        self.eris_mode = eris_mode
        self.policy_violations = []

    def check_egress(self, payload: Dict) -> bool:
        """
        Returns True if allowed to egress (to 127.0.0.1:8780 only, never internet)
        Denies if contains raw rgb + gps without consent
        """
        has_rgb = "rgb" in payload or "rgb_raw" in payload
        has_gps = "gps" in payload or "lat" in payload

        if has_rgb and has_gps and not payload.get("consent", {}).get("cloud_upload", False):
            # must be local only — allow loopback but flag
            if not payload.get("loopback_only", False):
                self.policy_violations.append("rgb+gps without consent and not loopback_only")
                return False
        return True

    def encrypt_blob(self, blob: bytes) -> Dict:
        """
        Mock GenCrypt: real would use NIST PQC KEM + AES-GCM + device-bound key
        """
        # Mock hash as integrity
        h = hashlib.sha256(blob).hexdigest()[:16]
        return {
            "enc": f"genCrypt_mock_{h}",
            "hash": h,
            "alg": "AES-GCM-256_mock+PQC_KEM_mock",
            "tamper_evident": True,
            "synthetic_only": True,
        }

    def anonymize_frame(self, rgb, mode="bpd"):
        """
        Face + plate blur — mock returns same with metadata that blur applied
        """
        return {
            "rgb_blurred": rgb,
            "face_blur_applied": True,
            "plate_blur_applied": True,
            "aggregate_only": mode=="bpd",
            "method": "mediapipe_face+plate_local_tiny",
            "synthetic_only": True,
        }

    def audit(self) -> Dict:
        return {
            "violations": self.policy_violations,
            "bpd_redact_default": self.bpd_mode,
            "loopback_only_allow": "127.0.0.1:8780",
            "egress_deny_wildcard": True,
            "synthetic_only": True,
        }
