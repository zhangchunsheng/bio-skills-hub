import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import SkillsView from './views/SkillsView.vue'

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/skills', name: 'skills', component: SkillsView },
  ],
})
