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

// All endpoints are served by the local PHP backend from the local SQLite
// database — no runtime dependency on skillhub.cn.
export const api = {
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
}
