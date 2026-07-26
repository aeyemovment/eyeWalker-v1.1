
import osmnx as ox

def get_harbor_graph(bbox=(39.29, 39.27, -76.56, -76.61)):
    """Get walkable graph including piers, marinas, footways — fixes harbor off-street issue"""
    north, south, east, west = bbox
    # Custom filter includes piers and footways that car maps ignore
    cf = '["foot"!~"no"]["access"!~"no"]["man_made"!~"no"]'
    G = ox.graph_from_bbox(north, south, east, west, custom_filter=cf, retain_all=True)
    G = ox.add_edge_grades(G)
    return G

def get_offstreet_features(bbox):
    tags = {
        "man_made": ["pier"],
        "leisure": ["marina"],
        "footway": ["boardwalk", "sidewalk", "crossing"],
        "amenity": ["bench"]
    }
    return ox.features_from_bbox(*bbox, tags=tags)
