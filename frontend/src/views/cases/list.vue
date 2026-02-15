<template>
  <div class="case-list-modern">
    <div class="page-header">
      <div class="header-left">
        <h2>案例管理</h2>
        <p>管理和维护所有的知识库案例</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" class="create-btn" @click="$router.push('/cases/create')">
          <el-icon><Plus /></el-icon> 创建新案例
        </el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-container">
      <el-form :inline="true" :model="filters" class="modern-form">
        <el-form-item>
          <el-input 
            v-model="filters.keyword" 
            placeholder="搜索案例标题..." 
            prefix-icon="Search"
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item>
          <el-select v-model="filters.category_id" placeholder="所有分类" clearable class="filter-select">
            <el-option label="账户安全" value="1" />
            <el-option label="财务管理" value="2" />
            <el-option label="产品介绍" value="3" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-select v-model="filters.status" placeholder="所有状态" clearable class="filter-select">
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending_approval" />
            <el-option label="已发布" value="published" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-radio-group v-model="filters.case_type" @change="handleSearch" class="type-radio">
            <el-radio-button value="" label="">全部</el-radio-button>
            <el-radio-button value="external" label="external">对外</el-radio-button>
            <el-radio-button value="internal" label="internal">对内</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-radio-group v-model="filters.case_form" @change="handleSearch" class="type-radio">
            <el-radio-button value="" label="">全部</el-radio-button>
            <el-radio-button value="faq" label="faq">FAQ</el-radio-button>
            <el-radio-button value="document" label="document">文档</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item class="action-items">
          <el-button @click="handleSearch" circle><el-icon><Refresh /></el-icon></el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table -->
    <div class="table-container" v-loading="loading">
      <el-table 
        :data="tableData" 
        style="width: 100%" 
        :header-cell-style="{ background: '#f9fafb', color: '#6b7280', fontWeight: '600' }"
        row-class-name="modern-row"
      >
        <el-table-column prop="title" label="案例标题" min-width="240">
          <template #default="{ row }">
            <div class="title-cell" @click="handleView(row.id)">
              <div class="icon-wrapper" :class="row.case_form === 'document' ? 'document' : 'faq'">
                <el-icon><Document /></el-icon>
              </div>
              <div class="title-info">
                <span class="title-text">{{ row.title }}</span>
                <el-tag
                  v-if="row.case_form === 'document'"
                  type="primary"
                  size="small"
                  effect="plain"
                  class="form-tag"
                >
                  文档
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="category_id" label="分类" width="140">
          <template #default="{ row }">
            <el-tag effect="plain" round class="category-tag">{{ row.categoryId || row.category_id }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="case_type" label="类型" width="120">
          <template #default="{ row }">
             <el-tag 
               :type="(row.caseType || row.case_type) === 'external' ? 'success' : 'warning'" 
               effect="light"
               size="small"
             >
              {{ (row.caseType || row.case_type) === 'external' ? '对外公开' : '内部专用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <div class="status-badge" :class="row.status">
              <span class="dot"></span>
              {{ getStatusText(row.status) }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="数据" width="180">
          <template #default="{ row }">
            <div class="stats-cell">
              <span title="浏览"><el-icon><View /></el-icon> {{ row.view_count ?? row.viewCount ?? 0 }}</span>
              <span title="点赞"><el-icon><Star /></el-icon> {{ row.like_count ?? row.likeCount ?? 0 }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="180">
           <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at || row.createdAt) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="actions-cell">
              <el-tooltip content="编辑" placement="top">
                <el-button link type="primary" @click="handleEdit(row.id)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="查看" placement="top">
                <el-button link type="primary" @click="handleView(row.id)">
                   <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
               <el-tooltip content="删除" placement="top">
                <el-button link type="danger" @click="handleDelete(row.id)">
                   <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSearch"
          @current-change="handleSearch"
          background
        />
      </div>
    </div>
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

// Using snake_case to match backend API
const filters = reactive({
  keyword: '',
  category_id: '',
  status: '',
  case_type: '',
  case_form: ''  // 案例形式筛选
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

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

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString() + ' ' + new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await caseApi.list({
      ...filters,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    tableData.value = res.data?.items || []
    pagination.total = res.data?.total || 0
  } catch (e) {
    // Fallback Mock
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

const handleView = (id) => {
  router.push(`/cases/${id}`)
}

const handleEdit = (id) => {
  router.push(`/cases/${id}/edit`)
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该案例吗？', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
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
.case-list-modern {
  padding: 0;
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
  
  .create-btn {
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
    transition: transform 0.2s;
    
    &:hover {
      transform: translateY(-2px);
    }
  }
}

.filter-container {
  background: white;
  padding: 20px 24px 0;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.modern-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  
  .search-input { width: 300px; }
  .filter-select { width: 160px; }
  
  .type-radio :deep(.el-radio-button__inner) {
    border-radius: 8px;
    border: none;
    background: #f3f4f6;
    margin-right: 8px;
    padding: 8px 16px;
    box-shadow: none;
    
    &:hover { color: #764ba2; }
  }
  
  .type-radio :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background: #764ba2;
    color: white;
    box-shadow: 0 2px 6px rgba(118, 75, 162, 0.25);
  }
}

.table-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;

  .icon-wrapper {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    transition: all 0.2s;

    &.document {
      background: #e0e7ff;
      color: #667eea;
    }

    &.faq {
      background: #fef3c7;
      color: #d97706;
    }
  }

  .title-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .title-text {
    font-weight: 500;
    color: #374151;
    transition: color 0.2s;
  }

  .form-tag {
    font-size: 11px;
    padding: 0 6px;
    height: 18px;
    line-height: 16px;
  }

  &:hover {
    .icon-wrapper { background: #e0e7ff; color: #667eea; }
    .title-text { color: #667eea; }
  }
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }
  
  &.published { color: #059669; .dot { background: #059669; } }
  &.pending_approval { color: #d97706; .dot { background: #d97706; } }
  &.draft { color: #6b7280; .dot { background: #6b7280; } }
  &.rejected { color: #dc2626; .dot { background: #dc2626; } }
}

.stats-cell {
  display: flex;
  gap: 16px;
  color: #9ca3af;
  font-size: 13px;
  
  span { display: flex; align-items: center; gap: 4px; }
}

.date-text { color: #6b7280; font-size: 13px; }

.actions-cell {
  display: flex;
  gap: 4px;
  
  .el-button { margin: 0; font-size: 16px; }
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
