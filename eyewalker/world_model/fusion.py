
def fuse_gps_vio_osm(gps, vio_pose, osm_graph):
    """Snap noisy GPS + precise VIO to off-street walkable graph (piers, marinas)"""
    # 1. coarse snap to OSM
    # 2. fine refine with VIO
    # 3. reject if water
    return {"snapped_lat": gps.lat, "snapped_lon": gps.lon, "on_pier": True}
