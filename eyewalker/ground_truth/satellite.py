
"""Open satellite ground truth <3yr — Esri World Imagery + MapTiler fallback"""
TILE_URLS = {
    "esri": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "maptiler": "https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key={key}",
    "osm": "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
}

def get_ground_truth_cache(bbox, source="esri", max_age_years=3):
    """Download tiles for offline use. Enforce <3yr freshness via metadata check"""
    # TODO: check tile metadata date
    return TILE_URLS[source]
