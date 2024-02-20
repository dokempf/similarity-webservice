export async function get (route: string, args: object): Promise<object> {
  const apiURL = 'http://localhost:5000/api'
  let returnObj: object
  try {
    const response: object = await fetch(apiURL + route + '?' + new URLSearchParams(args).toString(), { method: 'GET' })
    const responseContent: object = await response.json()
    returnObj = Object.assign(response, responseContent)
  } catch (error: unknown) {
    returnObj = {
      ok: false,
      status: 404,
      msg: error.message
    }
  }

  return returnObj
}
