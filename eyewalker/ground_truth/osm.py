"""Optional OSM network adapters with explicit network consent and provenance."""

from __future__ import annotations

import math

# OSMnx 2.x order: (left, bottom, right, top) in unprojected lon/lat degrees.
DEFAULT_BBOX = (-76.61, 39.27, -76.56, 39.29)
WALK_FILTER = '["foot"!~"no"]["access"!~"no"]["man_made"!~"no"]'


def _validated_bbox(bbox):
    try:
        left, bottom, right, top = (float(value) for value in bbox)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "bbox must be four finite values in (left, bottom, right, top) order"
        ) from exc
    if not all(math.isfinite(value) for value in (left, bottom, right, top)):
        raise ValueError("bbox values must be finite")
    if not (-180 <= left < right <= 180 and -90 <= bottom < top <= 90):
        raise ValueError(
            "bbox must satisfy -180 <= left < right <= 180 and "
            "-90 <= bottom < top <= 90"
        )
    return (left, bottom, right, top)


def _offline_descriptor(operation, bbox):
    bbox = _validated_bbox(bbox)
    return {
        "operation": operation,
        "bbox": list(bbox),
        "status": "network_not_requested",
        "network_access_allowed": False,
        "network_path_invoked": False,
        "network_used": False,
        "cache_used": False,
        "freshness_checked": False,
        "ground_truth_validated": False,
        "data": None,
    }


def get_harbor_graph(bbox=DEFAULT_BBOX, *, allow_network=False):
    """Return an offline descriptor unless network access is explicitly allowed."""
    bbox = _validated_bbox(bbox)
    if not allow_network:
        return _offline_descriptor("graph_from_bbox", bbox)

    import osmnx as ox

    graph = ox.graph.graph_from_bbox(
        bbox,
        custom_filter=WALK_FILTER,
        retain_all=True,
    )
    return {
        "operation": "graph_from_bbox",
        "bbox": list(bbox),
        "status": "osmnx_request_path_returned_unvalidated_data",
        "network_access_allowed": True,
        "network_path_invoked": True,
        # OSMnx may return cached data without making a network request. This
        # adapter cannot distinguish those cases from the returned graph.
        "network_used": None,
        # OSMnx may satisfy an Overpass request from its cache. The returned
        # graph does not expose which route was used, so do not guess.
        "cache_used": None,
        "cache_setting_enabled": bool(getattr(ox.settings, "use_cache", False)),
        "freshness_checked": False,
        "ground_truth_validated": False,
        "elevation_applied": False,
        "edge_grades_applied": False,
        "data": graph,
    }


def get_offstreet_features(bbox, *, allow_network=False):
    """Return an offline descriptor or explicitly request OSM features."""
    bbox = _validated_bbox(bbox)
    if not allow_network:
        return _offline_descriptor("features_from_bbox", bbox)

    import osmnx as ox

    tags = {
        "man_made": ["pier"],
        "leisure": ["marina"],
        "footway": ["boardwalk", "sidewalk", "crossing"],
        "amenity": ["bench"],
    }
    data = ox.features.features_from_bbox(bbox, tags)
    return {
        "operation": "features_from_bbox",
        "bbox": list(bbox),
        "status": "osmnx_request_path_returned_unvalidated_data",
        "network_access_allowed": True,
        "network_path_invoked": True,
        "network_used": None,
        "cache_used": None,
        "cache_setting_enabled": bool(getattr(ox.settings, "use_cache", False)),
        "freshness_checked": False,
        "ground_truth_validated": False,
        "data": data,
    }
