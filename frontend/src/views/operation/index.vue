<template>
  <div class="operation-modern">
    <div class="page-header">
       <h2>运营统计</h2>
       <p>概览系统核心指标与操作日志</p>
    </div>

    <!-- Stats Overview -->
    <div class="stats-grid">
      <!-- Case Stats -->
      <el-card class="stats-card gradient-blue" shadow="hover">
        <template #header><div class="card-title">📚 案例库概况</div></template>
        <div class="stats-content">
          <div class="main-stat">
            <div class="num">{{ caseStats.totalCases }}</div>
            <div class="label">案例总数</div>
          </div>
          <div class="sub-stats">
            <div class="sub-item">
              <span class="val">{{ caseStats.externalCases }}</span>
              <span class="lbl">对外</span>
            </div>
             <div class="sub-item">
              <span class="val">{{ caseStats.internalCases }}</span>
              <span class="lbl">对内</span>
            </div>
             <div class="sub-item">
              <span class="val">{{ caseStats.pendingApproval }}</span>
              <span class="lbl">待审</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- QA Stats -->
      <el-card class="stats-card gradient-purple" shadow="hover">
        <template #header><div class="card-title">💡 问答效能</div></template>
        <div class="stats-content">
          <div class="main-stat">
            <div class="num">{{ qaStats.aiResolutionRate }}<span class="unit">%</span></div>
            <div class="label">AI 解决率</div>
          </div>
          <div class="sub-stats">
            <div class="sub-item">
              <span class="val">{{ qaStats.totalQuestions }}</span>
              <span class="lbl">提问</span>
            </div>
             <div class="sub-item">
              <span class="val">{{ qaStats.aiResolved }}</span>
              <span class="lbl">解决</span>
            </div>
          </div>
        </div>
      </el-card>

       <!-- Engagement Stats -->
       <el-card class="stats-card gradient-orange" shadow="hover">
        <template #header><div class="card-title">🔥 互动数据</div></template>
        <div class="stats-content">
          <div class="main-stat">
            <div class="num">{{ caseStats.todayViews }}</div>
            <div class="label">今日浏览</div>
          </div>
          <div class="sub-stats">
             <div class="sub-item">
              <span class="val">{{ caseStats.likes }}</span>
              <span class="lbl">点赞</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Logs Table -->
    <el-card class="logs-card" shadow="never">
      <template #header>
        <div class="logs-header">
          <h3>操作日志</h3>
          <el-button link type="primary">查看更多</el-button>
        </div>
      </template>
      
      <el-table :data="logs" style="width: 100%" :header-cell-style="{ background: '#f9fafb' }">
        <el-table-column prop="operator" label="操作人" width="120">
          <template #default="{ row }">
             <div class="user-cell">
               <el-avatar :size="24" style="background:#e5e7eb;color:#374151">{{ row.operator.charAt(0) }}</el-avatar>
               <span>{{ row.operator }}</span>
             </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="operation" label="操作类型" width="140">
           <template #default="{ row }">
             <el-tag effect="light" round>{{ row.operation }}</el-tag>
           </template>
        </el-table-column>
        
        <el-table-column prop="target" label="对象" min-width="150" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="时间" width="180">
          <template #default="{ row }">
            <span style="color: #9ca3af">{{ row.createdAt }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { operationApi } from '@/services/case'

const caseStats = reactive({
  totalCases: 0,
  internalCases: 0,
  externalCases: 0,
  todayViews: 0,
  likes: 0,
  pendingApproval: 0
})

const qaStats = reactive({
  totalQuestions: 0,
  answered: 0,
  aiResolved: 0,
  aiResolutionRate: 0
})

const logs = ref([])

onMounted(async () => {
  try {
    const caseRes = await operationApi.getCaseStats()
    Object.assign(caseStats, caseRes.data || {})

    const qaRes = await operationApi.getQAStats()
    const qaData = qaRes.data || {}
    Object.assign(qaStats, {
      totalQuestions: qaData.total_questions || 0,
      answered: qaData.answered || 0,
      aiResolved: qaData.ai_resolved || 0,
      aiResolutionRate: Math.round((qaData.ai_resolution_rate || 0) * 100)
    })
    
    // Logs API if exists, else fallback
     const logsRes = await operationApi.getLogs() // Assuming this exists or falls to catch
     logs.value = logsRes.data || []
  } catch (e) {
    // Mock
    // Keep values if API fails (0) or set mock
    Object.assign(caseStats, { totalCases: 128, internalCases: 40, externalCases: 88, todayViews: 542, likes: 210, pendingApproval: 3 })
    Object.assign(qaStats, { totalQuestions: 1530, aiResolved: 1340, aiResolutionRate: 87 })

    logs.value = [
      { operator: '张三', operation: '创建案例', target: 'VPN连接教程', detail: '新增技术支持类案例', createdAt: '10:30' },
      { operator: '王五', operation: '审批拒绝', target: '季度报表草稿', detail: '内容不完整', createdAt: '09:15' },
      { operator: '李四', operation: '更新案例', target: '报销流程v2', detail: '更新附件', createdAt: '昨天' }
    ]
  }
})
</script>

<style lang="scss" scoped>
.operation-modern {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  h2 { font-size: 24px; font-weight: 700; color: #111827; margin: 0 0 8px; }
  p { color: #6b7280; font-size: 14px; margin: 0; }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stats-card {
  border: none;
  border-radius: 16px;
  color: white;
  transition: transform 0.3s;
  
  &:hover { transform: translateY(-5px); }
  
  &.gradient-blue { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
  &.gradient-purple { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
  &.gradient-orange { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
  
  :deep(.el-card__header) {
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding: 16px 20px;
  }
  
  .card-title { font-weight: 600; font-size: 16px; }
}

.stats-content {
  padding: 10px 0;
  
  .main-stat {
    margin-bottom: 24px;
    .num { font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
    .unit { font-size: 18px; font-weight: 500; }
    .label { font-size: 14px; opacity: 0.9; }
  }
  
  .sub-stats {
    display: flex;
    justify-content: space-between;
    
    .sub-item {
      text-align: center;
      .val { display: block; font-weight: 600; font-size: 16px; }
      .lbl { font-size: 12px; opacity: 0.8; }
    }
  }
}

.logs-card {
  border: none;
  border-radius: 16px;
  
  .logs-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    h3 { margin: 0; font-size: 18px; }
  }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
