import { api } from '$lib/api/client';
import type { AuditLog, AuditSummary } from './types';

export interface AuditParams {
  from?: string;
  to?: string;
  actor_id?: string;
  entity?: string;
  limit?: number;
  offset?: number;
}

export const auditApi = {
  logs: (params: AuditParams = {}) => api.get<AuditLog[]>('/audit/logs', params),
  summary: (params: Pick<AuditParams, 'from' | 'to'> = {}) =>
    api.get<AuditSummary>('/audit/summary', params),
};
