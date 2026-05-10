<script lang="ts">
  // Fondo sutil para el área de app: glows tenues + cuadrícula suave.
  // Mucho más calmado que AuthBackdrop para no distraer mientras se trabaja.
</script>

<div class="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
  <div class="absolute -left-40 -top-40 h-[420px] w-[420px] rounded-full bg-brand-200/30 blur-3xl"></div>
  <div class="absolute -bottom-40 -right-40 h-[480px] w-[480px] rounded-full bg-cyan-200/30 blur-3xl"></div>
  <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(15,23,42,.025)_1px,transparent_1px),linear-gradient(to_bottom,rgba(15,23,42,.025)_1px,transparent_1px)] bg-[size:64px_64px]"></div>
</div>
