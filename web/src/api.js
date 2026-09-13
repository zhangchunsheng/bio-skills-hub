const TOKEN_KEY = 'bsh_token'
const USER_KEY = 'bsh_user'

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
  const headers = { Accept: 'application/json', ...(options.headers || {}) }
  if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json'
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`

  const res = await fetch(url, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    // Laravel 验证错误格式：{ message, errors: { field: [...] } }
    const firstError = data.errors ? Object.values(data.errors)[0]?.[0] : null
    throw new Error(data.error || firstError || data.message || `HTTP ${res.status}`)
  }
  return data
}

// 用户端 API：全部来自本地 Laravel + SQLite，无外网依赖
export const api = {
  // 认证
  register: (payload) => request('/api/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  logout: () => request('/api/auth/logout', { method: 'POST' }),
  me: () => request('/api/auth/me'),
  changePassword: (payload) => request('/api/auth/password', { method: 'POST', body: JSON.stringify(payload) }),

  // 技能浏览
  searchSkills: (params) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.set(k, v)
    })
    return request(`/api/skills?${q}`)
  },
  getCategories: () => request('/api/categories'),
  getStats: () => request('/api/stats'),
  getSkill: (handle, slug) => request(`/api/skills/${handle}/${slug}`),
  getFileUrl: (handle, slug, path) =>
    `/api/skills/${handle}/${slug}/file?path=${encodeURIComponent(path)}`,

  // 上传（需登录）
  uploadSkill: (formData) => request('/api/skills', { method: 'POST', body: formData }),
  mySkills: () => request('/api/my/skills'),
  deleteMySkill: (id) => request(`/api/my/skills/${id}`, { method: 'DELETE' }),
}
