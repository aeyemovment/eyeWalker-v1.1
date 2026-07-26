"""Satellite tile-source descriptors; no download, cache, or freshness check."""

TILE_URL_TEMPLATES = {
    "esri": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "maptiler": "https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key={key}",
    "osm": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
}


def get_ground_truth_cache(bbox, source="esri", max_age_years=3):
    """Return an unvalidated source descriptor for backwards compatibility.

    The function name is historical. It does not access the network, download
    tiles, create a cache, inspect metadata, or establish ground truth.
    """
    if source not in TILE_URL_TEMPLATES:
        raise ValueError(f"unknown tile source: {source}")
    return {
        "source": source,
        "url_template": TILE_URL_TEMPLATES[source],
        "bbox_requested": bbox,
        "requested_max_age_years": max_age_years,
        "network_fetch_implemented": False,
        "cache_implemented": False,
        "freshness_checked": False,
        "ground_truth_validated": False,
        "status": "descriptor_only",
    }
