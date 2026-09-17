import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button } from './Button'
import { cn } from '@/lib/utils'

interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  title = 'Ocurrió un error al cargar los datos',
  message = 'No se pudo completar la solicitud. Por favor intenta nuevamente.',
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-10 text-center rounded-xl border border-rose-900/40 bg-rose-950/20',
        className
      )}
    >
      <div className="w-12 h-12 rounded-full bg-rose-900/40 border border-rose-800/60 flex items-center justify-center text-rose-400 mb-4">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h4 className="text-base font-semibold text-rose-200 mb-1">{title}</h4>
      <p className="text-sm text-slate-300 max-w-md mb-5">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} className="gap-2">
          <RefreshCw className="w-3.5 h-3.5" />
          Reintentar
        </Button>
      )}
    </div>
  )
}
