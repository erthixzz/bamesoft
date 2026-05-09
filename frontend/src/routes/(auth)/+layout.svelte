<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/stores/auth';
  import { get } from 'svelte/store';

  onMount(() => {
    if (get(isAuthenticated)) goto('/dashboard');
  });
</script>

<div class="grid min-h-screen place-items-center bg-gradient-to-br from-brand-50 to-slate-100 p-4">
  <div class="w-full max-w-md">
    <div class="mb-6 flex items-center justify-center gap-3">
      <div class="grid h-12 w-12 place-items-center rounded-xl bg-brand-600 text-2xl font-bold text-white">
        B
      </div>
      <div>
        <p class="text-2xl font-bold text-slate-900">Bamesoft</p>
        <p class="text-sm text-slate-500">Biomedical Engineering Suite</p>
      </div>
    </div>
    <slot />
  </div>
</div>
