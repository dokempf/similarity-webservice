<script>
  import { Button, Input, Label, Modal, P, Popover, Tooltip } from "flowbite-svelte";
  // For additional matching icons, see https://flowbite-svelte-icons.vercel.app/outline
  import { DatabaseOutline, DownloadOutline, EditOutline, FileCsvOutline, FileImportOutline, MagicWandOutline, TrashBinOutline, UploadOutline } from "flowbite-svelte-icons";
  import { changeDatasetName, deleteDataset, easyDBImport, getCollections, getCollection, finetuneModel } from "../utils/backend";

  // The state for modals on this page
  let delete_modal = {};
  let easydb_modal = {};
  let editname_modal = {};
  let finetune_modal = {};

  // The state for form elements on the modals on this page
  let easydb_url = {};
  let easydb_tag = {};
  let newname = {};
</script>

<div class="w-full h-full pt-8">
  <P>Explanatory Text...</P>
  <div class="pt-4">
    <Label>API Key:</Label>
    <Input type="text" class="w-full" id="apikey" required />
  </div>
  <div class="w-full pt-4">
    Add new (empty) data source:
    <Label>Dataset name:</Label>
    <Input type="text" class="w-full" id="datasetname" required />
    <Button class="w-full" color="blue">Add data source</Button>
  </div>
  <div class="pt-4">
    <Label>Existing Data Sources:</Label>
    <div class="h-full bg-slate-50">
      {#await getCollections()}
        <p>Loading datasets...</p>
      {:then collections}
        {#each collections as { id } }
          {#await getCollection(id)}
            <div class="p-4 bg-white rounded-lg shadow-md mb-4">
              Loading dataset details...
            </div>
          {:then details}
            <div class="p-4 bg-white rounded-lg shadow-md mb-4">
              <div class="grid grid-cols-2">
                <div>
                  <h2 class="text-xl font-semibold">{details["name"]}</h2>
                  <div class="text-sm">
                    <P>ID: {details["id"]}</P>
                    <P>Last modified: {details["last_modified"]}</P>
                    {#if details["last_finetuned"] !== null}
                      <P>Last finetuned: {details["last_finetuned"]}</P>
                    {:else}
                      <P>Not yet finetuned</P>
                    {/if}
                  </div>
                </div>
                <div>
                  <!-- The buttons shown for each dataset -->
                  <Button color="blue"><FileCsvOutline /><UploadOutline />Upload Data</Button>
                  <Button color="blue" on:click={() => (easydb_modal[id] = true)}><DatabaseOutline /><FileImportOutline />Import from EasyDB</Button>
                  <Button color="blue"><FileCsvOutline /><DownloadOutline />Download Data</Button>
                  <Button color="blue" on:click={() => (delete_modal[id] = true)}><TrashBinOutline />Delete Dataset</Button>
                  <Button color="blue" on:click={() => (editname_modal[id] = true)}><EditOutline />Edit Name</Button>
                  <Button color="blue" on:click={() => (finetune_modal[id] = true)}><MagicWandOutline />Finetune Model</Button>

                  <!-- Additional modal logic attached to above buttons -->
                  <Modal title="Import from EasyDB" bind:open={easydb_modal[id]} outsideclose autoclose>
                    <P>
                      We use the concept of EasyDB tags in order to select the subset of data that we want to
                      use for similarity search. In order to add tags, you need to be an administator of the
                      EasyDB instance.
                    </P>
                    <div class="p-4">
                      <Label>EasyDB Instance URL:</Label>
                      <Input type="text" class="w-full" bind:value={easydb_url[id]} id="easydb_url" placeholder="https://heidicon.ub.uni-heidelberg.de/" required />
                      <Label>EasyDB Tag</Label>
                      <Input type="text" class="w-full" bind:value={easydb_tag[id]} id="easydb_tag" required />
                    </div>
                    <svelte:fragment slot="footer">
                      <Button color="blue" on:click={() => (easyDBImport(id, easydb_url[id], easydb_tag[id]))}>Import data</Button>
                    </svelte:fragment>
                  </Modal>
                  <Modal title="Edit Dataset Name" bind:open={editname_modal[id]} outsideclose autoclose>
                    <P>
                      This changes the display name of the dataset with ID {id} and the current
                      display name <b>{details.name}</b>.
                    </P>
                    <div class="p-4">
                      <Label>New name:</Label>
                      <Input type="text" class="w-full" bind:value={newname[id]} placeholder="{details.name}" required />
                    </div>
                    <svelte:fragment slot="footer">
                      <Button color="blue" on:click={() => (changeDatasetName(id, newname[id]))}>Change name</Button>
                    </svelte:fragment>
                  </Modal>
                  <Modal name="Delete Dataset" bind:open={delete_modal[id]} outsideclose autoclose>
                    <P>
                      Are you sure you want to delete the dataset with ID {id} and the current
                      display name <b>{details.name}</b>?
                    </P>
                    <svelte:fragment slot="footer">
                      <Button color="blue" on:click={() => (deleteDataset(id))}>Yes, delete it!</Button>
                    </svelte:fragment>
                  </Modal>
                  <Modal title="Model finetuning" bind:open={finetune_modal[id]} outsideclose autoclose>
                    <P>Finetuning the model will take some time and GPU resources. Are you sure you want to continue?</P>
                    <svelte:fragment slot="footer">
                      <Button color="blue" on:click={() => (finetuneModel(id))}>Start finetuning</Button>
                    </svelte:fragment>
                  </Modal>
                </div>
              </div>
            </div>
          {/await}
        {/each}
      {/await}
    </div>
  </div>
</div>
