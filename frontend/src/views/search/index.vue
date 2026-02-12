<template>
  <div class="search-page-modern">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">探索知识库</h1>
        <p class="hero-subtitle">发现海量案例，获取专业解决方案</p>
        
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="搜索您感兴趣的案例..."
            size="large"
            class="hero-search-input"
            @keyup.enter.prevent="handleSearch"
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" class="search-btn" @click.prevent="handleSearch" :loading="loading">
                搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- Modern Tags Filter -->
        <div class="filter-tags">
          <div class="filter-group">
            <span class="filter-label">分类:</span>
            <div class="tags-wrapper">
              <span 
                class="filter-tag" 
                :class="{ active: !filters.categoryId }"
                @click="setFilter('categoryId', '')"
              >全部</span>
              <span 
                class="filter-tag" 
                :class="{ active: filters.categoryId === '1' }"
                @click="setFilter('categoryId', '1')"
              >账户安全</span>
              <span 
                class="filter-tag" 
                :class="{ active: filters.categoryId === '2' }"
                @click="setFilter('categoryId', '2')"
              >财务管理</span>
              <span 
                class="filter-tag" 
                :class="{ active: filters.categoryId === '3' }"
                @click="setFilter('categoryId', '3')"
              >产品介绍</span>
            </div>
          </div>

          <div class="filter-group">
             <span class="filter-label">类型:</span>
             <div class="tags-wrapper">
               <span 
                class="filter-tag" 
                :class="{ active: !filters.caseType }"
                @click="setFilter('caseType', '')"
              >全部</span>
               <span 
                class="filter-tag" 
                :class="{ active: filters.caseType === 'external' }"
                @click="setFilter('caseType', 'external')"
              >对外公开</span>
               <span 
                class="filter-tag" 
                :class="{ active: filters.caseType === 'internal' }"
                @click="setFilter('caseType', 'internal')"
              >内部专用</span>
             </div>
          </div>
        </div>
      </div>
      
      <!-- Decorative Background Elements -->
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
    </div>

    <!-- Results Section -->
    <div class="results-container" v-loading="loading">
      <div class="results-header" v-if="results.length > 0 || hasSearched">
        <span class="result-count">找到 <strong>{{ total }}</strong> 个相关结果</span>
      </div>

      <transition-group name="list" tag="div" class="results-grid">
        <div 
          v-for="item in results" 
          :key="item.id" 
          class="case-card"
          @click="handleClick(item)"
        >
          <div class="card-image-placeholder">
            <el-icon><Document /></el-icon>
          </div>
          <div class="card-content">
            <div class="card-badges">
              <span class="badge category">{{ item.categoryId }}</span>
              <span class="badge type" :class="item.caseType">{{ item.caseType === 'external' ? '对外' : '对内' }}</span>
            </div>
            <h3 class="card-title">{{ item.title }}</h3>
            <p class="card-desc">{{ item.content.substring(0, 100) }}...</p>
            <div class="card-footer">
              <span class="stat"><el-icon><View /></el-icon> {{ item.viewCount }}</span>
              <span class="stat"><el-icon><Time /></el-icon> {{ formatDate(item.createdAt) }}</span>
            </div>
          </div>
        </div>
      </transition-group>

      <el-empty 
        v-if="!loading && results.length === 0 && hasSearched" 
        description="未找到相关案例，换个关键词试试？" 
        image-size="200"
      />
      
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          background
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
import { searchApi, caseApi } from '@/services/case'

const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const loading = ref(false)
const results = ref([])
const total = ref(0)
const hasSearched = ref(false)

const filters = reactive({
  categoryId: '',
  caseType: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 12
})

const setFilter = (key, value) => {
  filters[key] = value
  handleSearch()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '刚刚'
  return new Date(dateStr).toLocaleDateString()
}

const handleSearch = async () => {
  loading.value = true
  hasSearched.value = true
  try {
    let res
    if (!searchQuery.value.trim()) {
      // Empty query: list recent cases instead of search
      res = await caseApi.list({
        ...filters,
        page: pagination.page,
        pageSize: pagination.pageSize
      })
    } else {
      // Perform search
      res = await searchApi.searchCases({
        query: searchQuery.value,
        ...filters,
        page: pagination.page,
        pageSize: pagination.pageSize
      })
    }
    
    results.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e) {
    console.error('Search failed:', e)
    // Fallback to empty state, do not mock unless necessary
    results.value = []
    total.value = 0
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
  } else {
    // Initial load recommended content
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
.search-page-modern {
  min-height: calc(100vh - 60px); // Adjust based on layout header height
  background-color: #f8f9fb;
}

/* Hero Section */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 20px 100px;
  text-align: center;
  color: #fff;
  overflow: hidden;
  border-radius: 0 0 40px 40px;
  box-shadow: 0 10px 30px rgba(118, 75, 162, 0.2);
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 40px;
  font-weight: 300;
}

.search-container {
  margin-bottom: 30px;
}

.hero-search-input {
  :deep(.el-input__wrapper) {
    border-radius: 50px;
    padding: 10px 20px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    font-size: 1.1rem;
    
    &.is-focus {
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
    }
  }
  
  :deep(.el-input-group__append) {
    border-radius: 0 50px 50px 0;
    background-color: transparent;
    border: none;
    padding: 0;
    
    .search-btn {
      border-radius: 0 50px 50px 0;
      height: 100%;
      padding: 0 25px;
      font-size: 1rem;
      font-weight: 600;
      background: #409EFF; // Brand color
      border: none;
      
      &:hover {
        background: #66b1ff;
      }
    }
  }
}

/* Filters */
.filter-tags {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 20px;
}

.filter-label {
  margin-right: 12px;
  font-weight: 500;
  font-size: 0.9rem;
}

.tags-wrapper {
  display: flex;
  gap: 8px;
}

.filter-tag {
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
  
  &.active {
    background: #fff;
    color: #764ba2;
    font-weight: 600;
  }
}

/* Decorative Circles */
.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  filter: blur(40px);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -50px;
  left: -100px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -20px;
  right: -50px;
}

/* Results Section */
.results-container {
  max-width: 1200px;
  margin: -60px auto 0;
  padding: 0 20px 40px;
  position: relative;
  z-index: 20;
}

.results-header {
  margin-bottom: 20px;
  color: #606266;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

/* Case Card */
.case-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 320px;
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
    
    .card-image-placeholder {
      background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
      color: #fff;
    }
  }
}

.card-image-placeholder {
  height: 140px;
  background: #eef2f7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #c0c4cc;
  transition: all 0.4s;
}

.card-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-badges {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  
  .badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    
    &.category {
      background: #f0f2f5;
      color: #909399;
    }
    
    &.type {
      &.external {
        background: #e1f3d8;
        color: #67c23a;
      }
      &.internal {
        background: #faecd8;
        color: #e6a23c;
      }
    }
  }
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
  line-height: 1.4;
  
  // Truncate two lines
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 0.9rem;
  color: #909399;
  line-height: 1.5;
  margin-bottom: auto; // Push footer to bottom
  
  // Truncate three lines
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: space-between;
  color: #c0c4cc;
  font-size: 0.85rem;
  
  .stat {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.pagination-wrapper {
  margin-top: 40px;
  text-align: center;
  display: flex;
  justify-content: center;
}

/* Animations */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

// Ensure items move smoothly when others leave
.list-leave-active {
  position: absolute; 
}
</style>
