
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const ObstacleHUD = ({ guidance, risk, obstacles }: any) => {
  const hasObstacle = obstacles && obstacles.length > 0;
  const active = obstacles?.[0];

  return (
    <View style={[styles.container, hasObstacle ? styles.danger : styles.clear]}>
      {hasObstacle ? (
        <>
          <Text style={styles.alert}>⚠ {active?.label?.toUpperCase()} {active?.distance_m}m ahead</Text>
          <Text style={styles.type}>Type: {active?.type} | Risk: {risk} | Conf: {active?.confidence}</Text>
          <Text style={styles.action}>→ {guidance}</Text>
        </>
      ) : (
        <>
          <Text style={styles.clearText}>✓ Path clear</Text>
          <Text style={styles.sub}>Walkable: pier boardwalk • Pier edge 1.2m left — keep right</Text>
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 14, minHeight: 80 },
  danger: { backgroundColor: '#220000', borderTopWidth: 2, borderTopColor: '#ff4444' },
  clear: { backgroundColor: '#002200', borderTopWidth: 2, borderTopColor: '#00aa55' },
  alert: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  type: { color: '#ffaaaa', fontSize: 10, marginTop: 2 },
  action: { color: '#fff', fontSize: 16, fontWeight: 'bold', marginTop: 4 },
  clearText: { color: '#aaffaa', fontSize: 14, fontWeight: 'bold' },
  sub: { color: '#88ff88', fontSize: 11, marginTop: 2 },
});
