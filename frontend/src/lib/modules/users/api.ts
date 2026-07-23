import { api } from '$lib/api/client';
import type { SignedUrl } from '$lib/modules/documents/types';
import type { User, UserCreate, UserInvite, UserUpdate } from './types';

export const usersApi = {
  list: (q?: string) => api.get<User[]>('/users', q ? { q } : undefined),
  get: (id: string) => api.get<User>(`/users/${id}`),
  me: () => api.get<User>('/users/me'),
  create: (payload: UserCreate) => api.post<User>('/users', payload),
  invite: (payload: UserInvite) => api.post<User>('/users/invite', payload),
  update: (id: string, payload: UserUpdate) => api.patch<User>(`/users/${id}`, payload),
  deactivate: (id: string) => api.delete<void>(`/users/${id}`),
  /** Sube (o reemplaza) la hoja de vida (CV) del usuario. */
  uploadCv: (id: string, file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return api.upload<User>(`/users/${id}/cv`, fd);
  },
  cvUrl: (id: string, expiresIn = 3600) =>
    api.get<SignedUrl>(`/users/${id}/cv-url`, { expires_in: expiresIn }),
};
