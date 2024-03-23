import React, { useState } from 'react';
import { StyleSheet, View, Button } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import MapViewDirections from 'react-native-maps-directions';

const Route = () => {

  const [destination, setDestination] = useState({
      latitude: 13.0827,
      longitude: 80.2707,
    });

  const [origin, setOrigin] = useState({
      latitude: 11.0168,
      longitude: 76.9558,
    });

  return (
    <View style={styles.container}>
      <MapView style={styles.map}
      initialRegion={{
        latitude: (origin.latitude + destination.latitude) / 2,
        longitude: (origin.longitude + destination.longitude) / 2,
        latitudeDelta: Math.abs(origin.latitude - destination.latitude) + 0.1,
        longitudeDelta: Math.abs(origin.longitude - destination.longitude) + 0.1,
      }
    }
      >
        <MapViewDirections
          origin={origin}
          destination={destination}
          apikey= {process.env.EXPO_PUBLIC_GOOGLE_API_KEY}
          strokeWidth={2}
          strokeColor="red"
          mode={'DRIVING'}
        />
       <Marker
          coordinate={origin}
          title="Starting Point"
        />
        <Marker
          coordinate={destination}
          title="Destination Point"
        />
      </MapView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
});

export default Route;