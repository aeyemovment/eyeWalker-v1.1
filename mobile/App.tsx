
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { CameraView } from './src/components/CameraView';
import { MapView } from './src/components/MapView';
import { ObstacleHUD } from './src/components/ObstacleHUD';
import { useLocation } from './src/hooks/useLocation';
import { useObstacleDetection } from './src/hooks/useObstacleDetection';

export default function App() {
  const [mode, setMode] = useState<'camera' | 'map' | 'split'>('split');
  const { location, heading } = useLocation();
  const { obstacles, currentGuidance, riskLevel } = useObstacleDetection(location);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>eyeWalker 👓 0.1.0</Text>
        <Text style={styles.subtitle}>Baltimore Harbor • {location ? `${location.coords.latitude.toFixed(4)}, ${location.coords.longitude.toFixed(4)}` : 'Acquiring GPS...'}</Text>
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
        <TouchableOpacity style={styles.btn} onPress={() => setMode('camera')}>
          <Text style={styles.btnText}>Camera</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btn} onPress={() => setMode('split')}>
          <Text style={styles.btnText}>Split</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btn} onPress={() => setMode('map')}>
          <Text style={styles.btnText}>Map</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.speakBtn]} onPress={() => {
          // Trigger TTS
          const msg = currentGuidance || "Path clear, pier edge 1.2 meters left, keep right";
          console.log("SPEAK:", msg);
        }}>
          <Text style={styles.btnText}>🔊 Speak</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Mission: world vision for the impaired • Noncommercial • NemoClaw optional (local-first docs only)</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0f1a' },
  header: { padding: 12, backgroundColor: '#111', borderBottomWidth: 1, borderBottomColor: '#333' },
  title: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  subtitle: { color: '#888', fontSize: 10, marginTop: 2 },
  main: { flex: 1, flexDirection: 'column' },
  half: { flex: 1, borderWidth: 1, borderColor: '#222' },
  full: { flex: 1 },
  controls: { flexDirection: 'row', padding: 8, gap: 6, backgroundColor: '#111' },
  btn: { flex: 1, backgroundColor: '#222', padding: 10, borderRadius: 8, alignItems: 'center' },
  speakBtn: { backgroundColor: '#00aa55' },
  btnText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  footer: { padding: 6, backgroundColor: '#000', alignItems: 'center' },
  footerText: { color: '#555', fontSize: 8 },
});
