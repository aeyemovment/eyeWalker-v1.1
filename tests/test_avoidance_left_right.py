"""Regression: step AWAY from obstacle bearing."""

from eyewalker.planner.avoidance import AvoidancePlanner


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
    assert "SIMULATED" in plan["instruction"] or "research" in plan["instruction"].lower()
