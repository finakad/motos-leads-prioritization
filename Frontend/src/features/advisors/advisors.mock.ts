import type { Advisor } from './advisor.types'

/**
 * Datos mock explícitos y locales de asesores comerciales.
 * Basados en la estructura real del proyecto:
 * - asesor_id (id)
 * - nombre (fullName)
 * - punto_venta_id (salesPointId)
 * - empresa_id (companyId)
 * - capacidad_diaria_leads (dailyLeadCapacity)
 * - activo (status: 'active' | 'inactive')
 * - fecha_ingreso (joinedAt)
 */
export const MOCK_ADVISORS: Advisor[] = [
  {
    id: 'ADV-001',
    companyId: 'EMP-01',
    salesPointId: 'PV-001',
    fullName: 'Daniela Restrepo',
    dailyLeadCapacity: 12,
    status: 'active',
    joinedAt: '2024-02-15T08:00:00Z',
  },
  {
    id: 'ADV-002',
    companyId: 'EMP-01',
    salesPointId: 'PV-001',
    fullName: 'Felipe Jaramillo',
    dailyLeadCapacity: 15,
    status: 'active',
    joinedAt: '2023-11-01T08:00:00Z',
  },
  {
    id: 'ADV-003',
    companyId: 'EMP-01',
    salesPointId: 'PV-001',
    fullName: 'Marcela Quintero',
    dailyLeadCapacity: 10,
    status: 'inactive',
    joinedAt: '2025-05-10T08:00:00Z',
  },
  {
    id: 'ADV-004',
    companyId: 'EMP-02',
    salesPointId: 'PV-002',
    fullName: 'Carolina Herrera',
    dailyLeadCapacity: 10,
    status: 'active',
    joinedAt: '2024-06-20T08:00:00Z',
  },
  {
    id: 'ADV-005',
    companyId: 'EMP-02',
    salesPointId: 'PV-002',
    fullName: 'Andrés Camilo Pérez',
    dailyLeadCapacity: 8,
    status: 'active',
    joinedAt: '2024-09-01T08:00:00Z',
  },
  {
    id: 'ADV-006',
    companyId: 'EMP-02',
    salesPointId: 'PV-002',
    fullName: 'Gabriel Jaime Ochoa',
    dailyLeadCapacity: 8,
    status: 'inactive',
    joinedAt: '2025-03-12T08:00:00Z',
  },
  {
    id: 'ADV-007',
    companyId: 'EMP-03',
    salesPointId: 'PV-003',
    fullName: 'Tatiana Morales',
    dailyLeadCapacity: 10,
    status: 'active',
    joinedAt: '2023-08-15T08:00:00Z',
  },
  {
    id: 'ADV-008',
    companyId: 'EMP-03',
    salesPointId: 'PV-003',
    fullName: 'Sebastián Betancur',
    dailyLeadCapacity: 12,
    status: 'active',
    joinedAt: '2024-01-22T08:00:00Z',
  },
]
