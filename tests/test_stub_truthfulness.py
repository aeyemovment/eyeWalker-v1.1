"""Regression tests for public research stubs that must not claim execution."""

from eyewalker.accessibility.audio import SpatialAudioEngine
from eyewalker.cusp.burst import BurstField
from eyewalker.cusp.egi import EGIEngine
from eyewalker.ground_truth.satellite import get_ground_truth_cache
from eyewalker.omniverse.bridge import OmniverseBridge
from eyewalker.perception.pavement import PavementFrame, PavementPerception
from eyewalker.perception.detector import detect_obstacles
from eyewalker.perception.rayban import RayBanCompanion
import sys
from types import SimpleNamespace

import pytest

from eyewalker.ground_truth.osm import get_harbor_graph, get_offstreet_features
from eyewalker.world_model.fusion import fuse_gps_vio_osm
from eyewalker.world_model.spark import EyeWalkerWorldModel


def test_satellite_helper_is_descriptor_only():
    result = get_ground_truth_cache(None, source="esri")

    assert result["status"] == "descriptor_only"
    assert result["network_fetch_implemented"] is False
    assert result["cache_implemented"] is False
    assert result["freshness_checked"] is False
    assert result["ground_truth_validated"] is False


def test_world_model_is_truthful_passthrough_stub():
    records = [{"simulated": True}]
    result = EyeWalkerWorldModel().build_scene(
        rgb=object(),
        depth=None,
        detections=records,
        osm_graph={"mock": True},
        gps={"lat": 1.0},
    )

    assert result["obstacles"] is records
    assert result["scene_graph_built"] is False
    assert result["fusion_applied"] is False
    assert result["models_executed"] == []
    assert result["walkable"]["confidence"] is None
    assert result["walkable"]["segmentation_applied"] is False


def test_egi_equation_does_not_fabricate_confidence():
    result = EGIEngine().predict_efference(None, None)

    assert result["confidence"] is None
    assert result["confidence_status"] == "not_calibrated"


def test_burst_requires_explicit_nonprobabilistic_fixture_score():
    with pytest.raises(ValueError, match="synthetic_visualization_score"):
        BurstField(grid_size=16).compute(
            [{"x": 1, "y": 1, "distance_m": 2.0, "confidence": 0.9}]
        )

    field = BurstField(grid_size=16)
    field.compute(
        [
            {
                "x": 1,
                "y": 1,
                "distance_m": 2.0,
                "synthetic_visualization_score": 0.5,
            }
        ]
    )
    assert field.psi_amplitudes[0]["synthetic_visualization_score"] == 0.5


def test_caller_detector_threshold_is_required_and_validated_before_models():
    class Detector:
        def __init__(self):
            self.threshold = None

        def open_vocab_detect(self, rgb, prompts, conf):
            self.threshold = conf
            return [SimpleNamespace(cx=0, cy=0)]

    model = Detector()
    with pytest.raises(TypeError):
        detect_obstacles(object(), lambda rgb: [[1.0]], model)
    with pytest.raises(ValueError, match="caller_score_threshold"):
        detect_obstacles(
            object(),
            lambda rgb: pytest.fail("invalid threshold reached depth model"),
            model,
            caller_score_threshold=True,
        )

    detection, _ = detect_obstacles(
        object(),
        lambda rgb: __import__("numpy").ones((1, 1)),
        model,
        caller_score_threshold=0.25,
    )
    assert model.threshold == 0.25
    assert detection[0].distance == 1.0


def test_fusion_stub_does_not_claim_snap_or_pier():
    result = fuse_gps_vio_osm(
        {"lat": 39.0, "lon": -76.0},
        vio_pose={"x": 1},
        osm_graph={"pier": True},
    )

    assert result["input_lat"] == 39.0
    assert result["snapped_lat"] is None
    assert result["on_pier"] is None
    assert result["snap_applied"] is False
    assert result["map_validated"] is False


