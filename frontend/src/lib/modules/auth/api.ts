import { api } from '$lib/api/client';
import type { Profile } from '$lib/stores/auth';

export const authApi = {
  whoami: () => api.get<Profile>('/auth/whoami'),
};
