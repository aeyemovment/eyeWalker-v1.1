"""GPS/VIO/map-fusion interface stub; no snapping or validation is performed."""


def _coordinate(gps, name):
    if isinstance(gps, dict):
        return gps.get(name)
    return getattr(gps, name, None)


def fuse_gps_vio_osm(gps, vio_pose, osm_graph):
    """Return caller GPS as unmodified input with explicit no-op provenance."""
    return {
        "input_lat": _coordinate(gps, "lat"),
        "input_lon": _coordinate(gps, "lon"),
        "snapped_lat": None,
        "snapped_lon": None,
        "on_pier": None,
        "snap_applied": False,
        "vio_fusion_applied": False,
        "water_rejection_applied": False,
        "map_validated": False,
        "status": "not_implemented",
    }
