const apiURL = 'http://localhost:5000/api'

export async function get (route: string, args: object): Promise<object> {
  const response: object = await fetch(
    apiURL + route + '?' + new URLSearchParams(args).toString(),
    {
      method: 'GET'
    }
  )
  return response.json()
}

export async function post (route: string, key: string, body: object = {}): Promise<object> {
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
  return response.json()
}

export async function postFile (route: string, key: string, file: File, mimetype: string): Promise<object> {
  const response: object = await fetch(
    apiURL + route,
    {
      method: 'POST',
      headers: {
        'API-Key': key,
        'Content-Type': mimetype
      },
      body: file
    }
  )
  return response.json()
}
