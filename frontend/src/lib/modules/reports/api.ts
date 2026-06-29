import { api } from '$lib/api/client';
import type {
  ComplianceReport,
  DashboardKPIs,
  OperationsReport,
  ProductivityReport,
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
};
