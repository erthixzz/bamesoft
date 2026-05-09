<script lang="ts">
  export let type: 'button' | 'submit' = 'button';
  export let variant: 'primary' | 'secondary' | 'danger' = 'primary';
  export let disabled = false;
  export let loading = false;

  $: cls =
    variant === 'primary'
      ? 'btn-primary'
      : variant === 'danger'
        ? 'btn-danger'
        : 'btn-secondary';
</script>

<button {type} class={cls} disabled={disabled || loading} on:click>
  {#if loading}
    <span class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
  {/if}
  <slot />
</button>
