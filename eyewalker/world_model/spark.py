"""World-model interface stub; no Muse model or segmentation executes here."""


class EyeWalkerWorldModel:
    def __init__(self, model_name="muse-spark-1.1"):
        self.model_name = model_name

    def build_scene(self, rgb, depth, detections, osm_graph, gps):
        """Package caller-supplied values without claiming model fusion."""
        return {
            "walkable": self.segment_walkable(rgb, osm_graph),
            "obstacles": detections,
            "depth": depth,
            "gps": gps,
            "map_context": osm_graph,
            "scene_graph_built": False,
            "fusion_applied": False,
            "models_executed": [],
            "inputs_passthrough": True,
            "research_prototype": True,
        }

    def segment_walkable(self, rgb, osm_graph):
        """Report the unimplemented segmentation path truthfully."""
        return {
            "mask": None,
            "confidence": None,
            "segmentation_applied": False,
            "model_executed": False,
            "status": "not_implemented",
        }
