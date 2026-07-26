
"""Baltimore Harbor 3.66mi loop — your actual route"""
import argparse
from eyewalker.ground_truth.osm import get_harbor_graph
from eyewalker.ground_truth.satellite import get_ground_truth_cache
from eyewalker.perception.detector import detect_obstacles
from eyewalker.obstacle.identifier import classify_obstacle, Obstacle, ObstacleType
from eyewalker.obstacle.risk import assess_risk
from eyewalker.planner.avoidance import AvoidancePlanner
from eyewalker.accessibility.audio import SpatialAudioEngine

def main():
    parser = argparse.ArgumentParser(description="eyeWalker Harbor Walk")
    parser.add_argument("--gpx", help="Path to Apple GPX export (3.66mi)")
    parser.add_argument("--satellite", default="esri", choices=["esri", "maptiler", "osm"])
    parser.add_argument("--mode", default="obstacle-avoidance")
    args = parser.parse_args()

    print(f"eyeWalker loading ground truth — source {args.satellite} <3yr")
    graph = get_harbor_graph()
    tiles = get_ground_truth_cache(None, source=args.satellite)
    print(f"Graph nodes: {len(graph.nodes)} (includes piers, marinas)")

    # Mock frame for demo — replace with Ray-Ban stream
    planner = AvoidancePlanner()
    audio = SpatialAudioEngine()

    mock_obstacles = [
        {"label": "trash can blocking path", "distance_m": 2.1, "bearing": 5, "conf": 0.94, "moving": False},
        {"label": "pier edge drop-off", "distance_m": 0.8, "bearing": -40, "conf": 0.99, "moving": False},
        {"label": "person walking", "distance_m": 4.0, "bearing": 20, "conf": 0.88, "moving": True, "vel": 1.2},
    ]

    for m in mock_obstacles:
        obs = Obstacle(
            label=m["label"],
            type=classify_obstacle(type('o', (), {"label": m["label"]})()),
            distance_m=m["distance_m"],
            bearing_deg=m["bearing"],
            confidence=m["conf"],
            is_moving=m["moving"],
            velocity_ms=m.get("vel", 0)
        )
        obs.risk = assess_risk(obs)
        plan = planner.plan(None, obs, None, None)
        print(f"[{obs.risk}] {obs.label} @ {obs.distance_m}m -> {plan['instruction']}")
        audio.guidance(plan, obs)

    print("\nMission: world vision for the impaired — harbor loop ready.")

if __name__ == "__main__":
    main()
