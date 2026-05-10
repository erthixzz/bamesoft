<script lang="ts">
  import { profile, logout } from '$lib/stores/auth';
  import { pageTitle } from '$lib/stores/page';
  import { toggleSidebar } from '$lib/stores/sidebar';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { Building2, LogOut, Menu } from 'lucide-svelte';
</script>

<header class="flex h-16 items-center justify-between gap-2 border-b border-slate-200 bg-white px-3 sm:px-6">
  <div class="flex min-w-0 items-center gap-2 sm:gap-3">
    <button
      class="grid h-9 w-9 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 md:hidden"
      on:click={toggleSidebar}
      aria-label="Abrir menú"
    >
      <Menu class="h-5 w-5" />
    </button>
    <h1 class="truncate text-sm font-semibold text-slate-900 sm:text-base">{$pageTitle}</h1>
  </div>

  <div class="flex shrink-0 items-center gap-2 sm:gap-4">
    {#if $profile?.clinic_name}
      <div class="hidden items-center gap-2 rounded-lg bg-slate-100 px-3 py-1.5 lg:flex">
        <Building2 class="h-4 w-4 text-slate-500" />
        <span class="max-w-[200px] truncate text-sm font-medium text-slate-700">{$profile.clinic_name}</span>
      </div>
    {/if}
    {#if $profile}
      <div class="hidden text-right sm:block">
        <p class="max-w-[160px] truncate text-sm font-medium leading-tight">{$profile.full_name}</p>
        <p class="text-xs text-slate-500">{ROLE_LABELS[$profile.role]}</p>
      </div>
      <div
        class="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-600 to-cyan-500 font-semibold text-white"
        title={`${$profile.full_name}${$profile.clinic_name ? ' · ' + $profile.clinic_name : ''}`}
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
