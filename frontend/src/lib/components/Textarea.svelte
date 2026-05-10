<script lang="ts">
  export let label = '';
  export let value: string = '';
  export let placeholder = '';
  export let rows = 3;
</script>

<label class="block">
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">{label}</span>
  {/if}
  <textarea class="input" {rows} {placeholder} bind:value on:input on:change></textarea>
</label>
