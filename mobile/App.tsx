// SPDX-License-Identifier: MIT
import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { CameraView } from './src/components/CameraView';
import { MapView } from './src/components/MapView';
import { ObstacleHUD } from './src/components/ObstacleHUD';
import { useLocation } from './src/hooks/useLocation';
import { useObstacleDetection } from './src/hooks/useObstacleDetection';
import { MOCK_PROVENANCE, SAFETY_SUFFIX } from './src/safety';

export default function App() {
  const [mode, setMode] = useState<'camera' | 'map' | 'split'>('split');
  const { location } = useLocation();
  const { obstacles, currentGuidance, riskLevel } = useObstacleDetection(location);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.safetyBanner} accessibilityRole="alert">
        <Text style={styles.safetyTitle}>SIMULATED RESEARCH ONLY — NO CAMERA, GPS, MAP, OR MODEL EXECUTES</Text>
        <Text style={styles.safetyText}>{SAFETY_SUFFIX}</Text>
      </View>
      <View style={styles.header}>
        <Text style={styles.title}>eyeWalker 👓 1.1.9 · SIMULATED RESEARCH UI</Text>
        <Text style={styles.subtitle}>
          {location
            ? `Fixed abstract layout · simulated coordinates ${location.coords.latitude.toFixed(4)}, ${location.coords.longitude.toFixed(4)}`
            : 'Loading deterministic mock coordinates…'}
        </Text>
        <Text style={styles.provenance}>{MOCK_PROVENANCE}</Text>
      </View>

      <View style={styles.main}>
        {(mode === 'camera' || mode === 'split') && (
          <View style={mode === 'split' ? styles.half : styles.full}>
            <CameraView obstacles={obstacles} />
          </View>
        )}
        {(mode === 'map' || mode === 'split') && (
          <View style={mode === 'split' ? styles.half : styles.full}>
            <MapView location={location} obstacles={obstacles} />
          </View>
        )}
      </View>

      <ObstacleHUD guidance={currentGuidance} risk={riskLevel} obstacles={obstacles} />

      <View style={styles.controls}>
        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="Show camera mock"
          accessibilityState={{ selected: mode === 'camera' }}
          style={styles.btn}
          onPress={() => setMode('camera')}
        >
          <Text style={styles.btnText}>Camera mock</Text>
        </TouchableOpacity>
        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="Show split camera and map mocks"
          accessibilityState={{ selected: mode === 'split' }}
          style={styles.btn}
          onPress={() => setMode('split')}
        >
          <Text style={styles.btnText}>Split mocks</Text>
        </TouchableOpacity>
        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="Show map mock"
          accessibilityState={{ selected: mode === 'map' }}
          style={styles.btn}
          onPress={() => setMode('map')}
        >
          <Text style={styles.btnText}>Map mock</Text>
        </TouchableOpacity>
        <TouchableOpacity accessibilityRole="button" accessibilityLabel="Log simulated research cue" style={[styles.btn, styles.speakBtn]} onPress={() => {
          // TTS is not wired in this mock. Keep the exact safe cue in the debug log.
          const msg = currentGuidance;
          console.log("SPEAK:", msg);
        }}>
          <Text style={styles.btnText}>🔊 Log mock cue</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>SIMULATED RESEARCH · {MOCK_PROVENANCE} · {SAFETY_SUFFIX}</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0f1a' },
  safetyBanner: { padding: 10, backgroundColor: '#ffcc00', borderBottomWidth: 2, borderBottomColor: '#000' },
  safetyTitle: { color: '#000', fontSize: 11, fontWeight: 'bold', textAlign: 'center' },
  safetyText: { color: '#000', fontSize: 11, fontWeight: 'bold', textAlign: 'center', marginTop: 3 },
  header: { padding: 12, backgroundColor: '#111', borderBottomWidth: 1, borderBottomColor: '#333' },
  title: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  subtitle: { color: '#888', fontSize: 10, marginTop: 2 },
  provenance: { color: '#ffcc00', fontSize: 9, marginTop: 2 },
  main: { flex: 1, flexDirection: 'column' },
  half: { flex: 1, borderWidth: 1, borderColor: '#222' },
  full: { flex: 1 },
  controls: { flexDirection: 'row', padding: 8, gap: 6, backgroundColor: '#111' },
  btn: { flex: 1, minHeight: 48, backgroundColor: '#222', padding: 10, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  speakBtn: { backgroundColor: '#00aa55' },
  btnText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  footer: { padding: 6, backgroundColor: '#000', alignItems: 'center' },
  footerText: { color: '#ffcc00', fontSize: 8, textAlign: 'center' },
});
