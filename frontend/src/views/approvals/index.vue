<template>
  <div class="approvals-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>审批管理</span>
          <el-radio-group v-model="activeTab">
            <el-radio-button value="pending">待审批</el-radio-button>
            <el-radio-button value="processed">已处理</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="approvals" v-loading="loading" style="width: 100%">
        <el-table-column prop="caseId" label="案例ID" width="100" />
        <el-table-column prop="caseTitle" label="案例标题" min-width="200" />
        <el-table-column prop="applicant" label="申请人" width="120" />
        <el-table-column prop="type" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'create' ? 'success' : 'warning'">
              {{ row.type === 'create' ? '新增' : '修改' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="申请时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row.caseId)">查看</el-button>
            <el-button
              v-if="activeTab === 'pending'"
              link
              type="success"
              @click="handleApprove(row.id)"
            >
              通过
            </el-button>
            <el-button
              v-if="activeTab === 'pending'"
              link
              type="danger"
              @click="handleReject(row.id)"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          :total="pagination.total"
          layout="prev, pager, next"
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
      { id: '1', caseId: '1', caseTitle: '如何重置密码', applicant: '张三', type: 'create', createdAt: '2024-01-15 10:30:00' },
      { id: '2', caseId: '2', caseTitle: '账单查询指南', applicant: '李四', type: 'update', createdAt: '2024-01-15 09:20:00' }
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
    await ElMessageBox.confirm('确定通过该审批吗？', '提示')
    await approvalApi.approve(id)
    ElMessage.success('审批已通过')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleReject = async (id) => {
  try {
    await ElMessageBox.confirm('确定拒绝该审批吗？', '提示', {
      type: 'warning'
    })
    await approvalApi.reject(id)
    ElMessage.success('已拒绝')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.approvals-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
