<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="brand">🧬 Bio Skills Hub</div>
      <div class="sub">管理后台登录</div>
      <el-form class="mt" @submit.prevent="submit">
        <el-form-item>
          <el-input v-model="email" type="email" placeholder="邮箱" size="large" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="密码" size="large" show-password :prefix-icon="Lock" @keyup.enter="submit" />
        </el-form-item>
        <el-alert v-if="error" :title="error" type="error" :closable="false" class="mb" />
        <el-button type="success" size="large" class="login-btn" :loading="loading" @click="submit">
          登 录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api, auth } from '../api.js'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  if (!email.value || !password.value) {
    error.value = '请输入邮箱和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const data = await api.login({ email: email.value, password: password.value })
    if (data.user.role !== 'admin') {
      error.value = '该账号不是管理员'
      return
    }
    auth.save(data.token, data.user)
    ElMessage.success('登录成功')
    router.replace('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #052e16 0%, #0f172a 100%);
}
.login-card { width: 380px; }
.brand { font-size: 22px; font-weight: 700; text-align: center; color: #16a34a; }
.sub { text-align: center; color: #909399; font-size: 13px; margin-top: 4px; }
.mt { margin-top: 24px; }
.mb { margin-bottom: 16px; }
.login-btn { width: 100%; }
</style>
