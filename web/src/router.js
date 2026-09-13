import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import SkillDetailView from './views/SkillDetailView.vue'
import UploadView from './views/UploadView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/skill/:handle/:slug', name: 'skill', component: SkillDetailView, props: true },
    { path: '/upload', name: 'upload', component: UploadView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
