import { Link } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Compass, ArrowLeft } from 'lucide-react'

export function NotFoundPage() {
  return (
    <div className="py-16 flex items-center justify-center">
      <Card className="max-w-md w-full text-center p-6 border-slate-800 bg-slate-900/60">
        <CardContent className="space-y-4">
          <div className="w-14 h-14 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-400 mx-auto">
            <Compass className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100">404 - Ruta no encontrada</h1>
            <p className="text-xs text-slate-400 mt-1">
              La dirección solicitada no corresponde a ningún módulo del sistema.
            </p>
          </div>
          <Link to="/dashboard" className="inline-block pt-2">
            <Button variant="primary" size="sm" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Ir al Dashboard
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}
