import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Bike, Building2, Database, RefreshCw, Sparkles } from 'lucide-react'

const DEMO_COMPANIES = ['EMP-01', 'EMP-02', 'EMP-03'] as const

interface CatalogHeaderProps {
  selectedCompany: string
  onSelectCompany: (companyId: string) => void
  dataSource: 'api' | 'mock'
  totalModels: number
  onRefresh: () => void
  isRefreshing: boolean
}

export function CatalogHeader({
  selectedCompany,
  onSelectCompany,
  dataSource,
  totalModels,
  onRefresh,
  isRefreshing,
}: CatalogHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-950/60 border border-indigo-800/50 flex items-center justify-center text-indigo-400">
            <Bike className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight text-slate-100">
                Catálogo de Motocicletas
              </h1>
              <Badge
                variant={dataSource === 'api' ? 'success' : 'warning'}
                size="sm"
                className="gap-1 normal-case font-semibold"
              >
                {dataSource === 'api' ? (
                  <>
                    <Database className="w-3 h-3 text-emerald-400" />
                    FastAPI Conectado
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3 h-3 text-amber-400" />
                    Modo Mock Local
                  </>
                )}
              </Badge>
            </div>
            <p className="text-sm text-slate-400 mt-0.5">
              Portafolio comercial, fichas técnicas, precios oficiales y disponibilidad por sede ({totalModels} modelos activos).
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 rounded-lg p-1">
          <Building2 className="w-4 h-4 text-slate-400 ml-2 mr-1" />
          <span className="text-xs text-slate-400 font-medium mr-1 hidden sm:inline">
            Empresa:
          </span>
          {DEMO_COMPANIES.map((compId) => (
            <button
              key={compId}
              type="button"
              onClick={() => onSelectCompany(compId)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
                selectedCompany === compId
                  ? 'bg-cyan-500 text-slate-950 shadow-sm shadow-cyan-500/30'
                  : 'text-slate-300 hover:text-slate-100 hover:bg-slate-800'
              }`}
            >
              {compId}
            </button>
          ))}
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={onRefresh}
          disabled={isRefreshing}
          className="gap-1.5"
          title="Actualizar catálogo desde backend"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">Actualizar</span>
        </Button>
      </div>
    </div>
  )
}
