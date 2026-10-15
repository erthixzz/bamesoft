<script lang="ts">
  /**
   * Cambio de contraseña obligatorio en el primer acceso.
   *
   * Las cuentas nuevas nacen con una contraseña provisional que el
   * administrador dicta en voz alta. Mientras `must_change_password` siga en
   * alto, el layout de la aplicación redirige aquí: no se puede usar nada hasta
   * elegir una propia.
   *
   * Vive en `(auth)` y no en `(app)` a propósito: aquí no hay sidebar ni guardia
   * de capacidades, así que no hay forma de dar un rodeo por otra ruta.
   */
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import BrandMark from '$lib/components/BrandMark.svelte';
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import { usersApi } from '$lib/modules/users/api';
  import { DEFAULT_PASSWORD, MIN_PASSWORD_LENGTH } from '$lib/modules/users/constants';
  import { isAuthenticated, logout, profile } from '$lib/stores/auth';
  import { toasts } from '$lib/stores/toasts';
  import { KeyRound, LogOut, ShieldCheck } from 'lucide-svelte';

  let pwd = '';
  let confirmPwd = '';
  let saving = false;
  let errors: Record<string, string> = {};

  onMount(() => {
    if (!$isAuthenticated) goto('/login');
  });

  function validate(): boolean {
    const e: Record<string, string> = {};
    if (pwd.length < MIN_PASSWORD_LENGTH) e.pwd = `Mínimo ${MIN_PASSWORD_LENGTH} caracteres`;
    else if (pwd === DEFAULT_PASSWORD) e.pwd = 'Elige una distinta de la provisional';
    if (confirmPwd !== pwd) e.confirmPwd = 'Las contraseñas no coinciden';
    errors = e;
    return Object.keys(e).length === 0;
  }

  async function save() {
    if (!validate()) return;
    saving = true;
    try {
      const updated = await usersApi.changePassword(pwd);
      profile.update((p) => (p ? { ...p, must_change_password: updated.must_change_password } : p));
      toasts.success('Contraseña actualizada. ¡Bienvenido!');
      goto('/dashboard');
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'No se pudo cambiar la contraseña');
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head><title>Cambia tu contraseña · Bamesoft</title></svelte:head>

<section class="w-full max-w-md" in:fly={{ y: 24, duration: 600, easing: cubicOut }}>
  <div
    class="relative rounded-2xl border border-white/60 bg-white/70 p-6 shadow-xl shadow-slate-900/5 backdrop-blur-xl sm:p-8"
  >
    <div
      class="pointer-events-none absolute -inset-px -z-10 rounded-2xl bg-gradient-to-br from-brand-500/30 via-cyan-400/20 to-emerald-400/20 opacity-50 blur-xl"
    ></div>

    <div class="mb-5 flex items-center gap-3">
      <div class="rounded-xl shadow-lg">
        <BrandMark size={40} />
      </div>
      <div>
        <h1 class="text-lg font-bold tracking-tight text-slate-900">Cambia tu contraseña</h1>
        <p class="text-sm text-slate-500">
          {$profile?.full_name ?? 'Tu cuenta'} · primer acceso
        </p>
      </div>
    </div>

    <p
      class="mb-5 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5 text-xs leading-relaxed text-amber-800"
    >
      <KeyRound class="mt-0.5 h-4 w-4 shrink-0" />
      <span>
        Entraste con la contraseña provisional. Elige una propia para continuar;
        nadie más debería conocerla.
      </span>
    </p>

    <form class="grid gap-3" on:submit|preventDefault={save}>
      <Input
        label="Nueva contraseña *"
        type="password"
        bind:value={pwd}
        error={errors.pwd}
        placeholder={`Mínimo ${MIN_PASSWORD_LENGTH} caracteres`}
      />
      <Input
        label="Repite la contraseña *"
        type="password"
        bind:value={confirmPwd}
        error={errors.confirmPwd}
        placeholder="La misma, otra vez"
      />
      <Button type="submit" loading={saving}>
        <ShieldCheck class="h-4 w-4" /> Guardar y entrar
      </Button>
    </form>

    <button
      type="button"
      class="mx-auto mt-5 flex items-center gap-1.5 text-xs font-medium text-slate-500 transition hover:text-danger-600"
      on:click={logout}
    >
      <LogOut class="h-3.5 w-3.5" /> Cerrar sesión
    </button>
  </div>
</section>
