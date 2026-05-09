<script lang="ts">
  import { goto } from '$app/navigation';
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import { login } from '$lib/stores/auth';
  import { toasts } from '$lib/stores/toasts';

  let email = '';
  let password = '';
  let loading = false;
  let error: string | null = null;

  async function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    error = null;
    try {
      await login(email, password);
      toasts.success('Bienvenido');
      goto('/dashboard');
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error al iniciar sesión';
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit={onSubmit} class="card space-y-4">
  <header>
    <h2 class="text-lg font-semibold text-slate-900">Iniciar sesión</h2>
    <p class="text-sm text-slate-500">Accede con tu cuenta corporativa.</p>
  </header>

  <Input label="Email" type="email" bind:value={email} required />
  <Input label="Contraseña" type="password" bind:value={password} required />

  {#if error}
    <p class="text-sm text-danger-600">{error}</p>
  {/if}

  <Button type="submit" {loading}>Entrar</Button>
</form>
