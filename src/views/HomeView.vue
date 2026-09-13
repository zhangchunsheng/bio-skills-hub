<template>
  <div>
    <!-- Hero -->
    <section class="text-center py-8">
      <h1 class="text-3xl font-bold">
        发现<span class="text-bio-400">生物分析</span> AI 技能
      </h1>
      <p class="mt-2 text-slate-400 text-sm">
        从 SkillHub 社区检索生物信息、基因组学、药物研发等方向的 Agent Skills，一键下载到本地使用
      </p>

      <!-- Search -->
      <form class="mt-6 max-w-xl mx-auto flex gap-2" @submit.prevent="doSearch(1)">
        <input
          v-model="keyword"
          type="search"
          placeholder="搜索技能，如 genomics、protein、scRNA-seq…"
          class="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-bio-500 placeholder:text-slate-600"
        />
        <button
          type="submit"
          class="px-5 py-2.5 rounded-lg bg-bio-600 hover:bg-bio-500 text-white text-sm font-medium transition"
        >搜索</button>
      </form>

      <!-- Bio topic chips -->
      <div class="mt-4 flex flex-wrap justify-center gap-2">
        <button
          v-for="t in topics"
          :key="t.keyword"
          class="px-3 py-1 rounded-full text-xs border transition"
          :class="activeKeyword === t.keyword
            ? 'bg-bio-600 border-bio-500 text-white'
            : 'border-slate-700 text-slate-400 hover:border-bio-600 hover:text-bio-300'"
          @click="selectTopic(t.keyword)"
        >{{ t.label }}</button>
      </div>
    </section>

    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-3 mb-4 text-sm">
      <select
        v-model="category"
        class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-bio-500"
        @change="doSearch(1)"
      >
        <option value="">全部分类</option>
        <option v-for="c in categories" :key="c.key" :value="c.key">{{ c.name }}</option>
      </select>
      <select
        v-model="sort"
        class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-bio-500"
        @change="doSearch(1)"
      >
        <option value="">综合排序</option>
        <option value="downloads">下载量</option>
        <option value="stars">收藏数</option>
        <option value="newest">最新发布</option>
      </select>
      <span v-if="total !== null" class="text-slate-500 text-xs ml-auto">
        共 {{ total.toLocaleString() }} 个技能
      </span>
    </div>

    <!-- States -->
    <div v-if="error" class="text-center py-16 text-red-400 text-sm">加载失败：{{ error }}</div>
    <div v-else-if="loading" class="text-center py-16 text-slate-500 text-sm">加载中…</div>
    <div v-else-if="skills.length === 0" class="text-center py-16 text-slate-500 text-sm">
      没有找到相关技能，换个关键词试试
    </div>

    <!-- Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <SkillCard v-for="s in skills" :key="s.namespace?.canonicalName || s.slug" :skill="s" :categories="categories" />
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-8 flex justify-center items-center gap-2 text-sm">
      <button
        class="px-3 py-1.5 rounded-lg border border-slate-700 disabled:opacity-40 hover:border-bio-600 transition"
        :disabled="page <= 1"
        @click="doSearch(page - 1)"
      >上一页</button>
      <span class="text-slate-500 px-2">{{ page }} / {{ totalPages }}</span>
      <button
        class="px-3 py-1.5 rounded-lg border border-slate-700 disabled:opacity-40 hover:border-bio-600 transition"
        :disabled="page >= totalPages"
        @click="doSearch(page + 1)"
      >下一页</button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api.js'
import SkillCard from '../components/SkillCard.vue'

const topics = [
  { label: '生物医药', keyword: 'bio' },
  { label: '基因组学', keyword: 'genomics' },
  { label: '蛋白质', keyword: 'protein' },
  { label: '单细胞测序', keyword: 'single-cell' },
  { label: '药物研发', keyword: 'drug discovery' },
  { label: '临床医疗', keyword: 'clinical' },
  { label: '文献调研', keyword: 'literature research' },
  { label: '数据分析', keyword: 'data analysis' },
]

const keyword = ref('bio')
const activeKeyword = ref('bio')
const category = ref('')
const sort = ref('')
const page = ref(1)
const pageSize = 24

const skills = ref([])
const total = ref(null)
const categories = ref([])
const loading = ref(false)
const error = ref('')

const totalPages = computed(() =>
  total.value === null ? 0 : Math.min(Math.ceil(total.value / pageSize), 50)
)

function selectTopic(kw) {
  keyword.value = kw
  doSearch(1)
}

async function doSearch(p) {
  page.value = p
  loading.value = true
  error.value = ''
  try {
    const params = { page: p, pageSize, keyword: keyword.value, category: category.value }
    if (sort.value) {
      if (sort.value === 'newest') {
        params.sortBy = 'created_at'
        params.order = 'desc'
      } else {
        params.sortBy = sort.value
        params.order = 'desc'
      }
    }
    const data = await api.searchSkills(params)
    skills.value = data.skills || []
    total.value = data.total ?? null
    activeKeyword.value = keyword.value
  } catch (e) {
    error.value = e.message
    skills.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  doSearch(1)
  try {
    const data = await api.getCategories()
    categories.value = (data.items || []).filter((c) => c.level === 1 && c.active)
  } catch {}
})
</script>
