import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Database, RefreshCw, Sparkles, Building2, Info } from 'lucide-react'

const DEMO_COMPANIES = ['EMP-01', 'EMP-02', 'EMP-03'] as const

interface DashboardHeaderProps {
  selectedCompany: string
  onSelectCompany: (companyId: string) => void
  dataSource: 'api' | 'mock'
  isDerived: boolean
  sampleSize: number
  totalCompanyLeads: number
  syncTime: string
  notice?: string
  onRefresh: () => void
  isRefreshing: boolean
}

export function DashboardHeader({
  selectedCompany,
  onSelectCompany,
  dataSource,
  isDerived,
  sampleSize,
  totalCompanyLeads,
  syncTime,
  notice,
  onRefresh,
  isRefreshing,
}: DashboardHeaderProps) {
  return (
    <div className="space-y-4">
      {/* Barra superior de título y controles */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Dashboard de Métricas y Priorización
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
          <p className="text-sm text-slate-400 mt-1">
            Analítica de cartera, distribución de prospectos comerciales y detección de alta probabilidad de compra.
          </p>
        </div>

        {/* Selector de Empresa y botón de refresco */}
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
            title="Actualizar datos desde backend"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Actualizar</span>
          </Button>
        </div>
      </div>

      {/* Banner explicativo de origen de datos y derivación */}
      <div
        className={`p-3.5 rounded-xl border flex items-start gap-3 text-xs leading-relaxed ${
          dataSource === 'api'
            ? 'bg-cyan-950/20 border-cyan-800/40 text-cyan-200'
            : 'bg-amber-950/25 border-amber-800/40 text-amber-200'
        }`}
      >
        <Info
          className={`w-4 h-4 shrink-0 mt-0.5 ${
            dataSource === 'api' ? 'text-cyan-400' : 'text-amber-400'
          }`}
        />
        <div className="flex-1">
          <div className="font-semibold mb-0.5">
            {dataSource === 'api'
              ? (isDerived
                  ? 'Agregación Derivada en Frontend desde Leads Priorizados (FastAPI)'
                  : 'Métricas Directas desde FastAPI')
              : 'Demostración de Dashboard con Datos Simulados (Mock Local)'}
          </div>
          <div className="text-slate-300">
            {notice ||
              (dataSource === 'api'
                ? `Métricas generadas por derivación sobre ${sampleSize} registros auditados de la empresa ${selectedCompany} (Censo total: ${totalCompanyLeads} leads). Sincronizado a las ${syncTime}.`
                : `Mostrando datos de demostración para ${selectedCompany}. Para ver datos reales, configure VITE_DATA_SOURCE=api y asegure el backend activo.`)}
          </div>
        </div>
      </div>
    </div>
  )
}
