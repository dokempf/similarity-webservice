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

export async function createDataset (collectionName: string, key: string): Promise<object> {
  return await post('/collection/create', key, { name: collectionName })
}

export async function changeDatasetName (collectionId: string, newName: string, key: string): Promise<void> {
  await post('/collection/' + collectionId + '/updatename', key, { name: newName })
}

export async function deleteDataset (collectionId: string, key: string): Promise<void> {
  await post('/collection/' + collectionId + '/delete', key, {})
}

export async function easyDBImport (collectionId: string, easydbURL: string, easydbTag: string): Promise<void> {
  console.log('Importing from EasyDB')
  console.log('Collection ID: ' + collectionId)
  console.log('EasyDB URL: ' + easydbURL)
  console.log('EasyDB Tag: ' + easydbTag)
}

export async function uploadCSVFile (collectionId: string, file: File, key: string): Promise<void> {
  await postFile('/collection/' + collectionId + '/updatecontent', key, file, 'text/csv')
}

export async function verifyAPIKey (key: string): Promise<object> {
  return await post('/verify', key, {})
}
