
"""VLM detector using Muse Spark 1.1 (or open fallback Qwen2-VL)"""
OBSTACLE_PROMPTS = [
    "trash can blocking path",
    "bench blocking sidewalk",
    "bollard",
    "construction cone",
    "low branch at head height",
    "curb up",
    "puddle",
    "uneven pavers",
    "person walking",
    "dog",
    "cyclist approaching",
    "pier edge drop-off"
]

def detect_obstacles(rgb, depth_model, vlm_model):
    depth = depth_model(rgb)
    detections = vlm_model.open_vocab_detect(rgb, OBSTACLE_PROMPTS, conf=0.5)
    # Attach distance from depth
    for d in detections:
        d.distance = float(depth[d.cy, d.cx])
    return detections, depth
