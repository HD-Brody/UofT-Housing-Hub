import React from 'react';
import 'leaflet/dist/leaflet.css';
import './Map.css';
import './fixLeafletIcons';

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

export function MapView({ listings }) {
    return (
        <MapContainer center={[43.662571, -79.39559]} zoom={15} className='map-container'>
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            />
            {listings.map((listing, i) => (
                <Marker key={i} position={[listing.lat, listing.lon]}>
                    <Popup>
                        <strong>{listing.title}</strong><br />
                        {listing.price}<br />
                        {listing.address}
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    )
}