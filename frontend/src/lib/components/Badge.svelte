<script lang="ts">
  export let tone: 'gray' | 'green' | 'yellow' | 'red' | 'blue' | 'purple' = 'gray';

  const map: Record<typeof tone, string> = {
    gray: 'bg-slate-100 text-slate-700',
    green: 'bg-emerald-100 text-emerald-700',
    yellow: 'bg-amber-100 text-amber-700',
    red: 'bg-red-100 text-red-700',
    blue: 'bg-brand-100 text-brand-700',
    purple: 'bg-violet-100 text-violet-700',
  };
</script>

<span class="badge {map[tone]}"><slot /></span>
