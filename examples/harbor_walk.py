
"""Deterministic synthetic Baltimore Harbor fixture; not for navigation."""
import argparse
from eyewalker.ground_truth.osm import get_harbor_graph
from eyewalker.ground_truth.satellite import get_ground_truth_cache
from eyewalker.obstacle.identifier import classify_obstacle, Obstacle, ObstacleType
from eyewalker.obstacle.risk import assess_risk
from eyewalker.planner.avoidance import AvoidancePlanner
from eyewalker.accessibility.audio import SpatialAudioEngine

def main():
    parser = argparse.ArgumentParser(
        description="eyeWalker deterministic synthetic Harbor fixture"
    )
    parser.add_argument("--satellite", default="esri", choices=["esri", "maptiler", "osm"])
    parser.add_argument(
        "--allow-osm-network",
        action="store_true",
        help="Explicitly allow an unvalidated OSMnx/Overpass request",
    )
    args = parser.parse_args()

    print(f"eyeWalker mock — preparing an unvalidated tile-source descriptor for {args.satellite}")
    graph_result = get_harbor_graph(allow_network=args.allow_osm_network)
    tiles = get_ground_truth_cache(None, source=args.satellite)
    graph = graph_result["data"]
    graph_nodes = len(graph.nodes) if graph is not None else 0
    print(
        f"OSM status: {graph_result['status']}; "
        f"network_access_allowed={graph_result['network_access_allowed']}; "
        f"network_path_invoked={graph_result['network_path_invoked']}; "
        f"network_used_observed={graph_result['network_used']}; nodes={graph_nodes}; "
        f"ground_truth_validated={graph_result['ground_truth_validated']}"
    )
    print(
        "Tile status: "
        f"{tiles['status']}; fetch={tiles['network_fetch_implemented']}; "
        f"cache={tiles['cache_implemented']}; freshness_checked={tiles['freshness_checked']}"
    )

    # Fixed in-code mock records only; no camera, wearable, or location stream.
    planner = AvoidancePlanner()
    audio = SpatialAudioEngine()

    synthetic_fixture_obstacles = [
        {"label": "trash can blocking path", "distance_m": 2.1, "bearing": 5, "moving": False},
        {"label": "pier edge drop-off", "distance_m": 0.8, "bearing": -40, "moving": False},
        {"label": "person walking", "distance_m": 4.0, "bearing": 20, "moving": True, "vel": 1.2},
    ]

    for m in synthetic_fixture_obstacles:
        obs = Obstacle(
            label=m["label"],
            type=classify_obstacle(type('o', (), {"label": m["label"]})()),
            distance_m=m["distance_m"],
            bearing_deg=m["bearing"],
            confidence=None,
            is_moving=m["moving"],
            velocity_ms=m.get("vel", 0)
        )
        obs.risk = assess_risk(obs)
        plan = planner.plan(None, obs, None, None)
        print(f"[{obs.risk}] {obs.label} @ {obs.distance_m}m -> {plan['instruction']}")
        audio.guidance(plan, obs)

    print(
        "\nSIMULATED RESEARCH DEMO complete — no live detector, ground-truth "
        "validation, navigation system, or spatial-audio renderer executed."
    )

if __name__ == "__main__":
    main()
