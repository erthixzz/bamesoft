<script lang="ts">
  /** Portón del QR. Escanear un equipo NO da acceso directo: siempre exige
   *  sesión. Si hay login → lleva al detalle protegido (con aislamiento por
   *  clínica). Si no → manda al login y regresa aquí tras autenticarse. */
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabase';
  import { ShieldCheck } from 'lucide-svelte';

  onMount(async () => {
    const code = $page.params.code ?? '';
    const target = `/equipment/${encodeURIComponent(code)}`;
    const { data } = await supabase.auth.getSession();
    if (data.session) {
      goto(target, { replaceState: true });
    } else {
      goto(`/login?next=${encodeURIComponent(target)}`, { replaceState: true });
    }
  });
</script>

<svelte:head>
  <title>Acceso seguro — Bamesoft</title>
  <meta name="robots" content="noindex" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
</svelte:head>

<div class="grid min-h-screen place-items-center bg-gradient-to-b from-slate-50 via-white to-slate-100 px-6">
  <div class="flex flex-col items-center gap-4 text-center">
    <img src="/logo.png" alt="Bamesoft" class="h-14 w-14 object-contain" />
    <div class="flex items-center gap-2 text-sm font-medium text-slate-600">
      <span class="h-4 w-4 animate-spin rounded-full border-2 border-slate-200 border-t-brand-600"></span>
      Verificando acceso seguro…
    </div>
    <p class="flex items-center gap-1.5 text-xs text-slate-400">
      <ShieldCheck class="h-3.5 w-3.5 text-emerald-600" />
      Este equipo requiere iniciar sesión
    </p>
  </div>
</div>
