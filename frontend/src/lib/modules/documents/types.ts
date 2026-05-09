import type { DocumentType } from '$lib/api/types';

export interface Doc {
  id: string;
  title: string;
  type: DocumentType;
  storage_path: string;
  mime_type: string;
  size_bytes: number;
  clinic_id?: string | null;
  equipment_id?: string | null;
  case_id?: string | null;
  uploaded_by?: string | null;
  created_at: string;
}

export interface SignedUrl {
  url: string;
  expires_in: number;
}
