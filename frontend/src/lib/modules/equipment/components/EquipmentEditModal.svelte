<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Button from '$lib/components/Button.svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import type { Equipment, EquipmentUpdate } from '$lib/modules/equipment/types';
  import { toasts } from '$lib/stores/toasts';

  export let open = false;
  export let equipment: Equipment;

  const dispatch = createEventDispatcher<{ saved: Equipment }>();

  let form: EquipmentUpdate & { name: string; brand: string; model: string; serial_number: string; manufacturer: string; status: string; risk_class: string; notes: string; acquisition_date: string; warranty_until: string };
  let saving = false;

  $: form = {
    name: equipment.name,
    brand: equipment.brand ?? '',
    model: equipment.model ?? '',
    serial_number: equipment.serial_number ?? '',
    manufacturer: equipment.manufacturer ?? '',
    status: equipment.status,
    risk_class: equipment.risk_class ?? '',
    notes: equipment.notes ?? '',
    acquisition_date: equipment.acquisition_date ?? '',
    warranty_until: equipment.warranty_until ?? '',
  };

  async function save() {
    saving = true;
    try {
      const payload = {
        name: form.name,
        brand: form.brand || null,
        model: form.model || null,
        serial_number: form.serial_number || null,
        manufacturer: form.manufacturer || null,
        status: form.status as Equipment['status'],
        risk_class: (form.risk_class || null) as Equipment['risk_class'],
        notes: form.notes || null,
        acquisition_date: form.acquisition_date || null,
        warranty_until: form.warranty_until || null,
      };
      const updated = await equipmentApi.update(equipment.id, payload);
      toasts.success('Equipo actualizado');
      dispatch('saved', updated);
      open = false;
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      saving = false;
    }
  }
</script>

<Modal bind:open title={`Editar ${equipment.code}`}>
  <div class="grid gap-4 sm:grid-cols-2">
    <div class="sm:col-span-2"><Input label="Nombre" bind:value={form.name} /></div>
    <Input label="Marca" bind:value={form.brand} />
    <Input label="Modelo" bind:value={form.model} />
    <Input label="Serial" bind:value={form.serial_number} />
    <Input label="Fabricante" bind:value={form.manufacturer} />
    <Select
      label="Estado"
      bind:value={form.status}
      options={[
        { value: 'operational', label: 'Operativo' },
        { value: 'under_maintenance', label: 'En mantenimiento' },
        { value: 'out_of_service', label: 'Fuera de servicio' },
        { value: 'retired', label: 'Retirado' },
      ]}
    />
    <Select
      label="Clase de riesgo"
      bind:value={form.risk_class}
      options={[
        { value: 'I', label: 'I' },
        { value: 'IIa', label: 'IIa' },
        { value: 'IIb', label: 'IIb' },
        { value: 'III', label: 'III' },
      ]}
    />
    <Input label="Adquirido" type="date" bind:value={form.acquisition_date} />
    <Input label="Garantía hasta" type="date" bind:value={form.warranty_until} />
    <div class="sm:col-span-2">
      <Textarea label="Notas" bind:value={form.notes} rows={3} />
    </div>
  </div>
  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2">
      <button class="btn-secondary" on:click={() => (open = false)}>Cancelar</button>
      <Button on:click={save} loading={saving}>Guardar</Button>
    </div>
  </svelte:fragment>
</Modal>
