import { NavLink } from 'react-router-dom'
import { navigationItems } from '@/config/navigation'
import {
  Flame,
  LayoutDashboard,
  Users,
  Bike,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const renderIcon = (iconName: string) => {
    switch (iconName) {
      case 'dashboard':
        return <LayoutDashboard className="w-4 h-4 text-cyan-400" />
      case 'leads':
        return <Flame className="w-4 h-4 text-amber-400" />
      case 'advisors':
        return <Users className="w-4 h-4 text-emerald-400" />
      case 'catalog':
        return <Bike className="w-4 h-4 text-indigo-400" />
      default:
        return null
    }
  }

  return (
    <>
      {/* Mobile Backdrop overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 z-30 lg:hidden backdrop-blur-xs transition-opacity"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={cn(
          'fixed lg:sticky top-0 left-0 z-40 h-screen w-64 border-r border-slate-800/80 bg-slate-900/95 lg:bg-slate-900/80 backdrop-blur-md flex flex-col justify-between shrink-0 transition-transform duration-200 ease-in-out',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div>
          {/* Brand Header */}
          <div className="h-16 flex items-center justify-between px-6 border-b border-slate-800/80">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center shadow-md shadow-amber-500/20">
                <Bike className="w-5 h-5 text-slate-950 stroke-[2.5]" />
              </div>
              <div>
                <span className="font-bold text-slate-100 text-sm tracking-tight block">
                  Motos Leads
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-wider text-amber-400 block">
                  Prioritization
                </span>
              </div>
            </div>

            {/* Mobile close button */}
            <button
              onClick={onClose}
              className="lg:hidden text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800"
              aria-label="Cerrar menú"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation links */}
          <nav className="p-4 space-y-1.5">
            <div className="px-3 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Navegación
            </div>
            {navigationItems.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                onClick={onClose}
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
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Footer / Multi-tenant indicator */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="text-xs font-semibold text-slate-200">
              Frontend Base
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
              Módulos listos para desacoplamiento e integración con API.
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}
