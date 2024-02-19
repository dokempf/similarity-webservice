<script lang="ts">
  import { Button, Dropzone, Gallery, Label, Select, Spinner } from "flowbite-svelte";
  import { get } from "../utils/requests";

  async function getCollections() {
    let collections = await get("/collection/list");
    let collection_options = [];
    for (let c in collections["ids"]) {
      collection_options.push({value: c.toString(), name: "Collection " + c});
    }
    return collection_options;
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

  function similaritySearch() {
    console.log("Search started");
    ongoing_query = true;
  }

  // The state of the search site
  let query = [];
  let ongoing_query = false;
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
            <Select class="mt-2" items={options} />
          {/if}
      {/await}
    </Label>
    <Button class="w-full" color="blue" disabled="{ongoing_query}" on:click={similaritySearch}>
      Start Search {#if ongoing_query} <Spinner size="4" color="white"/> {/if}
    </Button>
    <!-- https://flowbite-svelte.com/docs/forms/file-input -->
    <Dropzone
      id="dropzone"
      on:drop={dropHandle}
      on:dragover={(event) => { event.preventDefault(); }}
      >
      {#if query.length === 0}
        <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
        <p class="text-xs text-gray-500 dark:text-gray-400">PNG, JPG or GIF</p>
      {:else}
        <Gallery items={query} class="grid-cols-1" />
      {/if}
    </Dropzone>
  </div>
  <div>
    Similarity Search Results:
    <Gallery class="h-full bg-slate-50 gap-4 grid-cols-3">
      <!-- https://flowbite-svelte.com/docs/media/gallery -->
      <!-- Most likely, we will need to add the images one by one with a svelte loop -->
      <!-- because we cannot wrap the href elements out of the box. Should probably use -->
      <!-- a masonry grid for layouting. Delaying this until we implemented the similarity -->
      <!-- search in the backend, so that we have the real data around. -->
    </Gallery>
  </div>
</div>
