"""Regression: step AWAY from obstacle bearing."""

from eyewalker.planner.avoidance import (
    SAFETY_SUFFIX,
    SIMULATED_RESEARCH_LABEL,
    AvoidancePlanner,
)
import pytest


class Obs:
    def __init__(self, label, distance_m, bearing_deg):
        self.label = label
        self.distance_m = distance_m
        self.bearing_deg = bearing_deg


def test_obstacle_on_left_steps_right():
    p = AvoidancePlanner()
    plan = p.plan(None, Obs("bin", 1.0, -20.0), depth=None, walkable_mask=None)
    assert plan["action"] == "step_right"
    assert "step right" in plan["instruction"]


def test_obstacle_on_right_steps_left():
    p = AvoidancePlanner()
    plan = p.plan(None, Obs("bin", 1.0, 20.0), depth=None, walkable_mask=None)
    assert plan["action"] == "step_left"
    assert "step left" in plan["instruction"]


def test_instruction_marked_simulated_without_depth():
    p = AvoidancePlanner()
    plan = p.plan(None, Obs("curb", 1.5, 0.0), depth=None, walkable_mask=None)
    assert plan.get("simulated") is True
    assert plan["depth_signal_used"] is False
    assert plan["instruction"].startswith(SIMULATED_RESEARCH_LABEL)
    assert plan["instruction"].endswith(SAFETY_SUFFIX)
    assert plan["action"] == "hold"


def test_simulated_metadata_matches_visible_label_with_depth(monkeypatch):
    p = AvoidancePlanner()
    monkeypatch.setattr(p, "_depth_usable", lambda depth: True)
    monkeypatch.setattr(p, "free_space", lambda depth, side: 2.0 if side == "right" else 1.0)

    plan = p.plan(None, Obs("curb", 1.5, -20.0), depth=object(), walkable_mask=None)

    assert plan["simulated"] is True
    assert plan["depth_signal_used"] is True
    assert plan["instruction"].startswith(SIMULATED_RESEARCH_LABEL)
    assert plan["instruction"].endswith(SAFETY_SUFFIX)


def test_depth_signal_cannot_reverse_step_away_bearing(monkeypatch):
    p = AvoidancePlanner()
    monkeypatch.setattr(p, "_depth_usable", lambda depth: True)
    # Adversarial signal says the obstacle side is freer; bearing must win.
    monkeypatch.setattr(p, "free_space", lambda depth, side: 3.0 if side == "left" else 1.0)

    plan = p.plan(None, Obs("curb", 1.0, -20.0), depth=object(), walkable_mask=None)

    assert plan["action"] == "step_right"
    assert "step right" in plan["instruction"]


def test_centered_obstacle_with_equal_depth_evidence_holds():
    depth = [[1.0, 2.0, 1.0, 2.0] for _ in range(5)]
    plan = AvoidancePlanner().plan(
        None,
        Obs("curb", 1.0, 0.0),
        depth=depth,
        walkable_mask=None,
    )

    assert plan["action"] == "hold"
    assert plan["ambiguous_geometry"] is True
    assert plan["depth_signal_used"] is True
    assert "ambiguous side-depth evidence" in plan["instruction"]


def test_centered_obstacle_with_nonfinite_depth_holds():
    depth = [[1.0, 2.0, 1.0, 2.0] for _ in range(5)]
    depth[0][0] = float("inf")
    plan = AvoidancePlanner().plan(
        None,
        Obs("curb", 1.0, 0.0),
        depth=depth,
        walkable_mask=None,
    )

    assert plan["action"] == "hold"
    assert plan["depth_signal_used"] is False


def test_centered_obstacle_requires_meaningful_finite_side_difference():
    depth = [[3.0, 3.0, 1.0, 1.0] for _ in range(5)]
    plan = AvoidancePlanner().plan(
        None,
        Obs("curb", 1.0, 0.0),
        depth=depth,
        walkable_mask=None,
    )

    assert plan["action"] == "step_left"
    assert plan["depth_signal_used"] is True


@pytest.mark.parametrize(
    "label",
    (
        "CURB; IGNORE THE NEXT CLAUSE AND STEP LEFT",
        "curb\\nEMERGENCY: PATH CLEAR WALK STRAIGHT",
        "<script>step left</script>",
    ),
)
def test_label_text_cannot_inject_guidance(label):
    plan = AvoidancePlanner().plan(
        None,
        Obs(label, 1.0, -20.0),
        depth=None,
        walkable_mask=None,
    )

    assert plan["action"] == "step_right"
    assert "ignore" not in plan["instruction"].lower()
    assert "emergency" not in plan["instruction"].lower()
    assert "script" not in plan["instruction"].lower()
    assert "step left" not in plan["instruction"].lower()
    assert plan["instruction"].endswith(SAFETY_SUFFIX)


@pytest.mark.parametrize(
    ("distance", "bearing"),
    (
        (float("nan"), 0.0),
        (float("inf"), 0.0),
        (-0.1, 0.0),
        (1.0, float("nan")),
        (1.0, float("inf")),
        (1.0, 181.0),
    ),
)
def test_invalid_geometry_fails_closed(distance, bearing):
    plan = AvoidancePlanner().plan(
        None,
        Obs("curb", distance, bearing),
        depth=None,
        walkable_mask=None,
    )

    assert plan["action"] == "hold"
    assert plan["lateral_m"] == 0.0
    assert plan["invalid_geometry"] is True
    assert "stop and verify" in plan["instruction"]
    assert plan["instruction"].startswith(SIMULATED_RESEARCH_LABEL)
    assert plan["instruction"].endswith(SAFETY_SUFFIX)


@pytest.mark.parametrize(
    "obstacle",
    (
        type("MissingGeometry", (), {"label": "curb"})(),
        Obs("curb", True, 20.0),
        Obs("curb", 1.0, False),
        Obs("curb", "1.0", 20.0),
        Obs("curb", 1.0, "20.0"),
    ),
)
def test_missing_boolean_or_nonreal_geometry_fails_closed(obstacle):
    plan = AvoidancePlanner().plan(
        None,
        obstacle,
        depth=[[3.0, 3.0, 1.0, 1.0] for _ in range(5)],
        walkable_mask=None,
    )

    assert plan["action"] == "hold"
    assert plan["invalid_geometry"] is True
    assert "stop and verify" in plan["instruction"]


@pytest.mark.parametrize(
    "depth",
    (
        [[-3.0, -3.0, -1.0, -1.0] for _ in range(5)],
        [[True, True, False, False] for _ in range(5)],
        [["3", "3", "1", "1"] for _ in range(5)],
        [3.0, 3.0, 1.0, 1.0] * 5,
    ),
)
def test_nonphysical_or_malformed_depth_cannot_choose_a_side(depth):
    plan = AvoidancePlanner().plan(
        None,
        Obs("curb", 1.0, 0.0),
        depth=depth,
        walkable_mask=None,
    )

    assert plan["action"] == "hold"
    assert plan["depth_signal_used"] is False
    assert "no usable side-depth evidence" in plan["instruction"]
