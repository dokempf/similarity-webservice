<script lang="ts">
  import { Button, Fileupload, Helper, Input, Label, Modal, P, Toggle } from "flowbite-svelte";
  // For additional matching icons, see https://flowbite-svelte-icons.vercel.app/outline
  import { DatabaseOutline, DownloadOutline, EditOutline, EyeOutline, EyeSlashOutline, FileCsvOutline, FileImportOutline, MagicWandOutline, TrashBinOutline, UploadOutline } from "flowbite-svelte-icons";
  import { changeDatasetName, createDataset, deleteDataset, getCollections, getCollection, finetuneModel, uploadCSVFile, updateHeidicon, verifyAPIKey } from "../utils/backend";

  // State for a reload trigger of the collection list
  let reload = false;

  // The state for modals on this page
  let delete_modal = {};
  let editname_modal = {};
  let finetune_modal = {};
  let upload_modal = {};

  // The state for form elements on the modals on this page
  let newname = {};
  let csvfile = {};
  let createname = "";
  let heidicon = false;
  let heidicon_tag = "";

  // The state for the API key
  let apikey = "";
  let apikey_visible = false;
  let apikey_verified = false;

  async function deleteDatasetTrigger(id) {
    delete_modal[id] = false
    await deleteDataset(id, apikey)
    reload = !reload;
  }

  async function changeDatasetNameTrigger(id) {
    await changeDatasetName(id, newname[id], apikey)
    editname_modal[id] = false
    reload = !reload;
  }

  async function uploadCSVFileTrigger(id) {
    await uploadCSVFile(id, csvfile[id][0], apikey)
    upload_modal[id] = false
    reload = !reload;
  }

  async function createDatasetTrigger() {
    if (!heidicon) {
      heidicon_tag = ""
    }
    if (createname !== "") {
      await createDataset(createname, heidicon_tag, apikey)
      createname = ""
      reload = !reload;
    }
  }

  async function finetuneModelTrigger(id) {
    await finetuneModel(id, apikey)
    finetune_modal[id] = false
    reload = !reload;
  }

  async function verifyAPIKeyTrigger() {
    const response = await verifyAPIKey(apikey)
    apikey_verified = response.message === "API key is valid";
  }
</script>

