import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { ArrowLeft, Compass } from 'lucide-react'

export function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6">
      <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-amber-400 mb-4">
        <Compass className="w-8 h-8" />
      </div>
      <h1 className="text-3xl font-bold text-slate-100 tracking-tight mb-2">404 - Página no encontrada</h1>
      <p className="text-slate-400 text-sm max-w-md mb-6">
        La sección que estás buscando no existe o fue movida a otra ubicación.
      </p>
      <Link to="/leads">
        <Button variant="primary" className="gap-2">
          <ArrowLeft className="w-4 h-4" />
          Volver a Leads Priorizados
        </Button>
      </Link>
    </div>
  )
}
