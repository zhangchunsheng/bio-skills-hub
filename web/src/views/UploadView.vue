<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-bold">上传技能</h1>
      <p class="text-sm text-slate-500 mt-1">
        分享你自己的生物分析 Agent Skill，需包含 SKILL.md 文件
      </p>
    </div>

    <!-- 未登录 -->
    <div v-if="!authState.user" class="text-center py-20 bg-slate-900 border border-slate-800 rounded-xl">
      <p class="text-5xl mb-4">🔐</p>
      <p class="text-slate-400 text-sm">上传技能需要先登录</p>
      <button
        class="mt-4 px-5 py-2 rounded-lg bg-bio-600 hover:bg-bio-500 text-white text-sm font-medium transition"
        @click="showAuth = true"
      >登录 / 注册</button>
    </div>

    <template v-else>
      <!-- 上传表单 -->
      <form class="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4" @submit.prevent="submit">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label class="block">
            <span class="text-xs text-slate-500">名称 *</span>
            <input v-model="form.name" required placeholder="如：RNA-seq 差异表达分析"
              class="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
          </label>
          <label class="block">
            <span class="text-xs text-slate-500">slug（小写字母/数字/连字符，留空自动生成）</span>
            <input v-model="form.slug" placeholder="rna-seq-de-analysis" pattern="[a-z0-9][a-z0-9-]*"
              class="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
          </label>
          <label class="block">
            <span class="text-xs text-slate-500">版本</span>
            <input v-model="form.version" placeholder="1.0.0"
              class="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
          </label>
          <label class="block">
            <span class="text-xs text-slate-500">分类</span>
            <select v-model="form.category"
              class="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500">
              <option value="">未分类</option>
              <option v-for="c in categories" :key="c.key" :value="c.key">{{ c.name || c.key }}</option>
            </select>
          </label>
        </div>
        <label class="block">
          <span class="text-xs text-slate-500">中文描述</span>
          <textarea v-model="form.description_zh" rows="2" placeholder="简要说明技能用途…"
            class="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"></textarea>
        </label>
        <label class="block">
          <span class="text-xs text-slate-500">英文描述</span>
          <textarea v-model="form.description" rows="2"
            class="mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"></textarea>
        </label>
        <label class="block">
          <span class="text-xs text-slate-500">技能文件 *（必须包含 SKILL.md，最多 50 个，单个 ≤ 2MB）</span>
          <input ref="fileInput" type="file" multiple required
            class="mt-1 w-full text-sm text-slate-400 file:mr-3 file:px-3 file:py-1.5 file:rounded-lg file:border-0 file:bg-bio-700 file:text-white hover:file:bg-bio-600 file:cursor-pointer" />
        </label>

        <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
        <p v-if="success" class="text-sm text-bio-400">✓ 上传成功</p>

        <button type="submit" :disabled="uploading"
          class="px-5 py-2 rounded-lg bg-bio-600 hover:bg-bio-500 disabled:opacity-50 text-white text-sm font-medium transition">
          {{ uploading ? '上传中…' : '上传技能' }}
        </button>
      </form>

      <!-- 我的上传 -->
      <div class="mt-8">
        <h2 class="text-lg font-semibold mb-3">我的上传（{{ mySkills.length }}）</h2>
        <p v-if="mySkills.length === 0" class="text-sm text-slate-600">还没有上传过技能</p>
        <div v-else class="space-y-2">
          <div v-for="s in mySkills" :key="s.id"
            class="bg-slate-900 border border-slate-800 rounded-xl p-3 flex items-center gap-3">
            <div class="flex-1 min-w-0">
              <RouterLink :to="`/skill/${s.handle}/${s.slug}`" class="font-medium text-slate-100 hover:text-bio-300 transition">
                {{ s.name }}
              </RouterLink>
              <p class="text-xs text-slate-500">@{{ s.handle }}/{{ s.slug }} · v{{ s.version }} · {{ s.files_count }} 个文件</p>
            </div>
            <button class="px-3 py-1.5 rounded-lg border border-slate-700 text-sm text-red-400 hover:border-red-600 transition"
              :disabled="removing === s.id" @click="remove(s)">
              {{ removing === s.id ? '删除中…' : '删除' }}
            </button>
          </div>
        </div>
      </div>
    </template>

    <AuthDialog v-if="showAuth" @close="showAuth = false" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { api } from '../api.js'
import { authState } from '../store.js'
import AuthDialog from '../components/AuthDialog.vue'

const showAuth = ref(false)
const categories = ref([])
const mySkills = ref([])
const fileInput = ref(null)
const form = reactive({ name: '', slug: '', version: '1.0.0', category: '', description: '', description_zh: '' })
const uploading = ref(false)
const error = ref('')
const success = ref(false)
const removing = ref(null)

async function loadMine() {
  if (!authState.user) return
  try {
    mySkills.value = (await api.mySkills()).skills || []
  } catch {}
}

async function submit() {
  uploading.value = true
  error.value = ''
  success.value = false
  try {
    const fd = new FormData()
    Object.entries(form).forEach(([k, v]) => v && fd.append(k, v))
    if (form.category) {
      const cat = categories.value.find((c) => c.key === form.category)
      if (cat?.name) fd.append('category_name', cat.name)
    }
    for (const f of fileInput.value.files) fd.append('files[]', f, f.name)
    await api.uploadSkill(fd)
    success.value = true
    form.name = form.slug = form.description = form.description_zh = ''
    fileInput.value.value = ''
    loadMine()
  } catch (e) {
    error.value = e.message
  } finally {
    uploading.value = false
  }
}

async function remove(s) {
  if (!confirm(`确定删除「${s.name}」吗？`)) return
  removing.value = s.id
  try {
    await api.deleteMySkill(s.id)
    mySkills.value = mySkills.value.filter((x) => x.id !== s.id)
  } catch (e) {
    alert('删除失败：' + e.message)
  } finally {
    removing.value = null
  }
}

watch(() => authState.user, loadMine)

onMounted(() => {
  loadMine()
  api.getCategories().then((d) => (categories.value = d.items || [])).catch(() => {})
})
</script>
