async function request(url, options) {
  const res = await fetch(url, options)
  if (!res.ok) {
    let msg = `${res.status}`
    try {
      msg = (await res.json()).error || msg
    } catch {}
    throw new Error(msg)
  }
  return res.json()
}

export const api = {
  searchSkills: (params) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.set(k, v)
    })
    return request(`/api/remote/skills?${q}`)
  },
  getCategories: () => request('/api/remote/categories'),
  getSkill: (handle, slug) => request(`/api/remote/skills/${handle}/${slug}`),
  getRemoteFileUrl: (handle, slug, path) =>
    `/api/remote/skills/${handle}/${slug}/file?path=${encodeURIComponent(path)}`,
  getLocalSkills: () => request('/api/local/skills'),
  downloadSkill: (handle, slug) =>
    request('/api/local/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ handle, slug }),
    }),
  removeLocal: (handle, slug) =>
    request(`/api/local/skills/${handle}/${slug}`, { method: 'DELETE' }),
  getLocalFileUrl: (handle, slug, path) =>
    `/api/local/skills/${handle}/${slug}/file?path=${encodeURIComponent(path)}`,
}
