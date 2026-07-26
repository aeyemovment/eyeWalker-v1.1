
from dataclasses import dataclass
from enum import Enum

class ObstacleType(Enum):
    STATIC = "static"  # bench, trash can, bollard, cone
    DYNAMIC = "dynamic"  # person, dog, cyclist
    GROUND = "ground-level"  # puddle, uneven, curb
    OVERHEAD = "overhead"  # low branch, sign

@dataclass
class Obstacle:
    label: str
    type: ObstacleType
    distance_m: float
    bearing_deg: float  # 0=center, negative=left
    confidence: float
    is_moving: bool = False
    velocity_ms: float = 0.0
    risk: str = "LOW"

def classify_obstacle(det):
    if det.label in ["person walking", "dog", "cyclist approaching"]:
        return ObstacleType.DYNAMIC
    if det.label in ["low branch at head height"]:
        return ObstacleType.OVERHEAD
    if det.label in ["puddle", "uneven pavers", "curb up"]:
        return ObstacleType.GROUND
    return ObstacleType.STATIC
