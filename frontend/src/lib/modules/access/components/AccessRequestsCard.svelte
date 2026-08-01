<script lang="ts">
  /**
   * Bandeja de solicitudes de acceso.
   *
   * Aparece cuando alguien se autentica (normalmente con Google) y no tiene
   * perfil en Bamesoft. Sin esta pantalla, esa persona tendría que escribirle
   * al administrador por fuera y no quedaría rastro del intento.
   *
   * Solo la ve el super admin: una solicitud pendiente aún no tiene clínica,
   * así que mostrarla a un admin de clínica le revelaría correos de personas
   * que intentan entrar a otra.
   */
  import { createEventDispatcher, onMount } from 'svelte';
  import Badge from '$lib/components/Badge.svelte';
  import Button from '$lib/components/Button.svelte';
  import Card from '$lib/components/Card.svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Select from '$lib/components/Select.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import { accessApi } from '$lib/modules/access/api';
  import type { AccessRequest } from '$lib/modules/access/types';
  import type { Clinic } from '$lib/modules/clinics/types';
  import { toasts } from '$lib/stores/toasts';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { timeFromNow } from '$lib/utils/format';
  import { Check, Inbox, UserRoundPlus, X } from 'lucide-svelte';

  /** Clínicas disponibles para asignar (las carga la página de Usuarios). */
  export let clinics: Clinic[] = [];

  const dispatch = createEventDispatcher<{ approved: void }>();

  let requests: AccessRequest[] = [];
  let loading = true;
  let working = false;

  let approving: AccessRequest | null = null;
  let rejecting: AccessRequest | null = null;
  let clinicId = '';
  let role = 'client';
  let note = '';

  // El rol `admin` no se concede desde aquí: el super admin de la plataforma
  // se crea a mano, nunca aprobando una solicitud llegada desde fuera.
  const ROLE_OPTIONS = Object.entries(ROLE_LABELS)
    .filter(([value]) => value !== 'admin')
    .map(([value, label]) => ({ value, label }));

  async function load() {
    loading = true;
    try {
      requests = await accessApi.requests('pending');
    } catch {
      requests = []; // sin permiso (no es super admin) o error de red
    } finally {
      loading = false;
    }
  }

  onMount(load);

  function openApprove(req: AccessRequest) {
    approving = req;
    clinicId = clinics[0]?.id ?? '';
    role = 'client';
  }

  async function confirmApprove() {
    if (!approving || !clinicId) return;
    working = true;
    try {
      const user = await accessApi.approveRequest(approving.user_id, clinicId, role);
      toasts.success(`${user.full_name} ya tiene acceso.`);
      approving = null;
      await load();
      dispatch('approved');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo aprobar');
    } finally {
      working = false;
    }
  }

  async function confirmReject() {
    if (!rejecting) return;
    working = true;
    try {
      await accessApi.rejectRequest(rejecting.user_id, note);
      toasts.success('Solicitud descartada.');
      rejecting = null;
      note = '';
      await load();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo descartar');
    } finally {
      working = false;
    }
  }
</script>

{#if loading}
  <Card title="Solicitudes de acceso" icon={Inbox} accent="amber">
    <Spinner label="Buscando solicitudes…" />
  </Card>
{:else if requests.length > 0}
  <Card
    title="Solicitudes de acceso"
    description="Personas que iniciaron sesión y esperan que les asignes una clínica."
    icon={Inbox}
    accent="amber"
  >
    <svelte:fragment slot="actions">
      <Badge tone="yellow">{requests.length} pendiente{requests.length === 1 ? '' : 's'}</Badge>
    </svelte:fragment>

    <ul class="divide-y divide-slate-100">
      {#each requests as req (req.user_id)}
        <li class="flex flex-wrap items-center gap-3 py-3">
          <div class="min-w-0 flex-1">
            <p class="truncate font-medium text-slate-900">
              {req.full_name || req.email.split('@')[0]}
            </p>
            <p class="truncate font-mono text-xs text-slate-500">{req.email}</p>
            <p class="mt-0.5 text-xs text-slate-400">
              {#if req.provider}
                <span class="capitalize">{req.provider}</span> ·
              {/if}
              {timeFromNow(req.last_seen_at)}
              {#if req.attempts > 1}
                · {req.attempts} intentos
              {/if}
            </p>
          </div>

          <div class="flex shrink-0 gap-2">
            <Button on:click={() => openApprove(req)}>
              <span class="flex items-center gap-1.5">
                <UserRoundPlus class="h-4 w-4" /> Dar acceso
              </span>
            </Button>
            <button
              type="button"
              on:click={() => (rejecting = req)}
              class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-500 transition hover:border-danger-500 hover:text-danger-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
            >
              <X class="h-4 w-4" /> Descartar
            </button>
          </div>
        </li>
      {/each}
    </ul>
  </Card>
{/if}

<!-- Aprobar: hay que decidir clínica y rol; no hay valor por defecto seguro -->
<Modal open={!!approving} title="Dar acceso" on:close={() => (approving = null)}>
  {#if approving}
    <p class="mb-4 text-sm text-slate-600">
      <strong class="font-semibold text-slate-900">{approving.email}</strong>
      entrará a la clínica y el rol que elijas. Su sesión ya abierta empezará a
      funcionar en cuanto pulses <em>Comprobar de nuevo</em> en su pantalla.
    </p>

    <div class="space-y-3">
      <Select label="Clínica" bind:value={clinicId} options={clinics.map((c) => ({ value: c.id, label: c.name }))} />
      <Select label="Rol" bind:value={role} options={ROLE_OPTIONS} />
    </div>

    {#if clinics.length === 0}
      <p class="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">
        No hay clínicas creadas todavía. Crea una antes de dar acceso.
      </p>
    {/if}

    <div class="mt-6 flex justify-end gap-2">
      <button
        type="button"
        class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
        on:click={() => (approving = null)}
      >
        Cancelar
      </button>
      <Button loading={working} disabled={!clinicId} on:click={confirmApprove}>
        <span class="flex items-center gap-1.5"><Check class="h-4 w-4" /> Dar acceso</span>
      </Button>
    </div>
  {/if}
</Modal>

<!-- Descartar: queda registrado y no reaparece aunque la persona reintente -->
<Modal open={!!rejecting} title="Descartar solicitud" on:close={() => (rejecting = null)}>
  {#if rejecting}
    <p class="mb-4 text-sm text-slate-600">
      <strong class="font-semibold text-slate-900">{rejecting.email}</strong>
      no podrá entrar. Si vuelve a intentarlo no reaparecerá en esta lista.
    </p>
    <Textarea label="Motivo (opcional)" bind:value={note} rows={2} placeholder="No pertenece a ninguna clínica…" />
    <div class="mt-6 flex justify-end gap-2">
      <button
        type="button"
        class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
        on:click={() => (rejecting = null)}
      >
        Cancelar
      </button>
      <Button variant="danger" loading={working} on:click={confirmReject}>Descartar</Button>
    </div>
  {/if}
</Modal>
