
def assess_risk(obstacle, user_speed_ms=1.3):
    """Assign a deterministic fixture-risk label from mock geometry."""
    ttc = obstacle.distance_m / max(user_speed_ms, 0.1)
    if obstacle.is_moving:
        ttc = obstacle.distance_m / max(user_speed_ms + obstacle.velocity_ms, 0.1)

    if obstacle.distance_m < 1.0 and obstacle.type.value != "overhead":
        return "HIGH"
    if obstacle.type.value == "overhead" and obstacle.distance_m < 1.5:
        return "HIGH"
    if ttc < 2.0:
        return "HIGH"
    if ttc < 4.0:
        return "MEDIUM"
    return "LOW"
