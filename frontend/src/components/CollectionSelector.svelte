<script>
  import { Label, Select } from "flowbite-svelte";

  export let data = {"names": {}, "ids": []};
  export let collection_selection = Math.min(data.ids);
</script>

<Label>
  {#if data.names.length === 0}
    <p>No collections available</p>
  {:else}
    Dataset selection
    <Select class="mt-2 w-full p-4" items={data.names} bind:value={collection_selection} />
  {/if}
</Label>
