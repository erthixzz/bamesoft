import { createClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/public';
import WebSocket from 'ws';

const url = env.PUBLIC_SUPABASE_URL ?? '';
const key = env.PUBLIC_SUPABASE_ANON_KEY ?? '';

export const supabase = createClient(url, key, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
  realtime: {
    transport: WebSocket as any,
  },
});