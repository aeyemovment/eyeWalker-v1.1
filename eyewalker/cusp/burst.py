"""
|ΣΨ|² BURST field — CUSP* · |ΣΨ|² BURST holographic visual prototype

DT#9 synthetic research prototype. synthetic_only=true, bounded 0.25-3.0, core pure/invariant

For neuroscientists:
psi_i = complex salience wavefunction for i-th visual element (obstacle, walkable patch, flow vector)
|ΣΨ|² = sum_i |psi_i|² + cross_terms (interference = contextual grouping / clutter)
High |ΣΨ|² => high salience / urgency / need for foveation

This is analog to |ΣΨ|² BURST visualization seen in CUSP prototypes: colorful radial bursts on black canvas.

In eyeWalker: used to re-rank obstacle urgency when efference predicts attention shift.
Research note: provides a CUSP* burst overlay for on-device accessibility visualization

Bounded: psi amplitude scaled by severity_mod 0.25-3.0, never overrides HIGH safety holes
"""

import math
import numpy as np
from numbers import Real
from typing import List, Dict, Optional

class BurstField:
    def __init__(self, grid_size=64, decay_tau=0.3):
        self.grid_size = grid_size
        self.decay_tau = decay_tau  # core, invariant
        self.field = np.zeros((grid_size, grid_size), dtype=np.float32)
        self.psi_amplitudes = []

    def compute(self, detections: List[Dict], depth_map=None, efference: Optional[Dict]=None) -> np.ndarray:
        """
        Compute |ΣΨ|² map from detections
        detections: [{x,y, distance_m, synthetic_visualization_score, label}]
        ``synthetic_visualization_score`` is an explicit non-probabilistic
        fixture weight. Missing or invalid weights are rejected; they are never
        replaced by an invented confidence.
        Returns 2D array field + psi list
        """
        self.field = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        self.psi_amplitudes = []

        severity_mod = efference.get("severity_mod", 1.0) if efference and isinstance(efference, dict) else 1.0
        severity_mod = max(0.25, min(3.0, float(severity_mod)))

        for det in detections:
            # map world x,y or image x,y to grid — mock if not present
            cx = int(det.get("x", self.grid_size//2)) % self.grid_size
            cy = int(det.get("y", self.grid_size//2)) % self.grid_size
            raw_score = det.get("synthetic_visualization_score")
            if (
                not isinstance(raw_score, Real)
                or isinstance(raw_score, bool)
                or not math.isfinite(raw_score)
                or not 0.0 <= raw_score <= 1.0
            ):
                raise ValueError(
                    "each burst fixture requires synthetic_visualization_score in [0, 1]"
                )
            fixture_score = float(raw_score)
            dist = float(det.get("distance_m", det.get("dist_m", 2.0)))

            # Abstract fixture amplitude; not a probability or detector confidence.
            psi_amp = fixture_score * (1.0 / max(0.5, dist)) * severity_mod
            psi_amp = max(0.0, min(3.0, psi_amp))

            # build radial burst kernel
            self._add_burst(cx, cy, psi_amp, radius = int(8 * psi_amp))

            self.psi_amplitudes.append({
                "psi": psi_amp,
                "pos": (cx, cy),
                "label": det.get("label", ""),
                "synthetic_visualization_score": fixture_score,
            })

        # |ΣΨ|² = sum |psi|² (cross terms ignored for PoC, would capture grouping)
        psi2 = np.sum(self.field ** 2)  # scalar summary, but we keep full field
        return self.field

    def _add_burst(self, cx, cy, amp, radius=6):
        for dy in range(-radius, radius+1):
            for dx in range(-radius, radius+1):
                x = cx + dx
                y = cy + dy
                if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                    r = math.sqrt(dx*dx + dy*dy)
                    if r <= radius:
                        val = amp * math.exp(-r / max(1, radius/2))
                        self.field[y, x] = max(self.field[y, x], val)

    def to_overlay(self, threshold=0.3) -> List[Dict]:
        """
        Export bursts above threshold for PWA rendering
        """
        bursts = []
        # simple peak detection
        for info in self.psi_amplitudes:
            if info["psi"] > threshold:
                bursts.append({
                    "x": info["pos"][0] / self.grid_size,
                    "y": info["pos"][1] / self.grid_size,
                    "psi2": info["psi"]**2,
                    "amp": info["psi"],
                    "label": info["label"],
                    "render": "CUSP* burst",
                })
        return bursts

def compute_burst_field(detections, depth=None, efference=None):
    bf = BurstField()
    field = bf.compute(detections, depth, efference)
    return {"psi2_map": field, "bursts": bf.to_overlay(), "synthetic_only": True, "core": {"decay_tau": bf.decay_tau}}
