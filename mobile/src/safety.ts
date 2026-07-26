// SPDX-License-Identifier: MIT
export const SIMULATED_RESEARCH_PREFIX = 'SIMULATED RESEARCH CUE:';
export const SAFETY_SUFFIX = 'Keep your cane or guide dog. Not a medical device.';
export const MOCK_PROVENANCE = 'deterministic_mock_no_model_executed';

const SAFE_MOCK_LABELS = new Set([
  'bench',
  'bike',
  'bollard',
  'construction_cone',
  'crack',
  'curb',
  'low_branch',
  'manhole',
  'obstacle',
  'person',
  'pier_edge',
  'puddle',
  'shadow_trap',
  'tactile_paving',
  'trash_bin',
  'uneven_surface',
]);

export const safeMockLabel = (value: unknown) => {
  const normalized = String(value ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
  return SAFE_MOCK_LABELS.has(normalized) ? normalized : 'obstacle';
};

export const displayMockLabel = (value: unknown) => safeMockLabel(value).replace(/_/g, ' ');

export const sanitizeCueDetail = (detail: unknown) => {
  const safe = String(detail ?? '')
    .replace(/[\u0000-\u001f\u007f]/g, ' ')
    .replace(/\s+/g, ' ')
    .replaceAll(SIMULATED_RESEARCH_PREFIX, ' ')
    .replaceAll(SAFETY_SUFFIX, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 240);
  return safe || 'No safe mock detail available; pause and verify.';
};

export const simulatedResearchCue = (detail: unknown) =>
  `${SIMULATED_RESEARCH_PREFIX} ${sanitizeCueDetail(detail)} ${SAFETY_SUFFIX}`;

export const isExactSimulatedResearchCue = (value: unknown) => {
  if (typeof value !== 'string') return false;
  return value.length <= 512
    && !/[\u0000-\u001f\u007f]/.test(value)
    && value.startsWith(`${SIMULATED_RESEARCH_PREFIX} `)
    && value.endsWith(SAFETY_SUFFIX)
    && value.split(SIMULATED_RESEARCH_PREFIX).length === 2
    && value.split(SAFETY_SUFFIX).length === 2;
};
