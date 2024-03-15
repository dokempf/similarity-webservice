<script lang="ts">
  import { Button, Dropzone, Gallery, Label, Select, Spinner } from "flowbite-svelte";
  import { getCollections, similaritySearch } from "../utils/backend";
  import LinkedGallery from "../components/LinkedGallery.svelte";

  function dropHandle(event) {
    event.preventDefault();
    const file = event.dataTransfer.items[0];
    if(file.kind === "file") {
      query = [];
      const reader = new FileReader();
      reader.onload = (e) => {
        query.push({ src: e.target.result });
        query = query;
      };
      reader.readAsDataURL(file.getAsFile());
    }
  }

  async function similaritySearchCall() {
    ongoing_query = true;
    const result = await similaritySearch(collection_selection, query[0].src);
    let update = []
    for(const img of result) {
      update.push({ src: img.image_url, href: img.repo_url });
    }
    result_images = update
    ongoing_query = false;
  }

  // The state of the search site
  let collection_selection = 0;
  let query = [];
  let ongoing_query = false;
  let result_images = [];
</script>

<div class="h-full w-full grid grid-cols-2 gap-8 pt-8">
  <div>
    <Label>
      {#await getCollections()}
      Loading datasets...
      {:then options}
          {#if options.length === 0}
            <p>No collections available</p>
          {:else}
            Dataset selection
            <Select class="mt-2" items={options} bind:value={collection_selection} />
          {/if}
      {/await}
    </Label>
    <Button class="w-full" color="blue" disabled="{ongoing_query}" on:click={similaritySearchCall}>
      Start Search {#if ongoing_query} <Spinner size="4" color="white"/> {/if}
    </Button>
    <!-- https://flowbite-svelte.com/docs/forms/file-input -->
    <Dropzone
      id="dropzone"
      on:drop={dropHandle}
      on:dragover={(event) => { event.preventDefault(); }}
      >
      <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
      <p class="text-xs text-gray-500 dark:text-gray-400">PNG, JPG or GIF</p>
    </Dropzone>
    <Gallery items={query} class="grid-cols-1 max-h-full gap-4" />
  </div>
  <div>
    Similarity Search Results:
    <LinkedGallery class="h-full bg-slate-50 gap-4 grid-cols-3" items={result_images} />
  </div>
</div>
