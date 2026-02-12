<template>
  <div class="case-list">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>案例列表</span>
          <el-button type="primary" @click="$router.push('/cases/create')">
            <el-icon><Plus /></el-icon> 创建案例
          </el-button>
        </div>
      </template>

      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="分类">
          <el-select v-model="filters.categoryId" placeholder="请选择" clearable>
            <el-option label="账户安全" value="1" />
            <el-option label="财务管理" value="2" />
            <el-option label="产品介绍" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="请选择" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending_approval" />
            <el-option label="已发布" value="published" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.caseType" placeholder="请选择" clearable>
            <el-option label="对外案例" value="external" />
            <el-option label="对内案例" value="internal" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row.id)">
              {{ row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="categoryId" label="分类" width="120" />
        <el-table-column prop="caseType" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.caseType === 'external' ? 'success' : 'warning'" size="small">
              {{ row.caseType === 'external' ? '对外' : '对内' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="viewCount" label="浏览量" width="100" />
        <el-table-column prop="likeCount" label="点赞" width="80" />
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row.id)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row.id)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { caseApi } from '@/services/case'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])

const filters = reactive({
  categoryId: '',
  status: '',
  caseType: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const getStatusType = (status) => {
  const map = {
    'draft': 'info',
    'pending_approval': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'published': 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'draft': '草稿',
    'pending_approval': '待审批',
    'approved': '已审批',
    'rejected': '已拒绝',
    'published': '已发布'
  }
  return map[status] || status
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await caseApi.list({
      ...filters,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    tableData.value = res.data?.items || []
    pagination.total = res.data?.total || 0
  } catch (e) {
    // 使用模拟数据
    tableData.value = [
      { id: '1', title: '如何重置密码', categoryId: '账户安全', caseType: 'external', status: 'published', viewCount: 100, likeCount: 10, createdAt: '2024-01-15 10:30:00' },
      { id: '2', title: '账单查询指南', categoryId: '财务管理', caseType: 'external', status: 'pending_approval', viewCount: 50, likeCount: 5, createdAt: '2024-01-15 09:20:00' }
    ]
    pagination.total = 2
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  filters.categoryId = ''
  filters.status = ''
  filters.caseType = ''
  handleSearch()
}

const handleView = (id) => {
  router.push(`/cases/${id}`)
}

const handleEdit = (id) => {
  router.push(`/cases/${id}`)
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该案例吗？', '提示', {
      type: 'warning'
    })
    await caseApi.delete(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.case-list {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-form {
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
