<template>
  <div>
    <!-- Filters -->
    <el-card>
      <el-form inline @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="姓名 / 邮箱" clearable style="width: 220px" @keyup.enter="load(1)" @clear="load(1)" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="role" placeholder="全部" clearable style="width: 140px" @change="load(1)">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load(1)">查询</el-button>
          <el-button type="success" @click="openCreate">新建用户</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card class="mt">
      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'success'" size="small">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="上传技能" prop="skills_count" width="90" align="center" />
        <el-table-column label="注册时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openEdit(row)">编辑</el-button>
            <el-button size="small" plain @click="openResetPwd(row)">重置密码</el-button>
            <el-button size="small" type="danger" plain :disabled="row.id === me?.id" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pager" background layout="total, prev, pager, next"
        :total="total" :page-size="pageSize" :current-page="page" @current-change="load"
      />
    </el-card>

    <!-- Create/Edit dialog -->
    <el-dialog v-model="editVisible" :title="editForm.id ? '编辑用户' : '新建用户'" width="480px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名" required><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="邮箱" required><el-input v-model="editForm.email" type="email" /></el-form-item>
        <el-form-item label="角色" required>
          <el-radio-group v-model="editForm.role">
            <el-radio value="user">普通用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="!editForm.id" label="密码" required>
          <el-input v-model="editForm.password" type="password" show-password placeholder="至少 8 位" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- Reset password dialog -->
    <el-dialog v-model="pwdVisible" :title="`重置密码：${pwdTarget?.name}`" width="420px">
      <el-input v-model="newPassword" type="password" show-password placeholder="新密码（至少 8 位）" />
      <p class="pwd-tip">重置后该用户的所有登录状态将失效。</p>
      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="resetPwd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api, auth } from '../api.js'

const me = computed(() => auth.user)
const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const keyword = ref('')
const role = ref('')
const loading = ref(false)

const editVisible = ref(false)
const editForm = ref({})
const saving = ref(false)

const pwdVisible = ref(false)
const pwdTarget = ref(null)
const newPassword = ref('')

function formatDate(s) {
  return s ? new Date(s).toLocaleString('zh-CN') : '—'
}

async function load(p = page.value) {
  page.value = p
  loading.value = true
  try {
    const data = await api.listUsers({ page: p, pageSize, keyword: keyword.value, role: role.value })
    users.value = data.users
    total.value = data.total
  } catch (e) {
    ElMessage.error('加载失败：' + e.message)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editForm.value = { id: null, name: '', email: '', role: 'user', password: '' }
  editVisible.value = true
}

function openEdit(row) {
  editForm.value = { id: row.id, name: row.name, email: row.email, role: row.role }
  editVisible.value = true
}

async function save() {
  saving.value = true
  try {
    const f = editForm.value
    if (f.id) {
      await api.updateUser(f.id, { name: f.name, email: f.email, role: f.role })
    } else {
      if (!f.password || f.password.length < 8) {
        ElMessage.warning('密码至少 8 位')
        saving.value = false
        return
      }
      await api.createUser({ name: f.name, email: f.email, role: f.role, password: f.password })
    }
    editVisible.value = false
    ElMessage.success('已保存')
    load()
  } catch (e) {
    ElMessage.error('保存失败：' + e.message)
  } finally {
    saving.value = false
  }
}

function openResetPwd(row) {
  pwdTarget.value = row
  newPassword.value = ''
  pwdVisible.value = true
}

async function resetPwd() {
  if (newPassword.value.length < 8) {
    ElMessage.warning('密码至少 8 位')
    return
  }
  saving.value = true
  try {
    await api.updateUser(pwdTarget.value.id, { password: newPassword.value })
    pwdVisible.value = false
    ElMessage.success('密码已重置')
  } catch (e) {
    ElMessage.error('重置失败：' + e.message)
  } finally {
    saving.value = false
  }
}

function remove(row) {
  const warn = row.skills_count > 0
    ? `确定删除用户「${row.name}」？其上传的 ${row.skills_count} 个技能（含磁盘文件）将一并删除！`
    : `确定删除用户「${row.name}」？`
  ElMessageBox.confirm(warn, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    confirmButtonClass: 'el-button--danger',
  }).then(async () => {
    try {
      const res = await api.deleteUser(row.id)
      ElMessage.success(`已删除（清理技能 ${res.deleted_skills} 个）`)
      load()
    } catch (e) {
      ElMessage.error('删除失败：' + e.message)
    }
  }).catch(() => {})
}

onMounted(() => load(1))
</script>

<style scoped>
.mt { margin-top: 16px; }
.pager { margin-top: 16px; justify-content: flex-end; }
.pwd-tip { font-size: 12px; color: #909399; margin-top: 8px; }
</style>
