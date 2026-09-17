import { createBrowserRouter, Navigate } from 'react-router-dom'
import { RootLayout } from '@/components/layout/RootLayout'
import { LeadsPage } from '@/pages/LeadsPage'
import { LeadDetailPage } from '@/pages/LeadDetailPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { AdvisorsPage } from '@/pages/AdvisorsPage'
import { CatalogPage } from '@/pages/CatalogPage'
import { NotFoundPage } from '@/pages/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/leads" replace />,
      },
      {
        path: 'leads',
        element: <LeadsPage />,
      },
      {
        path: 'leads/:id',
        element: <LeadDetailPage />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'advisors',
        element: <AdvisorsPage />,
      },
      {
        path: 'catalog',
        element: <CatalogPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
])
