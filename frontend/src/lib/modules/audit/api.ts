import { api } from '$lib/api/client';
import type { AuditActor, AuditPage, AuditSummary } from './types';

export interface AuditParams {
  from?: string;
  to?: string;
  /** Filtra por quién lo hizo. */
  actor_id?: string;
  /** Filtra por módulo: cases, equipment, users… */
  entity?: string;
  /** Filtra por operación: POST (creó), PATCH/PUT (actualizó), DELETE (eliminó). */
  method?: string;
  /** Búsqueda libre sobre persona, acción, detalle o código del registro. */
  q?: string;
  limit?: number;
  offset?: number;
}

export const auditApi = {
  /** Devuelve la página de resultados junto al total que cumple el filtro. */
  logs: (params: AuditParams = {}) => api.get<AuditPage>('/audit/logs', params),
  /** Personas que aparecen en la bitácora, para poblar el desplegable. */
  actors: () => api.get<AuditActor[]>('/audit/actors'),
  summary: (params: Pick<AuditParams, 'from' | 'to'> = {}) =>
    api.get<AuditSummary>('/audit/summary', params),
};
