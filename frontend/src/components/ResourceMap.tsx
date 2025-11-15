import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

interface Resource {
  name: string
  address: string
  phone: string
  distance_miles?: number
  coordinates: {
    latitude: number
    longitude: number
  }
  services?: string[]
  hours?: string
}

interface ResourceMapProps {
  resources: Resource[]
  userLocation?: { latitude: number; longitude: number }
}

// Fix default marker icon issue in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

export function ResourceMap({ resources, userLocation }: ResourceMapProps) {
  const mapRef = useRef<L.Map | null>(null)
  const mapContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!mapContainerRef.current || resources.length === 0) return

    // Initialize map if not already created
    if (!mapRef.current) {
      const map = L.map(mapContainerRef.current).setView(
        userLocation
          ? [userLocation.latitude, userLocation.longitude]
          : [resources[0].coordinates.latitude, resources[0].coordinates.longitude],
        12
      )

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map)

      mapRef.current = map
    }

    const map = mapRef.current

    // Clear existing markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer)
      }
    })

    // Add user location marker (blue)
    if (userLocation) {
      const userIcon = L.divIcon({
        html: '<div style="background-color: #4a90e2; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.3);"></div>',
        className: '',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      })

      L.marker([userLocation.latitude, userLocation.longitude], { icon: userIcon })
        .addTo(map)
        .bindPopup('<b>Your Location</b>')
    }

    // Add resource markers (red)
    const bounds: L.LatLngBoundsExpression = []
    resources.forEach((resource, index) => {
      const { latitude, longitude } = resource.coordinates
      bounds.push([latitude, longitude])

      const resourceIcon = L.divIcon({
        html: `<div style="background-color: #e74c3c; color: white; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px;">${index + 1}</div>`,
        className: '',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      })

      const popupContent = `
        <div style="min-width: 250px;">
          <h3 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 16px;">${index + 1}. ${resource.name}</h3>
          <p style="margin: 5px 0; font-size: 13px;"><strong>Address:</strong><br/>${resource.address}</p>
          <p style="margin: 5px 0; font-size: 13px;"><strong>Phone:</strong> ${resource.phone}</p>
          ${resource.distance_miles ? `<p style="margin: 5px 0; font-size: 13px;"><strong>Distance:</strong> ${resource.distance_miles} miles</p>` : ''}
          ${resource.hours ? `<p style="margin: 5px 0; font-size: 13px;"><strong>Hours:</strong> ${resource.hours}</p>` : ''}
          <div style="margin-top: 10px;">
            <a href="https://www.google.com/maps/dir/?api=1&origin=${userLocation?.latitude},${userLocation?.longitude}&destination=${latitude},${longitude}&travelmode=transit"
               target="_blank"
               style="display: inline-block; background: #4a90e2; color: white; padding: 8px 12px; text-decoration: none; border-radius: 5px; font-size: 13px; margin-right: 5px;">
              🚌 Transit Directions
            </a>
            <a href="https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}"
               target="_blank"
               style="display: inline-block; background: #50c878; color: white; padding: 8px 12px; text-decoration: none; border-radius: 5px; font-size: 13px;">
              📍 View on Map
            </a>
          </div>
        </div>
      `

      L.marker([latitude, longitude], { icon: resourceIcon })
        .addTo(map)
        .bindPopup(popupContent)
    })

    // Include user location in bounds
    if (userLocation) {
      bounds.push([userLocation.latitude, userLocation.longitude])
    }

    // Fit map to show all markers
    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50] })
    }

  }, [resources, userLocation])

  if (resources.length === 0) {
    return null
  }

  return (
    <div style={{ marginTop: '20px', borderRadius: '10px', overflow: 'hidden', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
      <div ref={mapContainerRef} style={{ height: '400px', width: '100%' }} />
    </div>
  )
}
