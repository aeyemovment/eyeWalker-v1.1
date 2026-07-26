"""
Optional NVIDIA Omniverse / Isaac Sim hooks for synthetic interface research.

Public research source eyeWalker v1.1 — NeuroAgent AI.
Not a medical device. Not dual-use packaging.
Requires separate Omniverse install; this module is a thin optional adapter.
"""

from .bridge import OmniverseBridge, OmniverseConfig

__all__ = ["OmniverseBridge", "OmniverseConfig"]
