<script>
  import { onMount } from "svelte";
  import { Alert } from "flowbite-svelte";

  let visible = true;

  onMount(() => {
    setTimeout(() => {
      visible = false;
    }, 5000);
  });
</script>


{#if visible}
  <Alert on:close={() => { visible = false; }} {...$$restProps}>
    <slot />
  </Alert>
{/if}
