// Local storage for downloaded skills.
// Layout:
//   data/
//     index.json                        — list of downloaded skills (metadata)
//     downloads/<handle>__<slug>/       — one dir per skill
//       meta.json                       — metadata captured at download time
//       files/<original paths...>       — the skill's files (SKILL.md etc.)

import fs from 'node:fs/promises'
import path from 'node:path'

const DATA_DIR = path.resolve(process.cwd(), 'data')
const INDEX_FILE = path.join(DATA_DIR, 'index.json')
export const DOWNLOADS_DIR = path.join(DATA_DIR, 'downloads')

function skillKey(handle, slug) {
  return `${handle || '_'}__${slug}`.replace(/[^\w@.-]/g, '_')
}

async function readIndex() {
  try {
    return JSON.parse(await fs.readFile(INDEX_FILE, 'utf8'))
  } catch {
    return []
  }
}

async function writeIndex(index) {
  await fs.mkdir(DATA_DIR, { recursive: true })
  await fs.writeFile(INDEX_FILE, JSON.stringify(index, null, 2))
}

export async function listDownloads() {
  return readIndex()
}

export async function findDownload(handle, slug) {
  const index = await readIndex()
  return index.find((s) => s.handle === handle && s.slug === slug) || null
}

export function isSafeRelPath(p) {
  return (
    typeof p === 'string' &&
    p.length > 0 &&
    !p.startsWith('/') &&
    !p.split('/').includes('..')
  )
}

export async function saveDownload({ handle, slug, meta, files }) {
  // files: [{ path, content(Buffer) }]
  const dir = path.join(DOWNLOADS_DIR, skillKey(handle, slug))
  const filesDir = path.join(dir, 'files')
  await fs.mkdir(filesDir, { recursive: true })
  // clean previous files
  await fs.rm(filesDir, { recursive: true, force: true })
  await fs.mkdir(filesDir, { recursive: true })

  for (const f of files) {
    if (!isSafeRelPath(f.path)) continue
    const dest = path.join(filesDir, f.path)
    await fs.mkdir(path.dirname(dest), { recursive: true })
    await fs.writeFile(dest, f.content)
  }

  const record = {
    handle,
    slug,
    name: meta.name || slug,
    description: meta.description || meta.description_zh || '',
    description_zh: meta.description_zh || '',
    category: meta.category || '',
    version: meta.version || '',
    iconUrl: meta.iconUrl || '',
    source: meta.source || '',
    downloads: meta.downloads || 0,
    stars: meta.stars || 0,
    downloadedAt: Date.now(),
    files: files.filter((f) => isSafeRelPath(f.path)).map((f) => f.path),
    dir,
  }
  await fs.writeFile(path.join(dir, 'meta.json'), JSON.stringify(record, null, 2))

  const index = await readIndex()
  const i = index.findIndex((s) => s.handle === handle && s.slug === slug)
  if (i >= 0) index[i] = record
  else index.unshift(record)
  await writeIndex(index)
  return record
}

export async function removeDownload(handle, slug) {
  const dir = path.join(DOWNLOADS_DIR, skillKey(handle, slug))
  await fs.rm(dir, { recursive: true, force: true })
  const index = await readIndex()
  await writeIndex(index.filter((s) => !(s.handle === handle && s.slug === slug)))
}

export async function readLocalFile(handle, slug, relPath) {
  if (!isSafeRelPath(relPath)) throw new Error('invalid path')
  const file = path.join(DOWNLOADS_DIR, skillKey(handle, slug), 'files', relPath)
  return fs.readFile(file)
}
