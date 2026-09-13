// Client for the SkillHub.cn public API (https://api.skillhub.cn).
// Discovered from the site's frontend bundle; no auth required for reads.

const BASE = 'https://api.skillhub.cn'

async function getJson(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'bio-skills-hub/0.1', Accept: 'application/json' },
    signal: AbortSignal.timeout(20000),
  })
  if (!res.ok) throw new Error(`upstream ${res.status} for ${url}`)
  return res.json()
}

/**
 * Search / list skills.
 * Supports: page, pageSize, keyword, category, sortBy, order, source
 */
export async function searchSkills(query) {
  const params = new URLSearchParams()
  const { page = 1, pageSize = 24, keyword, category, sortBy, order } = query
  params.set('page', String(page))
  params.set('pageSize', String(Math.min(Number(pageSize) || 24, 100)))
  if (sortBy) params.set('sortBy', sortBy)
  if (order) params.set('order', order)
  if (keyword && keyword.trim()) params.set('keyword', keyword.trim())
  if (category) params.set('category', category)
  const data = await getJson(`${BASE}/api/skills?${params}`)
  if (data.code !== 0) throw new Error(data.message || 'upstream error')
  return data.data // { skills, total, page, pageSize }
}

export async function getCategories() {
  return getJson(`${BASE}/api/v1/categories`)
}

export async function getSkillDetail(slug, namespace) {
  const params = new URLSearchParams()
  if (namespace) params.set('namespace', namespace)
  return getJson(`${BASE}/api/v1/skills/${encodeURIComponent(slug)}?${params}`)
}

export async function getSkillFiles(slug, namespace) {
  const params = new URLSearchParams()
  if (namespace) params.set('namespace', namespace)
  return getJson(`${BASE}/api/v1/skills/${encodeURIComponent(slug)}/files?${params}`)
}

/**
 * Fetch a single file's content. The upstream /file endpoint 302-redirects
 * to Tencent COS; fetch follows redirects automatically.
 */
export async function getSkillFileContent(slug, namespace, path) {
  const params = new URLSearchParams({ path })
  if (namespace) params.set('namespace', namespace)
  const url = `${BASE}/api/v1/skills/${encodeURIComponent(slug)}/file?${params}`
  const res = await fetch(url, {
    headers: { 'User-Agent': 'bio-skills-hub/0.1' },
    signal: AbortSignal.timeout(30000),
    redirect: 'follow',
  })
  if (!res.ok) throw new Error(`upstream ${res.status} for file ${path}`)
  return Buffer.from(await res.arrayBuffer())
}
