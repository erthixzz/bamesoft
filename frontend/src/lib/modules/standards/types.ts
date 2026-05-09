export interface Standard {
  id: string;
  code: string;
  name: string;
  issuer?: string | null;
  version?: string | null;
  description?: string | null;
  document_id?: string | null;
  created_at: string;
}
