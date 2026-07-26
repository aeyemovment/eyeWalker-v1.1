"""
Optional unvalidated research overlays for eyeWalker (EGI / salience) v1.1.

Research prototype only. Not a medical device.
No personal identifiers, no dual-use program hooks in this public package.
"""

from .egi import predict_efference, EGIEngine
from .burst import compute_burst_field, BurstField
from .holo import HoloMorphology
from .security_adapter import PrivacyAdapter, CUSPSecurityAdapter
from .agentapi_bridge import CUSPAgentAPIBridge

__all__ = [
    "predict_efference",
    "EGIEngine",
    "compute_burst_field",
    "BurstField",
    "HoloMorphology",
    "PrivacyAdapter",
    "CUSPSecurityAdapter",
    "CUSPAgentAPIBridge",
]
