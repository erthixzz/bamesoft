<script lang="ts">
  import Badge from '$lib/components/Badge.svelte';
  import type { EquipmentStatus } from '$lib/api/types';

  export let status: EquipmentStatus;

  const map: Record<EquipmentStatus, { tone: 'green' | 'yellow' | 'red' | 'gray'; label: string }> = {
    operational: { tone: 'green', label: 'Operativo' },
    under_maintenance: { tone: 'yellow', label: 'En mantenimiento' },
    out_of_service: { tone: 'red', label: 'Fuera de servicio' },
    retired: { tone: 'gray', label: 'Retirado' },
  };
</script>

<Badge tone={map[status].tone}>{map[status].label}</Badge>
