<script lang="ts">
  import { profile, logout } from '$lib/stores/auth';
  import { pageTitle } from '$lib/stores/page';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { LogOut } from 'lucide-svelte';
</script>

<header class="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
  <h1 class="text-base font-semibold text-slate-900">{$pageTitle}</h1>
  <div class="flex items-center gap-4">
    {#if $profile}
      <div class="text-right">
        <p class="text-sm font-medium leading-tight">{$profile.full_name}</p>
        <p class="text-xs text-slate-500">{ROLE_LABELS[$profile.role]}</p>
      </div>
      <div
        class="grid h-9 w-9 place-items-center rounded-full bg-brand-600 font-semibold text-white"
      >
        {$profile.full_name.charAt(0).toUpperCase()}
      </div>
      <button
        class="text-slate-400 hover:text-slate-700"
        title="Salir"
        on:click={() => logout()}
      >
        <LogOut class="h-5 w-5" />
      </button>
    {/if}
  </div>
</header>
