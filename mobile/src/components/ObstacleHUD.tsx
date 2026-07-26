// SPDX-License-Identifier: MIT
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import {
  displayMockLabel,
  isExactSimulatedResearchCue,
  MOCK_PROVENANCE,
  simulatedResearchCue,
} from '../safety';

export const ObstacleHUD = ({ guidance, risk, obstacles }: any) => {
  const hasObstacle = obstacles && obstacles.length > 0;
  const active = obstacles?.[0];
  const activeLabel = displayMockLabel(active?.label);
  const activeType = active?.type === 'SYNTHETIC_FIXTURE' ? 'synthetic fixture' : 'unknown';
  const activeRisk = ['LOW', 'MEDIUM', 'HIGH'].includes(risk) ? risk : 'UNKNOWN';
  const confidence = typeof active?.confidence === 'number'
    && Number.isFinite(active.confidence)
    && active.confidence >= 0
    && active.confidence <= 1
    ? active.confidence.toFixed(2)
    : 'not computed';
  const safeGuidance = isExactSimulatedResearchCue(guidance)
    ? guidance
    : simulatedResearchCue('No safe mock guidance available; pause and verify.');

  return (
    <View
      style={[styles.container, hasObstacle ? styles.danger : styles.unknown]}
      accessibilityRole="alert"
      accessibilityLiveRegion="polite"
    >
      <Text style={styles.simulation}>SIMULATED RESEARCH · {MOCK_PROVENANCE}</Text>
      {hasObstacle ? (
        <>
          <Text style={styles.alert}>MOCK LABEL · {activeLabel.toUpperCase()} · {active?.distance_m}m</Text>
          <Text style={styles.type}>Mock type: {activeType} · Mock risk: {activeRisk} · Mock confidence: {confidence}</Text>
        </>
      ) : (
        <Text style={styles.unknownText}>NO MOCK OBSTACLE GENERATED — this is not a free-path claim</Text>
      )}
      <Text style={styles.action}>{safeGuidance}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 14, minHeight: 110 },
  danger: { backgroundColor: '#220000', borderTopWidth: 2, borderTopColor: '#ff4444' },
  unknown: { backgroundColor: '#2b2100', borderTopWidth: 2, borderTopColor: '#ffcc00' },
  simulation: { color: '#ffcc00', fontSize: 10, fontWeight: 'bold' },
  alert: { color: '#fff', fontSize: 14, fontWeight: 'bold', marginTop: 4 },
  type: { color: '#ffaaaa', fontSize: 10, marginTop: 2 },
  action: { color: '#fff', fontSize: 14, fontWeight: 'bold', marginTop: 4 },
  unknownText: { color: '#ffec99', fontSize: 12, fontWeight: 'bold', marginTop: 4 },
});
