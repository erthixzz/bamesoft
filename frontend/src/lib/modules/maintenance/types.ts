export interface MaintenanceSchedule {
  id: string;
  equipment_id: string;
  name: string;
  description?: string | null;
  frequency_days: number;
  last_done_at?: string | null;
  next_due_at?: string | null;
  created_at: string;
  updated_at: string;
}
