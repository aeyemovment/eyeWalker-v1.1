
"""Meta Ray-Ban ingestion — 6DoF via VIO"""
class RayBanCompanion:
    def __init__(self):
        self.vio = None  # Visual-Inertial Odometry

    def on_frame(self, rgb, imu, gps):
        """Called at ~0.66Hz from glasses (photo every 1.5s)"""
        pose = self.vio.update(rgb, imu) if self.vio else None
        return {
            "rgb": rgb,
            "imu": imu,
            "gps": gps,
            "pose": pose,  # 6DoF: x,y,z + pitch,yaw,roll
            "timestamp": imu.timestamp if hasattr(imu, 'timestamp') else 0
        }
