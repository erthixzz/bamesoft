import { writable, derived, get } from 'svelte/store';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '$lib/supabase';
import type { UserRole } from '$lib/api/types';

export interface Profile {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  active: boolean;
  avatar_url?: string | null;
  clinic_id?: string | null;
  clinic_name?: string | null;
}

export const session = writable<Session | null>(null);
export const profile = writable<Profile | null>(null);

export const isAuthenticated = derived(session, ($s) => !!$s?.access_token);
export const role = derived(profile, ($p) => $p?.role ?? null);

let initialized = false;

export async function initAuth(): Promise<void> {
  if (initialized) return;
  initialized = true;

  const { data } = await supabase.auth.getSession();
  session.set(data.session);

  supabase.auth.onAuthStateChange((_event, newSession) => {
    session.set(newSession);
    if (!newSession) profile.set(null);
  });
}

/**
 * Inicia sesión contra Supabase Auth.
 *
 * `captchaToken` es obligatorio cuando la protección CAPTCHA está activa en el
 * proyecto (Settings → Authentication → Bot and Abuse Protection). Se envía
 * solo si existe, para que el login siga funcionando en entornos donde esa
 * protección está apagada.
 */
export async function login(
  email: string,
  password: string,
  captchaToken?: string | null,
): Promise<void> {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
    ...(captchaToken ? { options: { captchaToken } } : {}),
  });
  if (error) throw error;
  // Setear el store sincrónicamente para evitar race con el listener async.
  if (data.session) session.set(data.session);
}

export async function logout(): Promise<void> {
  await supabase.auth.signOut();
  profile.set(null);
  session.set(null);
  // Forzamos un hard reload a /login para limpiar cualquier estado en memoria.
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

export function currentToken(): string | undefined {
  return get(session)?.access_token;
}
