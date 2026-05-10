<script lang="ts">
  import AuthBackdrop from '$lib/components/AuthBackdrop.svelte';
</script>

<div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-white via-slate-50 to-brand-50/40">
  <AuthBackdrop />

  <!-- Contenido encima del backdrop -->
  <div class="relative z-10 flex min-h-screen flex-col">
    <main class="flex flex-1 items-center justify-center px-4 py-10">
      <slot />
    </main>

    <footer class="relative z-10 px-6 py-4 text-center text-xs text-slate-500">
      Powered by
      <span class="font-semibold text-slate-700">Bamesoft Solutions</span>
      &nbsp;·&nbsp;
      <a class="hover:text-brand-700 hover:underline" href="#">Términos</a>
      &nbsp;·&nbsp;
      <a class="hover:text-brand-700 hover:underline" href="#">Privacidad</a>
    </footer>
  </div>
</div>
