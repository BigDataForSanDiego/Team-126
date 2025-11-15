import React, { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet'
import { Icon, LatLngExpression } from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers not showing
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

// @ts-ignore
delete Icon.Default.prototype._getIconUrl
Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
})

interface HealthService {
  id: number
  latitude: number
  longitude: number
  program: string
  address: string
  phone: string
  website: string
  description: string
  services: string
  language: string
  distance_km: number
  distance_miles: number
  similarity_score?: number
  combined_score?: number
  nearby_transit?: TransitStop[]
}

interface TransitStop {
  id: number
  name: string
  latitude: number
  longitude: number
  agency: string
  wheelchair_accessible: boolean
  distance_km: number
  distance_miles: number
}

interface ServiceMapProps {
  userLocation: { latitude: number; longitude: number }
  services: HealthService[]
  searchRadius?: number
}

// Component to fit map bounds to all markers
function FitBounds({ services, userLocation }: { services: HealthService[], userLocation: { latitude: number, longitude: number } }) {
  const map = useMap()

  useEffect(() => {
    if (services.length > 0) {
      const bounds: LatLngExpression[] = [
        [userLocation.latitude, userLocation.longitude],
        ...services.map(s => [s.latitude, s.longitude] as LatLngExpression)
      ]

      map.fitBounds(bounds, { padding: [50, 50] })
    }
  }, [services, userLocation, map])

  return null
}

// Custom icon for user location
const userIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
      <circle cx="12" cy="12" r="10" fill="#4a90e2" stroke="white" stroke-width="2"/>
      <circle cx="12" cy="12" r="4" fill="white"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 16],
  popupAnchor: [0, -16]
})

// Custom icon for health services
const healthIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
      <circle cx="12" cy="12" r="10" fill="#ff6b6b" stroke="white" stroke-width="2"/>
      <path d="M12 6v12M6 12h12" stroke="white" stroke-width="2" stroke-linecap="round"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
})

// Custom icon for transit stops
const transitIcon = new Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle cx="12" cy="12" r="8" fill="#50c878" stroke="white" stroke-width="2"/>
      <path d="M8 12h8M12 8v8" stroke="white" stroke-width="2" stroke-linecap="round"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12]
})

export function ServiceMap({ userLocation, services, searchRadius = 50 }: ServiceMapProps) {
  const center: LatLngExpression = [userLocation.latitude, userLocation.longitude]

  return (
    <div style={{ height: '500px', width: '100%', borderRadius: '10px', overflow: 'hidden' }}>
      <MapContainer
        center={center}
        zoom={12}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        {/* Base map tiles from OpenStreetMap */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* User location marker */}
        <Marker position={center} icon={userIcon}>
          <Popup>
            <strong>Your Location</strong>
          </Popup>
        </Marker>

        {/* Search radius circle */}
        <Circle
          center={center}
          radius={searchRadius * 1000} // Convert km to meters
          pathOptions={{
            color: '#4a90e2',
            fillColor: '#4a90e2',
            fillOpacity: 0.1,
            weight: 2,
            dashArray: '5, 10'
          }}
        />

        {/* Health service markers */}
        {services.map((service) => (
          <React.Fragment key={service.id}>
            <Marker
              position={[service.latitude, service.longitude]}
              icon={healthIcon}
            >
              <Popup maxWidth={300}>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  <h3 style={{ margin: '0 0 10px 0', color: '#ff6b6b' }}>
                    {service.program || 'Health Service'}
                  </h3>

                  <div style={{ marginBottom: '10px' }}>
                    <strong>📍 Distance:</strong> {service.distance_miles.toFixed(2)} miles ({service.distance_km.toFixed(2)} km)
                  </div>

                  {service.combined_score && (
                    <div style={{ marginBottom: '10px' }}>
                      <strong>🎯 Match Score:</strong> {(service.combined_score * 100).toFixed(0)}%
                    </div>
                  )}

                  {service.address && (
                    <div style={{ marginBottom: '10px' }}>
                      <strong>📮 Address:</strong><br />
                      {service.address}
                    </div>
                  )}

                  {service.phone && (
                    <div style={{ marginBottom: '10px' }}>
                      <strong>📞 Phone:</strong><br />
                      <a href={`tel:${service.phone}`}>{service.phone}</a>
                    </div>
                  )}

                  {service.website && (
                    <div style={{ marginBottom: '10px' }}>
                      <strong>🌐 Website:</strong><br />
                      <a href={service.website} target="_blank" rel="noopener noreferrer">
                        Visit Website
                      </a>
                    </div>
                  )}

                  {service.services && (
                    <div style={{ marginBottom: '10px' }}>
                      <strong>🏥 Services:</strong><br />
                      {service.services}
                    </div>
                  )}

                  {service.language && (
                    <div style={{ marginBottom: '10px' }}>
                      <strong>🗣️ Languages:</strong> {service.language}
                    </div>
                  )}

                  {service.description && (
                    <div style={{ marginBottom: '10px' }}>
                      <strong>ℹ️ Description:</strong><br />
                      <div style={{ fontSize: '0.9em', color: '#666' }}>
                        {service.description}
                      </div>
                    </div>
                  )}

                  {/* Nearby Transit Stops */}
                  {service.nearby_transit && service.nearby_transit.length > 0 && (
                    <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #eee' }}>
                      <strong>🚌 Nearby Transit ({service.nearby_transit.length}):</strong>
                      <ul style={{ margin: '5px 0', paddingLeft: '20px', fontSize: '0.9em' }}>
                        {service.nearby_transit.map((stop) => (
                          <li key={stop.id} style={{ marginBottom: '5px' }}>
                            {stop.name} - {stop.distance_miles.toFixed(2)} mi
                            {stop.wheelchair_accessible && ' ♿'}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid #eee' }}>
                    <a
                      href={`https://www.google.com/maps/dir/?api=1&origin=${userLocation.latitude},${userLocation.longitude}&destination=${service.latitude},${service.longitude}&travelmode=transit`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-block',
                        padding: '8px 16px',
                        background: '#4a90e2',
                        color: 'white',
                        textDecoration: 'none',
                        borderRadius: '5px',
                        fontSize: '0.9em'
                      }}
                    >
                      🗺️ Get Directions
                    </a>
                  </div>
                </div>
              </Popup>
            </Marker>

            {/* Transit stop markers for this service */}
            {service.nearby_transit?.map((stop) => (
              <Marker
                key={`transit-${stop.id}`}
                position={[stop.latitude, stop.longitude]}
                icon={transitIcon}
              >
                <Popup>
                  <div>
                    <strong>🚌 {stop.name}</strong><br />
                    Agency: {stop.agency}<br />
                    {stop.wheelchair_accessible && '♿ Wheelchair Accessible<br />'}
                    Distance: {stop.distance_miles.toFixed(2)} mi from service
                  </div>
                </Popup>
              </Marker>
            ))}
          </React.Fragment>
        ))}

        {/* Fit bounds to show all markers */}
        <FitBounds services={services} userLocation={userLocation} />
      </MapContainer>
    </div>
  )
}
