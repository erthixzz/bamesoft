<script lang="ts">
  import Badge from '$lib/components/Badge.svelte';
  import type { CasePriority } from '$lib/api/types';

  export let priority: CasePriority;

  const map: Record<CasePriority, { tone: 'gray' | 'yellow' | 'red'; label: string }> = {
    low: { tone: 'gray', label: 'Baja' },
    medium: { tone: 'yellow', label: 'Media' },
    high: { tone: 'red', label: 'Alta' },
    critical: { tone: 'red', label: 'Crítica' },
  };
</script>

<Badge tone={map[priority].tone}>{map[priority].label}</Badge>
