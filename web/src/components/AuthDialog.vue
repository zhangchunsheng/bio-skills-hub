<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-sm mx-4">
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-lg font-bold">{{ mode === 'login' ? '登录' : '注册' }}</h2>
        <button class="text-slate-500 hover:text-slate-300 text-xl leading-none" @click="$emit('close')">×</button>
      </div>

      <form class="space-y-3" @submit.prevent="submit">
        <input
          v-if="mode === 'register'"
          v-model="form.name"
          type="text"
          required
          placeholder="昵称"
          class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
        />
        <input
          v-model="form.email"
          type="email"
          required
          placeholder="邮箱"
          class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
        />
        <input
          v-model="form.password"
          type="password"
          required
          minlength="8"
          placeholder="密码（至少 8 位）"
          class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
        />
        <input
          v-if="mode === 'register'"
          v-model="form.password_confirmation"
          type="password"
          required
          minlength="8"
          placeholder="确认密码"
          class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
        />

        <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 rounded-lg bg-bio-600 hover:bg-bio-500 disabled:opacity-50 text-white text-sm font-medium transition"
        >{{ loading ? '请稍候…' : mode === 'login' ? '登录' : '注册并登录' }}</button>
      </form>

      <p class="mt-4 text-center text-xs text-slate-500">
        {{ mode === 'login' ? '还没有账号？' : '已有账号？' }}
        <button class="text-bio-400 hover:underline" @click="switchMode">
          {{ mode === 'login' ? '立即注册' : '去登录' }}
        </button>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { authState } from '../store.js'

const emit = defineEmits(['close', 'success'])

const mode = ref('login')
const form = reactive({ name: '', email: '', password: '', password_confirmation: '' })
const loading = ref(false)
const error = ref('')

function switchMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = ''
}

async function submit() {
  loading.value = true
  error.value = ''
  try {
    if (mode.value === 'login') {
      await authState.login({ email: form.email, password: form.password })
    } else {
      await authState.register({ ...form })
    }
    emit('success')
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
