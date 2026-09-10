const API_URL = import.meta.env.VITE_API_URL || '/api'

export const getSession = () => JSON.parse(localStorage.getItem('nexus_session') || 'null')
export const saveSession = (session) => localStorage.setItem('nexus_session', JSON.stringify(session))
export const clearSession = () => localStorage.removeItem('nexus_session')

function notifySessionExpired() {
  clearSession()
  window.dispatchEvent(new Event('nexus:session-expired'))
}

async function refreshSession(session) {
  if (!session?.refresh_token) return null

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: session.refresh_token }),
  })

  if (!response.ok) return null

  const nextSession = await response.json()
  saveSession(nextSession)
  return nextSession
}


export async function apiRequest(path, options = {}, retry = true) {
  const session = getSession()
  const headers = new Headers(options.headers || {})
  if (!(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  if (session?.access_token) headers.set('Authorization', `Bearer ${session.access_token}`)

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (response.status === 401 && retry && session?.refresh_token) {
    if (await refreshSession(session)) {
      return apiRequest(path, options, false)
    }
  }

  if (response.status === 401 && session?.access_token) {
    notifySessionExpired()
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || body.message || `Request failed (${response.status})`)
  }

  return response.status === 204 ? null : response.json()
}

export async function streamRequest(path, body, onEvent) {
  let session = getSession()
  let response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.access_token}` },
    body: JSON.stringify(body),
  })

  if (response.status === 401 && session?.refresh_token) {
    session = await refreshSession(session)
    if (session) {
      response = await fetch(`${API_URL}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.access_token}` },
        body: JSON.stringify(body),
      })
    }
  }

  if (response.status === 401 && session?.access_token) {
    notifySessionExpired()
  }

  if (!response.ok || !response.body) {
    const responseBody = await response.json().catch(() => ({}))
    throw new Error(responseBody.detail || responseBody.message || 'The research stream could not be opened.')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done })
    const chunks = buffer.split(/\r?\n\r?\n/)
    buffer = chunks.pop() || ''

    for (const chunk of chunks) {
      const data = chunk
        .split(/\r?\n/)
        .filter((item) => item.startsWith('data:'))
        .map((item) => item.slice(5).trim())
        .join('\n')
      if (data) onEvent(JSON.parse(data))
    }

    if (done) break
  }
}
