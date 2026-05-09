import { api } from '$lib/api/client';
import type { DocumentType } from '$lib/api/types';
import type { Doc, SignedUrl } from './types';

export const documentsApi = {
  upload: (file: File, meta: { title: string; type: DocumentType; equipment_id?: string; case_id?: string; clinic_id?: string }) => {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('title', meta.title);
    fd.append('type', meta.type);
    if (meta.equipment_id) fd.append('equipment_id', meta.equipment_id);
    if (meta.case_id) fd.append('case_id', meta.case_id);
    if (meta.clinic_id) fd.append('clinic_id', meta.clinic_id);
    return api.upload<Doc>('/documents', fd);
  },
  forEquipment: (equipmentId: string) =>
    api.get<Doc[]>(`/documents/equipment/${equipmentId}`),
  forCase: (caseId: string) => api.get<Doc[]>(`/documents/case/${caseId}`),
  signedUrl: (docId: string, expiresIn = 3600) =>
    api.get<SignedUrl>(`/documents/${docId}/signed-url`, { expires_in: expiresIn }),
};
