import { Users, Mail, Phone, Award } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

export function AdvisorsPage() {
  const advisors = [
    {
      id: 'adv-01',
      name: 'Daniela Restrepo',
      role: 'Asesora Senior de Motos Deportivas',
      email: 'daniela.restrepo@motocenter.com',
      phone: '+57 312 990 1234',
      activeLeads: 8,
      conversionRate: '34%',
      status: 'DISPONIBLE',
    },
    {
      id: 'adv-02',
      name: 'Felipe Jaramillo',
      role: 'Especialista en Gama Media y Retomas',
      email: 'felipe.jaramillo@motocenter.com',
      phone: '+57 315 880 5678',
      activeLeads: 12,
      conversionRate: '28%',
      status: 'DISPONIBLE',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
          <Users className="w-6 h-6 text-emerald-400" />
          Equipo de Asesores Comerciales
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Gestión de capacidad y asignación de leads priorizados por asesor en la sede.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {advisors.map((advisor) => (
          <Card key={advisor.id}>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-200 font-bold">
                  {advisor.name.charAt(0)}
                </div>
                <div>
                  <CardTitle>{advisor.name}</CardTitle>
                  <p className="text-xs text-slate-400">{advisor.role}</p>
                </div>
              </div>
              <Badge variant="success">Disponible</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2 text-slate-300">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  <span>{advisor.email}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  <span>{advisor.phone}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800 text-center">
                <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">Leads Activos</span>
                  <div className="text-base font-bold text-slate-100 font-mono mt-0.5">
                    {advisor.activeLeads}
                  </div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800">
                  <div className="flex items-center justify-center gap-1 text-[10px] text-amber-400 uppercase font-semibold">
                    <Award className="w-3 h-3" />
                    Conversión
                  </div>
                  <div className="text-base font-bold text-amber-400 font-mono mt-0.5">
                    {advisor.conversionRate}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
