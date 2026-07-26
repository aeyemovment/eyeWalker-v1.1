// SPDX-License-Identifier: MIT
import { MOCK_PROVENANCE, SAFETY_SUFFIX } from '../safety';

const MOCK_LOCATION = Object.freeze({
  coords: Object.freeze({ latitude: 0, longitude: 0, accuracy: null }),
  timestamp: 0,
  simulated: true,
  source: MOCK_PROVENANCE,
  safety: SAFETY_SUFFIX,
});

export const useLocation = () => {
  // Fixed synthetic coordinates for UI layout only. No location sensor executes.
  return {
    location: MOCK_LOCATION,
    heading: 0,
    provenance: MOCK_PROVENANCE,
    simulated: true,
    safety: SAFETY_SUFFIX,
  };
};
