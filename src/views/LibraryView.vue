<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">本地技能库</h1>
        <p class="text-sm text-slate-500 mt-1">
          已下载 {{ skills.length }} 个技能，保存在服务器 <code class="text-slate-400">data/downloads/</code> 目录
        </p>
      </div>
      <button
        class="px-3 py-1.5 rounded-lg border border-slate-700 text-sm text-slate-400 hover:border-bio-600 hover:text-bio-300 transition"
        @click="load"
      >刷新</button>
    </div>

    <div v-if="error" class="text-center py-16 text-red-400 text-sm">加载失败：{{ error }}</div>
    <div v-else-if="loading" class="text-center py-16 text-slate-500 text-sm">加载中…</div>
    <div v-else-if="skills.length === 0" class="text-center py-20">
      <p class="text-5xl mb-4">📦</p>
      <p class="text-slate-500 text-sm">还没有下载任何技能</p>
      <RouterLink to="/" class="inline-block mt-4 px-4 py-2 rounded-lg bg-bio-600 hover:bg-bio-500 text-white text-sm transition">
        去技能市场看看
      </RouterLink>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="s in skills"
        :key="s.handle + '/' + s.slug"
        class="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center gap-4"
      >
        <img
          v-if="s.iconUrl"
          :src="s.iconUrl"
          class="w-10 h-10 rounded-lg object-cover bg-slate-800"
          loading="lazy"
          alt=""
        />
        <div v-else class="w-10 h-10 rounded-lg bg-bio-900 flex items-center justify-center text-lg shrink-0">🧪</div>

        <div class="flex-1 min-w-0">
          <RouterLink
            :to="`/skill/${s.handle}/${s.slug}`"
            class="font-semibold text-slate-100 hover:text-bio-300 transition"
          >{{ s.name }}</RouterLink>
          <p class="text-xs text-slate-500 truncate">
            @{{ s.handle }}/{{ s.slug }} · v{{ s.version || '—' }} ·
            {{ s.files.length }} 个文件 · 下载于 {{ formatDate(s.downloadedAt) }}
          </p>
          <p class="text-sm text-slate-400 truncate mt-0.5">{{ s.description_zh || s.description }}</p>
        </div>

        <div class="flex gap-2 shrink-0">
          <RouterLink
            :to="`/skill/${s.handle}/${s.slug}`"
            class="px-3 py-1.5 rounded-lg border border-slate-700 text-sm text-slate-300 hover:border-bio-600 transition"
          >查看</RouterLink>
          <button
            class="px-3 py-1.5 rounded-lg border border-slate-700 text-sm text-red-400 hover:border-red-600 transition"
            :disabled="removing === s.handle + '/' + s.slug"
            @click="remove(s)"
          >{{ removing === s.handle + '/' + s.slug ? '删除中…' : '删除' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api.js'

const skills = ref([])
const loading = ref(true)
const error = ref('')
const removing = ref('')

function formatDate(ts) {
  return new Date(ts).toLocaleString('zh-CN')
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    skills.value = (await api.getLocalSkills()).skills || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function remove(s) {
  if (!confirm(`确定删除本地技能「${s.name}」吗？`)) return
  removing.value = s.handle + '/' + s.slug
  try {
    await api.removeLocal(s.handle, s.slug)
    skills.value = skills.value.filter((x) => !(x.handle === s.handle && x.slug === s.slug))
  } catch (e) {
    alert('删除失败：' + e.message)
  } finally {
    removing.value = ''
  }
}

onMounted(load)
</script>
