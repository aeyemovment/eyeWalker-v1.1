// SPDX-License-Identifier: MIT
import { MOCK_PROVENANCE, SAFETY_SUFFIX, simulatedResearchCue } from '../safety';
import { calculateAvoidance } from '../utils/avoidance';

const MOCK_OBSTACLES = [
  { label: 'trash bin', distance_m: 2.1, bearing: -18, type: 'SYNTHETIC_FIXTURE', confidence: null, risk: 'HIGH' },
].map((obstacle) => ({
  ...obstacle,
  simulated: true,
  source: MOCK_PROVENANCE,
  safety: SAFETY_SUFFIX,
}));

export const useObstacleDetection = (_location: any) => {
  // One fixed record avoids auto-updating an assistive live region. No camera,
  // sensor, timer, or model is executed.
  const obstacles = [MOCK_OBSTACLES[0]];
  const current = obstacles[0];
  return {
    obstacles,
    currentGuidance: current
      ? calculateAvoidance(current, 0, 0).instruction
      : simulatedResearchCue('No mock obstacle generated; pause and verify.'),
    riskLevel: current?.risk || 'UNKNOWN',
    provenance: MOCK_PROVENANCE,
    simulated: true,
    safety: SAFETY_SUFFIX,
  };
};
