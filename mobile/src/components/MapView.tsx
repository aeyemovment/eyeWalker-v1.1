
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const MapView = ({ location, obstacles }: any) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Ground Truth • Esri <3yr + OSM piers</Text>
      <View style={styles.mapMock}>
        {/* Harbor water */}
        <View style={styles.water} />
        {/* Route */}
        <View style={styles.route} />
        <View style={styles.routeDashed} />
        {/* Current pos */}
        <View style={[styles.dot, { left: '50%', top: '50%' }]} />
        {obstacles?.map((ob: any, i: number) => (
          <View key={i} style={[styles.ob, { left: `${30 + i*15}%`, top: `${20 + i*10}%`, backgroundColor: ob.risk === 'HIGH' ? '#ff4444' : '#ffaa00' }]} />
        ))}
      </View>
      <Text style={styles.coords}>{location ? `On pier boardwalk • Edge 0.8m left` : 'Loading...'}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a1931', padding: 8 },
  title: { color: '#fff', fontSize: 10, marginBottom: 6 },
  mapMock: { flex: 1, backgroundColor: '#0a2a5a', borderRadius: 8, overflow: 'hidden' },
  water: { position: 'absolute', bottom: 0, left: 0, right: 0, height: '40%', backgroundColor: '#082040' },
  route: { position: 'absolute', top: '30%', left: '10%', width: '80%', height: 3, backgroundColor: '#FFD400' },
  routeDashed: { position: 'absolute', top: '32%', left: '10%', width: '80%', height: 2, backgroundColor: '#333' },
  dot: { position: 'absolute', width: 14, height: 14, borderRadius: 7, backgroundColor: '#00ff88', borderWidth: 2, borderColor: '#fff' },
  ob: { position: 'absolute', width: 12, height: 12, borderRadius: 2, borderWidth: 1, borderColor: '#fff' },
  coords: { color: '#aaffaa', fontSize: 10, marginTop: 6 },
});
