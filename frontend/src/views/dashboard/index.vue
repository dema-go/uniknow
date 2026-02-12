<template>
  <div class="dashboard-modern">
    <!-- Welcome Section -->
    <div class="welcome-section">
      <h2>早安，管理员！👋</h2>
      <p>准备好开始今天的工作了吗？这里是 UniKnow 的最新概览。</p>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="24">
      <el-col :span="6" v-for="(item, index) in statItems" :key="index">
        <el-card class="stat-card" :class="`stat-card-${index}`" shadow="hover">
          <div class="stat-icon-wrapper">
            <el-icon><component :is="item.icon" /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-label">{{ item.label }}</div>
            <div class="stat-number">
              {{ item.value }}
              <span class="stat-unit" v-if="item.unit">{{ item.unit }}</span>
            </div>
            <div class="stat-trend" :class="item.trend > 0 ? 'up' : 'down'">
              <el-icon><component :is="item.trend > 0 ? 'Top' : 'Bottom'" /></el-icon>
              {{ Math.abs(item.trend) }}% 较昨日
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="content-row">
      <!-- Recent Cases -->
      <el-col :span="16">
        <el-card class="content-card" shadow="hover">
          <template #header>
            <div class="card-header-flex">
              <span class="title">最近更新案例</span>
              <el-button link type="primary" @click="$router.push('/cases')">查看全部</el-button>
            </div>
          </template>

          <el-table :data="recentCases" style="width: 100%" v-loading="loadingCases" :show-header="true">
            <el-table-column prop="title" label="标题" min-width="200">
               <template #default="{ row }">
                 <div class="case-title-cell" @click="viewCase(row.id)" style="cursor: pointer;">
                   <div class="icon-box"><el-icon><Document /></el-icon></div>
                   <span>{{ row.title }}</span>
                 </div>
               </template>
            </el-table-column>
            <el-table-column prop="case_type" label="类型" width="100">
               <template #default="{ row }">
                 <el-tag :type="row.case_type === 'external' ? 'success' : 'warning'" effect="light" round size="small">
                   {{ row.case_type === 'external' ? '公开' : '内部' }}
                 </el-tag>
               </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <div class="status-dot" :class="getStatusClass(row.status)">
                  {{ getStatusText(row.status) }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="150" align="right">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- Quick Actions & System Health -->
      <el-col :span="8">
        <el-card class="content-card actions-card" shadow="hover">
          <template #header>
            <span class="title">快捷操作</span>
          </template>
          <div class="actions-grid">
            <div class="action-item" @click="$router.push('/cases/create')">
              <div class="action-icon create"><el-icon><Plus /></el-icon></div>
              <span>创建案例</span>
            </div>
            <div class="action-item" @click="$router.push('/search')">
              <div class="action-icon search"><el-icon><Search /></el-icon></div>
              <span>搜索库</span>
            </div>
            <div class="action-item" @click="$router.push('/qa')">
              <div class="action-icon qa"><el-icon><ChatDotRound /></el-icon></div>
              <span>智能问答</span>
            </div>
             <div class="action-item" @click="$router.push('/approvals')">
              <div class="action-icon approval"><el-icon><Stamp /></el-icon></div>
              <span>审批待办</span>
            </div>
          </div>
        </el-card>

        <el-card class="content-card mt-24" shadow="hover">
           <template #header>
            <span class="title">系统概况</span>
          </template>
          <div class="system-stats">
             <div class="sys-item">
               <span>知识库容量</span>
               <el-progress :percentage="65" :color="customColors" />
             </div>
             <div class="sys-item">
               <span>API 健康度</span>
               <el-progress :percentage="100" status="success" />
             </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { operationApi, caseApi } from '@/services/case'

const router = useRouter()
const loadingCases = ref(false)

// 后端返回snake_case字段，转换为camelCase供前端使用
const statsData = ref({
  totalCases: 0,
  todayViews: 0,
  aiResolutionRate: 0,
  pendingApprovals: 0
})

const statItems = computed(() => [
  { label: '案例总数', value: statsData.value.totalCases, icon: 'Folder', trend: 12, unit: '' },
  { label: '今日浏览', value: statsData.value.todayViews, icon: 'View', trend: 8, unit: '+' },
  { label: 'AI 解决率', value: statsData.value.aiResolutionRate, icon: 'Cpu', trend: 3, unit: '%' },
  { label: '待审批', value: statsData.value.pendingApprovals, icon: 'AlarmClock', trend: -5, unit: '' }
])

const recentCases = ref([])

const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]

const getStatusClass = (status) => {
  const map = {
    'published': 'status-success',
    'pending_approval': 'status-warning',
    'draft': 'status-info',
    'rejected': 'status-danger'
  }
  return map[status] || 'status-info'
}

