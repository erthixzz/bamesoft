import adapter from '@sveltejs/adapter-vercel';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/**
 * Origen de una URL de entorno, o null si no está definida / es inválida.
 * Se usa para que la CSP permita exactamente la API y el Supabase configurados,
 * en vez de abrir `connect-src` a cualquier destino.
 */
function origin(value) {
  try {
    return value ? new URL(value).origin : null;
  } catch {
    return null;
  }
}

const apiOrigin = origin(process.env.PUBLIC_API_URL);
const supabaseOrigin = origin(process.env.PUBLIC_SUPABASE_URL);
// Supabase Realtime usa WebSocket sobre el mismo host.
const supabaseWs = supabaseOrigin ? supabaseOrigin.replace(/^https:/, 'wss:') : null;

const connectSrc = [
  'self',
  apiOrigin,
  supabaseOrigin,
  supabaseWs,
  // Red de seguridad para previews donde las variables aún no están fijadas.
  'https://*.supabase.co',
  'wss://*.supabase.co',
].filter(Boolean);

// La API sirve imágenes, no solo JSON: el PNG del QR de cada equipo se carga
// con <img src="{API}/public/equipment/{code}/qr.png">. Sin este origen en
// `img-src` el navegador lo bloquea y el QR sale roto.
const imgSrc = [
  'self',
  'data:',
  // PDFs y descargas generadas en el cliente.
  'blob:',
  apiOrigin,
  supabaseOrigin,
  // URLs firmadas de fotos y documentos.
  'https://*.supabase.co',
].filter(Boolean);

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),

  kit: {
    adapter: adapter({
      // Node 22: WebSocket global para Supabase Realtime en SSR. Requiere explícito; sin esto el adaptador solo acepta 18/20 al hacer build.
      runtime: 'nodejs22.x',
    }),

    /**
     * Content-Security-Policy. `mode: 'auto'` deja que SvelteKit añada
     * nonces/hashes a sus propios scripts inline, así `script-src` no necesita
     * 'unsafe-inline' (que es lo que haría inútil la CSP frente a XSS).
     *
     * `style-src` sí lo lleva: Tailwind y los estilos scoped de Svelte inyectan
     * CSS inline y sin él la app se ve rota.
     *
     * Las demás cabeceras de seguridad están en `src/hooks.server.ts`.
     */
    csp: {
      mode: 'auto',
      directives: {
        'default-src': ['self'],
        'script-src': ['self'],
        // Google Fonts (hoja de estilos) + estilos inline de Svelte/Tailwind.
        'style-src': ['self', 'unsafe-inline', 'https://fonts.googleapis.com'],
        'font-src': ['self', 'data:', 'https://fonts.gstatic.com'],
        'img-src': imgSrc,
        'connect-src': connectSrc,
        'object-src': ['none'],
        'base-uri': ['self'],
        'form-action': ['self'],
        'frame-ancestors': ['none'],
      },
    },

    alias: {
      $lib: './src/lib',
      '$lib/*': './src/lib/*'
    }
  }
};

export default config;
