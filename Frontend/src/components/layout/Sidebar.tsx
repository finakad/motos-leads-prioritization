import { NavLink } from 'react-router-dom'
import { navigationItems } from '@/config/navigation'
import {
  Flame,
  LayoutDashboard,
  Users,
  Bike,
  ShieldCheck,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function Sidebar() {
  const renderIcon = (iconName: string) => {
    switch (iconName) {
      case 'leads':
        return <Flame className="w-4 h-4 text-amber-400" />
      case 'dashboard':
        return <LayoutDashboard className="w-4 h-4 text-cyan-400" />
      case 'advisors':
        return <Users className="w-4 h-4 text-emerald-400" />
      case 'catalog':
        return <Bike className="w-4 h-4 text-indigo-400" />
      default:
        return null
    }
  }

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-900/80 backdrop-blur-md flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Bike className="w-5 h-5 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <span className="font-bold text-slate-100 text-sm tracking-tight block">
              Motos Leads
            </span>
            <span className="text-[10px] uppercase font-semibold tracking-wider text-amber-400 block">
              Prioritization AI
            </span>
          </div>
        </div>

        {/* Navigation items */}
        <nav className="p-4 space-y-1.5">
          <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Navegación
          </div>
          {navigationItems.map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                )
              }
            >
              <div className="flex items-center gap-3">
                {renderIcon(item.iconName)}
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-[10px] rounded-full bg-slate-800 text-slate-300 font-bold border border-slate-700">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer / Tenant isolation badge */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex items-center gap-2 mb-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs font-semibold text-slate-200">Aislamiento Activo</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Datos filtrados por compañía en el frontend. La seguridad definitiva depende de backend.
          </p>
        </div>
      </div>
    </aside>
  )
}
