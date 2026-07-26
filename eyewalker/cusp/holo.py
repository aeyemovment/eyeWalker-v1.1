"""
Short-horizon track memory for research overlays (not clinical).

eyeWalker v1.1 public research source. Synthetic / mock tracks only.
Not a security product. Not a medical device.
"""

from typing import List, Dict


class HoloMorphology:
    def __init__(self, n_tracks: int = 32, maturity: float = 0.8):
        self.n_tracks = max(1, min(int(n_tracks), 256))
        self.maturity = max(0.0, min(1.0, float(maturity)))
        self.tracks = []

    def update(self, detections: List[Dict], efference: Dict | None = None) -> Dict:
        for d in detections or []:
            self.tracks.append({
                "label": d.get("label", d.get("class", "")),
                "psi": float(d.get("cusp_psi2", 0.0) or 0.0),
                "age": 0,
                "source": d.get("source", "unknown"),
                "simulated": True,
            })
        # prune
        self.tracks = self.tracks[-self.n_tracks:]
        for tr in self.tracks:
            tr["age"] = int(tr.get("age", 0)) + 1
        self.tracks = [tr for tr in self.tracks if tr["age"] < 30]
        return {
            "n": len(self.tracks),
            "maturity": self.maturity,
            "tracks": list(self.tracks),
            "research_prototype": True,
            "synthetic_only": True,
        }


Holo267 = HoloMorphology  # back-compat alias
