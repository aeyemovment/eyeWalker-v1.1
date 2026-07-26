"""Omniverse bridge stub — synthetic sim only, no live clinical claims."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OmniverseConfig:
    """Config for optional Omniverse / Isaac research sessions."""

    enabled: bool = False
    synthetic_only: bool = True
    research_prototype: bool = True
    not_medical_device: bool = True
    # User sets path if Omniverse is installed locally
    kit_path: Optional[str] = None
    scene_usd: Optional[str] = None


class OmniverseBridge:
    """
    Thin adapter. Does not ship Omniverse binaries.
    When disabled (default), returns explicit not_available payloads.
    """

    def __init__(self, config: Optional[OmniverseConfig] = None):
        self.config = config or OmniverseConfig()

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "available": False if not self.config.enabled else self._probe(),
            "synthetic_only": True,
            "research_prototype": True,
            "not_medical_device": True,
            "note": "Optional research sim path; not required for PWA assistive demo.",
        }

    def _probe(self) -> bool:
        # Real Omniverse detection would check kit_path / imports; keep false-safe.
        return False

    def render_synthetic_frame(self, seed: int = 0) -> Dict[str, Any]:
        """Return a labeled synthetic frame descriptor for offline training."""
        return {
            "seed": seed,
            "obstacles": [],
            "source": "omniverse_stub",
            "simulated": True,
            "synthetic_only": True,
            "available": self._probe() if self.config.enabled else False,
        }

    def connect_nemoclaw(self) -> Dict[str, Any]:
        """Declare pairing with NemoClaw local-first harness (policy only)."""
        return {
            "nemoclaw": "optional_local_harness",
            "omniverse": "optional_synthetic_sim",
            "pairing": "research_docs_only",
            "egress": "local_first",
            "synthetic_only": True,
        }
