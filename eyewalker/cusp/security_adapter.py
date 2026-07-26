"""
Privacy helpers for local-first research (not a cryptography product).

eyeWalker v1.1 public research source — NeuroAgent AI.
Honest labels only: these are policy stubs / mock redaction metadata.
They do NOT provide real GenCrypt, PQC, or production security guarantees.
"""

from typing import Any, Dict, Optional
import hashlib


class PrivacyAdapter:
    """Local-first privacy policy helpers for assistive research demos."""

    def __init__(self, privacy_mode: bool = True):
        self.privacy_mode = privacy_mode

    def check_egress(self, payload: Dict[str, Any], consent_cloud: bool = False) -> Dict[str, Any]:
        """
        Fail-closed: block raw RGB+precise GPS together unless explicit consent.
        This is a research policy check, not a security product.
        """
        has_rgb = any(payload.get(key) is not None for key in ("rgb", "rgb_raw", "frame"))
        gps = payload.get("gps")
        if isinstance(gps, dict):
            coordinate_keys = ("lat", "lon", "latitude", "longitude")
            has_coordinates = any(gps.get(key) is not None for key in coordinate_keys)
            # A caller-controlled coarse flag cannot downgrade explicit
            # coordinates. A coarse-only descriptor must contain no coordinates.
            has_precise_gps = has_coordinates or (bool(gps) and not bool(gps.get("coarse")))
        else:
            has_precise_gps = gps is not None
        has_precise_gps = has_precise_gps or any(
            payload.get(key) is not None for key in ("lat", "lon", "latitude", "longitude")
        )
        if has_rgb and has_precise_gps and not consent_cloud:
            return {
                "allowed": False,
                "reason": "raw_rgb_plus_precise_gps_requires_explicit_consent",
                "research_only": True,
            }
        return {"allowed": True, "research_only": True}

    def integrity_hash(self, blob: bytes) -> str:
        """SHA-256 hex for local integrity notes — not encryption."""
        return hashlib.sha256(blob).hexdigest()

    def redact_metadata(self, meta: Optional[Dict] = None) -> Dict[str, Any]:
        meta = dict(meta or {})
        if self.privacy_mode:
            meta["face_blur_requested"] = True
            meta["face_blur_applied"] = False
            meta["plate_blur_requested"] = True
            meta["plate_blur_applied"] = False
            meta["aggregate_only_requested"] = True
            meta["aggregate_only_applied"] = False
            meta["note"] = "redaction flags only — actual CV blur must be implemented by caller"
        meta["security_product"] = False
        meta["research_prototype"] = True
        return meta


# Back-compat alias (old name implied real crypto — it does not)
CUSPSecurityAdapter = PrivacyAdapter
