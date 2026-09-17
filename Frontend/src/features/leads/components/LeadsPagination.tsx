import { Button } from '@/components/ui/Button'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface LeadsPaginationProps {
  currentPage: number
  totalPages: number
  totalItems: number
  pageSize: number
  onPageChange: (newPage: number) => void
}

export function LeadsPagination({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
}: LeadsPaginationProps) {
  if (totalItems === 0) {
    return null
  }

  const startItem = (currentPage - 1) * pageSize + 1
  const endItem = Math.min(currentPage * pageSize, totalItems)
  const isFirstPage = currentPage <= 1
  const isLastPage = currentPage >= totalPages

  return (
    <nav
      aria-label="Paginación de resultados"
      className="flex flex-col sm:flex-row items-center justify-between gap-3 px-2 py-2"
    >
      <div className="text-xs text-slate-400">
        Mostrando <strong className="text-slate-200">{startItem}</strong> a{' '}
        <strong className="text-slate-200">{endItem}</strong> de{' '}
        <strong className="text-slate-200">{totalItems}</strong> leads • Página{' '}
        <strong className="text-slate-200">{currentPage}</strong> de{' '}
        <strong className="text-slate-200">{Math.max(totalPages, 1)}</strong>
      </div>

      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={isFirstPage}
          onClick={() => onPageChange(currentPage - 1)}
          className="text-xs gap-1"
          aria-label="Ir a página anterior"
        >
          <ChevronLeft className="w-3.5 h-3.5" aria-hidden="true" />
          Anterior
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={isLastPage}
          onClick={() => onPageChange(currentPage + 1)}
          className="text-xs gap-1"
          aria-label="Ir a página siguiente"
        >
          Siguiente
          <ChevronRight className="w-3.5 h-3.5" aria-hidden="true" />
        </Button>
      </div>
    </nav>
  )
}
