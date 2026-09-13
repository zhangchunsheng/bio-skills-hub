<template>
  <!-- 登录页独占布局 -->
  <RouterView v-if="$route.name === 'login'" />

  <el-container v-else class="layout">
    <el-aside width="220px">
      <div class="brand">
        <span class="logo">🧬</span> Bio Skills Hub
        <div class="sub">管理后台</div>
      </div>
      <el-menu :default-active="$route.path" router background-color="#001529" text-color="#a6adb4" active-text-color="#52c41a">
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon><span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/skills">
          <el-icon><Collection /></el-icon><span>技能管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="page-title">{{ $route.name === 'skills' ? '技能管理' : '仪表盘' }}</span>
        <div class="right">
          <span class="user">{{ user?.name }}</span>
          <a href="/" target="_blank" class="site-link">查看用户端 →</a>
          <el-button size="small" text type="danger" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Odometer, Collection } from '@element-plus/icons-vue'
import { api, auth } from './api.js'

const router = useRouter()
const user = computed(() => auth.user)

async function logout() {
  try {
    await api.logout()
  } catch {}
  auth.clear()
  router.replace('/login')
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.el-aside { background: #001529; }
.brand {
  color: #fff; font-weight: 600; padding: 20px 16px 16px; font-size: 16px;
}
.brand .logo { font-size: 20px; }
.brand .sub { font-size: 12px; color: #6b7280; font-weight: 400; margin-top: 4px; }
.el-menu { border-right: none; }
.header {
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #e5e7eb; background: #fff;
}
.page-title { font-weight: 600; }
.right { display: flex; align-items: center; gap: 14px; }
.user { font-size: 13px; color: #606266; }
.site-link { font-size: 13px; color: #52c41a; text-decoration: none; }
.el-main { background: #f5f7fa; }
</style>
