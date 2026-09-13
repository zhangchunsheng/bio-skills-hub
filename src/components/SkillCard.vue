<template>
  <RouterLink
    :to="`/skill/${handle}/${skill.slug}`"
    class="block bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-bio-700 hover:shadow-lg hover:shadow-bio-950 transition group"
  >
    <div class="flex items-start gap-3">
      <img
        v-if="skill.iconUrl"
        :src="skill.iconUrl"
        class="w-10 h-10 rounded-lg object-cover bg-slate-800 shrink-0"
        loading="lazy"
        alt=""
      />
      <div v-else class="w-10 h-10 rounded-lg bg-bio-900 flex items-center justify-center text-lg shrink-0">🧪</div>
      <div class="min-w-0">
        <h3 class="font-semibold text-slate-100 truncate group-hover:text-bio-300 transition">
          {{ skill.name || skill.slug }}
        </h3>
        <p class="text-xs text-slate-500 truncate">@{{ handle }}/{{ skill.slug }}</p>
      </div>
    </div>

    <p class="mt-3 text-sm text-slate-400 line-clamp-3 min-h-[3.75rem]">
      {{ skill.description_zh || skill.description || '暂无描述' }}
    </p>

    <div class="mt-3 flex items-center gap-3 text-xs text-slate-500">
      <span v-if="skill.version" class="px-1.5 py-0.5 rounded bg-slate-800">v{{ skill.version }}</span>
      <span v-if="categoryName" class="px-1.5 py-0.5 rounded bg-slate-800">{{ categoryName }}</span>
      <span class="ml-auto flex items-center gap-2">
        <span>⬇ {{ formatNum(skill.downloads) }}</span>
        <span>★ {{ formatNum(skill.stars) }}</span>
      </span>
    </div>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  skill: { type: Object, required: true },
  categories: { type: Array, default: () => [] },
})

const handle = computed(() => props.skill.namespace?.handle || props.skill.ownerName || '_')
const categoryName = computed(
  () => props.categories.find((c) => c.key === props.skill.category)?.name || ''
)

function formatNum(n) {
  if (!n) return 0
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return n
}
</script>
