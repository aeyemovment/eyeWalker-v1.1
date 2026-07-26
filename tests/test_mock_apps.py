"""Truthfulness and determinism checks for both standalone demo copies."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

Image = pytest.importorskip("PIL.Image")


ROOT = Path(__file__).resolve().parents[1]
APP_PATHS = (
    ROOT / "hf-space-final" / "app.py",
    ROOT / "meta_submission" / "app.py",
)


def _load_logic(path: Path) -> dict:
    tree = ast.parse(path.read_text())
    body = []
    for node in tree.body:
        if isinstance(node, ast.With):
            break
        if isinstance(node, ast.Import) and any(
            alias.name == "gradio" for alias in node.names
        ):
            continue
        body.append(node)
    module = ast.Module(body=body, type_ignores=[])
    namespace: dict = {}
    exec(compile(module, str(path), "exec"), namespace)
    return namespace


def test_deployment_copies_are_byte_identical():
    assert APP_PATHS[0].read_bytes() == APP_PATHS[1].read_bytes()
    assert (
        (ROOT / "hf-space-final" / "README.md").read_bytes()
        == (ROOT / "meta_submission" / "README_HF.md").read_bytes()
    )


def test_same_pixels_produce_same_mock_records_and_no_model_provenance():
    logic = _load_logic(APP_PATHS[0])
    image = Image.new("RGB", (640, 480), (20, 40, 60))

    first = logic["generate_mock_records"](image)
    second = logic["generate_mock_records"](image.copy())

    assert first == second
    assert first
    assert all(record["simulated"] is True for record in first)
    assert all(record["source"] == "deterministic_mock" for record in first)
    output = logic["process_image"](image)[1]
    assert output["provenance"]["models_executed"] == []
    assert output["provenance"]["model"] == "deterministic_mock_no_model_executed"
    assert "timestamp" not in output


def test_mock_plan_steps_away_and_keeps_exact_safety_contract():
    logic = _load_logic(APP_PATHS[0])
    prefix = logic["SIMULATION_LABEL"]
    suffix = logic["SAFETY_SUFFIX"]

    left = logic["simulated_plan"](
        [{"class": "curb", "distance_m": 1.0, "bearing_deg": -20, "urgency": "HIGH"}]
    )
    right = logic["simulated_plan"](
        [{"class": "curb", "distance_m": 1.0, "bearing_deg": 20, "urgency": "HIGH"}]
    )

    assert left["action"] == "step_right"
    assert right["action"] == "step_left"
    for plan in (left, right):
        assert plan["instruction"].startswith(prefix)
        assert plan["instruction"].endswith(suffix)
        assert plan["simulated"] is True
        assert plan["guidance_source"] == "local_step_away"


def test_mock_plan_holds_for_empty_or_centered_records():
    logic = _load_logic(APP_PATHS[0])
    empty = logic["simulated_plan"]([])
    centered = logic["simulated_plan"](
        [{"class": "curb", "distance_m": 1.0, "bearing_deg": 0.0, "urgency": "HIGH"}]
    )

    for plan in (empty, centered):
        assert plan["action"] == "hold"
        assert plan["lateral_m"] == 0.0
        assert "stop and verify" in plan["instruction"]
        assert "side-step" not in plan["instruction"]
    assert centered["guidance_source"] == "local_fail_closed_ambiguous_bearing"


def test_hosted_upload_privacy_is_visible_in_app_and_readme():
    app = APP_PATHS[0].read_text()
    readme = (ROOT / "hf-space-final" / "README.md").read_text()

    for text in (app, readme):
        assert "Space host" in text
        assert "sent to the" in text or "transmitted to the" in text
        assert "synthetic" in text
        assert "non-sensitive" in text


def test_low_only_mock_records_report_low_consistently():
    logic = _load_logic(APP_PATHS[0])
    logic["generate_mock_records"] = lambda image: [
        {
            "class": "uneven_surface",
            "distance_m": 2.0,
            "bearing_deg": 0.0,
            "urgency": "LOW",
            "source": "deterministic_mock",
            "simulated": True,
        }
    ]

    output = logic["process_image"](Image.new("RGB", (640, 480)))[1]

    assert output["simulated_risk_level"] == "LOW"


@pytest.mark.parametrize("size", ((4097, 1), (1, 4097)))
def test_hosted_mock_rejects_oversized_dimensions_before_pixel_hash(size):
    logic = _load_logic(APP_PATHS[0])
    image = Image.new("RGB", size)

    with pytest.raises(ValueError, match="reviewed hosted-demo limit"):
        logic["process_image"](image)


def test_hosted_dependencies_and_input_limits_are_exact_and_aligned():
    expected = "gradio==6.20.0\npillow==12.3.0\n"
    assert (ROOT / "hf-space-final" / "requirements.txt").read_text() == expected
    assert (ROOT / "meta_submission" / "requirements.txt").read_text() == expected

    app = APP_PATHS[0].read_text()
    assert "MAX_IMAGE_DIMENSION = 4096" in app
    assert "MAX_IMAGE_PIXELS = 16_000_000" in app
    assert "_validated_image(image).convert(\"RGB\")" in app
