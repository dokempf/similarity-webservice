import { alerts } from './alerts'

const apiURL = import.meta.env.VITE_BACKEND_BASE_URL

function triggerAlert (response: any): void {
  if ('message_type' in response) {
    if (response.message_type === 'error') {
      alerts.add(response.message, 'red')
    }
    if (response.message_type === 'push') {
      alerts.add(response.message, 'green')
    }
  }
}

export async function get (route: string, args: object): Promise<object> {
  try {
    const response: object = await fetch(
      apiURL + route + '?' + new URLSearchParams(args).toString(),
      {
        method: 'GET'
      }
    )
    const json = await response.json()
    triggerAlert(json)
    return json
  } catch (error: unknown) {
    triggerAlert(error)
  }
}

export async function post (route: string, key: string, body: object = {}): Promise<object> {
  try {
    const response: object = await fetch(
      apiURL + route,
      {
        method: 'POST',
        headers: {
          'API-Key': key,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      }
    )
    const json = await response.json()
    triggerAlert(json)
    return json
  } catch (error: unknown) {
    triggerAlert(error)
  }
}

export async function postFile (route: string, key: string, file: File, mimetype: string, query: object): Promise<object> {
  try {
    const response: object = await fetch(
      apiURL + route + "?" + new URLSearchParams(query).toString(),
      {
        method: 'POST',
        headers: {
          'API-Key': key,
          'Content-Type': mimetype
        },
        body: file
      }
    )
    const json = await response.json()
    triggerAlert(json)
    return json
  } catch (error: unknown) {
    triggerAlert(error)
  }
}
