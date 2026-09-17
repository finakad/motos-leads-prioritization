export interface NavItem {
  name: string
  href: string
  iconName: 'leads' | 'dashboard' | 'advisors' | 'catalog'
  badge?: string
}

export const navigationItems: NavItem[] = [
  {
    name: 'Leads Priorizados',
    href: '/leads',
    iconName: 'leads',
  },
  {
    name: 'Dashboard Métricas',
    href: '/dashboard',
    iconName: 'dashboard',
  },
  {
    name: 'Asesores Comerciales',
    href: '/advisors',
    iconName: 'advisors',
  },
  {
    name: 'Catálogo de Motos',
    href: '/catalog',
    iconName: 'catalog',
  },
]
