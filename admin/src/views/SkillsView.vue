<template>
  <div>
    <!-- Filters -->
    <el-card>
      <el-form inline @submit.prevent>
        <el-form-item label="关键词">
          <el-input
            v-model="keyword"
            placeholder="名称 / slug / 描述"
            clearable
            style="width: 240px"
            @keyup.enter="load(1)"
            @clear="load(1)"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="category" placeholder="全部" clearable style="width: 180px" @change="load(1)">
            <el-option v-for="c in categories" :key="c.key" :label="`${c.name || c.key}（${c.count}）`" :value="c.key" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load(1)">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card class="mt">
      <el-table v-loading="loading" :data="skills" stripe>
        <el-table-column label="技能" min-width="280">
          <template #default="{ row }">
            <div class="skill-cell">
              <el-image v-if="row.icon_url" :src="row.icon_url" class="icon" fit="cover" lazy />
              <div v-else class="icon placeholder">🧪</div>
              <div>
                <div class="name">{{ row.name }}</div>
                <div class="slug">@{{ row.handle }}/{{ row.slug }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">{{ row.category_name || row.category || '—' }}</template>
        </el-table-column>
        <el-table-column label="版本" prop="version" width="90" />
        <el-table-column label="文件数" prop="files_count" width="80" align="center" />
        <el-table-column label="下载" prop="downloads" width="90" align="right" sortable />
        <el-table-column label="收藏" prop="stars" width="80" align="right" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">详情</el-button>
            <el-button size="small" type="primary" plain @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pager"
        background
        layout="total, prev, pager, next, jumper"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="load"
      />
    </el-card>

    <!-- Detail drawer -->
    <el-drawer v-model="detailVisible" :title="current?.name" size="55%">
      <template v-if="current">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="命名空间">@{{ current.handle }}/{{ current.slug }}</el-descriptions-item>
          <el-descriptions-item label="版本">{{ current.version || '—' }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ current.category_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ current.source || '—' }}</el-descriptions-item>
          <el-descriptions-item label="下载">{{ current.downloads }}</el-descriptions-item>
          <el-descriptions-item label="收藏">{{ current.stars }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ current.description_zh || current.description }}</el-descriptions-item>
          <el-descriptions-item v-if="current.source_url" label="上游地址" :span="2">
            <el-link :href="current.source_url" target="_blank" type="primary">{{ current.source_url }}</el-link>
          </el-descriptions-item>
        </el-descriptions>

        <h4 class="files-title">文件（{{ current.files?.length ?? 0 }}）</h4>
        <el-table :data="current.files || []" size="small" max-height="420">
          <el-table-column prop="path" label="路径" min-width="220" />
          <el-table-column prop="size" label="大小" width="110" align="right">
            <template #default="{ row }">{{ formatSize(row.size) }}</template>
          </el-table-column>
          <el-table-column width="110" align="center">
            <template #default="{ row }">
              <el-link type="primary" @click="previewFile(row.path)">预览</el-link>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-drawer>

    <!-- File preview dialog -->
    <el-dialog v-model="fileVisible" :title="filePath" width="70%" top="5vh">
      <pre v-loading="fileLoading" class="file-content">{{ fileContent }}</pre>
    </el-dialog>

    <!-- Edit dialog -->
    <el-dialog v-model="editVisible" title="编辑技能" width="560px">
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="editForm.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="中文描述"><el-input v-model="editForm.description_zh" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="editForm.category_name" placeholder="显示名" /></el-form-item>
        <el-form-item label="版本"><el-input v-model="editForm.version" /></el-form-item>
        <el-form-item label="图标 URL"><el-input v-model="editForm.icon_url" /></el-form-item>
        <el-form-item label="上游地址"><el-input v-model="editForm.source_url" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api.js'

const skills = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const keyword = ref('')
const category = ref('')
const loading = ref(false)

const detailVisible = ref(false)
const current = ref(null)

const fileVisible = ref(false)
const filePath = ref('')
const fileContent = ref('')
const fileLoading = ref(false)

const editVisible = ref(false)
const editForm = ref({})
const saving = ref(false)

function formatSize(n) {
  if (n > 1048576) return (n / 1048576).toFixed(1) + ' MB'
  if (n > 1024) return (n / 1024).toFixed(1) + ' KB'
  return n + ' B'
}

async function load(p = page.value) {
  page.value = p
  loading.value = true
  try {
    const data = await api.listSkills({ page: p, pageSize, keyword: keyword.value, category: category.value })
    skills.value = data.skills
    total.value = data.total
  } catch (e) {
    ElMessage.error('加载失败：' + e.message)
  } finally {
    loading.value = false
  }
}

async function openDetail(row) {
  current.value = row
  detailVisible.value = true
  try {
    current.value = (await api.getSkill(row.id)).skill
  } catch (e) {
    ElMessage.error('加载详情失败：' + e.message)
  }
}

async function previewFile(path) {
  filePath.value = path
  fileContent.value = ''
  fileLoading.value = true
  fileVisible.value = true
  try {
    const url = `/api/skills/${current.value.handle}/${current.value.slug}/file?path=${encodeURIComponent(path)}`
    const res = await fetch(url)
    fileContent.value = res.ok ? await res.text() : `加载失败：${res.status}`
  } catch (e) {
    fileContent.value = '加载失败：' + e.message
  } finally {
    fileLoading.value = false
  }
}

function openEdit(row) {
  editForm.value = {
    name: row.name,
    description: row.description,
    description_zh: row.description_zh,
    category_name: row.category_name,
    version: row.version,
    icon_url: row.icon_url,
    source_url: row.source_url,
  }
  current.value = row
  editVisible.value = true
}

async function save() {
  saving.value = true
  try {
    const { skill } = await api.updateSkill(current.value.id, editForm.value)
    Object.assign(current.value, skill)
    editVisible.value = false
    ElMessage.success('已保存')
  } catch (e) {
    ElMessage.error('保存失败：' + e.message)
  } finally {
    saving.value = false
  }
}

function remove(row) {
  ElMessageBox.confirm(`确定删除「${row.name}」？将同时删除磁盘上的 ${row.files_count} 个文件。`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    confirmButtonClass: 'el-button--danger',
  }).then(async () => {
    try {
      await api.deleteSkill(row.id)
      ElMessage.success('已删除')
      load()
    } catch (e) {
      ElMessage.error('删除失败：' + e.message)
    }
  }).catch(() => {})
}

onMounted(() => {
  load(1)
  api.categories().then((d) => (categories.value = d.items || [])).catch(() => {})
})
</script>

<style scoped>
.mt { margin-top: 16px; }
.skill-cell { display: flex; align-items: center; gap: 10px; }
.icon { width: 36px; height: 36px; border-radius: 6px; }
.icon.placeholder { display: flex; align-items: center; justify-content: center; background: #f0f5ff; font-size: 18px; }
.name { font-weight: 600; }
.slug { font-size: 12px; color: #909399; }
.pager { margin-top: 16px; justify-content: flex-end; }
.files-title { margin: 20px 0 10px; }
.file-content {
  max-height: 65vh; overflow: auto; background: #f6f8fa; padding: 12px;
  border-radius: 6px; font-size: 12px; white-space: pre-wrap; word-break: break-all;
}
</style>
