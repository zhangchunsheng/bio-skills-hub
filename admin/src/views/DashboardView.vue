<template>
  <div>
    <!-- Stat cards -->
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Sync -->
    <el-card class="mt">
      <template #header>
        <div class="card-header">
          <span>数据同步</span>
          <el-tag v-if="status?.running" type="warning">同步中…</el-tag>
          <el-tag v-else type="success">空闲</el-tag>
        </div>
      </template>
      <p class="sync-info">
        最近同步：<b>{{ stats?.lastSync ? formatDate(stats.lastSync) : '从未' }}</b>
        <span v-if="status?.finished_at && !status.running">
          （上次完成于 {{ formatDate(status.finished_at) }}<span v-if="status.skills">，收录 {{ status.skills }} 技能 / {{ status.files }} 文件</span>）
        </span>
      </p>
      <p class="sync-info" v-if="status?.error">
        <el-text type="danger">上次同步出错：{{ status.error }}</el-text>
      </p>
      <div class="sync-actions">
        <el-button type="primary" :loading="starting || status?.running" @click="startSync(false)">
          增量同步
        </el-button>
        <el-button type="danger" plain :disabled="starting || status?.running" @click="confirmRefresh">
          全量重抓
        </el-button>
        <el-button @click="loadLog">查看日志</el-button>
      </div>
      <el-input
        v-if="log"
        v-model="log"
        type="textarea"
        :rows="14"
        readonly
        class="log-view"
      />
    </el-card>

    <!-- Keywords -->
    <el-card class="mt" v-if="stats?.keywords?.length">
      <template #header><span>同步关键词（{{ stats.keywords.length }}）</span></template>
      <el-tag v-for="kw in stats.keywords" :key="kw" class="kw-tag">{{ kw }}</el-tag>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api.js'

const stats = ref(null)
const status = ref(null)
const starting = ref(false)
const log = ref('')
let timer = null

const cards = computed(() => [
  { label: '收录技能', value: stats.value?.skills ?? '—' },
  { label: '技能文件', value: stats.value?.files ?? '—' },
  { label: '覆盖分类', value: stats.value?.categories ?? '—' },
  { label: '同步关键词', value: stats.value?.keywords?.length ?? '—' },
])

function formatDate(ts) {
  return new Date(ts * 1000).toLocaleString('zh-CN')
}

async function load() {
  try {
    ;[stats.value, status.value] = await Promise.all([api.stats(), api.syncStatus()])
  } catch (e) {
    ElMessage.error('加载失败：' + e.message)
  }
}

async function startSync(refresh) {
  starting.value = true
  try {
    await api.startSync({ refresh })
    ElMessage.success('同步已在后台启动')
    poll()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    starting.value = false
  }
}

function confirmRefresh() {
  ElMessageBox.confirm('全量重抓将重新下载所有技能文件，耗时较长，确定继续？', '确认', {
    type: 'warning',
  }).then(() => startSync(true)).catch(() => {})
}

async function loadLog() {
  try {
    // 状态接口不含日志正文，这里简单提示；日志在服务器 storage/logs/sync.log
    ElMessage.info('日志文件位于服务器 server/storage/logs/sync.log')
  } catch {}
}

function poll() {
  clearInterval(timer)
  timer = setInterval(async () => {
    await load()
    if (!status.value?.running) {
      clearInterval(timer)
      ElMessage.success('同步完成')
    }
  }, 5000)
}

onMounted(() => {
  load()
  poll() // 若页面打开时正在同步则持续刷新
})

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.mt { margin-top: 16px; }
.stat-value { font-size: 28px; font-weight: 700; color: #1f2d3d; }
.stat-label { color: #909399; font-size: 13px; margin-top: 4px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.sync-info { margin: 4px 0; color: #606266; font-size: 14px; }
.sync-actions { margin-top: 12px; }
.log-view { margin-top: 12px; font-family: monospace; }
.kw-tag { margin: 0 8px 8px 0; }
</style>
