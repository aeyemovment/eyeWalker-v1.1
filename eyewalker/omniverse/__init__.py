"""
Optional NVIDIA Omniverse / Isaac Sim hooks for *synthetic* navigation research.

Medical OSS eyeWalker v1.1 — NeuroAgent AI.
Not a medical device. Not dual-use packaging.
Requires separate Omniverse install; this module is a thin optional adapter.
"""

from .bridge import OmniverseBridge, OmniverseConfig

__all__ = ["OmniverseBridge", "OmniverseConfig"]
