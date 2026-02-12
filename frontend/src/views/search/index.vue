<template>
  <div class="search-page">
    <el-card shadow="never" class="search-card">
      <el-input
        v-model="searchQuery"
        placeholder="搜索案例..."
        size="large"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </template>
      </el-input>

      <div class="filter-section">
        <span class="filter-label">筛选：</span>
        <el-select v-model="filters.categoryId" placeholder="全部分类" clearable>
          <el-option label="账户安全" value="1" />
          <el-option label="财务管理" value="2" />
          <el-option label="产品介绍" value="3" />
        </el-select>
        <el-select v-model="filters.caseType" placeholder="全部类型" clearable>
          <el-option label="对外案例" value="external" />
          <el-option label="对内案例" value="internal" />
        </el-select>
      </div>
    </el-card>

    <div class="search-results" v-loading="loading">
      <div class="results-header" v-if="results.length > 0">
        共找到 <strong>{{ total }}</strong> 条相关案例
      </div>

      <el-empty v-if="!loading && results.length === 0" description="暂无相关内容" />

      <div class="result-list">
        <el-card
          v-for="item in results"
          :key="item.id"
          shadow="hover"
          class="result-item"
          @click="handleClick(item)"
        >
          <div class="result-title">
            <el-icon><Document /></el-icon>
            {{ item.title }}
          </div>
          <div class="result-content">
            {{ item.content.substring(0, 200) }}...
          </div>
          <div class="result-meta">
            <el-tag size="small">{{ item.categoryId }}</el-tag>
            <el-tag size="small" :type="item.caseType === 'external' ? 'success' : 'warning'">
              {{ item.caseType === 'external' ? '对外' : '对内' }}
            </el-tag>
            <span class="views">浏览 {{ item.viewCount }}</span>
          </div>
        </el-card>
      </div>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="handleSearch"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchApi } from '@/services/case'

const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const loading = ref(false)
const results = ref([])
const total = ref(0)

const filters = reactive({
  categoryId: '',
  caseType: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20
})

const handleSearch = async () => {
  loading.value = true
  try {
    const res = await searchApi.searchCases({
      query: searchQuery.value,
      ...filters,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    results.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e) {
    // 模拟数据
    results.value = [
      { id: '1', title: '如何重置密码', content: '如果您忘记了密码，可以按照以下步骤重置密码...', categoryId: '账户安全', caseType: 'external', viewCount: 100 },
      { id: '2', title: '账单查询指南', content: '您可以通过以下方式查询您的账单记录...', categoryId: '财务管理', caseType: 'external', viewCount: 50 }
    ]
    total.value = 2
  } finally {
    loading.value = false
  }
}

const handleClick = (item) => {
  router.push(`/cases/${item.id}`)
}

onMounted(() => {
  if (route.query.q) {
    searchQuery.value = route.query.q
    handleSearch()
  }
})

watch(() => route.query.q, (newVal) => {
  if (newVal) {
    searchQuery.value = newVal
    handleSearch()
  }
})
</script>

<style lang="scss" scoped>
.search-page {
  .search-card {
    margin-bottom: 20px;
  }

  .filter-section {
    margin-top: 15px;
    display: flex;
    align-items: center;
    gap: 10px;

    .filter-label {
      color: $text-secondary;
    }
  }

  .results-header {
    margin-bottom: 15px;
    color: $text-secondary;
  }

  .result-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .result-item {
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }

  .result-title {
    font-size: 16px;
    font-weight: 500;
    color: $primary-color;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .result-content {
    color: $text-regular;
    line-height: 1.6;
    margin-bottom: 10px;
  }

  .result-meta {
    display: flex;
    align-items: center;
    gap: 10px;

    .views {
      color: $text-secondary;
      font-size: 13px;
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }
}
</style>
