"""Research VLM interfaces.

The local Spark-named path is a deterministic pseudo-record generator. Any
remote xAI request requires explicit remote-processing consent.
"""
from .hybrid_agent import HybridVLMAgent, HybridConfig

__all__ = ["HybridVLMAgent", "HybridConfig"]
