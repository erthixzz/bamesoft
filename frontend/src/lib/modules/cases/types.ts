import type { CasePriority, CaseStatus, CaseType } from '$lib/api/types';

export interface Case {
  id: string;
  code: string;
  title: string;
  description?: string | null;
  type: CaseType;
  status: CaseStatus;
  priority: CasePriority;
  equipment_id: string;
  sector_id?: string | null;
  reported_by?: string | null;
  assigned_to?: string | null;
  opened_at?: string | null;
  closed_at?: string | null;
  sla_due_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CaseCreate {
  title: string;
  description?: string;
  type: CaseType;
  priority?: CasePriority;
  equipment_id: string;
  sector_id?: string;
  assigned_to?: string;
  sla_due_at?: string;
}

export interface CaseUpdate {
  title?: string;
  description?: string;
  priority?: CasePriority;
  status?: CaseStatus;
  assigned_to?: string;
  sla_due_at?: string;
}

export interface CaseActivity {
  id: string;
  case_id: string;
  author_id: string | null;
  action: string;
  notes: string | null;
  created_at: string;
}
