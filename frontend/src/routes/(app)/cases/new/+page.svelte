<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import Card from '$lib/components/Card.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Button from '$lib/components/Button.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import { ClipboardList, UserCog } from 'lucide-svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import { usersApi } from '$lib/modules/users/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { Sector } from '$lib/modules/sectors/types';
  import type { User } from '$lib/modules/users/types';
  import type { CaseType, CasePriority } from '$lib/api/types';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';

  let equipment: Equipment[] = [];
  let sectors: Sector[] = [];
  let engineers: User[] = [];
  let loading = false;

  let form = {
    title: '',
    description: '',
    type: 'corrective' as CaseType,
    priority: 'medium' as CasePriority,
    equipment_id: '',
    sector_id: '',
    assigned_to: '',
    sla_due_at: '',
  };

  // Cuando cambia el sector, autocompletar el ingeniero por defecto.
  $: if (form.sector_id) {
    const s = sectors.find((x) => x.id === form.sector_id);
    if (s?.default_engineer_id && !form.assigned_to) {
      form.assigned_to = s.default_engineer_id;
    }
  }

  // Equipos de la unidad seleccionada (el equipo depende del sector).
  $: equipmentForSector = form.sector_id
    ? equipment.filter((e) => e.sector_id === form.sector_id)
    : [];

  // Al cambiar de unidad, limpiar el equipo si ya no pertenece a ella.
  function onSectorChange() {
    if (
      form.equipment_id &&
      !equipment.some((e) => e.id === form.equipment_id && e.sector_id === form.sector_id)
    ) {
      form.equipment_id = '';
    }
  }

  onMount(async () => {
    setPageTitle('Nuevo caso');
    try {
      const [eq, sec, all] = await Promise.all([
        equipmentApi.list({ limit: 200 }),
        sectorsApi.list(),
        usersApi.list().catch(() => [] as User[]),
      ]);
      equipment = eq;
      sectors = sec;
      engineers = all.filter((u) =>
        ['admin', 'engineer', 'service', 'support'].includes(u.role),
      );

      // Preselección desde parámetros (equipo concreto o unidad).
      const params = get(page).url.searchParams;
      const eqId = params.get('equipment_id');
      const secId = params.get('sector_id');
      if (eqId) {
        const e = equipment.find((x) => x.id === eqId);
        if (e) {
          form.sector_id = e.sector_id ?? '';
          form.equipment_id = e.id;
        }
      } else if (secId) {
        form.sector_id = secId;
      }
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error cargando datos');
    }
  });

  async function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    try {
      const payload = {
        title: form.title,
        description: form.description || undefined,
        type: form.type,
        priority: form.priority,
        equipment_id: form.equipment_id,
        sector_id: form.sector_id || undefined,
        assigned_to: form.assigned_to || undefined,
        sla_due_at: form.sla_due_at ? new Date(form.sla_due_at).toISOString() : undefined,
      };
      const c = await casesApi.create(payload);
      toasts.success(`Caso ${c.code} creado`);
      goto(`/cases/${c.code}`);
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'Error al crear');
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit={onSubmit} class="animate-fade-up grid gap-4 lg:grid-cols-3">
  <div class="min-w-0 lg:col-span-2">
    <Card title="Datos del caso" description="Describe la falla o el trabajo a realizar" icon={ClipboardList} accent="amber">
      <div class="grid gap-4">
        <Input label="Título *" bind:value={form.title} required placeholder="Ventilador no enciende" />
        <Textarea label="Descripción" bind:value={form.description} rows={4} placeholder="Detalle del problema, contexto, antecedentes…" />
        <div class="grid gap-4 sm:grid-cols-2">
          <Select
            label="Tipo *"
            bind:value={form.type}
            required
            options={[
              { value: 'corrective', label: 'Correctivo' },
              { value: 'preventive', label: 'Preventivo' },
              { value: 'calibration', label: 'Calibración' },
              { value: 'installation', label: 'Instalación' },
              { value: 'inspection', label: 'Inspección' },
            ]}
          />
          <Select
            label="Prioridad"
            bind:value={form.priority}
            options={[
              { value: 'low', label: 'Baja' },
              { value: 'medium', label: 'Media' },
              { value: 'high', label: 'Alta' },
              { value: 'critical', label: 'Crítica' },
            ]}
          />
        </div>
      </div>
    </Card>
  </div>

  <div>
    <Card title="Asignación" description="Unidad, equipo e ingeniero" icon={UserCog} accent="brand">
      <div class="grid gap-4">
        <Select
          label="Unidad de servicio *"
          bind:value={form.sector_id}
          required
          on:change={onSectorChange}
          options={sectors.map((s) => ({ value: s.id, label: s.name }))}
          placeholder="— Selecciona la unidad —"
        />
        <div>
          <Select
            label="Equipo *"
            bind:value={form.equipment_id}
            required
            disabled={!form.sector_id}
            options={equipmentForSector.map((e) => ({ value: e.id, label: `${e.code} · ${e.name}` }))}
            placeholder={form.sector_id ? '— Selecciona el equipo —' : 'Elige primero una unidad'}
          />
          {#if form.sector_id && equipmentForSector.length === 0}
            <p class="mt-1 text-xs text-amber-600">
              Esta unidad no tiene equipos.
              <a class="font-medium underline" href={`/equipment/new?sector_id=${form.sector_id}`}>Añadir equipo</a>
            </p>
          {/if}
        </div>
        <Select
          label="Asignar a ingeniero"
          bind:value={form.assigned_to}
          options={engineers.map((u) => ({ value: u.id, label: `${u.full_name} (${u.role})` }))}
        />
        <p class="text-xs text-slate-500">
          Si dejas el ingeniero en blanco, se asigna automáticamente al ingeniero por
          defecto de la unidad (si tiene uno).
        </p>
        <DatePicker label="SLA (fecha límite)" mode="datetime" bind:value={form.sla_due_at} />
      </div>
    </Card>

    <div class="mt-4 flex flex-col gap-2">
      <Button type="submit" {loading}>Crear caso</Button>
      <a class="btn-secondary" href="/cases">Cancelar</a>
    </div>
  </div>
</form>
