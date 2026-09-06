const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export type Role = 'COMMUNITY_MEMBER' | 'RANGER' | 'SUPERVISOR' | 'ADMIN'

export type User = {
  id: number
  username: string
  first_name: string
  last_name: string
  role: Role
  phone_number: string
}

export type Incident = {
  id: number
  species: { id: number; name: string; danger_factor: number }
  community: { id: number; name: string; county: string }
  reporter: { id: number; username: string; role: Role }
  description: string
  animal_count: number
  severity: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL'
  status: 'REPORTED' | 'UNDER_REVIEW' | 'VERIFIED' | 'REJECTED' | 'DISPATCHED' | 'RESPONDING' | 'RESOLVED' | 'CLOSED'
  event_time: string
  verified: boolean
  risk_score: number
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL'
  location: { type: 'Point'; coordinates: [number, number] } | string
  created_at: string
  updated_at: string
}

export type Alert = {
  id: number
  incident: Incident
  title: string
  message: string
  priority: string
  created_at: string
}

type TokenResponse = { access: string; refresh: string }

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('wildguard_access_token')
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const details = Object.values(body).flat().join(' ')
    throw new Error(body.detail ?? (details || `Request failed (${response.status})`))
  }

  return response.json() as Promise<T>
}

export async function login(username: string, password: string) {
  const tokens = await request<TokenResponse>('/auth/token/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  localStorage.setItem('wildguard_access_token', tokens.access)
  localStorage.setItem('wildguard_refresh_token', tokens.refresh)
  return getCurrentUser()
}

export function logout() {
  localStorage.removeItem('wildguard_access_token')
  localStorage.removeItem('wildguard_refresh_token')
}

export function getCurrentUser() { return request<User>('/auth/me/') }
export function getIncidents() { return request<Incident[]>('/incidents/') }
export function getAlerts() { return request<Alert[]>('/alerts/') }

export function performIncidentAction(id: number, action: string) {
  return request<Incident>(`/incidents/${id}/action/`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  })
}