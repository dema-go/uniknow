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
            @click="activeTab = 'pending'; fetchData()"
          >
            待审批
            <span class="badge" v-if="pagination.total > 0 && activeTab === 'pending'">{{ pagination.total }}</span>
          </div>
          <div 
            class="tab-item" 
            :class="{ active: activeTab === 'processed' }"
            @click="activeTab = 'processed'; fetchData()"
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
        <el-table-column prop="caseId" label="案例ID" width="100">
           <template #default="{ row }">
             <span class="mono-font">#{{ row.caseId }}</span>
           </template>
        </el-table-column>
        
        <el-table-column prop="caseTitle" label="案例标题" min-width="240">
           <template #default="{ row }">
             <span class="title-link" @click="handleView(row.caseId)">{{ row.caseTitle }}</span>
           </template>
        </el-table-column>
        
        <el-table-column prop="applicant" label="申请人" width="120">
           <template #default="{ row }">
             <div class="user-cell">
               <el-avatar :size="24" class="sm-avatar">{{ row.applicant.charAt(0) }}</el-avatar>
               <span>{{ row.applicant }}</span>
             </div>
           </template>
        </el-table-column>
        
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'create' ? 'success' : 'warning'" effect="light" round>
              {{ row.type === 'create' ? '新增' : '修改' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="createdAt" label="申请时间" width="180">
           <template #default="{ row }">
             <span class="text-gray">{{ row.createdAt }}</span>
           </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="actions-cell">
              <el-button link type="primary" @click="handleView(row.caseId)">查看</el-button>
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

const fetchData = async () => {
  loading.value = true
  try {
    const res = await approvalApi.list({
      status: activeTab.value === 'pending' ? 'pending' : 'processed',
      page: pagination.page
    })
    approvals.value = res.data?.items || []
    pagination.total = res.data?.total || 0
  } catch (e) {
    // 模拟数据
    approvals.value = [
      { id: '1', caseId: '1024', caseTitle: '如何高效重置用户密码', applicant: '张三', type: 'create', createdAt: '2024-01-15 10:30' },
      { id: '2', caseId: '1025', caseTitle: '账单查询流程更新', applicant: '李四', type: 'update', createdAt: '2024-01-15 09:20' }
    ]
    pagination.total = 2
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
