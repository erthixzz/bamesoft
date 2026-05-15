import { createClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/public';

const url = env.PUBLIC_SUPABASE_URL ?? '';
const key = env.PUBLIC_SUPABASE_ANON_KEY ?? '';

/**
 * En SSR (Vercel), Supabase Realtime necesita WebSocket global.
 * Node 20 en serverless no lo trae; en Node 22 sí. Usa `engines.node` 22.x y en Vercel
 * Project Settings → Node.js Version → 22.x si hiciera falta.
 */
export const supabase = createClient(url, key, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
