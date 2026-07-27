"""
AgentAPI :8780 loopback policy bridge for CUSP.

synthetic_only=true research prototype. Not a medical device.

No HTTP transport is implemented in this module. A future transport may use:
- GET /health
- POST /api/cusp/infer — {rgb, gps_coarse, efference, psi_hints} -> {psi2_map, severity_mod, tracks}

The configured base is validated as HTTP loopback port 8780. Sensitive payloads
passed through ``try_post`` are checked by PrivacyAdapter before the local mock
fallback runs. This is application-level validation, not a sandbox or security
boundary.
"""

from ipaddress import ip_address
from typing import Dict, Optional
from urllib.parse import urlparse

from .security_adapter import PrivacyAdapter


def _validated_loopback_base(base: str) -> str:
    """Return a normalized base URL or reject anything except HTTP loopback:8780."""
    if not isinstance(base, str) or not base.strip():
        raise ValueError("AgentAPI base must be a non-empty URL")

    parsed = urlparse(base.strip())
    if parsed.scheme != "http" or parsed.username or parsed.password:
        raise ValueError("AgentAPI base must use unauthenticated HTTP loopback")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("AgentAPI base must not include a path, query, or fragment")

    host = parsed.hostname
    try:
        if not host or not ip_address(host).is_loopback:
            raise ValueError
    except ValueError as exc:
        raise ValueError("AgentAPI base host must be a numeric loopback address") from exc

    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("AgentAPI base has an invalid port") from exc
    if port != 8780:
        raise ValueError("AgentAPI base port must be 8780")
    return base.strip().rstrip("/")


class CUSPAgentAPIBridge:
    def __init__(
        self,
        base: str = "http://127.0.0.1:8780",
        timeout_ms: int = 50,
        privacy_adapter: Optional[PrivacyAdapter] = None,
    ):
        self.base = _validated_loopback_base(base)
        self.timeout_ms = max(1, int(timeout_ms))
        self.privacy_adapter = privacy_adapter or PrivacyAdapter()
        self.last_ok = None

    def health(self) -> Dict:
        """Report the unimplemented transport without probing the network."""
        return {
            "status": "transport_not_implemented",
            "network_used": False,
            "synthetic_only": True,
        }

    def try_get_cusp_context(self, frame_bundle=None, efference=None) -> Dict:
        """
        Return local mock context while the HTTP transport is unimplemented.
        """
        health = self.health()
        if health["status"] != "ok":
            result = self._local_fallback(efference)
            result["health"] = health
            return result

        # Reserved for a future, tested HTTP transport.
        return {"psi2_map": None, "severity_mod": 1.0, "source": "agentapi", "health": health, "synthetic_only": True}

    def _local_fallback(self, efference) -> Dict:
        # No transport or calibrated model runs here. Use a named neutral
        # fixture value rather than converting a missing/fabricated confidence.
        sev = 1.0
        return {
            "psi2_map": None,
            "severity_mod": sev,
            "severity_mod_source": "neutral_unvalidated_fixture_value",
            "bursts": [],
            "tracks": [],
            "source": "local_fallback",
            "fallback_reason": "transport_not_implemented",
            "synthetic_only": True,
            "transport": "not_implemented",
            "network_used": False,
        }

    def try_post(self, payload: Dict, consent_cloud: bool = False) -> Dict:
        """
        Apply the privacy policy before the local mock fallback.

        No network request is made. The check remains in this method so a future
        transport cannot be added without passing through the same policy gate.
        """
        policy = self.privacy_adapter.check_egress(payload, consent_cloud=consent_cloud)
        if not policy["allowed"]:
            return {
                "status": "blocked_by_privacy_policy",
                "privacy_policy": policy,
                "network_used": False,
                "synthetic_only": True,
            }

        result = self.try_get_cusp_context()
        result["privacy_policy"] = policy
        return result


def try_get_cusp(*args, **kwargs):
    bridge = CUSPAgentAPIBridge()
    return bridge.try_get_cusp_context(*args, **kwargs)
