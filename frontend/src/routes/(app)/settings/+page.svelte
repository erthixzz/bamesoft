<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { profile } from '$lib/stores/auth';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { setPageTitle } from '$lib/stores/page';

  onMount(() => setPageTitle('Ajustes'));
</script>

<Card title="Perfil">
  {#if $profile}
    <dl class="grid grid-cols-2 gap-y-2 text-sm">
      <dt class="text-slate-500">Nombre</dt><dd>{$profile.full_name}</dd>
      <dt class="text-slate-500">Email</dt><dd>{$profile.email}</dd>
      <dt class="text-slate-500">Rol</dt><dd>{ROLE_LABELS[$profile.role]}</dd>
    </dl>
  {/if}
</Card>
