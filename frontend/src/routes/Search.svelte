<script>
  import { Dropzone, Gallery } from "flowbite-svelte";

  let query = [];
</script>

<div class="grid grid-cols-2 gap-2">
  <!-- https://flowbite-svelte.com/docs/forms/file-input -->
  <div>
    <Dropzone id="dropzone">
      {#if query.length === 0}
        <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
        <p class="text-xs text-gray-500 dark:text-gray-400">PNG, JPG or GIF</p>
      {:else}
        Foo
      {/if}
    </Dropzone>
  </div>
  <div>
    <Gallery>
      <!-- https://flowbite-svelte.com/docs/media/gallery -->
    </Gallery>
  </div>
</div>
