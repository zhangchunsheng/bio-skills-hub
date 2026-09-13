import express from 'express'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import * as hub from './skillhub.js'
import * as store from './storage.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const app = express()
const PORT = process.env.PORT || 3001

app.use(express.json())

const wrap = (fn) => (req, res) =>
  fn(req, res).catch((err) => {
    console.error(err)
    res.status(502).json({ error: String(err.message || err) })
  })

// ---- Remote (upstream SkillHub.cn) ----

app.get('/api/remote/skills', wrap(async (req, res) => {
  res.json(await hub.searchSkills(req.query))
}))

app.get('/api/remote/categories', wrap(async (_req, res) => {
  res.json(await hub.getCategories())
}))

// Normalize the upstream detail payload (metadata is nested under detail.skill
// with displayName/summary fields) into the same shape the list API returns.
function normalizeDetail(detail, slug, version) {
  const raw = detail?.skill || {}
  return {
    name: raw.displayName || detail?.slug || slug,
    slug: raw.slug || slug,
    description: raw.summary || '',
    description_zh: raw.summary_zh || '',
    category: raw.category || '',
    iconUrl: raw.iconUrl || '',
    source: raw.source || '',
    sourceUrl: raw.sourceUrl || '',
    upstream_url: raw.upstream_url || '',
    verified: !!raw.verified,
    downloads: raw.stats?.downloads ?? 0,
    stars: raw.stats?.stars ?? 0,
    installs: raw.stats?.installs ?? 0,
    version: version || detail?.latestVersion?.version || '',
  }
}

app.get('/api/remote/skills/:handle/:slug', wrap(async (req, res) => {
  const { handle, slug } = req.params
  const [detail, fileList] = await Promise.all([
    hub.getSkillDetail(slug, handle),
    hub.getSkillFiles(slug, handle).catch(() => ({ files: [] })),
  ])
  const local = await store.findDownload(handle, slug)
  const version = fileList.version || detail?.latestVersion?.version || ''
  res.json({
    skill: normalizeDetail(detail, slug, version),
    owner: detail?.owner || null,
    securityReports: detail?.securityReports || null,
    files: fileList.files || [],
    version,
    local: !!local,
  })
}))

// Proxy a remote file's content (used for preview without downloading)
app.get('/api/remote/skills/:handle/:slug/file', wrap(async (req, res) => {
  const { handle, slug } = req.params
  const buf = await hub.getSkillFileContent(slug, handle, req.query.path)
  res.type('text/plain; charset=utf-8').send(buf)
}))

// ---- Local downloads ----

app.get('/api/local/skills', wrap(async (_req, res) => {
  res.json({ skills: await store.listDownloads() })
}))

// Download a skill (all files) to local disk
app.post('/api/local/download', wrap(async (req, res) => {
  const { handle, slug } = req.body || {}
  if (!handle || !slug) return res.status(400).json({ error: 'handle and slug required' })

  const detail = await hub.getSkillDetail(slug, handle)
  const { files = [], version } = await hub.getSkillFiles(slug, handle)
  const contents = []
  for (const f of files) {
    const content = await hub.getSkillFileContent(slug, handle, f.path)
    contents.push({ path: f.path, content })
  }
  const record = await store.saveDownload({
    handle,
    slug,
    meta: normalizeDetail(detail, slug, version || detail?.latestVersion?.version),
    files: contents,
  })
  res.json({ ok: true, record })
}))

app.delete('/api/local/skills/:handle/:slug', wrap(async (req, res) => {
  await store.removeDownload(req.params.handle, req.params.slug)
  res.json({ ok: true })
}))

app.get('/api/local/skills/:handle/:slug/file', wrap(async (req, res) => {
  const buf = await store.readLocalFile(req.params.handle, req.params.slug, req.query.path)
  res.type('text/plain; charset=utf-8').send(buf)
}))

// ---- Static frontend (production build) ----
if (process.env.NODE_ENV === 'production') {
  const dist = path.resolve(__dirname, '..', 'dist')
  app.use(express.static(dist))
  app.get('*', (_req, res) => res.sendFile(path.join(dist, 'index.html')))
}

app.listen(PORT, () => {
  console.log(`bio-skills-hub server listening on http://localhost:${PORT}`)
})
