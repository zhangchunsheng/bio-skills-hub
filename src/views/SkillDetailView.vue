<template>
  <div>
    <div class="mb-4">
      <button class="text-sm text-slate-400 hover:text-bio-300 transition" @click="$router.back()">
        ← 返回
      </button>
    </div>

    <div v-if="error" class="text-center py-16 text-red-400 text-sm">加载失败：{{ error }}</div>
    <div v-else-if="loading" class="text-center py-16 text-slate-500 text-sm">加载中…</div>

    <template v-else-if="skill">
      <!-- Header -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div class="flex flex-wrap items-start gap-4">
          <img
            v-if="skill.iconUrl"
            :src="skill.iconUrl"
            class="w-16 h-16 rounded-xl object-cover bg-slate-800"
            alt=""
          />
          <div v-else class="w-16 h-16 rounded-xl bg-bio-900 flex items-center justify-center text-3xl">🧪</div>
          <div class="flex-1 min-w-0">
            <h1 class="text-2xl font-bold text-slate-100">{{ skill.name || skill.slug }}</h1>
            <p class="text-sm text-slate-500 mt-0.5">@{{ handle }}/{{ slug }} · v{{ version || '—' }}</p>
            <p class="mt-2 text-sm text-slate-300">{{ skill.description_zh || skill.description }}</p>
            <div class="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
              <span>⬇ 下载 {{ skill.downloads ?? 0 }}</span>
              <span>★ 收藏 {{ skill.stars ?? 0 }}</span>
              <span v-if="skill.source">来源：{{ skill.source }}</span>
              <a
                v-if="skill.upstream_url"
                :href="skill.upstream_url"
                target="_blank"
                class="text-bio-400 hover:underline"
              >上游仓库 ↗</a>
            </div>
          </div>
          <div class="shrink-0">
            <button
              v-if="isLocal"
              class="px-4 py-2 rounded-lg bg-slate-800 text-bio-300 text-sm cursor-default"
              disabled
            >✓ 已下载到本地</button>
            <button
              v-else
              class="px-4 py-2 rounded-lg bg-bio-600 hover:bg-bio-500 disabled:opacity-50 text-white text-sm font-medium transition"
              :disabled="downloading"
              @click="download"
            >{{ downloading ? '下载中…' : '下载到本地' }}</button>
            <p v-if="downloadError" class="mt-2 text-xs text-red-400">{{ downloadError }}</p>
          </div>
        </div>
      </div>

      <!-- Files -->
      <div class="mt-6 grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-4">
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-3 h-fit">
          <h2 class="text-xs font-semibold text-slate-500 uppercase tracking-wide px-2 mb-2">
            文件（{{ files.length }}）
          </h2>
          <button
            v-for="f in files"
            :key="f.path"
            class="w-full text-left px-2 py-1.5 rounded-md text-sm truncate transition"
            :class="selectedFile === f.path
              ? 'bg-bio-900/60 text-bio-300'
              : 'text-slate-400 hover:bg-slate-800'"
            @click="selectFile(f.path)"
          >{{ f.path }}</button>
          <p v-if="files.length === 0" class="px-2 text-sm text-slate-600">无文件信息</p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden min-h-[300px]">
          <div class="flex items-center justify-between px-4 py-2 border-b border-slate-800 text-xs text-slate-500">
            <span class="truncate">{{ selectedFile || '选择左侧文件预览' }}</span>
            <span v-if="fileLoading">加载中…</span>
          </div>
          <pre
            v-if="fileContent !== null"
            class="scroll-slim p-4 text-xs leading-relaxed text-slate-300 overflow-auto max-h-[70vh] whitespace-pre-wrap break-words"
          >{{ fileContent }}</pre>
          <div v-else-if="!fileLoading" class="p-8 text-center text-sm text-slate-600">
            点击文件查看内容
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api.js'

const props = defineProps({
  handle: { type: String, required: true },
  slug: { type: String, required: true },
})

const skill = ref(null)
const version = ref('')
const files = ref([])
const isLocal = ref(false)
const loading = ref(true)
const error = ref('')
const downloading = ref(false)
const downloadError = ref('')

const selectedFile = ref('')
const fileContent = ref(null)
const fileLoading = ref(false)

async function selectFile(path) {
  selectedFile.value = path
  fileContent.value = null
  fileLoading.value = true
  try {
    const url = isLocal.value
      ? api.getLocalFileUrl(props.handle, props.slug, path)
      : api.getRemoteFileUrl(props.handle, props.slug, path)
    const res = await fetch(url)
    fileContent.value = res.ok ? await res.text() : `加载失败：${res.status}`
  } catch (e) {
    fileContent.value = `加载失败：${e.message}`
  } finally {
    fileLoading.value = false
  }
}

async function download() {
  downloading.value = true
  downloadError.value = ''
  try {
    await api.downloadSkill(props.handle, props.slug)
    isLocal.value = true
  } catch (e) {
    downloadError.value = e.message
  } finally {
    downloading.value = false
  }
}

onMounted(async () => {
  try {
    const data = await api.getSkill(props.handle, props.slug)
    skill.value = data.skill
    version.value = data.version || ''
    files.value = data.files || []
    isLocal.value = data.local
    const skillMd = files.value.find((f) => /skill\.md$/i.test(f.path))
    if (skillMd) selectFile(skillMd.path)
    else if (files.value.length) selectFile(files.value[0].path)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
