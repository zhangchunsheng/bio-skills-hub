import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command }) => ({
  // 生产构建部署在 Laravel public/admin/ 下，基础路径为 /admin/
  base: command === 'build' ? '/admin/' : '/',
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
}))
