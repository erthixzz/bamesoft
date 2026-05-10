<script lang="ts">
  // No hacemos goto aquí: dejamos que sea el formulario de login el que
  // navegue tras autenticación correcta. Esto evita loops cuando ambos
  // layouts compiten por redirigir.
</script>

<div class="grid min-h-screen place-items-center bg-gradient-to-br from-brand-50 to-slate-100 p-4">
  <div class="w-full max-w-md">
    <div class="mb-6 flex items-center justify-center gap-3">
      <div class="grid h-12 w-12 place-items-center rounded-xl bg-brand-600 text-2xl font-bold text-white">
        B
      </div>
      <div>
        <p class="text-2xl font-bold text-slate-900">Bamesoft</p>
        <p class="text-sm text-slate-500">Biomedical Engineering Suite</p>
      </div>
    </div>
    <slot />
  </div>
</div>
