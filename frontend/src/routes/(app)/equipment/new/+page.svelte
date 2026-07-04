<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import Card from '$lib/components/Card.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Button from '$lib/components/Button.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import { Stethoscope, StickyNote, MapPin } from 'lucide-svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import type { Clinic, Location } from '$lib/modules/clinics/types';
  import type { Sector } from '$lib/modules/sectors/types';
  import type { EquipmentCategory } from '$lib/modules/equipment/types';
  import { profile } from '$lib/stores/auth';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { get } from 'svelte/store';

  let clinics: Clinic[] = [];
  let locations: Location[] = [];
  let sectors: Sector[] = [];
  let categories: EquipmentCategory[] = [];
  let loading = false;

  // Modelo del formulario
  let form = {
    code: '',
    name: '',
    brand: '',
    model: '',
    serial_number: '',
    manufacturer: '',
    category_id: '',
    risk_class: '' as '' | 'I' | 'IIa' | 'IIb' | 'III',
    status: 'operational' as 'operational' | 'out_of_service' | 'under_maintenance' | 'retired',
    clinic_id: get(profile)?.clinic_id ?? '',
    location_id: '',
    sector_id: '',
    acquisition_date: '',
    warranty_until: '',
    notes: '',
  };

  $: if (form.clinic_id) loadClinicScoped(form.clinic_id);

  async function loadClinicScoped(clinicId: string) {
    [locations, sectors] = await Promise.all([
      clinicsApi.locations(clinicId).catch(() => []),
      sectorsApi.list(clinicId).catch(() => []),
    ]);
  }

  onMount(async () => {
    setPageTitle('Nuevo equipo');
    [clinics, categories] = await Promise.all([clinicsApi.list(), equipmentApi.categories()]);
    if (!form.clinic_id && clinics[0]) form.clinic_id = clinics[0].id;
    // Preseleccionar la unidad de servicio si se llegó desde una unidad concreta.
    const sid = get(page).url.searchParams.get('sector_id');
    if (sid) form.sector_id = sid;
  });

  async function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    try {
      const payload = {
        code: form.code,
        name: form.name,
        brand: form.brand || undefined,
        model: form.model || undefined,
        serial_number: form.serial_number || undefined,
        manufacturer: form.manufacturer || undefined,
        category_id: form.category_id || undefined,
        risk_class: form.risk_class || undefined,
        status: form.status,
        clinic_id: form.clinic_id,
        location_id: form.location_id || undefined,
        sector_id: form.sector_id || undefined,
        acquisition_date: form.acquisition_date || undefined,
        warranty_until: form.warranty_until || undefined,
        notes: form.notes || undefined,
      };
      const eq = await equipmentApi.create(payload);
      toasts.success(`Equipo ${eq.code} creado`);
      goto(`/equipment/${eq.code}`);
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'Error al crear');
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit={onSubmit} class="animate-fade-up grid gap-4 lg:grid-cols-3">
  <div class="min-w-0 lg:col-span-2">
    <Card title="Información del equipo" description="Identificación y clasificación" icon={Stethoscope} accent="brand">
      <div class="grid gap-4 sm:grid-cols-2">
        <Input label="Código *" bind:value={form.code} required placeholder="EQ-0010" />
        <Input label="Nombre *" bind:value={form.name} required placeholder="Monitor Mindray uMEC12" />
        <Input label="Marca" bind:value={form.brand} placeholder="Mindray" />
        <Input label="Modelo" bind:value={form.model} placeholder="uMEC12" />
        <Input label="Serial" bind:value={form.serial_number} />
        <Input label="Fabricante" bind:value={form.manufacturer} />
        <Select
          label="Categoría"
          bind:value={form.category_id}
          options={categories.map((c) => ({ value: c.id, label: `${c.code} · ${c.name}` }))}
        />
        <Select
          label="Clase de riesgo"
          bind:value={form.risk_class}
          options={[
            { value: 'I', label: 'I — Bajo riesgo' },
            { value: 'IIa', label: 'IIa — Riesgo moderado' },
            { value: 'IIb', label: 'IIb — Riesgo alto' },
            { value: 'III', label: 'III — Riesgo crítico' },
          ]}
        />
        <DatePicker label="Adquirido" bind:value={form.acquisition_date} />
        <DatePicker label="Garantía hasta" bind:value={form.warranty_until} />
      </div>
    </Card>

    <div class="mt-4">
      <Card title="Notas" icon={StickyNote} accent="slate">
        <Textarea bind:value={form.notes} placeholder="Notas internas, observaciones, advertencias…" />
      </Card>
    </div>
  </div>

  <div>
    <Card title="Ubicación y estado" description="Clínica, unidad y disponibilidad" icon={MapPin} accent="cyan">
      <div class="grid gap-4">
        <Select
          label="Clínica *"
          bind:value={form.clinic_id}
          options={clinics.map((c) => ({ value: c.id, label: c.name }))}
          required
        />
        <Select
          label="Unidad de servicio"
          bind:value={form.sector_id}
          options={sectors.map((s) => ({ value: s.id, label: s.name }))}
        />
        <Select
          label="Ubicación"
          bind:value={form.location_id}
          options={locations.map((l) => ({ value: l.id, label: `${l.code} · ${l.name}` }))}
        />
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
      </div>
    </Card>

    <div class="mt-4 flex flex-col gap-2">
      <Button type="submit" {loading}>Crear equipo</Button>
      <a class="btn-secondary" href="/equipment">Cancelar</a>
    </div>
  </div>
</form>
