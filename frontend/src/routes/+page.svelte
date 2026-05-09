<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/stores/auth';
  import { get } from 'svelte/store';

  onMount(() => {
    goto(get(isAuthenticated) ? '/dashboard' : '/login');
  });
</script>

<div class="grid min-h-screen place-items-center">
  <p class="text-slate-500">Cargando…</p>
</div>
