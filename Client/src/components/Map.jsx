import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function ChangeView({ sites }) {
  const map = useMap();
  React.useEffect(() => {
    if (sites.length > 0) {
      const bounds = L.latLngBounds([]);
      sites.forEach(site => {
        if (site.latitude && site.longitude) {
          bounds.extend([site.latitude, site.longitude]);
        }
      });
      if (bounds.isValid()) {
        map.fitBounds(bounds, { maxZoom: 13, padding: [40, 40] });
      }
    }
  }, [sites, map]);
  return null;
}

export default function Map({ sites }) {
  const center = sites.length > 0 && sites[0].latitude ? [sites[0].latitude, sites[0].longitude] : [20, 0];
  
  return (
    <div className="h-full w-full rounded-2xl overflow-hidden shadow-inner bg-gray-100">
      <MapContainer center={center} zoom={2} style={{ height: '100%', width: '100%' }}>
        <ChangeView sites={sites} />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {sites.map(site => (
          <React.Fragment key={site.site_id}>
            {site.geometry && (
              <GeoJSON 
                data={site.geometry} 
                style={{
                  color: getImpactHexColor(site.impact_level),
                  weight: 2,
                  fillOpacity: 0.3,
                }}
              >
                <Popup>
                  <div className="p-1">
                    <h3 className="font-bold">{site.name}</h3>
                    <p className="text-[10px] text-gray-500 font-bold uppercase">{site.activities?.[0]}</p>
                    <div className="mt-2 flex items-center gap-2 border-t pt-2">
                       <span className="text-[10px] font-black uppercase text-gray-400">Impact Score:</span>
                       <span className="text-xs font-bold text-orange-600">{site.priority_score?.toFixed(0)}</span>
                    </div>
                  </div>
                </Popup>
              </GeoJSON>
            )}
            {/* Also show marker for easier finding if geometry is small */}
            {site.latitude && site.longitude && (
              <Marker position={[site.latitude, site.longitude]}>
                <Popup>
                   <div className="p-1">
                    <h3 className="font-bold">{site.name}</h3>
                    <p className="text-xs text-gray-500">{site.activities?.[0]}</p>
                  </div>
                </Popup>
              </Marker>
            )}
          </React.Fragment>
        ))}
      </MapContainer>
    </div>
  );
}


function getImpactHexColor(level) {
  switch(level) {
    case 'VH': return '#dc2626';
    case 'H': return '#f87171';
    case 'M': return '#fb923c';
    case 'L': return '#fcd34d';
    case 'VL': return '#fde047';
    default: return '#fb923c';
  }
}
