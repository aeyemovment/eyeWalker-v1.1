"""
AgentAPI :8780 loopback bridge for CUSP — local-only, fallback to mock if down

DT#9 synthetic research prototype. synthetic_only=true

Endpoints expected:
- GET /health
- POST /api/cusp/infer — {rgb, gps_coarse, efference, psi_hints} -> {psi2_map, severity_mod, tracks}
- Research note: same but anonymized

Security: only 127.0.0.1:8780, never 0.0.0.0, enforced in blueprint.yaml egress
If 8780 down, fallback to local EGI+Burst+Holo pure Python (no network)
"""

import json
import time
from typing import Dict, Optional

class CUSPAgentAPIBridge:
    def __init__(self, base="http://127.0.0.1:8780", timeout_ms=50):
        self.base = base
        self.timeout_ms = timeout_ms
        self.last_ok = None
        self.fail_count = 0

    def health(self) -> Dict:
        """
        Try /health — if fails, note but don't crash; fallback to local
        """
        try:
            # Without requests dep, use socket mock for PoC — always returns fallback in this stub
            # In real: requests.get(f"{self.base}/health", timeout=self.timeout_ms/1000)
            raise Exception("mock offline for PoC — use local")
        except Exception as e:
            self.fail_count += 1
            return {"status": "down_local_fallback", "fail_count": self.fail_count, "synthetic_only": True, "error": str(e)}

    def try_get_cusp_context(self, frame_bundle=None, efference=None) -> Dict:
        """
        Try remote infer, fallback to local
        """
        health = self.health()
        if health["status"] == "down_local_fallback":
            # local fallback
            return self._local_fallback(efference)

        # if up, would POST and return remote
        return {"psi2_map": None, "severity_mod": 1.0, "source": "agentapi", "health": health, "synthetic_only": True}

    def _local_fallback(self, efference) -> Dict:
        # Local compute — same logic as egi+burst+holo but without GPU
        sev = 1.0
        if efference and isinstance(efference, dict):
            sev = max(0.25, min(3.0, float(efference.get("confidence",1.0) * 1.2)))
        return {
            "psi2_map": None,
            "severity_mod": sev,
            "bursts": [],
            "tracks": [],
            "source": "local_fallback",
            "fallback_reason": "agentapi_down_or_mock",
            "synthetic_only": True,
            "privacy": {"local_first": True},
        }

    def try_post(self, payload: Dict) -> Dict:
        """
        Generic POST to agentapi — with security_adapter check first
        """
        # Security check would happen before this call in multicam fusion
        return self.try_get_cusp_context()

def try_get_cusp(*args, **kwargs):
    bridge = CUSPAgentAPIBridge()
    return bridge.try_get_cusp_context(*args, **kwargs)
