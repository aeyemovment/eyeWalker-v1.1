
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const CameraView = ({ obstacles }: any) => {
  return (
    <View style={styles.container}>
      <View style={styles.cameraMock}>
        <Text style={styles.mockText}>[Live Camera Feed]</Text>
        <Text style={styles.subText}>Muse Spark 1.1 • Depth ✓ Detect ✓</Text>
        {obstacles?.slice(0,2).map((ob: any, i: number) => (
          <View key={i} style={[styles.bbox, { left: `${20 + i*30}%`, top: `${30 + i*10}%` }]}>
            <Text style={styles.bboxLabel}>{ob.label} {ob.distance_m}m</Text>
          </View>
        ))}
      </View>
      <View style={styles.crosshair}>
        <Text style={styles.crosshairText}>+</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  cameraMock: { flex: 1, backgroundColor: '#111', justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: '#00ff88', borderStyle: 'dashed' },
  mockText: { color: '#666', fontSize: 14 },
  subText: { color: '#00ff88', fontSize: 10, marginTop: 4 },
  bbox: { position: 'absolute', borderWidth: 2, borderColor: '#ff4444', padding: 4, backgroundColor: 'rgba(255,0,0,0.2)' },
  bboxLabel: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  crosshair: { position: 'absolute', top: '50%', left: '50%', marginLeft: -10, marginTop: -10 },
  crosshairText: { color: '#00ff88', fontSize: 20 },
});
