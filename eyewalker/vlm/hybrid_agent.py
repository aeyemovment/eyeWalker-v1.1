"""Grok <> Muse Spark hybrid VLM agent (research prototype).

Modes (experiment knob):
  - spark_only: Muse Spark 1.1 scene graph / ground obstacles (local stub)
  - grok_only: xAI vision chat if XAI_API_KEY set
  - hybrid: Spark proposes ground obstacles; Grok re-ranks / natural language guidance
  - mock: deterministic harbor walk heuristics (offline / open-source default)

Not a medical device. Assistive research only — keep cane / guide dog.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


GROUND_CLASSES = (
    "manhole",
    "shadow_trap",
    "crack",
    "curb",
    "bench",
    "trash_bin",
    "pier_edge",
    "person",
    "low_branch",
    "bike",
)


@dataclass
class HybridConfig:
    mode: str = "hybrid"  # spark_only | grok_only | hybrid | mock
    model_spark: str = "muse-spark-1.1"
    model_grok: str = "grok-2-vision-latest"
    ground_mode: bool = True
    max_obstacles: int = 6
    xai_base: str = "https://api.x.ai/v1"
    synthetic_only: bool = True
    research_prototype: bool = True


@dataclass
class Obstacle:
    class_name: str
    distance_m: float
    bearing_deg: float
    urgency: str
    source: str  # spark | grok | hybrid | mock
    confidence: float = 0.6

    def to_dict(self) -> dict[str, Any]:
        return {
            "class": self.class_name,
            "distance_m": round(self.distance_m, 2),
            "bearing_deg": round(self.bearing_deg, 1),
            "urgency": self.urgency,
            "source": self.source,
            "confidence": round(self.confidence, 3),
        }


class HybridVLMAgent:
    """Real-time-ish VLM data producer for eyeWalker v1.1."""

    def __init__(self, config: HybridConfig | None = None):
        self.config = config or HybridConfig()
        self._step = 0
        self.session_id = time.strftime("%Y%m%dT%H%M%SZ")
        self.log_path = Path("docs/training/exports") / f"vlm_stream_{self.session_id}.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _spark_ground(self, frame_bytes: bytes | None, gps: dict | None) -> list[Obstacle]:
        """Muse Spark local path: hash-stable pseudo-detections (open-source runnable).

        When real weights land, replace with true forward pass. Ground-mode prioritizes
        surface hazards: manhole, shadow, crack, curb.
        """
        seed = hashlib.sha256((frame_bytes or b"demo")[:4096]).hexdigest()
        n = int(seed[0], 16) % 4  # 0-3 obstacles
        out: list[Obstacle] = []
        classes = (
            ("manhole", "HIGH"),
            ("shadow_trap", "MEDIUM"),
            ("crack", "MEDIUM"),
            ("curb", "LOW"),
            ("trash_bin", "MEDIUM"),
            ("bench", "LOW"),
        )
        for i in range(n + (1 if self.config.ground_mode else 0)):
            c, urg = classes[(int(seed[i + 1], 16) + i) % len(classes)]
            dist = 0.6 + (int(seed[i + 4], 16) % 25) / 10.0  # 0.6–3.1m
            bear = -35 + (int(seed[i + 6], 16) % 70)
            out.append(
                Obstacle(
                    class_name=c,
                    distance_m=dist,
                    bearing_deg=bear,
                    urgency=urg,
                    source="spark",
                    confidence=0.55 + (int(seed[i + 8], 16) % 30) / 100.0,
                )
            )
        return out[: self.config.max_obstacles]

    def _grok_rerank(self, obstacles: list[Obstacle], frame_note: str) -> tuple[list[Obstacle], str]:
        """Optional Grok pass. Without API key → return Spark set + local NL guidance."""
        key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
        if not key or self.config.mode in ("spark_only", "mock"):
            return obstacles, self._local_guidance(obstacles)

        # Lightweight HTTP optional — fail open to Spark
        try:
            import urllib.request

            prompt = (
                "You are eyeWalker assistive VLM (research prototype, not medical). "
                "Given ground obstacles, return JSON {obstacles:[{class,distance_m,bearing_deg,urgency}], guidance:str}. "
                f"Candidates: {json.dumps([o.to_dict() for o in obstacles])}. Context: {frame_note}"
            )
            body = json.dumps(
                {
                    "model": self.config.model_grok,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                }
            ).encode()
            req = urllib.request.Request(
                f"{self.config.xai_base}/chat/completions",
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
            text = data["choices"][0]["message"]["content"]
            # best-effort parse
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(text[start:end])
                obs = []
                for item in parsed.get("obstacles") or []:
                    obs.append(
                        Obstacle(
                            class_name=str(item.get("class", "obstacle")),
                            distance_m=float(item.get("distance_m", 2.0)),
                            bearing_deg=float(item.get("bearing_deg", 0)),
                            urgency=str(item.get("urgency", "MEDIUM")),
                            source="hybrid",
                            confidence=0.75,
                        )
                    )
                if obs:
                    return obs, str(parsed.get("guidance") or self._local_guidance(obs))
            return obstacles, text[:240]
        except Exception as e:
            g = self._local_guidance(obstacles)
            return obstacles, f"{g} (grok offline: {type(e).__name__})"

    def _local_guidance(self, obstacles: list[Obstacle]) -> str:
        if not obstacles:
            return "Path clear. Walk straight. Keep your cane."
        top = sorted(obstacles, key=lambda o: (0 if o.urgency == "HIGH" else 1, o.distance_m))[0]
        side = "left" if top.bearing_deg < -8 else ("right" if top.bearing_deg > 8 else "side-step")
        step = 0.4 if top.distance_m < 1.2 else 0.5
        return (
            f"{top.class_name.replace('_', ' ').upper()} {top.distance_m:.1f}m ahead, "
            f"step {side} {step:.1f}m. Keep your cane."
        )

    def infer(
        self,
        frame_bytes: bytes | None = None,
        gps: dict | None = None,
        note: str = "",
    ) -> dict[str, Any]:
        self._step += 1
        mode = self.config.mode
        if mode == "mock":
            obs = self._spark_ground(frame_bytes, gps)
            for o in obs:
                o.source = "mock"
            guidance = self._local_guidance(obs)
        elif mode == "spark_only":
            obs = self._spark_ground(frame_bytes, gps)
            guidance = self._local_guidance(obs)
        elif mode == "grok_only":
            obs = self._spark_ground(frame_bytes, gps)
            obs, guidance = self._grok_rerank(obs, note or "grok_only")
            for o in obs:
                o.source = "grok"
        else:  # hybrid
            spark = self._spark_ground(frame_bytes, gps)
            obs, guidance = self._grok_rerank(spark, note or "hybrid")
            for o in obs:
                if o.source == "spark":
                    o.source = "hybrid"

        payload = {
            "ts": time.time(),
            "step": self._step,
            "mode": mode,
            "model_spark": self.config.model_spark,
            "model_grok": self.config.model_grok,
            "ground_mode": self.config.ground_mode,
            "gps": gps or {},
            "obstacles": [o.to_dict() for o in obs],
            "guidance": guidance,
            "dt9": {
                "synthetic_only": self.config.synthetic_only,
                "research_prototype": self.config.research_prototype,
                "not_medical_device": True,
            },
        }
        with self.log_path.open("a") as f:
            f.write(json.dumps(payload) + "\n")
        return payload


def demo_once(mode: str = "hybrid") -> dict[str, Any]:
    agent = HybridVLMAgent(HybridConfig(mode=mode, ground_mode=True))
    return agent.infer(frame_bytes=b"harbor-demo-frame", gps={"lat": 39.2815, "lon": -76.5930})
