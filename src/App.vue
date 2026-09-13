<template>
  <div class="min-h-screen flex flex-col">
    <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-20">
      <div class="max-w-7xl mx-auto px-4 h-14 flex items-center gap-6">
        <RouterLink to="/" class="flex items-center gap-2 font-bold text-lg">
          <span class="text-2xl">🧬</span>
          <span class="text-bio-400">Bio Skills Hub</span>
        </RouterLink>
        <nav class="flex gap-1 text-sm">
          <RouterLink
            to="/"
            class="px-3 py-1.5 rounded-md hover:bg-slate-800 transition"
            :class="{ 'bg-slate-800 text-bio-300': $route.name === 'home' }"
          >技能库</RouterLink>
        </nav>
        <div class="ml-auto text-xs text-slate-500 hidden sm:block">
          本地离线技能库 · SQLite
        </div>
      </div>
    </header>

    <main class="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
      <RouterView />
    </main>

    <footer class="border-t border-slate-800 py-4 text-center text-xs text-slate-600">
      Bio Skills Hub · 技能内容来源于
      <a href="https://www.skillhub.cn/" target="_blank" class="text-slate-500 hover:text-bio-400">SkillHub 社区</a>
      的公开发布，已离线收录 · 仅供学习研究使用
    </footer>
  </div>
</template>
