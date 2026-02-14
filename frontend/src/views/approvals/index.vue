<template>
  <div class="approvals-modern">
    <div class="page-header">
      <div class="header-left">
        <h2>审批管理</h2>
        <p>处理案例发布与更新申请</p>
      </div>
      <div class="header-right">
        <div class="tab-pills">
          <div
            class="tab-item"
            :class="{ active: activeTab === 'pending' }"
            @click.stop="handleTabChange('pending')"
          >
            待审批
            <span class="badge" v-if="pagination.total > 0 && activeTab === 'pending'">{{ pagination.total }}</span>
          </div>
          <div
            class="tab-item"
            :class="{ active: activeTab === 'processed' }"
            @click.stop="handleTabChange('processed')"
          >
            已处理
          </div>
        </div>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table 
        :data="approvals" 
        v-loading="loading" 
        style="width: 100%"
        :header-cell-style="{ background: '#f9fafb', color: '#6b7280', fontWeight: '600' }"
      >
        <el-table-column prop="case_id" label="案例ID" width="100">
           <template #default="{ row }">
             <span class="mono-font">#{{ row.case_id }}</span>
           </template>
        </el-table-column>
        
        <el-table-column prop="case_title" label="案例标题" min-width="240">
           <template #default="{ row }">
             <span class="title-link" @click="handleView(row.case_id)">{{ row.case_title }}</span>
           </template>
        </el-table-column>
        
        <el-table-column prop="requester_name" label="申请人" width="120">
           <template #default="{ row }">
             <div class="user-cell">
               <el-avatar :size="24" class="sm-avatar">{{ (row.requester_name || '-').charAt(0) }}</el-avatar>
               <span>{{ row.requester_name || '-' }}</span>
             </div>
           </template>
        </el-table-column>
        
        <el-table-column prop="case_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.case_type === 'external' ? 'success' : row.case_type === 'internal' ? 'warning' : 'info'" effect="light" round>
              {{ row.case_type === 'external' ? '对外' : row.case_type === 'internal' ? '对内' : '-' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="申请时间" width="180">
           <template #default="{ row }">
             <span class="text-gray">{{ formatDateTime(row.created_at) }}</span>
           </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="actions-cell">
              <el-button link type="primary" @click="handleView(row.case_id)">查看</el-button>
              <template v-if="activeTab === 'pending'">
                <el-divider direction="vertical" />
                <el-button link type="success" @click="handleApprove(row.id)">通过</el-button>
                <el-button link type="danger" @click="handleReject(row.id)">拒绝</el-button>
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          :total="pagination.total"
          layout="prev, pager, next"
          background
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { approvalApi } from '@/services/case'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('pending')
const approvals = ref([])

const pagination = reactive({
  page: 1,
  total: 0
})

const formatDateTime = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await approvalApi.list({
      status: activeTab.value === 'pending' ? 'pending' : 'processed',
      page: pagination.page
    })
    // 修复：res 已经是响应对象，直接使用 res.data
    approvals.value = res.data?.items || []
    pagination.total = res.data?.total || 0
  } catch (e) {
    console.error('获取审批列表失败:', e)
    ElMessage.error('获取审批列表失败，请稍后重试')
    // 清空数据而不是使用模拟数据
    approvals.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const handleView = (caseId) => {
  router.push(`/cases/${caseId}`)
}

const handleApprove = async (id) => {
  try {
    await ElMessageBox.confirm('确定通过该审批吗？', '确认', {
      confirmButtonText: '通过',
      cancelButtonText: '取消',
      type: 'success'
    })
    await approvalApi.approve(id)
    ElMessage.success('审批已通过')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

const handleReject = async (id) => {
  try {
    await ElMessageBox.confirm('确定拒绝该审批吗？', '拒接', {
      confirmButtonText: '拒绝',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await approvalApi.reject(id)
    ElMessage.success('已拒绝')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

const handleTabChange = (tab) => {
  activeTab.value = tab
  pagination.page = 1  // 重置分页到第一页
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.approvals-modern {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .header-left {
    h2 { font-size: 24px; font-weight: 700; color: #111827; margin: 0 0 8px; }
    p { color: #6b7280; font-size: 14px; margin: 0; }
  }
}

.tab-pills {
  display: flex;
  background: #e5e7eb;
  padding: 4px;
  border-radius: 12px;
  
  .tab-item {
    padding: 8px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 6px;
    
    &.active {
      background: white;
      color: #111827;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .badge {
      background: #ef4444;
      color: white;
      font-size: 11px;
      padding: 1px 6px;
      border-radius: 10px;
    }
  }
}

.table-card {
  border: none;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.03);
  padding: 8px;
}

.title-link {
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  &:hover { color: #8b5cf6; text-decoration: underline; }
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .sm-avatar { background: #d1d5db; color: white; font-size: 12px; }
}

.mono-font {
  font-family: monospace;
  color: #6b7280;
}

.text-gray { color: #9ca3af; font-size: 13px; }

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
