"""
Privacy helpers for local-first research (not a cryptography product).

eyeWalker v1.1 medical OSS — NeuroAgent AI.
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
        has_rgb = "rgb" in payload or "frame" in payload
        has_precise_gps = bool(payload.get("gps") and not payload.get("gps", {}).get("coarse"))
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
            meta["plate_blur_requested"] = True
            meta["aggregate_only"] = True
            meta["note"] = "redaction flags only — actual CV blur must be implemented by caller"
        meta["security_product"] = False
        meta["research_prototype"] = True
        return meta


# Back-compat alias (old name implied real crypto — it does not)
CUSPSecurityAdapter = PrivacyAdapter
