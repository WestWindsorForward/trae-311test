import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import { useState } from 'react'
import 'leaflet/dist/leaflet.css'

const ClickHandler = ({ onSelect }) => {
  useMapEvents({
    click(e) {
      onSelect(e.latlng)
    }
  })
  return null
}

const MapPicker = ({ value, onChange }) => {
  const [pos, setPos] = useState(value || { lat: 40.0, lng: -74.0 })
  const handleSelect = (latlng) => {
    setPos(latlng)
    onChange(latlng)
  }
  return (
    <div className="h-64 w-full">
      <MapContainer center={[pos.lat, pos.lng]} zoom={13} className="h-full w-full">
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <ClickHandler onSelect={handleSelect} />
        <Marker position={[pos.lat, pos.lng]} />
      </MapContainer>
    </div>
  )
}

export default MapPicker
