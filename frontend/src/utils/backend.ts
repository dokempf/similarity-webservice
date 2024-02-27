import { get, post, postFile } from './requests'

export async function getCollections (): Promise<object> {
  const collections = await get('/collection/list', {})
  const collectionOptions = []
  for (const c of collections.ids) {
    collectionOptions.push({ id: c, name: 'Collection ' + c })
  }
  return collectionOptions
}

export async function getCollection (collectionId: string): Promise<object> {
  return await get('/collection/' + collectionId + '/info', {})
}

export async function finetuneModel (collectionId: string): Promise<void> {
  console.log('Finetuning model for collection ' + collectionId)
}

export async function createDataset (collectionName: string, heidiconTag: string, key: string): Promise<object> {
  return await post('/collection/create', key, { name: collectionName, heidicon_tag: heidiconTag })
}

export async function changeDatasetName (collectionId: string, newName: string, key: string): Promise<void> {
  await post('/collection/' + collectionId + '/updatename', key, { name: newName })
}

export async function deleteDataset (collectionId: string, key: string): Promise<void> {
  await post('/collection/' + collectionId + '/delete', key, {})
}

export async function uploadCSVFile (collectionId: string, file: File, key: string): Promise<void> {
  await postFile('/collection/' + collectionId + '/updatecontent', key, file, 'text/csv')
}

export async function updateHeidicon (collectionId: string, key: string): Promise<void> {
  await post('/collection/' + collectionId + '/updatecontent', key, {})
}

export async function verifyAPIKey (key: string): Promise<object> {
  return await post('/verify', key, {})
}
