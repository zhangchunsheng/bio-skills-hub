<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-sm mx-4">
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-lg font-bold">修改密码</h2>
        <button class="text-slate-500 hover:text-slate-300 text-xl leading-none" @click="$emit('close')">×</button>
      </div>

      <form class="space-y-3" @submit.prevent="submit">
        <input
          v-model="form.current_password"
          type="password"
          required
          placeholder="当前密码"
          class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
        />
        <input
          v-model="form.password"
          type="password"
          required
          minlength="8"
          placeholder="新密码（至少 8 位）"
          class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
        />
        <input
          v-model="form.password_confirmation"
          type="password"
          required
          minlength="8"
          placeholder="确认新密码"
          class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
        />

        <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
        <p v-if="done" class="text-sm text-bio-400">✓ 密码已修改，其它设备的登录状态已失效</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 rounded-lg bg-bio-600 hover:bg-bio-500 disabled:opacity-50 text-white text-sm font-medium transition"
        >{{ loading ? '提交中…' : '确认修改' }}</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { api } from '../api.js'

const emit = defineEmits(['close'])

const form = reactive({ current_password: '', password: '', password_confirmation: '' })
const loading = ref(false)
const error = ref('')
const done = ref(false)

async function submit() {
  error.value = ''
  if (form.password !== form.password_confirmation) {
    error.value = '两次输入的新密码不一致'
    return
  }
  loading.value = true
  try {
    await api.changePassword({ ...form })
    done.value = true
    setTimeout(() => emit('close'), 1200)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
