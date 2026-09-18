import type { Motorcycle } from '../catalog.types'
import { CatalogCard } from './CatalogCard'

interface CatalogGridProps {
  motorcycles: Motorcycle[]
  onSelect: (motorcycle: Motorcycle) => void
}

export function CatalogGrid({ motorcycles, onSelect }: CatalogGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {motorcycles.map((m) => (
        <CatalogCard key={m.sku} motorcycle={m} onSelect={onSelect} />
      ))}
    </div>
  )
}
