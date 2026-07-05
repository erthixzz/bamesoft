import { api } from '$lib/api/client';
import type {
  BreakdownReport,
  ComplianceReport,
  DashboardKPIs,
  EquipmentReport,
  OperationsReport,
  ProductivityReport,
  ServicesReport,
} from './types';

export interface RangeParams {
  date_from?: string;
  date_to?: string;
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
  services: (params: RangeParams & { engineer_id?: string; equipment_id?: string } = {}) =>
    api.get<ServicesReport>('/reports/services', params),
  breakdown: (params: RangeParams = {}) => api.get<BreakdownReport>('/reports/breakdown', params),
};
