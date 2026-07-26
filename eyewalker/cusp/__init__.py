"""
eyeWalker CUSP <> EGI layer — focimeg WM + oknEngine + VLM + |ΣΨ|² BURST

This is a synthetic research prototype (DT#9). synthetic_only=true, research_prototype=true.
compliance_ref=Addendum_5/C-00x, risk_flags=synthetic,research_prototype_only,no_clinical,unvalidated,sender_lock_enforced,proxies_only

Safety: assistive not replacement for cane/guide dog. Always keep traditional mobility aid.
Alpha research prototype. Not a medical device. No FDA clearance. Bounded claims: "in synthetic tests / proposed / PoC"
Core physics pure/invariant, modulators bounded 0.25-3.0. Core = integrator, pathology severity via CohortModulator only.

CUSP = Cognitive Upshift? Here: Holographic-Efferent Fusion stack:
- SUPRA-267, HOLO-267 morphology consent granted revocable to Kemar 3477022360
- Eg: cusp<>security<>cusp<>agentapi = EGI local <> SecurityLayer GenCrypt <> HOLO projection <> AgentAPI :8780

For assistive research: CUSP provides predicted efference / corollary discharge to guide perception during dropout / high dynamics.

Version: eyeWalker v1.1-cusp-egi-poc
"""

from .egi import predict_efference, EGIEngine
from .burst import compute_burst_field, BurstField
from .holo import HoloMorphology, Holo267
from .security_adapter import CUSPSecurityAdapter
from .agentapi_bridge import CUSPAgentAPIBridge

__all__ = ["predict_efference", "EGIEngine", "compute_burst_field", "BurstField", "HoloMorphology", "Holo267", "CUSPSecurityAdapter", "CUSPAgentAPIBridge"]