def test_audio_stub_reports_console_text_only(capsys):
    result = SpatialAudioEngine().speak("SIMULATED RESEARCH CUE: test")

    assert result["console_output_applied"] is True
    assert result["tts_applied"] is False
    assert result["binaural_rendering_applied"] is False
    assert result["spatial_audio_applied"] is False
    assert "[SIMULATED TEXT CUE]" in capsys.readouterr().out


def test_nemoclaw_omniverse_pairing_is_explicitly_unimplemented():
    result = OmniverseBridge().connect_nemoclaw()

    assert result["integration_implemented"] is False
    assert result["egress_enforced"] is False
    assert result["policy_loaded"] is False
    assert result["schema_validated"] is False


def test_osm_network_is_off_by_default():
    result = get_harbor_graph()

    assert result["status"] == "network_not_requested"
    assert result["network_access_allowed"] is False
    assert result["network_path_invoked"] is False
    assert result["network_used"] is False
    assert result["freshness_checked"] is False
    assert result["ground_truth_validated"] is False
    assert result["data"] is None


def test_osm_network_opt_in_uses_osmnx_2_bbox_contract(monkeypatch):
    calls = {}

    def graph_from_bbox(bbox, **kwargs):
        calls["graph"] = (bbox, kwargs)
        return {"graph": "unvalidated"}

    def features_from_bbox(bbox, tags):
        calls["features"] = (bbox, tags)
        return {"features": "unvalidated"}

    fake = SimpleNamespace(
        graph=SimpleNamespace(graph_from_bbox=graph_from_bbox),
        features=SimpleNamespace(features_from_bbox=features_from_bbox),
        settings=SimpleNamespace(use_cache=True),
    )
    monkeypatch.setitem(sys.modules, "osmnx", fake)
    bbox = (-76.61, 39.27, -76.56, 39.29)

    graph = get_harbor_graph(bbox, allow_network=True)
    features = get_offstreet_features(bbox, allow_network=True)

    assert calls["graph"][0] == bbox
    assert calls["features"][0] == bbox
    assert graph["network_access_allowed"] is True
    assert graph["network_path_invoked"] is True
    assert graph["network_used"] is None
    assert graph["cache_used"] is None
    assert graph["cache_setting_enabled"] is True
    assert graph["edge_grades_applied"] is False
    assert graph["ground_truth_validated"] is False
    assert features["network_access_allowed"] is True
    assert features["network_path_invoked"] is True
    assert features["network_used"] is None
    assert features["cache_used"] is None
    assert features["ground_truth_validated"] is False


@pytest.mark.parametrize(
    "bbox",
    (
        (39.29, 39.27, -76.56, -76.61),
        (-76.61, 39.27, -76.56, float("inf")),
        (-181, 39.27, -76.56, 39.29),
    ),
)
def test_osm_rejects_invalid_or_legacy_bbox_order(bbox):
    with pytest.raises(ValueError):
        get_harbor_graph(bbox)


def test_pavement_records_are_explicit_fixtures_not_detections():
    result = PavementPerception().ingest(PavementFrame(rgb=object()))

    assert result["input_provenance"] == "caller_supplied_unknown"
    assert result["rgb_analyzed"] is False
    assert result["detection_applied"] is False
    assert result["depth_applied"] is False
    assert result["models_executed"] == []
    assert result["not_for_navigation"] is True
    assert all(record["simulated"] is True for record in result["hazards"])
    assert all(record["model_executed"] is False for record in result["hazards"])
    costmap = PavementPerception().to_costmap(result)
    assert costmap["costmap"] is None
    assert costmap["planner_priority_assigned"] is False


def test_rayban_named_adapter_is_caller_passthrough_only():
    rgb = object()
    gps = {"lat": 1.0}
    result = RayBanCompanion().on_frame(rgb, object(), gps)

    assert result["rgb"] is rgb
    assert result["gps"] is gps
    assert result["device_connection_implemented"] is False
    assert result["rgb_analyzed_by_this_adapter"] is False
    assert result["privacy_processing_applied"] is False
    assert result["synthetic_status"] == "unknown"
