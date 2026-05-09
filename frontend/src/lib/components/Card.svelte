<script lang="ts">
  export let title: string | null = null;
  export let description: string | null = null;
</script>

<div class="card">
  {#if title}
    <header class="mb-3 flex items-start justify-between gap-4">
      <div>
        <h3 class="text-base font-semibold text-slate-900">{title}</h3>
        {#if description}
          <p class="text-sm text-slate-500">{description}</p>
        {/if}
      </div>
      <slot name="actions" />
    </header>
  {/if}
  <slot />
</div>
