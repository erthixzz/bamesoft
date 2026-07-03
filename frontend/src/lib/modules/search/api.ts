import { api } from '$lib/api/client';
import type { SearchOut } from './types';

export const searchApi = {
  global: (q: string) => api.get<SearchOut>('/search', { q }),
};
