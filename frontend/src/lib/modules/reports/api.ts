import { api } from '$lib/api/client';
import type { ComplianceReport, DashboardKPIs } from './types';

export const reportsApi = {
  dashboard: () => api.get<DashboardKPIs>('/reports/dashboard'),
  compliance: () => api.get<ComplianceReport>('/reports/compliance'),
};
