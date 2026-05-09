<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { isAuthenticated, profile } from '$lib/stores/auth';
  import { authApi } from '$lib/modules/auth/api';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Header from '$lib/components/Header.svelte';

  onMount(async () => {
    if (!get(isAuthenticated)) {
      goto('/login');
      return;
    }
    if (!get(profile)) {
      try {
        const p = await authApi.whoami();
        profile.set(p);
      } catch {
        goto('/login');
      }
    }
  });
</script>

<div class="flex min-h-screen">
  <Sidebar />
  <div class="flex w-full min-w-0 flex-col">
    <Header />
    <main class="min-w-0 flex-1 overflow-x-hidden p-6">
      <slot />
    </main>
  </div>
</div>
