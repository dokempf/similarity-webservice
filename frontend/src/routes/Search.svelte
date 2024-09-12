<script lang="ts">
  import { Button, Dropzone, Gallery, Label, P, Select, Spinner } from "flowbite-svelte";
  import { getCollections, similaritySearch } from "../utils/backend";
  import ResultGallery from "../components/ResultGallery.svelte";

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
    result_images = await similaritySearch(collection_selection, query[0].src);
    ongoing_query = false;
  }

  // The state of the search site
  let collection_selection = 1;
  let query = [];
  let ongoing_query = false;
  let result_images = [];
</script>

<div class="flex flex-col md:flex-row w-full mt-8">
  <div class="md:flex-shrink-0 md:w-1/4 w-full min-w-[300px] m-4">
    <Label>
      {#await getCollections()}
      Loading datasets...
      {:then options}
          {#if options.names.length === 0}
            <p>No collections available</p>
          {:else}
            Dataset selection
            <Select class="mt-2 w-full p-4" items={options.names} bind:value={collection_selection} />
          {/if}
      {/await}
    </Label>
    <Button class="mt-4 w-full" color="blue" disabled="{ongoing_query}" on:click={similaritySearchCall}>
      Start Search {#if ongoing_query} <Spinner size="4" color="white"/> {/if}
    </Button>
    <!-- https://flowbite-svelte.com/docs/forms/file-input -->
    <Dropzone
      id="dropzone"
      on:change={handleChange}
      on:drop={dropHandle}
      on:dragover={(event) => { event.preventDefault(); }}
      class="w-full mt-4"
      >
      <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
      <p class="text-xs text-gray-500 dark:text-gray-400">PNG, JPG or GIF</p>
    </Dropzone>
    <Gallery items={query} class="mt-4 w-full" />
  </div>
  <div class="md:flex-grow m-4 w-full min-w-[500px]">
    <Label>Similarity Search Results</Label>
    {#if ongoing_query}
      <div class="easydb-waiting flex justify-center">
        <P class="pt-24">
          <Spinner class="h-48 w-48"/>
        </P>
      </div>
    {:else}
      <ResultGallery class="h-full gap-4 grid-cols-3 mt-2 rounded-lg" items={result_images} />
    {/if}
  </div>
</div>
