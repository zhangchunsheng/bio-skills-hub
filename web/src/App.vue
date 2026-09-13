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
          <RouterLink
            to="/upload"
            class="px-3 py-1.5 rounded-md hover:bg-slate-800 transition"
            :class="{ 'bg-slate-800 text-bio-300': $route.name === 'upload' }"
          >上传技能</RouterLink>
        </nav>

        <div class="ml-auto flex items-center gap-3">
          <template v-if="authState.user">
            <span class="text-sm text-slate-400">
              {{ authState.user.name }}
              <span v-if="authState.user.role === 'admin'" class="ml-1 px-1.5 py-0.5 rounded bg-bio-900 text-bio-300 text-xs">管理员</span>
            </span>
            <button class="text-xs text-slate-500 hover:text-slate-300 transition" @click="showPassword = true">修改密码</button>
            <button class="text-xs text-slate-500 hover:text-slate-300 transition" @click="authState.logout()">退出</button>
          </template>
          <button
            v-else
            class="px-3 py-1.5 rounded-lg bg-bio-600 hover:bg-bio-500 text-white text-sm transition"
            @click="showAuth = true"
          >登录 / 注册</button>
        </div>
      </div>
    </header>

    <main class="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
      <RouterView />
    </main>

    <footer class="border-t border-slate-800 py-4 text-center text-xs text-slate-600">
      Bio Skills Hub · 技能内容来源于
      <a href="https://www.skillhub.cn/" target="_blank" class="text-slate-500 hover:text-bio-400">SkillHub 社区</a>
      的公开发布与用户上传 · 仅供学习研究使用
    </footer>

    <AuthDialog v-if="showAuth" @close="showAuth = false" />
    <PasswordDialog v-if="showPassword" @close="showPassword = false" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authState } from './store.js'
import AuthDialog from './components/AuthDialog.vue'
import PasswordDialog from './components/PasswordDialog.vue'

const showAuth = ref(false)
const showPassword = ref(false)
</script>
