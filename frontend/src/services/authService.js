import { apiRequest, clearSession, getSession, saveSession } from '../api/client'

export async function login(credentials) {
  const session = await apiRequest('/auth/login', { method: 'POST', body: JSON.stringify(credentials) }, false)
  saveSession(session)
  return session
}

export async function register(credentials) {
  const session = await apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(credentials) }, false)
  saveSession(session)
  return session
}

export async function logout() {
  const session = getSession()
  if (session?.refresh_token) {
    await apiRequest('/auth/logout', { method: 'POST', body: JSON.stringify({ refresh_token: session.refresh_token }) }).catch(() => {})
  }
  clearSession()
}
