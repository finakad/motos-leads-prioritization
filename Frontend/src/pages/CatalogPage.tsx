import { PlaceholderPage } from '@/components/ui/PlaceholderPage'
import { Bike } from 'lucide-react'

export function CatalogPage() {
  return (
    <PlaceholderPage
      moduleName="Módulo de Producto"
      title="Catálogo de Motocicletas"
      description="Espacio reservado para inventario, marcas y fichas técnicas. Pendiente de definición y exposición de endpoints en FastAPI."
      routePath="/catalog"
      icon={<Bike className="w-6 h-6 text-indigo-400" />}
    />
  )
}
