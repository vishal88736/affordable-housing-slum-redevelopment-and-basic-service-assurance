import { ReactNode } from 'react'
import { ArrowUpRight, Info } from 'lucide-react'
import { MapContainer, ImageOverlay, CircleMarker, Popup, ZoomControl, Marker } from 'react-leaflet'
import L from 'leaflet'
import { Pocket } from '../lib/api'
import 'leaflet/dist/leaflet.css'
import { useI18n } from '../i18n'

export const tierColors: Record<string, string> = { Critical: '#dc5b50', High: '#e9a73c', Medium: '#159d9a', Low: '#698cc6' }
export function Badge({ children, tone = 'teal' }: { children: ReactNode; tone?: string }) { return <span className={`badge ${tone}`}>{children}</span> }
export function SectionTitle({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) { return <div className="section-heading"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div> }
export function Metric({ label, value, note, icon, color = 'teal' }: { label: string; value: string; note?: string; icon?: ReactNode; color?: string }) { return <div className="metric card"><div className={`metric-icon ${color}`}>{icon}</div><span>{label}</span><strong>{value}</strong><small>{note && <ArrowUpRight size={13} />}{note}</small></div> }
export function Panel({ title, subtitle, children, action, className = '' }: { title?: string; subtitle?: string; children: ReactNode; action?: ReactNode; className?: string }) { return <section className={`card panel ${className}`}>{title && <div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</div>}{children}</section> }
export function Note({ children }: { children: ReactNode }) { return <div className="note"><Info size={16} /><span>{children}</span></div> }
export function PocketMap({ pockets, onSelect, mode = 'priority', small = false }: { pockets: Pocket[]; onSelect?: (id: string) => void; mode?: string; small?: boolean }) {
  const { t } = useI18n()
  const cityLabels: Record<string, string> = { Mumbai: t('cityMumbai'), Thane: t('cityThane'), Kalyan: t('cityKalyan'), Ambarnath: t('cityAmbarnath'), Ulhasnagar: t('cityUlhasnagar') }
  const cityMarkers = [{ name: 'Mumbai', position: [19.04, 72.91] as [number, number] }, { name: 'Thane', position: [19.22, 72.99] as [number, number] }, { name: 'Kalyan', position: [19.24, 73.13] as [number, number] }, { name: 'Ulhasnagar', position: [19.22, 73.16] as [number, number] }, { name: 'Ambarnath', position: [19.19, 73.19] as [number, number] }]
  return <div className={`map-shell ${small ? 'small' : ''}`}><MapContainer center={[19.17, 73.04]} zoom={11} zoomControl={false} scrollWheelZoom={false} attributionControl={false}>
    <ImageOverlay url="/mmr-map.svg" bounds={[[18.91, 72.77], [19.34, 73.29]]} />
    <ZoomControl position="bottomright" />
    {!small && cityMarkers.map(city => <Marker key={city.name} position={city.position} icon={L.divIcon({ className: 'map-city-label', html: cityLabels[city.name], iconSize: undefined })} interactive={false} />)}
     {pockets.filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lon)).slice(0, 200).map((p, i) => {
      const risk = mode === 'flood' ? p.flood_risk_score : mode === 'fire' ? p.fire_risk_score : mode === 'services' ? 100 - p.water_hours_per_day * 8 : p.priority_score
      const color = mode === 'priority' ? tierColors[p.tier] : risk > 70 ? '#dc5b50' : risk > 45 ? '#e9a73c' : '#159d9a'
       return <CircleMarker key={p.pocket_id} center={[p.lat, p.lon]} radius={small ? 5 + (i % 3) : 7 + (i % 4)} pathOptions={{ color: '#fff', fillColor: color, fillOpacity: .85, weight: 2 }} eventHandlers={{ click: () => onSelect?.(p.pocket_id) }}><Popup><strong>{p.pocket_id}</strong><p>{cityLabels[p.city] || p.city} · {p.ward}</p><p>{t('priorityLabel')}: {p.priority_score.toFixed(1)} · {t(`tier.${p.tier.toLowerCase()}`)}</p><button onClick={() => onSelect?.(p.pocket_id)}>{t('viewPocket')} →</button></Popup></CircleMarker>
     })}
   </MapContainer><div className="map-caption">{t('mapCaption')}</div><div className="map-legend">{Object.entries(tierColors).map(([tier, color]) => <span key={tier}><i style={{ background: color }} />{t(`tier.${tier.toLowerCase()}`)}</span>)}</div></div>
}
export const chartColors = { teal: '#159d9a', amber: '#e9a73c', red: '#dc5b50', navy: '#173c54' }
