"""Caller-buffer companion adapter; no Meta/Ray-Ban connection is implemented."""


class RayBanCompanion:
    """Preserve a legacy interface while reporting passthrough provenance."""

    def __init__(self, vio_backend=None):
        self.vio = vio_backend

    def on_frame(self, rgb, imu, gps):
        """Pass caller buffers through; optionally execute a caller VIO backend."""
        pose = self.vio.update(rgb, imu) if self.vio else None
        return {
            "rgb": rgb,
            "imu": imu,
            "gps": gps,
            "pose": pose,
            "timestamp": getattr(imu, "timestamp", 0),
            "input_provenance": "caller_supplied_unknown",
            "device_connection_implemented": False,
            "capture_rate_measured": False,
            "rgb_analyzed_by_this_adapter": False,
            "vio_backend_supplied": self.vio is not None,
            "vio_backend_executed": self.vio is not None,
            "raw_rgb_returned_to_caller": True,
            "raw_gps_returned_to_caller": gps is not None,
            "privacy_processing_applied": False,
            "synthetic_status": "unknown",
            "not_for_navigation": True,
        }
