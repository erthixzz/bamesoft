<script lang="ts">
  import Badge from '$lib/components/Badge.svelte';
  import type { CaseStatus } from '$lib/api/types';

  export let status: CaseStatus;

  const map: Record<CaseStatus, { tone: 'gray' | 'green' | 'yellow' | 'red' | 'blue' | 'purple'; label: string }> = {
    open: { tone: 'blue', label: 'Abierto' },
    assigned: { tone: 'purple', label: 'Asignado' },
    in_progress: { tone: 'yellow', label: 'En progreso' },
    waiting_parts: { tone: 'yellow', label: 'Esperando repuestos' },
    waiting_client: { tone: 'yellow', label: 'Esperando cliente' },
    closed: { tone: 'green', label: 'Cerrado' },
    cancelled: { tone: 'gray', label: 'Cancelado' },
  };
</script>

<Badge tone={map[status].tone}>{map[status].label}</Badge>
