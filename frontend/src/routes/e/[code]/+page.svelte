<script lang="ts">
  /** Ficha móvil del equipo (tras escanear el QR). Requiere sesión: si no hay,
   *  manda al login y regresa aquí. Vista limpia y accesible, optimizada para
   *  móvil, con acción destacada "Reportar caso". Respeta el aislamiento por
   *  clínica (el fetch del equipo es scoped). */
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { fly, fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { supabase } from '$lib/supabase';
  import BrandMark from '$lib/components/BrandMark.svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { casesApi } from '$lib/modules/cases/api';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { Case } from '$lib/modules/cases/types';
  import type { CaseType } from '$lib/api/types';
  import { STATUS_META, TYPE_LABEL, TYPE_OPTIONS, isActive } from '$lib/modules/cases/ui';
  import { formatDate } from '$lib/utils/format';
  import { get } from 'svelte/store';
  import { role, profile } from '$lib/stores/auth';
  import { authApi } from '$lib/modules/auth/api';
  import { accessApi } from '$lib/modules/access/api';
  import { documentsApi } from '$lib/modules/documents/api';
  import { can, setPermissions } from '$lib/utils/permissions';
  import Modal from '$lib/components/Modal.svelte';
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Select from '$lib/components/Select.svelte';
  import Button from '$lib/components/Button.svelte';
  import {
    Wrench, ArrowRight, Building2, Hash, Cpu, ShieldCheck, Activity,
    AlertTriangle, ExternalLink, CheckCircle2, ImagePlus, Send, X,
  } from 'lucide-svelte';

  let code = '';
  let eq: Equipment | null = null;
  let cases: Case[] = [];
  let sectorName = '';
  let loading = true;
  let error: string | null = null;
  let authed = false; // sesión válida confirmada

  const EQ_STATUS: Record<string, { label: string; cls: string; dot: string }> = {
    operational: { label: 'Operativo', cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', dot: 'bg-emerald-500' },
    under_maintenance: { label: 'En mantenimiento', cls: 'bg-amber-50 text-amber-700 ring-amber-200', dot: 'bg-amber-500' },
    out_of_service: { label: 'Fuera de servicio', cls: 'bg-rose-50 text-rose-700 ring-rose-200', dot: 'bg-rose-500' },
    retired: { label: 'Retirado', cls: 'bg-slate-100 text-slate-600 ring-slate-300', dot: 'bg-slate-400' },
  };
  $: eqStatus = eq ? (EQ_STATUS[eq.status] ?? { label: eq.status, cls: 'bg-slate-100 text-slate-600 ring-slate-300', dot: 'bg-slate-400' }) : null;
  $: openCases = cases.filter(isActive).length;

  // --- Reporte simplificado (solo lo esencial para quien escanea) ---
  let reportOpen = false;
  let submitting = false;
  let submitted = false;
  let submittedCode = '';
  let formErr = '';
  let rTitle = '';
  let rDesc = '';
  let rType: CaseType = 'corrective';
  let photoFile: File | null = null;
  let photoPreview: string | null = null;
  let fileInput: HTMLInputElement;

  function openReport() {
    submitted = false;
    formErr = '';
    rTitle = '';
    rDesc = '';
    rType = 'corrective';
    clearPhoto();
    reportOpen = true;
  }

  function clearPhoto() {
    if (photoPreview) URL.revokeObjectURL(photoPreview);
    photoFile = null;
    photoPreview = null;
  }

  function onPhoto(e: Event) {
    const f = (e.target as HTMLInputElement).files?.[0] ?? null;
    if (photoPreview) URL.revokeObjectURL(photoPreview);
    photoFile = f;
    photoPreview = f ? URL.createObjectURL(f) : null;
  }

  async function submitReport() {
    formErr = '';
    if (!rTitle.trim()) {
      formErr = 'Escribe un título breve del problema.';
      return;
    }
    if (!eq) return;
    submitting = true;
    try {
      const c = await casesApi.create({
        title: rTitle.trim(),
        description: rDesc.trim() || undefined,
        type: rType,
        equipment_id: eq.id,
      });
      if (photoFile) {
        // La foto es opcional: si falla, el caso ya quedó registrado.
        try {
          await documentsApi.upload(photoFile, {
            title: `Foto · ${c.code}`,
            type: 'photo',
            case_id: c.id,
            equipment_id: eq.id,
          });
        } catch {
          /* ignore */
        }
      }
      submittedCode = c.code;
      submitted = true;
      // Refresca el contador/lista para que se vea el caso recién creado.
      cases = await casesApi.list({ equipment_id: eq.id, limit: 8 }).catch(() => cases);
    } catch (e) {
      formErr = e instanceof Error ? e.message : 'No se pudo enviar el caso. Intenta de nuevo.';
    } finally {
      submitting = false;
    }
  }

  onMount(async () => {
    code = $page.params.code ?? '';
    // El QR SIEMPRE exige iniciar sesión. Solo continuamos si venimos de un
    // login recién verificado (?v=1) Y hay sesión; de lo contrario mandamos al
    // login. Cada escaneo abre la URL sin ?v=1 → fuerza el login otra vez.
    const verified = $page.url.searchParams.get('v') === '1';
    const { data } = await supabase.auth.getSession();
    if (!data.session || !verified) {
      goto(`/login?next=${encodeURIComponent(`/e/${code}?v=1`)}`, { replaceState: true });
      return;
    }
    authed = true;
    // Esta ruta no está bajo el layout (app): cargamos perfil + matriz de roles
    // aquí para que `$role` y `can.*` funcionen (si no, el botón se ocultaría).
    if (!get(profile)) {
      try {
        profile.set(await authApi.whoami());
      } catch {
        /* la ficha funciona igual sin perfil */
      }
    }
    accessApi
      .getRoles()
      .then((r) => setPermissions(r.matrix))
      .catch(() => {});
    try {
      eq = await equipmentApi.byCode(code);
      const eqId = eq.id;
      cases = await casesApi.list({ equipment_id: eqId, limit: 8 }).catch(() => []);
      if (eq.sector_id) sectorName = (await sectorsApi.get(eq.sector_id).catch(() => null))?.name ?? '';
    } catch (e) {
      error = e instanceof Error ? e.message : 'No se pudo cargar el equipo.';
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>{eq ? `${eq.code} · ${eq.name}` : 'Equipo'} — Bamesoft</title>
  <meta name="robots" content="noindex" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 pb-28">
  <!-- Barra de marca -->
  <header class="sticky top-0 z-10 border-b border-slate-200/70 bg-white/85 backdrop-blur-xl">
    <div class="mx-auto flex max-w-2xl items-center gap-2.5 px-4 py-3">
      <BrandMark size={34} />
      <div class="leading-tight">
        <p class="text-sm font-black tracking-tight text-slate-900">Bamesoft</p>
        <p class="text-[10px] font-bold uppercase tracking-[0.15em] text-brand-700">Ficha de equipo</p>
      </div>
      {#if eq && can.manageEquipment($role)}
        <a href={`/equipment/${eq.code}`} class="ml-auto inline-flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-brand-700">
          Ficha completa <ExternalLink class="h-3.5 w-3.5" />
        </a>
      {/if}
    </div>
  </header>

  <main class="mx-auto max-w-2xl px-4 pt-5">
    {#if loading}
      <div class="space-y-4" in:fade>
        <div class="h-36 animate-pulse rounded-3xl bg-slate-200/70"></div>
        <div class="grid grid-cols-2 gap-3">
          <div class="h-20 animate-pulse rounded-2xl bg-slate-200/70"></div>
          <div class="h-20 animate-pulse rounded-2xl bg-slate-200/70"></div>
        </div>
        <div class="h-40 animate-pulse rounded-2xl bg-slate-200/70"></div>
      </div>
    {:else if error || !eq}
      <div in:fly={{ y: 16, duration: 400 }} class="mt-10 rounded-3xl border border-rose-200 bg-rose-50/70 p-8 text-center">
        <div class="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-rose-100 text-rose-600">
          <AlertTriangle class="h-7 w-7" />
        </div>
        <h1 class="text-lg font-bold text-slate-900">No se pudo abrir la ficha</h1>
        <p class="mt-2 text-sm text-slate-600">{error ?? 'Equipo no encontrado o no pertenece a tu clínica.'}</p>
      </div>
    {:else}
      <!-- HERO -->
      <section in:fly={{ y: 18, duration: 500, easing: cubicOut }} class="relative overflow-hidden rounded-3xl border border-white/60 bg-gradient-to-br from-brand-600 via-brand-500 to-cyan-500 p-6 text-white shadow-xl shadow-brand-600/20">
        <div class="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/15 blur-2xl"></div>
        <div class="relative flex items-start gap-4">
          <div class="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-white/15 ring-2 ring-white/30">
            <Cpu class="h-8 w-8" />
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1.5 text-xs font-semibold text-white/80"><Hash class="h-3.5 w-3.5" />{eq.code}</div>
            <h1 class="mt-0.5 text-2xl font-bold leading-tight">{eq.name}</h1>
            {#if eqStatus}
              <span class="mt-2 inline-flex items-center gap-1.5 rounded-full bg-white/15 px-2.5 py-1 text-xs font-bold ring-1 ring-white/25 backdrop-blur">
                <span class="h-1.5 w-1.5 rounded-full {eqStatus.dot}"></span>{eqStatus.label}
              </span>
            {/if}
          </div>
        </div>
        <div class="relative mt-4 flex flex-wrap gap-x-4 gap-y-1.5 text-sm text-white/90">
          {#if sectorName}<span class="inline-flex items-center gap-1.5"><Building2 class="h-4 w-4 text-white/70" />{sectorName}</span>{/if}
          <span class="inline-flex items-center gap-1.5"><Activity class="h-4 w-4 text-white/70" />{eq.brand ?? 'Sin marca'} {eq.model ?? ''}</span>
        </div>
      </section>

      <!-- CTA reportar: grande, con marca y animado (único botón) -->
      {#if authed}
        <button
          type="button"
          on:click={openReport}
          class="animate-float group relative mt-5 flex w-full items-center gap-3 overflow-hidden rounded-2xl bg-gradient-to-r from-brand-600 via-cyan-500 to-brand-600 px-5 py-4 text-left text-white shadow-xl shadow-brand-600/30 transition active:scale-[0.98] animate-gradient"
          aria-label="Reportar un caso para este equipo"
        >
          <!-- brillo que se desliza en bucle -->
          <span class="pointer-events-none absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shine"></span>
          <span class="relative grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-white/20 ring-1 ring-white/30 backdrop-blur">
            <Wrench class="h-6 w-6" />
          </span>
          <span class="relative flex min-w-0 flex-col leading-tight">
            <span class="text-[11px] font-semibold uppercase tracking-[0.14em] text-white/80">Acción rápida</span>
            <span class="text-lg font-extrabold">Reportar un caso</span>
          </span>
          <span class="relative ml-auto grid h-8 w-8 shrink-0 place-items-center rounded-full bg-white/20 transition group-hover:translate-x-0.5 group-hover:bg-white/30">
            <ArrowRight class="h-5 w-5" />
          </span>
        </button>
      {/if}

      <!-- Stat rápida -->
      <section in:fly={{ y: 16, duration: 500, delay: 80, easing: cubicOut }} class="mt-4 grid grid-cols-2 gap-3">
        <div class="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
          <Wrench class="mx-auto mb-1 h-5 w-5 text-amber-500" />
          <p class="text-2xl font-black tabular-nums text-slate-900">{openCases}</p>
          <p class="text-[11px] font-medium text-slate-500">casos abiertos</p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
          <ShieldCheck class="mx-auto mb-1 h-5 w-5 text-emerald-500" />
          <p class="text-sm font-bold text-slate-900">{eq.risk_class ?? '—'}</p>
          <p class="text-[11px] font-medium text-slate-500">clase de riesgo</p>
        </div>
      </section>

      <!-- Info general -->
      <section in:fly={{ y: 16, duration: 500, delay: 140, easing: cubicOut }} class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 class="mb-3 flex items-center gap-2 text-sm font-bold text-slate-900"><Activity class="h-4 w-4 text-brand-600" /> Información general</h2>
        <dl class="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
          {#each [['Marca', eq.brand], ['Modelo', eq.model], ['Serial', eq.serial_number], ['Fabricante', eq.manufacturer], ['Unidad', sectorName || null], ['Garantía', eq.warranty_until ? formatDate(eq.warranty_until) : null]] as [label, value]}
            <div class="min-w-0">
              <dt class="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</dt>
              <dd class="truncate font-semibold text-slate-800">{value ?? '—'}</dd>
            </div>
          {/each}
        </dl>
      </section>

      <!-- Casos recientes -->
      {#if cases.length}
        <section in:fly={{ y: 16, duration: 500, delay: 200, easing: cubicOut }} class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-3 flex items-center gap-2 text-sm font-bold text-slate-900"><Wrench class="h-4 w-4 text-amber-500" /> Casos recientes</h2>
          <ul class="space-y-2.5">
            {#each cases as c}
              <a href={`/cases/${c.code}`} class="block rounded-xl border border-slate-100 bg-slate-50/60 p-3 transition hover:border-brand-200 hover:bg-brand-50/40">
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <p class="truncate text-sm font-semibold text-slate-900">{c.title}</p>
                    <p class="mt-0.5 text-xs text-slate-500">{c.code} · {TYPE_LABEL[c.type]}{#if c.opened_at} · {formatDate(c.opened_at)}{/if}</p>
                  </div>
                  <span class="shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold" style="background:{STATUS_META[c.status].color}22;color:{STATUS_META[c.status].color}">
                    {STATUS_META[c.status].label}
                  </span>
                </div>
              </a>
            {/each}
          </ul>
        </section>
      {/if}

      <p class="mt-8 text-center text-xs text-slate-400">Información protegida · <span class="font-semibold text-slate-500">Bamesoft Solutions</span></p>
    {/if}
  </main>
</div>

<!-- Modal de reporte simplificado: solo título, descripción, tipo y foto -->
<Modal bind:open={reportOpen} title="Reportar un caso" size="md">
  {#if submitted}
    <!-- Confirmación -->
    <div class="py-4 text-center">
      <div class="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-2xl bg-emerald-50 text-emerald-600">
        <CheckCircle2 class="h-9 w-9" />
      </div>
      <h3 class="text-lg font-bold text-slate-900">¡Caso reportado!</h3>
      <p class="mx-auto mt-2 max-w-xs text-sm text-slate-600">
        Tu reporte <span class="font-semibold text-slate-800">{submittedCode}</span> quedó registrado.
        El equipo de ingeniería lo revisará y asignará. Gracias.
      </p>
    </div>
  {:else}
    <div class="space-y-4">
      <div class="rounded-xl bg-slate-50 px-3.5 py-2.5 text-sm">
        <span class="text-slate-500">Equipo:</span>
        <span class="font-semibold text-slate-800">{eq?.code} · {eq?.name}</span>
      </div>

      <Input label="Título *" bind:value={rTitle} placeholder="Ej.: No enciende / hace ruido" required />
      <Textarea label="Descripción" bind:value={rDesc} rows={4} placeholder="Cuéntanos qué está pasando…" />
      <Select label="Tipo" bind:value={rType} options={TYPE_OPTIONS} />

      <!-- Foto opcional (abre cámara en móvil) -->
      <div>
        <span class="mb-1.5 block text-sm font-medium text-slate-700">Foto (opcional)</span>
        <input
          bind:this={fileInput}
          type="file"
          accept="image/*"
          capture="environment"
          class="hidden"
          on:change={onPhoto}
        />
        {#if photoPreview}
          <div class="relative overflow-hidden rounded-xl border border-slate-200">
            <img src={photoPreview} alt="Vista previa" class="max-h-52 w-full object-cover" />
            <button
              type="button"
              on:click={clearPhoto}
              class="absolute right-2 top-2 grid h-8 w-8 place-items-center rounded-full bg-slate-900/60 text-white backdrop-blur"
              aria-label="Quitar foto"
            >
              <X class="h-4 w-4" />
            </button>
          </div>
        {:else}
          <button
            type="button"
            on:click={() => fileInput?.click()}
            class="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 py-4 text-sm font-medium text-slate-500 transition hover:border-brand-300 hover:text-brand-600"
          >
            <ImagePlus class="h-5 w-5" /> Agregar una foto
          </button>
        {/if}
      </div>

      {#if formErr}
        <p class="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{formErr}</p>
      {/if}
    </div>
  {/if}

  <svelte:fragment slot="footer">
    {#if submitted}
      <div class="flex gap-2">
        <button
          type="button"
          class="btn-secondary flex-1"
          on:click={openReport}
        >
          Reportar otro
        </button>
        <button type="button" class="btn-primary flex-1" on:click={() => (reportOpen = false)}>
          Listo
        </button>
      </div>
    {:else}
      <div class="flex items-center justify-end gap-2">
        <button type="button" class="btn-secondary" on:click={() => (reportOpen = false)}>Cancelar</button>
        <Button on:click={submitReport} loading={submitting}>
          <span class="flex items-center gap-2"><Send class="h-4 w-4" /> Enviar caso</span>
        </Button>
      </div>
    {/if}
  </svelte:fragment>
</Modal>
