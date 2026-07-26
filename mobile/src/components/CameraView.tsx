// SPDX-License-Identifier: MIT
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { displayMockLabel, MOCK_PROVENANCE, SAFETY_SUFFIX } from '../safety';

export const CameraView = ({ obstacles }: any) => {
  return (
    <View style={styles.container} accessibilityLabel="Simulated research camera mock">
      <View style={styles.cameraMock}>
        <Text style={styles.mockText}>SIMULATED RESEARCH CAMERA MOCK</Text>
        <Text style={styles.subText}>No camera or perception model executed</Text>
        <Text style={styles.provenance}>{MOCK_PROVENANCE}</Text>
        {obstacles?.slice(0, 2).map((ob: any, i: number) => (
          <View key={i} style={[styles.bbox, { left: `${20 + i * 30}%`, top: `${30 + i * 10}%` }]}>
            <Text style={styles.bboxLabel}>SIM MOCK · {displayMockLabel(ob.label)} · {ob.distance_m}m</Text>
          </View>
        ))}
        <Text style={styles.safety}>{SAFETY_SUFFIX}</Text>
      </View>
      <View style={styles.crosshair} accessibilityElementsHidden>
        <Text style={styles.crosshairText}>+</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  cameraMock: { flex: 1, backgroundColor: '#111', justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: '#ffcc00', borderStyle: 'dashed' },
  mockText: { color: '#ffcc00', fontSize: 14, fontWeight: 'bold' },
  subText: { color: '#f8fafc', fontSize: 11, marginTop: 4 },
  provenance: { color: '#9ca3af', fontSize: 9, marginTop: 3 },
  safety: { color: '#ffcc00', fontSize: 10, fontWeight: 'bold', marginTop: 10, textAlign: 'center', paddingHorizontal: 8 },
  bbox: { position: 'absolute', borderWidth: 2, borderColor: '#ff4444', padding: 4, backgroundColor: 'rgba(255,0,0,0.2)' },
  bboxLabel: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  crosshair: { position: 'absolute', top: '50%', left: '50%', marginLeft: -10, marginTop: -10 },
  crosshairText: { color: '#ffcc00', fontSize: 20 },
});
