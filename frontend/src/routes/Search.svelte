<script lang="ts">
  import { Button, Dropzone, Gallery, Label, Select, Spinner } from "flowbite-svelte";
  import { getCollections, similaritySearch } from "../utils/backend";
  import LinkedGallery from "../components/LinkedGallery.svelte";

  function handleChange(event) {
    query = [];
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      query.push({ src: e.target.result });
      query = query;
    };
    reader.readAsDataURL(file);
  }

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
  <div class="pl-20 pr-20">
    <Label>
      {#await getCollections()}
      Loading datasets...
      {:then options}
          {#if options.names.length === 0}
            <p>No collections available</p>
          {:else}
            Dataset selection
            <Select class="mt-2 w-80 p-4" items={options.names} bind:value={collection_selection} />
          {/if}
      {/await}
    </Label>
    <Button class="w-80 p-4" color="blue" disabled="{ongoing_query}" on:click={similaritySearchCall}>
      Start Search {#if ongoing_query} <Spinner size="4" color="white"/> {/if}
    </Button>
    <!-- https://flowbite-svelte.com/docs/forms/file-input -->
    <Dropzone
      id="dropzone"
      on:change={handleChange}
      on:drop={dropHandle}
      on:dragover={(event) => { event.preventDefault(); }}
      class="w-80"
      >
      <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
      <p class="text-xs text-gray-500 dark:text-gray-400">PNG, JPG or GIF</p>
    </Dropzone>
    <Gallery items={query} class="gap-4 p- w-80" />
  </div>
  <div>
    Similarity Search Results:
    <LinkedGallery class="h-full bg-slate-50 gap-4 grid-cols-3" items={result_images} />
  </div>
</div>
