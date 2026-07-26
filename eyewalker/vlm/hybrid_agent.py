"""Grok <> Muse Spark hybrid VLM agent (research prototype).

Modes (experiment knob):
  - spark_only: Muse Spark 1.1 scene graph / ground obstacles (local stub)
  - grok_only: local pseudo-records; optional xAI annotation only with key + explicit consent
  - hybrid: local pseudo-records; optional consented xAI class annotation
  - mock: deterministic harbor-style fixtures (offline evaluation mode)

Not a medical device. Assistive research only — keep cane / guide dog.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from dataclasses import dataclass
from numbers import Real
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


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

SIMULATED_RESEARCH_LABEL = "SIMULATED RESEARCH CUE:"
SAFETY_SUFFIX = "Keep your cane or guide dog. Not a medical device."
VALID_MODES = frozenset({"spark_only", "grok_only", "hybrid", "mock"})
VALID_URGENCIES = frozenset({"HIGH", "MEDIUM", "LOW"})
URGENCY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
CANONICAL_XAI_BASE = "https://api.x.ai/v1"
ALLOWED_GROK_MODELS = frozenset({"grok-4.5"})
SAFE_TOKEN = re.compile(r"^[a-z0-9_]{1,64}$")


def _finite_real(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


@dataclass
class HybridConfig:
    mode: str = "hybrid"  # spark_only | grok_only | hybrid | mock
    model_spark: str = "muse-spark-1.1"
    # Exact reviewed model ID. Aliases such as ``*-latest`` are intentionally
    # rejected because their target may change without a code review.
    model_grok: str = "grok-4.5"
    ground_mode: bool = True
    max_obstacles: int = 6
    xai_base: str = CANONICAL_XAI_BASE
    # Remote processing is always explicit opt-in. Merely having an API key in
    # the environment is not consent to transmit candidate records or notes.
    remote_processing_consent: bool = False
    log_enabled: bool = False
    log_dir: str | None = None
    log_precise_gps: bool = False
    synthetic_only: bool = True
    research_prototype: bool = True


@dataclass
class Obstacle:
    class_name: str
    distance_m: float
    bearing_deg: float
    urgency: str
    source: str  # simulated_spark | simulated_grok | simulated_hybrid | mock
    confidence: float | None = None

    @property
    def simulated(self) -> bool:
        return isinstance(self.source, str) and (
            self.source == "mock" or self.source.startswith("simulated_")
        )

    def to_dict(self) -> dict[str, Any]:
        geometry_valid = (
            _finite_real(self.distance_m)
            and self.distance_m >= 0
            and _finite_real(self.bearing_deg)
            and -180 <= self.bearing_deg <= 180
        )
        class_valid = isinstance(self.class_name, str) and bool(
            SAFE_TOKEN.fullmatch(self.class_name)
        )
        urgency_valid = self.urgency in VALID_URGENCIES
        source_valid = isinstance(self.source, str) and bool(
            SAFE_TOKEN.fullmatch(self.source)
        )
        payload = {
            "class": self.class_name if class_valid else "obstacle",
            "distance_m": round(float(self.distance_m), 2) if geometry_valid else None,
            "bearing_deg": round(float(self.bearing_deg), 1) if geometry_valid else None,
            "urgency": self.urgency if urgency_valid else "UNKNOWN",
            "source": self.source if source_valid else "invalid_local_record",
            # No detector-calibrated confidence exists in this prototype.
            "confidence": None,
            "simulated": self.simulated,
        }
        if not (geometry_valid and class_valid and urgency_valid and source_valid):
            payload["invalid_record"] = True
        return payload


class HybridVLMAgent:
    """Synthetic research payload producer with an optional consented remote path."""

    def __init__(self, config: HybridConfig | None = None):
        self.config = config or HybridConfig()
        self._validate_mode(self.config.mode)
        self._validate_remote_config()
        self._step = 0
        self.session_id = time.strftime("%Y%m%dT%H%M%SZ")
        self.log_path: Path | None = None
        if self.config.log_enabled:
            base = (
                Path(self.config.log_dir).expanduser()
                if self.config.log_dir
                else Path.home() / ".local" / "state" / "eyewalker"
            )
            base.mkdir(parents=True, exist_ok=True)
            self.log_path = base / f"vlm_stream_{self.session_id}.jsonl"

    @staticmethod
    def _validate_mode(mode: str) -> str:
        if mode not in VALID_MODES:
            allowed = ", ".join(sorted(VALID_MODES))
            raise ValueError(f"unsupported mode {mode!r}; expected one of: {allowed}")
        return mode

    def _validate_remote_config(self) -> None:
        if self.config.model_grok not in ALLOWED_GROK_MODELS:
            allowed = ", ".join(sorted(ALLOWED_GROK_MODELS))
            raise ValueError(f"unsupported Grok model; expected exactly: {allowed}")
        if not isinstance(self.config.xai_base, str):
            raise ValueError("xAI base must be the canonical HTTPS API origin")
        if (
            not isinstance(self.config.max_obstacles, int)
            or isinstance(self.config.max_obstacles, bool)
            or not 1 <= self.config.max_obstacles <= 50
        ):
            raise ValueError("max_obstacles must be an integer from 1 through 50")
        parsed = urlsplit(self.config.xai_base)
        if (
            self.config.xai_base != CANONICAL_XAI_BASE
            or parsed.scheme != "https"
            or parsed.hostname != "api.x.ai"
            or parsed.port is not None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path != "/v1"
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                f"xAI base must be exactly {CANONICAL_XAI_BASE}; "
                "custom origins and paths are not allowed"
            )

    @staticmethod
    def _obstacle_error(obstacle: Obstacle) -> str | None:
        if not isinstance(obstacle, Obstacle):
            return "record is not an Obstacle"
        if not isinstance(obstacle.class_name, str) or not SAFE_TOKEN.fullmatch(
            obstacle.class_name
        ):
            return "class is not a sanitized token"
        if obstacle.urgency not in VALID_URGENCIES:
            return "urgency is outside HIGH/MEDIUM/LOW"
        if not isinstance(obstacle.source, str) or not SAFE_TOKEN.fullmatch(
            obstacle.source
        ):
            return "source is not a sanitized token"
        if not _finite_real(obstacle.distance_m) or obstacle.distance_m < 0:
            return "distance is not a finite nonnegative real"
        if (
            not _finite_real(obstacle.bearing_deg)
            or not -180 <= obstacle.bearing_deg <= 180
        ):
            return "bearing is not a finite real in [-180, 180]"
        return None

    @classmethod
    def _obstacle_collection_error(cls, obstacles: list[Obstacle]) -> str | None:
        if not isinstance(obstacles, list):
            return "obstacle collection is not a list"
        for obstacle in obstacles:
            error = cls._obstacle_error(obstacle)
            if error:
                return error
        return None

    @staticmethod
    def _serialize_obstacle(obstacle: Any) -> dict[str, Any]:
        if isinstance(obstacle, Obstacle):
            return obstacle.to_dict()
        return {
            "class": "obstacle",
            "distance_m": None,
            "bearing_deg": None,
            "urgency": "UNKNOWN",
            "source": "invalid_local_record",
            "confidence": None,
            "simulated": True,
            "invalid_record": True,
        }

    @classmethod
    def _top_obstacle(cls, obstacles: list[Obstacle]) -> Obstacle | None:
        if not obstacles:
            return None
        error = cls._obstacle_collection_error(obstacles)
        if error:
            raise ValueError(f"invalid obstacle record: {error}")
        return sorted(
            obstacles,
            key=lambda obstacle: (
                URGENCY_RANK[obstacle.urgency],
                obstacle.distance_m,
            ),
        )[0]

    def _spark_ground(self, frame_bytes: bytes | None, gps: dict | None) -> list[Obstacle]:
        """Muse Spark local path: hash-stable source-available pseudo-records.

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
                    source="simulated_spark",
                    confidence=None,
                )
            )
        return out[: self.config.max_obstacles]

    def _grok_rerank(
        self,
        obstacles: list[Obstacle],
        frame_note: str,
        remote_source: str,
    ) -> tuple[list[Obstacle], bool, bool, bool]:
        """Optionally refine obstacles with Grok, never user-facing movement guidance.

        Returns ``(obstacles, attempted, responded, applied)``. The model's
        free-form guidance is intentionally ignored: direction and safety
        wording are always regenerated by :meth:`_local_guidance`.
        """
        # Revalidate mutable configuration before reading or attaching a key.
        self._validate_remote_config()
        if self._obstacle_collection_error(obstacles):
            return obstacles, False, False, False
        key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
        if (
            not self.config.remote_processing_consent
            or not key
            or self.config.mode in ("spark_only", "mock")
        ):
            return obstacles, False, False, False

        # Lightweight optional HTTP; any failure falls back to local records.
        try:
            import urllib.request

            prompt = (
                "You are eyeWalker assistive VLM (research prototype, not medical). "
                "Given ground obstacles, return JSON "
                "{obstacles:[{class,distance_m,bearing_deg,urgency}]}. "
                "Obstacle bearings are user-relative: negative is left and positive is right. "
                "Do not author movement guidance; a local safety planner derives it. "
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
                response_body = resp.read().decode()
        except Exception:
            return obstacles, True, False, False

        # The request completed. A malformed response is still truthful provenance,
        # but it must not replace the local obstacle set or movement planner.
        try:
            data = json.loads(response_body)
            text = data["choices"][0]["message"]["content"]
            # best-effort parse
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(text[start:end])
                remote_items = parsed.get("obstacles") or []
                obs = []
                any_annotation_applied = False
                # Remote output may annotate a local class label, but it never
                # controls distance, bearing, urgency, confidence, or which
                # local obstacle is selected. Movement geometry stays local.
                for local, item in zip(
                    obstacles[: self.config.max_obstacles],
                    remote_items[: self.config.max_obstacles],
                ):
                    if not isinstance(item, dict):
                        continue
                    class_name = (
                        str(item.get("class", local.class_name))
                        .strip()
                        .lower()
                        .replace("-", "_")
                        .replace(" ", "_")
                    )
                    if class_name not in GROUND_CLASSES:
                        class_name = local.class_name
                    changed = class_name != local.class_name
                    any_annotation_applied = any_annotation_applied or changed
                    obs.append(
                        Obstacle(
                            class_name=class_name,
                            distance_m=local.distance_m,
                            bearing_deg=local.bearing_deg,
                            urgency=local.urgency,
                            source=remote_source if changed else local.source,
                            confidence=local.confidence,
                        )
                    )
                if len(obs) == len(obstacles[: self.config.max_obstacles]):
                    return obs, True, True, any_annotation_applied
            return obstacles, True, True, False
        except Exception:
            return obstacles, True, True, False

    def _local_guidance(self, obstacles: list[Obstacle]) -> str:
        """Step AWAY from obstacle bearing: neg=left obstacle → step right."""
        if not obstacles:
            return (
                f"{SIMULATED_RESEARCH_LABEL} no simulated obstacle record is "
                "available; stop and verify. "
                f"{SAFETY_SUFFIX}"
            )
        try:
            top = self._top_obstacle(obstacles)
        except ValueError:
            return (
                f"{SIMULATED_RESEARCH_LABEL} invalid simulated obstacle record; "
                f"HOLD and stop and verify. {SAFETY_SUFFIX}"
            )
        if top is None:
            raise RuntimeError("top-obstacle invariant failed")
        if top.bearing_deg < -8:
            side = "right"
        elif top.bearing_deg > 8:
            side = "left"
        else:
            return (
                f"{SIMULATED_RESEARCH_LABEL} simulated obstacle bearing is "
                f"centered or ambiguous; HOLD and stop and verify. {SAFETY_SUFFIX}"
            )
        step = 0.4 if top.distance_m < 1.2 else 0.5
        class_name = top.class_name if top.class_name in GROUND_CLASSES else "obstacle"
        return (
            f"{SIMULATED_RESEARCH_LABEL} {class_name.replace('_', ' ').upper()} "
            f"{top.distance_m:.1f}m ahead (bearing {top.bearing_deg:+.0f}°), "
            f"step {side} {step:.1f}m. {SAFETY_SUFFIX}"
        )

    def infer(
        self,
        frame_bytes: bytes | None = None,
        gps: dict | None = None,
        note: str = "",
    ) -> dict[str, Any]:
        mode = self._validate_mode(self.config.mode)
        self._validate_remote_config()
        self._step += 1
        remote_attempted = False
        remote_responded = False
        remote_applied = False
        if mode == "mock":
            obs = self._spark_ground(frame_bytes, gps)
            if self._obstacle_collection_error(obs) is None:
                for o in obs:
                    o.source = "mock"
        elif mode == "spark_only":
            obs = self._spark_ground(frame_bytes, gps)
        elif mode == "grok_only":
            obs = self._spark_ground(frame_bytes, gps)
            obs, remote_attempted, remote_responded, remote_applied = self._grok_rerank(
                obs,
                note or "grok_only",
                remote_source="simulated_grok",
            )
        else:  # hybrid
            spark = self._spark_ground(frame_bytes, gps)
            obs, remote_attempted, remote_responded, remote_applied = self._grok_rerank(
                spark,
                note or "hybrid",
                remote_source="simulated_hybrid",
            )

        # All current perception paths are deterministic/model research paths,
        # not a validated live detector. Keep the visible cue and metadata aligned.
        guidance = self._local_guidance(obs)
        simulated = True

        obstacle_error = self._obstacle_collection_error(obs)
        top = None if obstacle_error else self._top_obstacle(obs)
        if obstacle_error:
            guidance_source = "local_fail_closed_invalid_record"
        elif top is None:
            guidance_source = "local_fail_closed_no_obstacle_record"
        elif -8 <= top.bearing_deg <= 8:
            guidance_source = "local_fail_closed_ambiguous_bearing"
        else:
            guidance_source = "local_step_away"

        payload = {
            "ts": time.time(),
            "step": self._step,
            "mode": mode,
            "model_spark": self.config.model_spark,
            "model_grok": self.config.model_grok,
            "ground_mode": self.config.ground_mode,
            "gps": gps or {},
            "gps_provenance": (
                "caller_supplied_synthetic"
                if gps and gps.get("synthetic") is True
                else "caller_supplied_unknown"
                if gps
                else "not_supplied"
            ),
            "obstacles": [self._serialize_obstacle(o) for o in obs],
            "guidance": guidance,
            "guidance_source": guidance_source,
            "simulated": simulated,
            "remote_model_attempted": remote_attempted,
            "remote_model_executed": remote_responded,
            "remote_model_applied": remote_applied,
            "models_executed": [self.config.model_grok] if remote_responded else [],
            "dt9": {
                "synthetic_only": simulated,
                "research_prototype": self.config.research_prototype,
                "not_medical_device": True,
            },
        }
        if self.log_path is not None:
            log_payload = dict(payload)
            if gps and not self.config.log_precise_gps:
                log_payload["gps"] = {
                    "present": True,
                    "precise_redacted": True,
                }
            with self.log_path.open("a") as f:
                f.write(json.dumps(log_payload) + "\n")
        return payload


def demo_once(mode: str = "hybrid") -> dict[str, Any]:
    agent = HybridVLMAgent(HybridConfig(mode=mode, ground_mode=True))
    return agent.infer(frame_bytes=b"synthetic-demo-frame", gps=None)
