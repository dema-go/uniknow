<template>
  <div class="operation-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>案例统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-value">{{ caseStats.totalCases }}</div>
                <div class="stat-label">案例总数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-value">{{ caseStats.internalCases }}</div>
                <div class="stat-label">对内案例</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-value">{{ caseStats.externalCases }}</div>
                <div class="stat-label">对外案例</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-value">{{ caseStats.todayViews }}</div>
                <div class="stat-label">今日浏览</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-value">{{ caseStats.likes }}</div>
                <div class="stat-label">累计点赞</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-value">{{ caseStats.pendingApproval }}</div>
                <div class="stat-label">待审批</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>问答统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-box">
                <div class="stat-value">{{ qaStats.totalQuestions }}</div>
                <div class="stat-label">问题总数</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box success">
                <div class="stat-value">{{ qaStats.aiResolved }}</div>
                <div class="stat-label">AI 解决</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-box primary">
                <div class="stat-value">{{ qaStats.aiResolutionRate }}%</div>
                <div class="stat-label">解决率</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <span>操作日志</span>
          </template>
          <el-table :data="logs" style="width: 100%">
            <el-table-column prop="operator" label="操作人" width="120" />
            <el-table-column prop="operation" label="操作类型" width="120" />
            <el-table-column prop="target" label="操作对象" />
            <el-table-column prop="detail" label="详情" />
            <el-table-column prop="createdAt" label="时间" width="180" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { operationApi } from '@/services/case'

const caseStats = reactive({
  totalCases: 100,
  internalCases: 30,
  externalCases: 70,
  todayViews: 500,
  likes: 200,
  pendingApproval: 5
})

const qaStats = reactive({
  totalQuestions: 1000,
  answered: 850,
  aiResolved: 700,
  aiResolutionRate: 82
})

const logs = ref([])

onMounted(async () => {
  try {
    const caseRes = await operationApi.getCaseStats()
    Object.assign(caseStats, caseRes.data || {})

    const qaRes = await operationApi.getQAStats()
    Object.assign(qaStats, qaRes.data || {})
  } catch (e) {
    // 使用模拟数据
    logs.value = [
      { operator: '张三', operation: '创建案例', target: '如何重置密码', detail: '创建新案例', createdAt: '2024-01-15 10:30:00' },
      { operator: '李四', operation: '审批通过', target: '账单查询指南', detail: '审批通过案例', createdAt: '2024-01-15 09:20:00' }
    ]
  }
})
</script>

<style lang="scss" scoped>
.operation-page {
  .stat-box {
    text-align: center;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;

    &.success {
      background: #f0f9eb;
      .stat-value { color: $success-color; }
    }

    &.primary {
      background: #ecf5ff;
      .stat-value { color: $primary-color; }
    }

    .stat-value {
      font-size: 28px;
      font-weight: bold;
      color: $text-primary;
    }

    .stat-label {
      font-size: 13px;
      color: $text-secondary;
      margin-top: 8px;
    }
  }
}
</style>
