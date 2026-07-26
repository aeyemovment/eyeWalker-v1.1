"""Privacy and AgentAPI honesty regressions."""

import unittest

from eyewalker.cusp.agentapi_bridge import CUSPAgentAPIBridge
from eyewalker.cusp.security_adapter import PrivacyAdapter
from eyewalker.perception.bodycam import BodycamFrame, BodycamPerception
from eyewalker.perception.multicam import MultiCamFrameBundle, MultiCamFusion


class PrivacyAdapterTests(unittest.TestCase):
    def test_precise_gps_and_rgb_are_blocked_without_consent(self):
        result = PrivacyAdapter().check_egress(
            {"rgb": b"frame", "gps": {"lat": 39.0, "lon": -76.0}}
        )
        self.assertFalse(result["allowed"])

    def test_top_level_coordinates_are_also_treated_as_precise(self):
        result = PrivacyAdapter().check_egress(
            {"frame": b"frame", "lat": 39.0, "lon": -76.0}
        )
        self.assertFalse(result["allowed"])

    def test_caller_coarse_flag_cannot_downgrade_explicit_coordinates(self):
        result = PrivacyAdapter().check_egress(
            {
                "rgb": b"frame",
                "gps": {"coarse": True, "lat": 39.0, "lon": -76.0},
            }
        )
        self.assertFalse(result["allowed"])

    def test_coarse_only_descriptor_without_coordinates_is_allowed(self):
        result = PrivacyAdapter().check_egress(
            {"rgb": b"frame", "gps": {"coarse": True, "region": "test-cell"}}
        )
        self.assertTrue(result["allowed"])

    def test_redaction_metadata_never_claims_applied_processing(self):
        result = PrivacyAdapter().redact_metadata()
        self.assertTrue(result["face_blur_requested"])
        self.assertFalse(result["face_blur_applied"])
        self.assertTrue(result["aggregate_only_requested"])
        self.assertFalse(result["aggregate_only_applied"])
        self.assertNotIn("aggregate_only", result)

    def test_bodycam_returns_raw_data_with_not_applied_status(self):
        raw = object()
        result = BodycamPerception().ingest(BodycamFrame(rgb=raw))
        self.assertIs(result["rgb"], raw)
        self.assertEqual(result["rgb_redaction_status"], "not_applied")
        self.assertFalse(result["privacy"]["face_blur_applied"])
        self.assertTrue(result["privacy"]["raw_frame_returned_to_caller"])
        self.assertFalse(result["stabilization_applied"])

    def test_bodycam_privacy_disabled_does_not_request_blur(self):
        result = BodycamPerception(privacy_mode=False).ingest(BodycamFrame(rgb=object()))
        self.assertFalse(result["privacy"]["face_blur_requested"])
        self.assertFalse(result["privacy"]["plate_blur_requested"])

    def test_multicam_labels_policy_requests_without_enforcement_claim(self):
        result = MultiCamFusion().fuse(MultiCamFrameBundle())
        self.assertNotIn("privacy_enforced", result)
        self.assertIn("privacy_requests", result)
        self.assertFalse(result["privacy_requests"]["face_blur_applied"])
        self.assertFalse(result["validated_sensor_fusion"])
        self.assertEqual(result["synthetic_status"], "unknown")
        self.assertEqual(result["models_executed"], [])


class AgentAPIBridgeTests(unittest.TestCase):
    def test_health_is_an_explicit_no_network_stub(self):
        result = CUSPAgentAPIBridge().health()
        self.assertEqual(result["status"], "transport_not_implemented")
        self.assertFalse(result["network_used"])

    def test_external_host_is_rejected(self):
        with self.assertRaises(ValueError):
            CUSPAgentAPIBridge("https://example.com:8780")

    def test_nonstandard_port_is_rejected(self):
        with self.assertRaises(ValueError):
            CUSPAgentAPIBridge("http://127.0.0.1:8080")

    def test_hostname_is_rejected_in_favor_of_numeric_loopback(self):
        with self.assertRaises(ValueError):
            CUSPAgentAPIBridge("http://localhost:8780")

    def test_sensitive_payload_is_blocked_before_mock_transport(self):
        result = CUSPAgentAPIBridge().try_post(
            {"rgb": b"frame", "gps": {"lat": 39.0, "lon": -76.0}}
        )
        self.assertEqual(result["status"], "blocked_by_privacy_policy")
        self.assertFalse(result["network_used"])

    def test_consented_payload_uses_explicit_no_network_fallback(self):
        result = CUSPAgentAPIBridge().try_post(
            {"rgb": b"frame", "gps": {"lat": 39.0, "lon": -76.0}},
            consent_cloud=True,
        )
        self.assertEqual(result["transport"], "not_implemented")
        self.assertFalse(result["network_used"])
        self.assertTrue(result["privacy_policy"]["allowed"])

    def test_local_fallback_does_not_convert_confidence_into_severity(self):
        result = CUSPAgentAPIBridge().try_get_cusp_context(
            efference={"confidence": 0.99}
        )

        self.assertEqual(result["severity_mod"], 1.0)
        self.assertEqual(
            result["severity_mod_source"],
            "neutral_unvalidated_fixture_value",
        )


if __name__ == "__main__":
    unittest.main()