<div class="w-full h-full pt-8">
  <P class="text-gray-600 mb-3">
    This interface is only relevant if you are looking to add additional imaging data to this instance of
    the similarity search webservice. In order to do any operation, you need to provide a valid API key.
    If you do not have one, please get in touch with the system administrator of this instance.
  </P>
  <P class="text-gray-600 mb-3">
    Image collection can be entered in two ways: The default way is to upload a CSV file that consists of one row
    per image and two columns: The first column must contain a URL to the image, the second column must
    contain a URL (e.g. in a data repository) that should be linked to in the search results.
  </P>
  <P class="text-gray-600 mb-3">
    Alternatively, you may also directly link to data that is already managed on <a href="https://heidicon.ub.uni-heidelberg.de/">HeidICON</a>.
    In this case, you need to provide the name of a tag that is applied to the relevant data on HeidICON.
  </P>
  <div class="pt-4">
    <h1 class="text-2xl m-2">Authentication</h1>
    <Label color={apikey_verified ? "green" :  "red"}>API Key:</Label>
    <Input color={apikey_verified ? "green" :  "red"} on:blur={verifyAPIKeyTrigger} type={apikey_visible ? "text" : "password"} class="w-full" id="apikey" bind:value={apikey}>
      <button type="button" slot="right" on:click={() => (apikey_visible = !apikey_visible)} tabindex=-1>
        {#if apikey_visible}
          <EyeSlashOutline class="w-6 h-6" />
        {:else}
          <EyeOutline class="w-6 h-6" />
        {/if}
      </button>
    </Input>
  </div>
  <div class="pt-4">
    <h1 class="text-2xl m-2">Existing Data Sources</h1>
    <div class="h-full bg-slate-50">
      {#key reload}
        {#await getCollections()}
          <p>Loading datasets...</p>
        {:then collections }
          {#each collections.ids as id }
            {#await getCollection(id)}
              <div class="p-4 bg-white rounded-lg shadow-md mb-4">
                Loading dataset details...
              </div>
            {:then details}
              <div class="p-4 bg-white rounded-lg shadow-md mb-4">
                <div class="grid grid-cols-2">
                  <div>
                    <h2 class="text-xl font-semibold">{details.name}</h2>
                    <div class="text-sm">
                      <P>ID: {details["id"]}, contains {details["number_of_images"]} images</P>
                      <P>Last modified: {details["last_modified"]}</P>
                      {#if details.finetuning_progess === null }
                        {#if details["last_finetuned"] !== null}
                          <P>Last finetuned: {details["last_finetuned"]} {#if details.requires_finetuning}<b>(outdated!)</b>{/if}</P>
                        {:else}
                          <P>Not yet finetuned</P>
                        {/if}
                      {:else}
                        <P>Finetuning in progress: { details.finetuning_progess }%</P>
                      {/if}
                    </div>
                  </div>
                  <div>
                    <!-- The buttons shown for each dataset -->
                    {#if details.heidicon_tag === null }
                      <Button class="m-2" color="blue" on:click={() => (upload_modal[id] = true)}><FileCsvOutline /><UploadOutline />Upload Data</Button>
                    {/if}
                    {#if details.heidicon_tag !== null}
                      <Button class="m-2" color="blue" on:click={() => (updateHeidicon(id, apikey))}><DatabaseOutline /><FileImportOutline />Synchronize with HeidIcon</Button>
                    {/if}
                    <form action="{import.meta.env.VITE_BACKEND_BASE_URL}/collection/{id}/csvfile" class="inline">
                      <Button class="m-2" color="blue" type="submit"><FileCsvOutline /><DownloadOutline />Download Data</Button>
                    </form>
                    <Button class="m-2" color="blue" on:click={() => (delete_modal[id] = true)}><TrashBinOutline />Delete Dataset</Button>
                    <Button class="m-2" color="blue" on:click={() => (editname_modal[id] = true)}><EditOutline />Edit Name</Button>
                    <Button class="m-2" color="blue" on:click={() => (finetune_modal[id] = true)}><MagicWandOutline />Finetune Model</Button>

                    <!-- Additional modal logic attached to above buttons -->
                    <Modal title="Upload CSV file" bind:open={upload_modal[id]} outsideclose autoclose>
                      <P>
                        Please choose a CSV file to upload. The first column should contain the URL
                        of the image, the second column should contain the URL of the entry in the
                        data repository of your choice. <b>Note that you overwrite existing content with
                        this operation.</b>
                      </P>
                      <div class="p-4">
                        <Fileupload  class="w-full" accept=".csv" name="file" bind:files={csvfile[id]} required />
                        <Helper>CSV File with commata as delimiter and exactly two columns</Helper>
                      </div>
                      <svelte:fragment slot="footer">
                        <Button color="blue" on:click={() => uploadCSVFileTrigger(id)}>Upload file</Button>
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
                        <Button color="blue" on:click={() => (changeDatasetNameTrigger(id))}>Change name</Button>
                      </svelte:fragment>
                    </Modal>
                    <Modal name="Delete Dataset" bind:open={delete_modal[id]} outsideclose autoclose>
                      <P>
                        Are you sure you want to delete the dataset with ID {id} and the current
                        display name <b>{details.name}</b>?
                      </P>
                      <svelte:fragment slot="footer">
                        <Button color="blue" on:click={() => (deleteDatasetTrigger(id))}>Yes, delete it!</Button>
                      </svelte:fragment>
                    </Modal>
                    <Modal title="Model finetuning" bind:open={finetune_modal[id]} outsideclose autoclose>
                      <P>Finetuning the model will take some time and GPU resources. Are you sure you want to continue?</P>
                      <svelte:fragment slot="footer">
                        <Button color="blue" on:click={() => (finetuneModelTrigger(id))}>Start finetuning</Button>
                      </svelte:fragment>
                    </Modal>
                  </div>
                </div>
              </div>
            {/await}
          {/each}
        {/await}
      {/key}
    </div>
  </div>
  <div class="w-full pt-4">
    <h1 class="text-2xl m-2">
      Adding new (empty) data source
    </h1>
    <Label>Dataset name:</Label>
    <Input type="text" class="w-full m-2" bind:value={createname} id="datasetname" required />
    <Toggle bind:checked={heidicon} class="m-2">This dataset is managed on HeidICON</Toggle>
    {#if heidicon}
      <Label>
        The images in HeidIcon are tagged with the following tag:
        <Input type="text" class="w-full m-2" bind:value={heidicon_tag} id="heidicon_tag" />
      </Label>
    {/if}
    <Button class="w-full m-2" color="blue" on:click={createDatasetTrigger}>Add data source</Button>
  </div>
</div>
