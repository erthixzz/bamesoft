import type { AlertSeverity, AlertType } from '$lib/api/types';

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  equipment_id?: string | null;
  case_id?: string | null;
  due_at?: string | null;
  acknowledged_at?: string | null;
  resolved_at?: string | null;
  created_at: string;
}
