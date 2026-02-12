<template>
  <div class="case-detail-modern">
    <el-skeleton v-if="!caseData" :rows="10" animated />
    
    <div v-else class="detail-container">
      <!-- Header Area -->
      <div class="detail-header">
        <div class="header-content">
          <div class="breadcrumb">
            <span class="back-link" @click="$router.push('/cases')">
              <el-icon><ArrowLeft /></el-icon> 返回列表
            </span>
          </div>
          <div class="header-main">
            <div class="title-section">
              <h1 class="case-title">{{ caseData.title }}</h1>
               <div class="meta-tags">
                 <el-tag :type="caseData.caseType === 'external' ? 'success' : 'warning'" effect="light" round>
                  {{ caseData.caseType === 'external' ? '对外公开' : '内部专用' }}
                </el-tag>
                <el-tag type="info" effect="plain" round>{{ getStatusText(caseData.status) }}</el-tag>
                <el-tag effect="plain" round class="category-tag">{{ caseData.categoryId }}</el-tag>
              </div>
            </div>
            <div class="header-actions">
              <el-button @click="handleEdit" type="primary" plain>
                 <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>
          </div>
          
          <div class="meta-row">
            <div class="meta-item">
              <el-avatar :size="24" class="creator-avatar" icon="UserFilled" />
              <span>{{ caseData.creatorId }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Clock /></el-icon> 发布于 {{ formatDate(caseData.createdAt) }}
            </div>
            <div class="meta-item stat">
              <el-icon><View /></el-icon> {{ caseData.viewCount }}
            </div>
            <div class="meta-item stat">
              <el-icon><Star /></el-icon> {{ caseData.likeCount }}
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="content-wrapper">
        <el-card class="content-card" shadow="never">
           <div class="article-content">{{ caseData.content }}</div>
           
           <div class="article-footer">
             <div class="interaction-bar">
               <el-button round class="action-btn like" @click="handleLike" :type="liked ? 'primary' : 'default'">
                 <el-icon><Star /></el-icon> <span>{{ caseData.likeCount }} 赞</span>
               </el-button>
               <el-button round class="action-btn dislike" @click="handleDislike">
                 <el-icon><StarFilled /></el-icon> <span>踩</span>
               </el-button>
               <el-button round class="action-btn copy" @click="handleCopy">
                 <el-icon><CopyDocument /></el-icon> <span>复制</span>
               </el-button>
             </div>
           </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { caseApi } from '@/services/case'

const route = useRoute()
const router = useRouter()

const caseData = ref(null)
const liked = ref(false)

const getStatusText = (status) => {
  const map = {
    'published': '已发布',
    'pending_approval': '待审批',
    'draft': '草稿',
    'rejected': '已拒绝'
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

const fetchData = async () => {
  try {
    const res = await caseApi.get(route.params.id)
    caseData.value = res.data
  } catch (e) {
    // Mock
    caseData.value = {
      id: route.params.id,
      title: '如何重置用户密码（标准流程）',
      content: '如果您忘记了密码，可以按照以下步骤重置：\n\n1. 点击登录页面的"忘记密码"链接\n2. 输入您的注册邮箱地址\n3. 检查邮箱收到的重置链接\n4. 点击链接设置新密码\n5. 使用新密码登录\n\n注意：重置链接24小时内有效。',
      categoryId: '账户安全',
      caseType: 'external',
      status: 'published',
      creatorId: '系统管理员',
      createdAt: '2024-01-15 10:30:00',
      viewCount: 124,
      likeCount: 45,
      dislikeCount: 0
    }
  }
}

const handleEdit = () => {
  router.push(`/cases/create?id=${route.params.id}`) // Assuming create handles edit
}

const handleLike = () => {
  if (liked.value) return
  caseData.value.likeCount++
  liked.value = true
  ElMessage.success('点赞成功')
}

const handleDislike = () => {
  ElMessage.warning('已记录您的反馈')
}

const handleCopy = () => {
  navigator.clipboard.writeText(caseData.value.content)
  ElMessage.success('已复制到剪贴板')
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.case-detail-modern {
  max-width: 1000px;
  margin: 0 auto;
}

.detail-header {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  
  .back-link {
    cursor: pointer;
    color: #6b7280;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 16px;
    &:hover { color: #764ba2; }
  }
  
  .header-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
    .case-title {
      font-size: 28px;
      font-weight: 700;
      color: #111827;
      margin: 0 0 12px 0;
      line-height: 1.3;
    }
    
    .meta-tags {
      display: flex;
      gap: 8px;
    }
  }
  
  .meta-row {
    display: flex;
    align-items: center;
    gap: 24px;
    color: #6b7280;
    font-size: 14px;
    padding-top: 24px;
    border-top: 1px solid #f3f4f6;
    
    .meta-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    
    .creator-avatar {
      background: #e0e7ff;
      color: #667eea;
    }
  }
}

.content-wrapper {
  .content-card {
    border: none;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  }
  
  .article-content {
    font-size: 16px;
    line-height: 1.8;
    color: #374151;
    white-space: pre-wrap;
    min-height: 200px;
  }
  
  .article-footer {
    margin-top: 60px;
    display: flex;
    justify-content: center;
    
    .interaction-bar {
      display: flex;
      gap: 16px;
      
      .action-btn {
        padding: 12px 24px;
        height: auto;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
        
        &:hover {
          transform: translateY(-2px);
        }
        
        &.like {
          // styles
        }
      }
    }
  }
}
</style>
