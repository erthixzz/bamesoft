export interface AuditLog {
  id: string;
  actor_id?: string | null;
  actor_name?: string | null;
  actor_role?: string | null;
  method: string;
  action: string;
  entity?: string | null;
  entity_id?: string | null;
  status_code?: number | null;
  created_at: string;
}

export interface CountRow {
  key: string;
  label: string;
  count: number;
}

export interface DayCount {
  day: string;
  count: number;
}

export interface AuditSummary {
  total: number;
  actors: number;
  by_actor: CountRow[];
  by_action: CountRow[];
  by_entity: CountRow[];
  by_day: DayCount[];
}
