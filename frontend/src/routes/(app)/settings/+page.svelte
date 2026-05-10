<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { profile, logout } from '$lib/stores/auth';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { setPageTitle } from '$lib/stores/page';
  import { Settings, Mail, Building2, ShieldCheck, LogOut } from 'lucide-svelte';

  onMount(() => setPageTitle('Ajustes'));

  function doLogout(e: MouseEvent) {
    e.preventDefault();
    logout();
  }
</script>

<PageHeader title="Ajustes" subtitle="Tu cuenta y preferencias" icon={Settings} gradient="brand" />

<div class="grid gap-4 lg:grid-cols-3">
  <div class="lg:col-span-2">
    <Card title="Perfil">
      {#if $profile}
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start">
          <div class="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-brand-600 to-cyan-500 text-2xl font-bold text-white shadow-md">
            {$profile.full_name.charAt(0).toUpperCase()}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-lg font-semibold text-slate-900">{$profile.full_name}</p>
            <p class="text-sm text-slate-500">{ROLE_LABELS[$profile.role]}</p>
            <dl class="mt-4 grid gap-3 sm:grid-cols-2">
              <div>
                <dt class="flex items-center gap-2 text-xs uppercase tracking-wider text-slate-500">
                  <Mail class="h-3.5 w-3.5" /> Email
                </dt>
                <dd class="truncate text-sm text-slate-700">{$profile.email}</dd>
              </div>
              <div>
                <dt class="flex items-center gap-2 text-xs uppercase tracking-wider text-slate-500">
                  <Building2 class="h-3.5 w-3.5" /> Clínica
                </dt>
                <dd class="truncate text-sm text-slate-700">{$profile.clinic_name ?? '—'}</dd>
              </div>
              <div>
                <dt class="flex items-center gap-2 text-xs uppercase tracking-wider text-slate-500">
                  <ShieldCheck class="h-3.5 w-3.5" /> Rol
                </dt>
                <dd class="text-sm text-slate-700">{ROLE_LABELS[$profile.role]}</dd>
              </div>
              <div>
                <dt class="flex items-center gap-2 text-xs uppercase tracking-wider text-slate-500">Estado</dt>
                <dd><span class="badge bg-emerald-100 text-emerald-700">Activo</span></dd>
              </div>
            </dl>
          </div>
        </div>
      {/if}
    </Card>
  </div>

  <Card title="Sesión">
    <p class="text-sm text-slate-600">
      Cerrar sesión limpia los datos en este dispositivo. Tendrás que volver a entrar con tu email y contraseña.
    </p>
    <a href="/login" on:click={doLogout} class="btn-danger mt-4 inline-flex">
      <LogOut class="h-4 w-4" /> Cerrar sesión
    </a>
  </Card>
</div>
