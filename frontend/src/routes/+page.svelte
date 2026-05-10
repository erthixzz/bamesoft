<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/stores/auth';
  import { get } from 'svelte/store';

  onMount(() => {
    goto(get(isAuthenticated) ? '/dashboard' : '/login');
  });
</script>

<script lang="ts" context="module"></script>

<div class="grid min-h-screen place-items-center">
  <span class="h-10 w-10 animate-spin rounded-full border-[3px] border-slate-200 border-t-brand-600"></span>
</div>
