const TOKEN_KEY = 'bsh_admin_token'
const USER_KEY = 'bsh_admin_user'

export const auth = {
  get token() {
    return localStorage.getItem(TOKEN_KEY) || ''
  },
  get user() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
    } catch {
      return null
    }
  },
  save(token, user) {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}

async function request(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', Accept: 'application/json', ...(options.headers || {}) }
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`

  const res = await fetch(url, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (res.status === 401) {
    auth.clear()
    if (!location.pathname.endsWith('/login')) {
      location.assign((import.meta.env.BASE_URL || '/') + 'login')
    }
    throw new Error(data.error || '未登录')
  }
  if (!res.ok) {
    const firstError = data.errors ? Object.values(data.errors)[0]?.[0] : null
    throw new Error(data.error || firstError || data.message || `HTTP ${res.status}`)
  }
  return data
}

export const api = {
  login: (payload) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  logout: () => request('/api/auth/logout', { method: 'POST' }),

  stats: () => request('/api/stats'),
  categories: () => request('/api/categories'),
  listSkills: (params) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.set(k, v)
    })
    return request(`/api/admin/skills?${q}`)
  },
  getSkill: (id) => request(`/api/admin/skills/${id}`),
  updateSkill: (id, data) => request(`/api/admin/skills/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteSkill: (id) => request(`/api/admin/skills/${id}`, { method: 'DELETE' }),
  syncStatus: () => request('/api/admin/sync-status'),
  startSync: (opts) => request('/api/admin/sync', { method: 'POST', body: JSON.stringify(opts) }),

  listUsers: (params) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.set(k, v)
    })
    return request(`/api/admin/users?${q}`)
  },
  createUser: (data) => request('/api/admin/users', { method: 'POST', body: JSON.stringify(data) }),
  updateUser: (id, data) => request(`/api/admin/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteUser: (id) => request(`/api/admin/users/${id}`, { method: 'DELETE' }),
}
