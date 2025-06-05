import 'leaflet/dist/leaflet.css';
import './Map.css';

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

export function MapView({ listings }) {
    return (
        <MapContainer center={[43.662571, -79.39559]} zoom={14} className='map-container'>

        </MapContainer>
    )
}