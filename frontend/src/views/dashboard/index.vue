<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>案例总数</template>
          <div class="stat-value">{{ stats.totalCases }}</div>
          <div class="stat-trend up">
            <el-icon><Top /></el-icon> 较昨日 +12%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>今日浏览</template>
          <div class="stat-value">{{ stats.todayViews }}</div>
          <div class="stat-trend up">
            <el-icon><Top /></el-icon> 较昨日 +8%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>AI 解决率</template>
          <div class="stat-value">{{ stats.aiResolutionRate }}%</div>
          <div class="stat-trend up">
            <el-icon><Top /></el-icon> 较昨日 +3%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>待审批</template>
          <div class="stat-value">{{ stats.pendingApprovals }}</div>
          <div class="stat-trend">
            <el-icon><Clock /></el-icon> 5 个待处理
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <span>最近案例</span>
          </template>
          <el-table :data="recentCases" style="width: 100%">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="创建时间" width="180" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>快捷入口</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/cases/create')">
              <el-icon><Plus /></el-icon> 创建案例
            </el-button>
            <el-button @click="$router.push('/search')">
              <el-icon><Search /></el-icon> 搜索案例
            </el-button>
            <el-button @click="$router.push('/qa')">
              <el-icon><ChatDotRound /></el-icon> 智能问答
            </el-button>
            <el-button @click="$router.push('/approvals')">
              <el-icon><Clock /></el-icon> 审批管理
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { operationApi } from '@/services/case'

const stats = ref({
  totalCases: 0,
  todayViews: 0,
  aiResolutionRate: 0,
  pendingApprovals: 0
})

const recentCases = ref([
  { id: 1, title: '如何重置密码', category: '账户安全', status: '已发布', createdAt: '2024-01-15 10:30' },
  { id: 2, title: '账单查询指南', category: '财务管理', status: '待审批', createdAt: '2024-01-15 09:20' },
  { id: 3, title: '产品功能介绍', category: '产品介绍', status: '草稿', createdAt: '2024-01-14 16:45' }
])

const getStatusType = (status) => {
  const map = {
    '已发布': 'success',
    '待审批': 'warning',
    '草稿': 'info',
    '已拒绝': 'danger'
  }
  return map[status] || 'info'
}

onMounted(async () => {
  try {
    const res = await operationApi.getCaseStats()
    stats.value = res.data || stats.value
  } catch (e) {
    console.log('使用模拟数据')
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  :deep(.el-card__header) {
    font-weight: 500;
    color: $text-secondary;
  }
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: $text-primary;
}

.stat-trend {
  margin-top: 10px;
  font-size: 13px;
  color: $text-secondary;

  &.up {
    color: $success-color;
  }

  &.down {
    color: $danger-color;
  }
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .el-button {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
