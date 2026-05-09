<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { initAuth } from '$lib/stores/auth';
  import Toasts from '$lib/components/Toasts.svelte';

  onMount(() => {
    initAuth();
  });
</script>

<Toasts />
<slot />
