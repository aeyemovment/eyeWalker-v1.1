
import { useState, useEffect } from 'react';

export const useLocation = () => {
  const [location, setLocation] = useState<any>(null);
  const [heading, setHeading] = useState(0);

  useEffect(() => {
    // Mock Baltimore Harbor location for demo
    // In prod: Location.getCurrentPositionAsync + watchPosition
    const mock = {
      coords: { latitude: 39.2805, longitude: -76.592, accuracy: 5 },
      timestamp: Date.now()
    };
    setLocation(mock);
    const interval = setInterval(() => {
      // Simulate walking 1.3 m/s
      setLocation((prev: any) => ({
        coords: {
          latitude: prev.coords.latitude + (Math.random()-0.5)*0.00005,
          longitude: prev.coords.longitude + (Math.random()-0.5)*0.00005,
          accuracy: 4
        },
        timestamp: Date.now()
      }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return { location, heading };
};
