import { reactive } from 'vue'
import { auth, api } from './api.js'

// 全局认证状态（简单响应式 store）
export const authState = reactive({
  user: auth.user,

  async login(payload) {
    const data = await api.login(payload)
    auth.save(data.token, data.user)
    this.user = data.user
  },

  async register(payload) {
    const data = await api.register(payload)
    auth.save(data.token, data.user)
    this.user = data.user
  },

  async logout() {
    try {
      await api.logout()
    } catch {}
    auth.clear()
    this.user = null
  },
})
