import { createBrowserRouter, Navigate } from 'react-router-dom'
import { RootLayout } from '@/components/layout/RootLayout'
import { DashboardPage } from '@/pages/DashboardPage'
import { LeadsPage } from '@/pages/LeadsPage'
import { LeadDetailPage } from '@/pages/LeadDetailPage'
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
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'leads',
        element: <LeadsPage />,
      },
      {
        path: 'leads/:leadId',
        element: <LeadDetailPage />,
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
