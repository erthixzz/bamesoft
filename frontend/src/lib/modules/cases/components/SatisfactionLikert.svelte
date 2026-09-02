<script lang="ts">
  /** Escala Likert de 7 puntos para «¿Qué tan satisfecho(a) está con el servicio?».
   *  Reemplaza al selector de 3 caritas: los 7 puntos siempre están a la vista,
   *  con anclas a los extremos y la etiqueta del punto elegido debajo, que es la
   *  forma en la que la gente ya sabe leer una escala de satisfacción.
   *
   *  Móvil primero: los 7 botones son una grilla `grid-cols-7` que se reparte el
   *  ancho disponible, así que entra igual en 320 px que en un escritorio. */
  import { createEventDispatcher } from 'svelte';
  import type { SatisfactionScore } from '$lib/api/types';
  import { SATISFACTION_QUESTION, SATISFACTION_SCALE } from '$lib/modules/cases/ui';

  /** Puntaje seleccionado; `null` = sin calificar. */
  export let value: SatisfactionScore | null = null;
  export let label = SATISFACTION_QUESTION;
  export let required = false;
  export let error: string | null = null;
  export let disabled = false;
  /** Solo lectura: pinta el punto elegido sin permitir cambiarlo. */
  export let readonly = false;

  const dispatch = createEventDispatcher<{ change: SatisfactionScore | null }>();

  function pick(score: SatisfactionScore) {
    if (disabled || readonly) return;
    value = value === score ? null : score; // volver a tocar el mismo lo limpia
    dispatch('change', value);
  }

  $: selected = value ? SATISFACTION_SCALE.find((s) => s.score === value) ?? null : null;
</script>

<div class="block">
  {#if label}
    <span class="mb-2 block text-sm font-medium text-slate-700">
      {label}{#if required}<span class="ml-0.5 font-semibold text-danger-500">*</span>{/if}
    </span>
  {/if}

  <div
    class="grid grid-cols-7 gap-1 sm:gap-1.5"
    role="radiogroup"
    aria-label={label || SATISFACTION_QUESTION}
  >
    {#each SATISFACTION_SCALE as s (s.score)}
      {@const active = value === s.score}
      <button
        type="button"
        {disabled}
        role="radio"
        aria-checked={active}
        aria-label="{s.score} — {s.label}"
        title="{s.score} — {s.label}"
        on:click={() => pick(s.score)}
        class="group flex flex-col items-center gap-1 rounded-xl border-2 px-0.5 py-2 transition
          {active
          ? `${s.tint} ${s.text} shadow-sm`
          : 'border-slate-200 bg-white text-slate-400 hover:border-slate-300 hover:bg-slate-50'}
          {disabled || readonly ? 'cursor-default' : 'cursor-pointer'}"
        style={active ? `border-color:${s.color}` : ''}
      >
        <span class="text-base font-bold leading-none tabular-nums sm:text-lg">{s.score}</span>
        <span
          class="h-1.5 w-full max-w-[26px] rounded-full transition"
          style="background:{active ? s.color : '#e2e8f0'}"
        ></span>
      </button>
    {/each}
  </div>

  <!-- Anclas de los extremos: leen la escala sin tener que abrir nada -->
  <div class="mt-1.5 flex items-start justify-between gap-2 text-[11px] leading-tight text-slate-400">
    <span>1 · Muy insatisfecho</span>
    <span class="text-right">7 · Muy satisfecho</span>
  </div>

  <!-- Punto elegido, en grande y con su color -->
  <div class="mt-2 min-h-[34px]">
    {#if selected}
      <span
        class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-semibold {selected.tint} {selected.text}"
      >
        <span class="grid h-5 w-5 place-items-center rounded-full text-[11px] font-bold text-white" style="background:{selected.color}">
          {selected.score}
        </span>
        {selected.label}
      </span>
    {:else if !readonly}
      <span class="text-xs text-slate-400">Toca un número del 1 al 7 para calificar.</span>
    {:else}
      <span class="value-pending text-xs">Sin calificar</span>
    {/if}
  </div>

  {#if error}
    <p class="mt-1 text-xs text-danger-600">{error}</p>
  {/if}
</div>
