import { createRouter, createWebHistory } from 'vue-router'
import { auth } from './api.js'
import DashboardView from './views/DashboardView.vue'
import SkillsView from './views/SkillsView.vue'
import LoginView from './views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/skills', name: 'skills', component: SkillsView },
  ],
})

// 管理后台全部页面需要登录（管理员）
router.beforeEach((to) => {
  if (to.name === 'login') return true
  if (!auth.token || auth.user?.role !== 'admin') {
    return { name: 'login' }
  }
  return true
})

export default router
