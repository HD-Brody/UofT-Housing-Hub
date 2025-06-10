import React, { useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';
import './fixLeafletIcons';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

const defaultIcon = new L.Icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

const hoverIcon = new L.Icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconSize: [35, 51],
    iconAnchor: [17, 51],
    popupAnchor: [1, -40],
    className: 'hovered-marker'
});


function findDuplicateLocations(listings) {
    const locationMap = new Map();

    for (const listing of listings) {
        const key = `${listing.lat},${listing.lon}`;
        if (!locationMap.has(key)) {
            locationMap.set(key, []);
        }
        locationMap.get(key).push(listing);
    }

    // Filter to only include locations with more than one listing
    const duplicates = [];
    for (const [key, group] of locationMap.entries()) {
        if (group.length > 1) {
            duplicates.push({ location: key, listings: group });
        }
    }

    return duplicates;
}


export function MapView({ listings, hoveredListingUrl }) {
    const [hoveredMarkerUrl, setHoveredMarkerUrl] = useState(null);

    const duplicates = findDuplicateLocations(listings);
    console.log('Duplicate locations:', duplicates);

    return (
        <MapContainer center={[43.662571, -79.39559]} zoom={15} className='map-container'>
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            />
            {listings.map((listing) => {
                const isHovered = hoveredListingUrl === listing.url || hoveredMarkerUrl === listing.url;

                return (
                    <Marker
                        key={listing.url}
                        position={[listing.lat, listing.lon]}
                        icon={isHovered ? hoverIcon : defaultIcon}
                        eventHandlers={{
                            mouseover: () => setHoveredMarkerUrl(listing.url),
                            mouseout: () => setHoveredMarkerUrl(null),
                        }}
                    >
                        <Popup className="custom-popup">
                            <div className='popup-content'>
                                <img src={listing.image_url} alt='' className='popup-img'/>
                                <div className='popup-text'>
                                    <strong>{listing.title}</strong><br />
                                    {listing.price}<br />
                                    {listing.address}
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                );
            })}
        </MapContainer>
    );
}