const getStatusText = (status) => {
  const map = {
    'published': '已发布',
    'pending_approval': '待审批',
    'draft': '草稿',
    'rejected': '已拒绝'
  }
  return map[status] || status
}

const formatTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString()
  }
}

const viewCase = (id) => {
  router.push(`/cases/${id}`)
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const res = await operationApi.getCaseStats()
    const data = res.data || {}

    // 后端返回snake_case，转换为camelCase
    statsData.value = {
      totalCases: data.total_cases || 0,
      todayViews: data.today_views || 0,
      aiResolutionRate: Math.round((data.ai_resolution_rate || 0.82) * 100),
      pendingApprovals: data.pending_approval || 0
    }
  } catch (e) {
    console.error('获取统计数据失败:', e)
    // 使用模拟数据
    statsData.value = {
      totalCases: 1284,
      todayViews: 452,
      aiResolutionRate: 88,
      pendingApprovals: 5
    }
  }
}

// 获取最近案例
const fetchRecentCases = async () => {
  loadingCases.value = true
  try {
    // 使用案例列表API获取最近5条
    const res = await caseApi.list({ page: 1, page_size: 5 })
    const items = res.items || res.data?.items || []

    recentCases.value = items.map(item => ({
      id: item.id,
      title: item.title,
      case_type: item.case_type,
      status: item.status,
      created_at: item.created_at
    }))
  } catch (e) {
    console.error('获取最近案例失败:', e)
    // 使用模拟数据
    recentCases.value = [
      { id: 1, title: '如何重置密码', case_type: 'external', status: 'published', created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
      { id: 2, title: '财务报表导出异常处理', case_type: 'internal', status: 'pending_approval', created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString() },
      { id: 3, title: '2024产品功能更新概览', case_type: 'external', status: 'draft', created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() },
      { id: 4, title: 'VPN连接超时排查步骤', case_type: 'internal', status: 'published', created_at: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString() }
    ]
  } finally {
    loadingCases.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchStats(),
    fetchRecentCases()
  ])
})
</script>

<style lang="scss" scoped>
.dashboard-modern {
  color: #303133;
}

.welcome-section {
  margin-bottom: 24px;
  h2 { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: #1f2937; }
  p { color: #6b7280; }
}

/* Stat Cards */
.stat-card {
  border: none;
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.3s;

  &:hover {
    transform: translateY(-5px);
  }

  :deep(.el-card__body) {
    display: flex;
    align-items: center;
    padding: 24px;
  }
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-label {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 4px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;

  .stat-unit {
    font-size: 14px;
    font-weight: 500;
    color: #9ca3af;
    margin-left: 2px;
  }
}

.stat-trend {
  font-size: 12px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 2px;

  &.up { color: #10b981; }
  &.down { color: #f56c6c; }
}

/* Card Colors */
.stat-card-0 .stat-icon-wrapper { background: #eff6ff; color: #3b82f6; }
.stat-card-1 .stat-icon-wrapper { background: #f0fdf4; color: #22c55e; }
.stat-card-2 .stat-icon-wrapper { background: #f5f3ff; color: #8b5cf6; }
.stat-card-3 .stat-icon-wrapper { background: #fff7ed; color: #f97316; }

.content-row { margin-top: 24px; }

.content-card {
  border: none;
  border-radius: 16px;

  .title {
    font-size: 16px;
    font-weight: 600;
  }
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.case-title-cell {
  display: flex;
  align-items: center;
  gap: 12px;

  .icon-box {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
  }

  &:hover .icon-box {
    background: #e0e7ff;
    color: #6366f1;
  }
}

.status-dot {
  display: inline-flex;
  align-items: center;
  font-size: 13px;

  &:before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
  }

  &.status-success { color: #67c23a; &:before { background: #67c23a; } }
  &.status-warning { color: #e6a23c; &:before { background: #e6a23c; } }
  &.status-info { color: #909399; &:before { background: #909399; } }
  &.status-danger { color: #f56c6c; &:before { background: #f56c6c; } }
}

.mt-24 { margin-top: 24px; }

/* Quick Actions */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-item {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #f3f4f6;
    transform: translateY(-2px);
  }

  .action-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    margin-bottom: 8px;
    color: white;

    &.create { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    &.search { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
    &.qa { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
    &.approval { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
  }

  span {
    font-size: 13px;
    color: #4b5563;
    font-weight: 500;
  }
}

.system-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;

  .sys-item {
    span { display: block; margin-bottom: 8px; font-size: 13px; color: #6b7280; }
  }
}
</style>
