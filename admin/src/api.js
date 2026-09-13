async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    ...options,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || data.message || `HTTP ${res.status}`)
  return data
}

export const api = {
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
}
