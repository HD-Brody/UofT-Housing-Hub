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


export function MapView({ listings, hoveredListingUrl }) {
    const [hoveredMarkerUrl, setHoveredMarkerUrl] = useState(null);

    function hashStringToOffset(str, maxOffset = 0.0003) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const offset = (hash % 100) / 100 * maxOffset;
        return offset - maxOffset / 2;
    }

    function applyJitteredOffset(lat, lon, url) {
        const latOffset = hashStringToOffset(url + 'lat');
        const lonOffset = hashStringToOffset(url + 'lon');
        return [lat + latOffset, lon + lonOffset];
    }

    return (
        <MapContainer center={[43.662571, -79.39559]} zoom={15} className='map-container'>
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            />
            {listings.map((listing, i) => {
                const isHovered = hoveredListingUrl === listing.url || hoveredMarkerUrl === listing.url;

                return (
                    <Marker
                        key={listing.url}
                        position={applyJitteredOffset(listing.lat, listing.lon, listing.url)}
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
