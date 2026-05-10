<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Card from '$lib/components/Card.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Button from '$lib/components/Button.svelte';
  import { alertsApi } from '$lib/modules/alerts/api';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { AlertType, AlertSeverity } from '$lib/api/types';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';

  let equipment: Equipment[] = [];
  let loading = false;
  let form = {
    type: 'custom' as AlertType,
    severity: 'info' as AlertSeverity,
    title: '',
    message: '',
    equipment_id: '',
    due_at: '',
  };

  onMount(async () => {
    setPageTitle('Nueva alerta');
    equipment = await equipmentApi.list({ limit: 200 });
  });

  async function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    try {
      const payload = {
        type: form.type,
        severity: form.severity,
        title: form.title,
        message: form.message,
        equipment_id: form.equipment_id || undefined,
        due_at: form.due_at ? new Date(form.due_at).toISOString() : undefined,
      };
      await alertsApi.create(payload);
      toasts.success('Alerta creada');
      goto('/alerts');
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'Error');
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit={onSubmit} class="mx-auto max-w-2xl">
  <Card title="Crear alerta manual">
    <div class="grid gap-4">
      <Input label="Título *" bind:value={form.title} required />
      <Textarea label="Mensaje *" bind:value={form.message} rows={3} />
      <div class="grid gap-4 sm:grid-cols-2">
        <Select
          label="Tipo"
          bind:value={form.type}
          options={[
            { value: 'custom', label: 'Personalizada' },
            { value: 'preventive_due', label: 'Mantenimiento preventivo' },
            { value: 'calibration_due', label: 'Calibración' },
            { value: 'warranty_expiring', label: 'Garantía por vencer' },
            { value: 'case_sla', label: 'SLA de caso' },
          ]}
        />
        <Select
          label="Severidad"
          bind:value={form.severity}
          options={[
            { value: 'info', label: 'Info' },
            { value: 'warning', label: 'Advertencia' },
            { value: 'critical', label: 'Crítica' },
          ]}
        />
      </div>
      <Select
        label="Equipo (opcional)"
        bind:value={form.equipment_id}
        options={equipment.map((e) => ({ value: e.id, label: `${e.code} · ${e.name}` }))}
      />
      <Input label="Vence el" type="datetime-local" bind:value={form.due_at} />
    </div>
  </Card>
  <div class="mt-4 flex gap-2">
    <Button type="submit" {loading}>Crear alerta</Button>
    <a class="btn-secondary" href="/alerts">Cancelar</a>
  </div>
</form>
