<script lang="ts">
  /** Marca un caso YA CREADO como evento de tecnovigilancia.
   *
   *  Tecnovigilancia = el paciente (o el operador) sufrió, o pudo sufrir, un
   *  daño relacionado con el dispositivo. El modal se resuelve en tres pasos
   *  visibles de una sola pantalla: ¿lo es? → ¿en qué etapa va? → ¿qué pasó?
   *  Al desmarcar se limpian etapa y descripción. */
  import { createEventDispatcher } from 'svelte';
  import { ShieldAlert, Check, Trash2 } from 'lucide-svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Button from '$lib/components/Button.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case } from '$lib/modules/cases/types';
  import type { TecnovigilanciaStage } from '$lib/api/types';
  import {
    TECNOVIGILANCIA_STAGE_META,
    TECNOVIGILANCIA_STAGE_ORDER,
  } from '$lib/modules/cases/ui';
  import { toasts } from '$lib/stores/toasts';

  export let open = false;
  export let value: Case | null = null;

  const dispatch = createEventDispatcher<{ saved: Case; close: void }>();

  let isTecno = false;
  let stage: TecnovigilanciaStage | null = null;
  let description = '';
  let saving = false;
  let stageError = '';

  // Rellena el formulario al abrir, sin pisar lo que el usuario ya escribió.
  let hydratedId = '';
  $: if (open && value) hydrate(value);

  function hydrate(c: Case) {
    if (hydratedId === c.id) return;
    hydratedId = c.id;
    isTecno = c.is_tecnovigilancia;
    stage = c.tecnovigilancia_stage ?? null;
    description = c.tecnovigilancia_description ?? '';
    stageError = '';
  }

  function close() {
    hydratedId = '';
    open = false;
    dispatch('close');
  }

  function setTecno(v: boolean) {
    isTecno = v;
    stageError = '';
    if (v && !stage) stage = 'detection'; // arranque razonable: recién detectado
  }

  async function save() {
    if (!value) return;
    if (isTecno && !stage) {
      stageError = 'Selecciona la etapa del proceso.';
      return;
    }
    saving = true;
    try {
      const updated = await casesApi.setTecnovigilancia(value.id, {
        is_tecnovigilancia: isTecno,
        stage: isTecno ? stage : null,
        description: isTecno ? description.trim() || null : null,
      });
      toasts.success(
        isTecno
          ? `Caso ${updated.code} marcado como tecnovigilancia`
          : `Caso ${updated.code} ya no es de tecnovigilancia`,
      );
      hydratedId = '';
      open = false;
      dispatch('saved', updated);
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar');
    } finally {
      saving = false;
    }
  }
</script>

<Modal
  {open}
  title={value ? `Tecnovigilancia · ${value.code}` : 'Tecnovigilancia'}
  size="lg"
  on:close={close}
>
  {#if value}
    <!-- Qué es, en una frase: nadie debería tener que adivinarlo -->
    <div class="mb-4 flex gap-3 rounded-xl border border-amber-200 bg-amber-50 px-3.5 py-3">
      <ShieldAlert class="h-5 w-5 shrink-0 text-amber-600" />
      <p class="text-xs leading-relaxed text-amber-800">
        Un caso es de <strong>tecnovigilancia</strong> cuando el equipo causó —o pudo causar— un
        <strong>daño al paciente o al operador</strong>. Marcarlo aquí lo hace visible en Reportes
        para su reporte y seguimiento.
      </p>
    </div>

    <!-- Paso 1 · ¿Es o no es? -->
    <span class="mb-2 block text-sm font-medium text-slate-700">
      ¿Este caso es de tecnovigilancia?
    </span>
    <div class="grid grid-cols-2 gap-2">
      <button
        type="button"
        aria-pressed={isTecno}
        on:click={() => setTecno(true)}
        class="rounded-xl border-2 px-3 py-3 text-left transition
          {isTecno
          ? 'border-danger-500 bg-danger-50 text-danger-800 shadow-sm'
          : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-50'}"
      >
        <span class="flex items-center gap-2 text-sm font-semibold">
          <ShieldAlert class="h-4 w-4" /> Sí, hubo o pudo haber daño
        </span>
        <span class="mt-0.5 block text-xs opacity-80">Se hace seguimiento como evento adverso.</span>
      </button>
      <button
        type="button"
        aria-pressed={!isTecno}
        on:click={() => setTecno(false)}
        class="rounded-xl border-2 px-3 py-3 text-left transition
          {!isTecno
          ? 'border-slate-400 bg-slate-50 text-slate-800 shadow-sm'
          : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-50'}"
      >
        <span class="flex items-center gap-2 text-sm font-semibold">
          <Check class="h-4 w-4" /> No
        </span>
        <span class="mt-0.5 block text-xs opacity-80">Caso de servicio normal, sin daño.</span>
      </button>
    </div>

    {#if isTecno}
      <!-- Paso 2 · ¿En qué etapa va? -->
      <div class="mt-5">
        <span class="mb-2 block text-sm font-medium text-slate-700">
          ¿En qué etapa va? <span class="font-semibold text-danger-500">*</span>
        </span>
        <div class="grid gap-2 sm:grid-cols-2">
          {#each TECNOVIGILANCIA_STAGE_ORDER as s, i (s)}
            {@const m = TECNOVIGILANCIA_STAGE_META[s]}
            {@const active = stage === s}
            <button
              type="button"
              aria-pressed={active}
              on:click={() => {
                stage = s;
                stageError = '';
              }}
              class="flex items-start gap-2.5 rounded-xl border-2 px-3 py-2.5 text-left transition
                {active
                ? `${m.tint} ${m.text} shadow-sm`
                : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-50'}"
              style={active ? `border-color:${m.color}` : ''}
            >
              <span
                class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full text-[11px] font-bold text-white"
                style="background:{active ? m.color : '#cbd5e1'}"
              >
                {i + 1}
              </span>
              <span class="min-w-0">
                <span class="block text-sm font-semibold">{m.label}</span>
                <span class="block text-xs leading-snug opacity-80">{m.description}</span>
              </span>
            </button>
          {/each}
        </div>
        {#if stageError}
          <p class="mt-1 text-xs text-danger-600">{stageError}</p>
        {/if}
      </div>

      <!-- Paso 3 · ¿Qué pasó? -->
      <div class="mt-5">
        <Textarea
          label="¿Qué pasó? (descripción breve)"
          bind:value={description}
          rows={3}
          placeholder="Ej. Durante la terapia el equipo entregó una dosis mayor a la programada; el paciente presentó…"
        />
        <p class="mt-1 text-xs text-slate-400">
          Describe el evento en una o dos frases: qué ocurrió, a quién afectó y cómo se contuvo.
        </p>
      </div>
    {/if}
  {/if}

  <svelte:fragment slot="footer">
    <div class="flex flex-wrap justify-end gap-2">
      <button type="button" class="btn-secondary" on:click={close}>Cancelar</button>
      <Button on:click={save} loading={saving}>
        {#if isTecno}
          <ShieldAlert class="h-4 w-4" /> Guardar tecnovigilancia
        {:else if value?.is_tecnovigilancia}
          <Trash2 class="h-4 w-4" /> Quitar marca
        {:else}
          <Check class="h-4 w-4" /> Guardar
        {/if}
      </Button>
    </div>
  </svelte:fragment>
</Modal>
