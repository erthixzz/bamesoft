import { api } from '$lib/api/client';
import type { CaseStatus } from '$lib/api/types';
import type { Case, CaseActivity, CaseCreate, CaseUpdate } from './types';

export interface ListParams {
  status?: CaseStatus;
  assigned_to?: string;
  equipment_id?: string;
  limit?: number;
  offset?: number;
}

export const casesApi = {
  list: (params: ListParams = {}) => api.get<Case[]>('/cases', params),
  get: (id: string) => api.get<Case>(`/cases/${id}`),
  create: (payload: CaseCreate) => api.post<Case>('/cases', payload),
  update: (id: string, payload: CaseUpdate) => api.patch<Case>(`/cases/${id}`, payload),
  activities: (id: string) => api.get<CaseActivity[]>(`/cases/${id}/activities`),
  addActivity: (id: string, action: string, notes?: string) =>
    api.post<CaseActivity>(`/cases/${id}/activities`, { action, notes }),
};
