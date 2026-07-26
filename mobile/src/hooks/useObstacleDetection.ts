
import { useState, useEffect } from 'react';

const MOCK_OBSTACLES = [
  { label: 'trash bin', distance_m: 2.1, bearing: 5, type: 'STATIC', confidence: 0.94, risk: 'HIGH', action: 'step LEFT 0.5m' },
  { label: 'pier edge', distance_m: 0.8, bearing: -40, type: 'GROUND', confidence: 0.99, risk: 'HIGH', action: 'keep RIGHT' },
  { label: 'person + dog', distance_m: 4.0, bearing: 20, type: 'DYNAMIC 1.2m/s', confidence: 0.88, risk: 'MED', action: 'hold LEFT' },
  { label: 'bench blocking', distance_m: 3.0, bearing: 0, type: 'STATIC', confidence: 0.92, risk: 'HIGH', action: 'go RIGHT 1m' },
];

export const useObstacleDetection = (location: any) => {
  const [idx, setIdx] = useState(0);
  const [obstacles, setObstacles] = useState<any[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const next = (idx + 1) % MOCK_OBSTACLES.length;
      setIdx(next);
      // Simulate VLM detection cycle 0.66Hz
      setObstacles([MOCK_OBSTACLES[next]]);
    }, 2500);
    return () => clearInterval(interval);
  }, [idx]);

  const current = obstacles[0];
  return {
    obstacles,
    currentGuidance: current ? `Obstacle: ${current.label} ${current.distance_m}m ahead, ${current.action}` : 'Path clear, pier edge 1.2m left, keep right',
    riskLevel: current?.risk || 'LOW'
  };
};
