import { api } from '$lib/api/client';
import type { TecnovigilanciaStage } from '$lib/api/types';
import type {
  BreakdownReport,
  ComplianceReport,
  DashboardKPIs,
  EquipmentReport,
  OperationsReport,
  ProductivityReport,
  ServicesReport,
  TecnovigilanciaReport,
} from './types';

export interface RangeParams {
  date_from?: string;
  date_to?: string;
}

/** Filtros del detalle de servicios (además del rango de fechas). */
export interface ServicesParams extends RangeParams {
  engineer_id?: string;
  equipment_id?: string;
  /** Satisfacción Likert: rango cerrado [min, max] dentro de 1-7. */
  satisfaction_min?: number;
  satisfaction_max?: number;
  tecnovigilancia?: boolean;
}

export const reportsApi = {
  dashboard: () => api.get<DashboardKPIs>('/reports/dashboard'),
  compliance: () => api.get<ComplianceReport>('/reports/compliance'),
  productivity: (params: RangeParams = {}) =>
    api.get<ProductivityReport>('/reports/productivity', params),
  operations: (params: RangeParams = {}) =>
    api.get<OperationsReport>('/reports/operations', params),
  equipment: (params: RangeParams = {}) =>
    api.get<EquipmentReport>('/reports/equipment', params),
  services: (params: ServicesParams = {}) => api.get<ServicesReport>('/reports/services', params),
  breakdown: (params: RangeParams = {}) => api.get<BreakdownReport>('/reports/breakdown', params),
  tecnovigilancia: (params: RangeParams & { stage?: TecnovigilanciaStage } = {}) =>
    api.get<TecnovigilanciaReport>('/reports/tecnovigilancia', params),
};
