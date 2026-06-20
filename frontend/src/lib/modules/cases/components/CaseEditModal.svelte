<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Select from '$lib/components/Select.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import Button from '$lib/components/Button.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case, CaseUpdate } from '$lib/modules/cases/types';
  import type { User } from '$lib/modules/users/types';
  import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '$lib/modules/cases/ui';
  import { toasts } from '$lib/stores/toasts';

  export let open = false;
  export let value: Case | null = null;
  export let engineers: User[] = [];

  const dispatch = createEventDispatcher<{ saved: Case; close: void }>();

  let title = '';
  let description = '';
  let priority = 'medium';
  let status = 'open';
  let assigned_to = '';
  let sla_due_at = '';
  let saving = false;

  // Rellena el formulario cada vez que se abre con un caso.
  $: if (open && value) hydrate(value);

  let hydratedId = '';
  function hydrate(c: Case) {
    if (hydratedId === c.id) return; // evita pisar lo que el usuario escribe
    hydratedId = c.id;
    title = c.title ?? '';
    description = c.description ?? '';
    priority = c.priority;
    status = c.status;
    assigned_to = c.assigned_to ?? '';
    // El backend entrega ISO con zona; el DatePicker usa "YYYY-MM-DDTHH:MM".
    sla_due_at = c.sla_due_at ? new Date(c.sla_due_at).toISOString().slice(0, 16) : '';
  }

  $: engineerOptions = engineers.map((u) => ({ value: u.id, label: `${u.full_name} (${u.role})` }));

  function close() {
    hydratedId = '';
    open = false;
    dispatch('close');
  }

  async function save() {
    if (!value) return;
    if (!title.trim()) {
      toasts.error('El título es obligatorio');
      return;
    }
    saving = true;
    try {
      const payload: CaseUpdate = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority: priority as Case['priority'],
        status: status as Case['status'],
        assigned_to: assigned_to || undefined,
        sla_due_at: sla_due_at ? new Date(sla_due_at).toISOString() : undefined,
      };
      const updated = await casesApi.update(value.id, payload);
      toasts.success(`Caso ${updated.code} actualizado`);
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

<Modal {open} title={value ? `Editar ${value.code}` : 'Editar caso'} size="lg" on:close={close}>
  {#if value}
    <div class="grid gap-4">
      <Input label="Título *" bind:value={title} placeholder="Ventilador no enciende" />
      <Textarea label="Descripción" bind:value={description} rows={3} placeholder="Detalle del problema…" />
      <div class="grid gap-4 sm:grid-cols-2">
        <Select label="Prioridad" bind:value={priority} options={PRIORITY_OPTIONS} />
        <Select label="Estado" bind:value={status} options={STATUS_OPTIONS} />
      </div>
      <Select
        label="Asignar a ingeniero"
        bind:value={assigned_to}
        options={engineerOptions}
        placeholder="— Sin asignar —"
      />
      <DatePicker label="SLA (fecha límite)" mode="datetime" bind:value={sla_due_at} />
    </div>
  {/if}

  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2">
      <button type="button" class="btn-secondary" on:click={close}>Cancelar</button>
      <Button on:click={save} loading={saving}>Guardar cambios</Button>
    </div>
  </svelte:fragment>
</Modal>
