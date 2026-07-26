
"""Spatial audio guidance — binaural rendering of obstacle positions"""
class SpatialAudioEngine:
    def speak(self, text, bearing_deg=0, distance_m=2.0):
        """Render speech at 3D position (bearing, distance) so user hears where obstacle is"""
        # Use WebAudio / Resonance Audio in prod
        # For now, TTS
        print(f"[AUDIO {bearing_deg:.0f}° {distance_m:.1f}m] {text}")

    def guidance(self, avoidance_plan, obstacle):
        bearing = obstacle.bearing_deg
        msg = avoidance_plan["instruction"]
        self.speak(msg, bearing_deg=bearing, distance_m=obstacle.distance_m)
