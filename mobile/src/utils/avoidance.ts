// SPDX-License-Identifier: MIT
import {
  displayMockLabel,
  MOCK_PROVENANCE,
  SAFETY_SUFFIX,
  simulatedResearchCue,
} from '../safety';

export const calculateAvoidance = (obstacle: any, freeLeft: number, freeRight: number) => {
  const rawBearing = obstacle?.bearing_deg ?? obstacle?.bearing;
  const rawDistance = obstacle?.distance_m;
  const geometryValid = typeof rawBearing === 'number'
    && Number.isFinite(rawBearing)
    && Math.abs(rawBearing) <= 180
    && typeof rawDistance === 'number'
    && Number.isFinite(rawDistance)
    && rawDistance >= 0
    && rawDistance <= 1000;
  const bearing = geometryValid ? rawBearing : 0;
  const distance = geometryValid ? rawDistance : 0;
  let direction: 'left' | 'right' | 'hold' = 'hold';

  // A lateral mock bearing is the invariant: always cue away from it. Mock
  // free-space scores choose a side only when the mock obstacle is centered.
  if (geometryValid && bearing < -8) direction = 'right';
  else if (geometryValid && bearing > 8) direction = 'left';
  else if (
    geometryValid
    && Number.isFinite(freeLeft)
    && Number.isFinite(freeRight)
    && freeLeft >= 0
    && freeRight >= 0
    && Math.abs(freeLeft - freeRight) >= 0.1
  ) {
    if (freeLeft > freeRight) direction = 'left';
    else if (freeRight > freeLeft) direction = 'right';
  }

  const label = displayMockLabel(obstacle?.label);
  const movementDetail = direction === 'hold'
    ? `${label} mock geometry is missing or ambiguous; hold position and verify.`
    : `${label} mock ${distance.toFixed(1)}m away at bearing ${bearing >= 0 ? '+' : ''}${bearing.toFixed(0)} degrees; step ${direction} 0.5m.`;
  return {
    direction,
    lateral: direction === 'hold' ? 0 : 0.5,
    instruction: simulatedResearchCue(movementDetail),
    source: MOCK_PROVENANCE,
    simulated: true,
    geometry_valid: geometryValid,
    safety: SAFETY_SUFFIX,
  };
};
