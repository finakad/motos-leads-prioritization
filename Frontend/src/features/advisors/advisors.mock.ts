import type { Advisor } from './advisor.types'

/**
 * Nómina real de asesores sincronizada con la base de datos PostgreSQL:
 * 42 asesores distribuidos en las 3 empresas (EMP-01, EMP-02, EMP-03)
 * y en sus respectivas sedes (PV-001 a PV-015).
 */
export const MOCK_ADVISORS: Advisor[] = [
  // EMP-01
  { id: 'AS-001', companyId: 'EMP-01', salesPointId: 'PV-001', fullName: 'Édinson Mosquera Pérez', dailyLeadCapacity: 12, status: 'active', joinedAt: '2026-02-27T00:00:00Z' },
  { id: 'AS-002', companyId: 'EMP-01', salesPointId: 'PV-001', fullName: 'Andrés Felipe Bedoya Salazar', dailyLeadCapacity: 25, status: 'active', joinedAt: '2025-02-10T00:00:00Z' },
  { id: 'AS-003', companyId: 'EMP-01', salesPointId: 'PV-001', fullName: 'Sebastián Mosquera Rodríguez', dailyLeadCapacity: 20, status: 'active', joinedAt: '2024-02-24T00:00:00Z' },
  { id: 'AS-004', companyId: 'EMP-01', salesPointId: 'PV-001', fullName: 'Sebastián Cardona Londoño', dailyLeadCapacity: 20, status: 'active', joinedAt: '2024-01-18T00:00:00Z' },
  { id: 'AS-005', companyId: 'EMP-01', salesPointId: 'PV-002', fullName: 'Luisa Ospina Vargas', dailyLeadCapacity: 18, status: 'active', joinedAt: '2024-03-08T00:00:00Z' },
  { id: 'AS-006', companyId: 'EMP-01', salesPointId: 'PV-002', fullName: 'Duván Ramírez Londoño', dailyLeadCapacity: 15, status: 'active', joinedAt: '2024-03-24T00:00:00Z' },
  { id: 'AS-007', companyId: 'EMP-01', salesPointId: 'PV-002', fullName: 'Leidy Johana Herrera Castaño', dailyLeadCapacity: 18, status: 'active', joinedAt: '2025-08-06T00:00:00Z' },
  { id: 'AS-008', companyId: 'EMP-01', salesPointId: 'PV-002', fullName: 'Cristian Franco Zapata', dailyLeadCapacity: 12, status: 'active', joinedAt: '2025-04-27T00:00:00Z' },
  { id: 'AS-009', companyId: 'EMP-01', salesPointId: 'PV-003', fullName: 'Liliana Muñoz Zapata', dailyLeadCapacity: 18, status: 'active', joinedAt: '2025-06-28T00:00:00Z' },
  { id: 'AS-010', companyId: 'EMP-01', salesPointId: 'PV-003', fullName: 'Paula Andrea Londoño Cardona', dailyLeadCapacity: 18, status: 'active', joinedAt: '2024-04-27T00:00:00Z' },
  { id: 'AS-011', companyId: 'EMP-01', salesPointId: 'PV-003', fullName: 'Sebastián Valencia Cardona', dailyLeadCapacity: 12, status: 'active', joinedAt: '2025-11-28T00:00:00Z' },
  { id: 'AS-012', companyId: 'EMP-01', salesPointId: 'PV-003', fullName: 'Julián Osorio Mosquera', dailyLeadCapacity: 18, status: 'active', joinedAt: '2025-10-18T00:00:00Z' },
  { id: 'AS-013', companyId: 'EMP-01', salesPointId: 'PV-004', fullName: 'Liliana Londoño Bedoya', dailyLeadCapacity: 12, status: 'active', joinedAt: '2024-04-22T00:00:00Z' },
  { id: 'AS-014', companyId: 'EMP-01', salesPointId: 'PV-004', fullName: 'Luz Marina Cardona Mosquera', dailyLeadCapacity: 20, status: 'active', joinedAt: '2024-10-26T00:00:00Z' },
  { id: 'AS-015', companyId: 'EMP-01', salesPointId: 'PV-005', fullName: 'Katherine Vargas Jiménez', dailyLeadCapacity: 25, status: 'active', joinedAt: '2026-04-27T00:00:00Z' },
  { id: 'AS-016', companyId: 'EMP-01', salesPointId: 'PV-005', fullName: 'Leidy Johana Castaño Jiménez', dailyLeadCapacity: 15, status: 'active', joinedAt: '2026-03-28T00:00:00Z' },

  // EMP-02
  { id: 'AS-017', companyId: 'EMP-02', salesPointId: 'PV-006', fullName: 'Julián Zapata Ramírez', dailyLeadCapacity: 15, status: 'active', joinedAt: '2025-09-25T00:00:00Z' },
  { id: 'AS-018', companyId: 'EMP-02', salesPointId: 'PV-006', fullName: 'Erika Muñoz Vargas', dailyLeadCapacity: 20, status: 'active', joinedAt: '2024-02-01T00:00:00Z' },
  { id: 'AS-019', companyId: 'EMP-02', salesPointId: 'PV-007', fullName: 'Alexander Vargas Restrepo', dailyLeadCapacity: 12, status: 'active', joinedAt: '2024-06-15T00:00:00Z' },
  { id: 'AS-020', companyId: 'EMP-02', salesPointId: 'PV-007', fullName: 'Yesenia Salazar Muñoz', dailyLeadCapacity: 12, status: 'active', joinedAt: '2026-01-27T00:00:00Z' },
  { id: 'AS-021', companyId: 'EMP-02', salesPointId: 'PV-008', fullName: 'Nelson Correa Correa', dailyLeadCapacity: 20, status: 'active', joinedAt: '2026-02-21T00:00:00Z' },
  { id: 'AS-022', companyId: 'EMP-02', salesPointId: 'PV-008', fullName: 'Jhon Jairo Vargas Quintero', dailyLeadCapacity: 20, status: 'active', joinedAt: '2024-06-20T00:00:00Z' },
  { id: 'AS-023', companyId: 'EMP-02', salesPointId: 'PV-008', fullName: 'Nelson Vargas Giraldo', dailyLeadCapacity: 20, status: 'active', joinedAt: '2025-01-17T00:00:00Z' },
  { id: 'AS-024', companyId: 'EMP-02', salesPointId: 'PV-009', fullName: 'Sandra Milena Betancur Giraldo', dailyLeadCapacity: 20, status: 'active', joinedAt: '2024-06-24T00:00:00Z' },
  { id: 'AS-025', companyId: 'EMP-02', salesPointId: 'PV-009', fullName: 'Wilmar Quintero Vargas', dailyLeadCapacity: 20, status: 'active', joinedAt: '2025-04-21T00:00:00Z' },
  { id: 'AS-026', companyId: 'EMP-02', salesPointId: 'PV-009', fullName: 'Kevin Cardona Herrera', dailyLeadCapacity: 15, status: 'active', joinedAt: '2024-01-05T00:00:00Z' },
  { id: 'AS-027', companyId: 'EMP-02', salesPointId: 'PV-010', fullName: 'Claudia Patricia Salazar Torres', dailyLeadCapacity: 12, status: 'active', joinedAt: '2024-10-24T00:00:00Z' },
  { id: 'AS-028', companyId: 'EMP-02', salesPointId: 'PV-010', fullName: 'Yuliana Arias Pérez', dailyLeadCapacity: 15, status: 'active', joinedAt: '2026-04-30T00:00:00Z' },

  // EMP-03
  { id: 'AS-029', companyId: 'EMP-03', salesPointId: 'PV-011', fullName: 'Leidy Johana Pérez Torres', dailyLeadCapacity: 15, status: 'active', joinedAt: '2024-07-08T00:00:00Z' },
  { id: 'AS-030', companyId: 'EMP-03', salesPointId: 'PV-011', fullName: 'María Fernanda Restrepo Gómez', dailyLeadCapacity: 15, status: 'active', joinedAt: '2025-04-11T00:00:00Z' },
  { id: 'AS-031', companyId: 'EMP-03', salesPointId: 'PV-011', fullName: 'Paula Andrea Castaño Correa', dailyLeadCapacity: 15, status: 'active', joinedAt: '2025-03-10T00:00:00Z' },
  { id: 'AS-032', companyId: 'EMP-03', salesPointId: 'PV-011', fullName: 'Sandra Milena Salazar Franco', dailyLeadCapacity: 15, status: 'active', joinedAt: '2025-12-29T00:00:00Z' },
  { id: 'AS-033', companyId: 'EMP-03', salesPointId: 'PV-012', fullName: 'Natalia Rodríguez Arias', dailyLeadCapacity: 25, status: 'active', joinedAt: '2026-06-01T00:00:00Z' },
  { id: 'AS-034', companyId: 'EMP-03', salesPointId: 'PV-012', fullName: 'Yuliana Muñoz Marín', dailyLeadCapacity: 18, status: 'active', joinedAt: '2025-11-08T00:00:00Z' },
  { id: 'AS-035', companyId: 'EMP-03', salesPointId: 'PV-012', fullName: 'Cristian Gómez Zapata', dailyLeadCapacity: 25, status: 'active', joinedAt: '2024-03-20T00:00:00Z' },
  { id: 'AS-036', companyId: 'EMP-03', salesPointId: 'PV-012', fullName: 'Julián Arias Osorio', dailyLeadCapacity: 18, status: 'active', joinedAt: '2024-08-12T00:00:00Z' },
  { id: 'AS-037', companyId: 'EMP-03', salesPointId: 'PV-013', fullName: 'Luisa Muñoz Escobar', dailyLeadCapacity: 15, status: 'inactive', joinedAt: '2025-12-05T00:00:00Z' },
  { id: 'AS-038', companyId: 'EMP-03', salesPointId: 'PV-013', fullName: 'Luz Marina Hernández Restrepo', dailyLeadCapacity: 12, status: 'active', joinedAt: '2024-03-09T00:00:00Z' },
  { id: 'AS-039', companyId: 'EMP-03', salesPointId: 'PV-014', fullName: 'Édinson Ospina Arias', dailyLeadCapacity: 20, status: 'active', joinedAt: '2025-06-13T00:00:00Z' },
  { id: 'AS-040', companyId: 'EMP-03', salesPointId: 'PV-014', fullName: 'Marcela Hernández Rodríguez', dailyLeadCapacity: 18, status: 'inactive', joinedAt: '2025-04-19T00:00:00Z' },
  { id: 'AS-041', companyId: 'EMP-03', salesPointId: 'PV-015', fullName: 'Estefanía Escobar Mosquera', dailyLeadCapacity: 25, status: 'active', joinedAt: '2026-05-08T00:00:00Z' },
  { id: 'AS-042', companyId: 'EMP-03', salesPointId: 'PV-015', fullName: 'Adriana Escobar Giraldo', dailyLeadCapacity: 12, status: 'active', joinedAt: '2024-11-12T00:00:00Z' },
]
