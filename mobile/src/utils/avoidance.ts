
export const calculateAvoidance = (obstacle: any, freeLeft: number, freeRight: number) => {
  if (obstacle.label.includes('pier edge')) {
    return { direction: 'right', lateral: 0.5, instruction: 'Pier edge 0.8m left, keep right' };
  }
  return freeLeft > freeRight
    ? { direction: 'left', lateral: 0.5, instruction: `Obstacle: ${obstacle.label} ${obstacle.distance_m}m ahead, step left 0.5m` }
    : { direction: 'right', lateral: 0.5, instruction: `Obstacle: ${obstacle.label} ${obstacle.distance_m}m ahead, step right 0.5m` };
};
