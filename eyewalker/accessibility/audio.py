"""Console text-output stub; no TTS, binaural, or spatial audio is rendered."""


class SpatialAudioEngine:
    """Backwards-compatible class name for an explicit console-only stub."""

    def speak(self, text, bearing_deg=0, distance_m=2.0):
        result = {
            "text": text,
            "bearing_deg_metadata": bearing_deg,
            "distance_m_metadata": distance_m,
            "console_output_applied": True,
            "tts_applied": False,
            "binaural_rendering_applied": False,
            "spatial_audio_applied": False,
            "status": "console_text_only",
        }
        print(f"[SIMULATED TEXT CUE] {text}")
        return result

    def guidance(self, avoidance_plan, obstacle):
        return self.speak(
            avoidance_plan["instruction"],
            bearing_deg=obstacle.bearing_deg,
            distance_m=obstacle.distance_m,
        )
