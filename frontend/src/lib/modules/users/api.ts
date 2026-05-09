import { api } from '$lib/api/client';
import type { User, UserCreate, UserUpdate } from './types';

export const usersApi = {
  list: () => api.get<User[]>('/users'),
  get: (id: string) => api.get<User>(`/users/${id}`),
  me: () => api.get<User>('/users/me'),
  create: (payload: UserCreate) => api.post<User>('/users', payload),
  update: (id: string, payload: UserUpdate) => api.patch<User>(`/users/${id}`, payload),
  deactivate: (id: string) => api.delete<void>(`/users/${id}`),
};
