export interface NavItem {
  name: string
  href: string
  iconName: 'dashboard' | 'leads' | 'advisors' | 'catalog'
}

export const navigationItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    iconName: 'dashboard',
  },
  {
    name: 'Leads Priorizados',
    href: '/leads',
    iconName: 'leads',
  },
  {
    name: 'Asesores',
    href: '/advisors',
    iconName: 'advisors',
  },
  {
    name: 'Catálogo',
    href: '/catalog',
    iconName: 'catalog',
  },
]
