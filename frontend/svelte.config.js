import adapter from '@sveltejs/adapter-vercel';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),

  kit: {
    adapter: adapter({
      // Node 22: WebSocket global para Supabase Realtime en SSR. Requiere explícito; sin esto el adaptador solo acepta 18/20 al hacer build.
      runtime: 'nodejs22.x',
    }),

    alias: {
      $lib: './src/lib',
      '$lib/*': './src/lib/*'
    }
  }
};

export default config;