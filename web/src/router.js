import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import SkillDetailView from './views/SkillDetailView.vue'
import UploadView from './views/UploadView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { title: 'Bio Skills Hub - 生物分析 AI 技能库' } },
    { path: '/skill/:handle/:slug', name: 'skill', component: SkillDetailView, props: true, meta: { title: '技能详情 - Bio Skills Hub' } },
    { path: '/upload', name: 'upload', component: UploadView, meta: { title: '上传技能 - Bio Skills Hub' } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

// 客户端导航时更新页面标题（服务端已为爬虫注入完整 meta）
router.afterEach((to) => {
  if (to.meta.title) document.title = to.meta.title
})

export default router
