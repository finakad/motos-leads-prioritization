import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from './Card'
import { Construction } from 'lucide-react'

export interface PlaceholderPageProps {
  moduleName: string
  title: string
  description: string
  routePath: string
  icon?: React.ReactNode
  children?: React.ReactNode
}

export function PlaceholderPage({
  moduleName,
  title,
  description,
  routePath,
  icon,
  children,
}: PlaceholderPageProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div>
          <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider block mb-1">
            {moduleName}
          </span>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
            {icon}
            {title}
          </h1>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 font-mono bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 self-start sm:self-auto">
          <span className="text-slate-500">Ruta:</span>
          <span className="text-slate-200">{routePath}</span>
        </div>
      </div>

      <Card className="border-dashed border-slate-800 bg-slate-900/40">
        <CardHeader>
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Construction className="w-4 h-4" />
            </div>
            <div>
              <CardTitle>Módulo en Preparación</CardTitle>
              <p className="text-xs text-slate-400 mt-0.5">{description}</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-xs text-slate-400 leading-relaxed">
            La estructura técnica, enrutador y providers están listos. Las vistas definitivas y
            componentes de negocio se conectarán una vez aprobados los contratos de la API.
          </p>
          {children}
        </CardContent>
      </Card>
    </div>
  )
}
