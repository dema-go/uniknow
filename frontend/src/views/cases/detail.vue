<template>
  <div class="case-detail">
    <el-card shadow="never" v-if="caseData">
      <template #header>
        <div class="card-header">
          <div class="title-area">
            <h2>{{ caseData.title }}</h2>
            <div class="tags">
              <el-tag :type="caseData.caseType === 'external' ? 'success' : 'warning'" size="small">
                {{ caseData.caseType === 'external' ? '对外' : '对内' }}
              </el-tag>
              <el-tag type="info" size="small">{{ getStatusText(caseData.status) }}</el-tag>
            </div>
          </div>
          <div class="actions">
            <el-button @click="$router.back()">返回</el-button>
            <el-button type="primary" @click="handleEdit">编辑</el-button>
          </div>
        </div>
      </template>

      <div class="meta-info">
        <span><el-icon><User /></el-icon> {{ caseData.creatorId }}</span>
        <span><el-icon><Clock /></el-icon> {{ caseData.createdAt }}</span>
        <span><el-icon><View /></el-icon> {{ caseData.viewCount }} 次浏览</span>
        <span><el-icon><Star /></el-icon> {{ caseData.likeCount }} 点赞</span>
      </div>

      <el-divider />

      <div class="content">
        <div class="content-text">{{ caseData.content }}</div>
      </div>

      <div class="footer-actions">
        <el-button @click="handleLike">
          <el-icon><Star /></el-icon> 点赞 {{ caseData.likeCount }}
        </el-button>
        <el-button @click="handleDislike">
          <el-icon><StarFilled /></el-icon> 点踩 {{ caseData.dislikeCount }}
        </el-button>
        <el-button @click="handleCopy">
          <el-icon><CopyDocument /></el-icon> 复制内容
        </el-button>
      </div>
    </el-card>

    <el-skeleton v-else :rows="10" animated />
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

const getStatusText = (status) => {
  const map = {
    'draft': '草稿',
    'pending_approval': '待审批',
    'published': '已发布',
    'rejected': '已拒绝'
  }
  return map[status] || status
}

const fetchData = async () => {
  try {
    const res = await caseApi.get(route.params.id)
    caseData.value = res.data
  } catch (e) {
    // 模拟数据
    caseData.value = {
      id: route.params.id,
      title: '如何重置密码',
      content: '如果您忘记了密码，可以按照以下步骤重置：\n\n1. 点击登录页面的"忘记密码"链接\n2. 输入您的注册邮箱地址\n3. 检查邮箱收到的重置链接\n4. 点击链接设置新密码\n5. 使用新密码登录\n\n注意：重置链接24小时内有效。',
      categoryId: '账户安全',
      caseType: 'external',
      status: 'published',
      creatorId: '张三',
      createdAt: '2024-01-15 10:30:00',
      viewCount: 100,
      likeCount: 10,
      dislikeCount: 1
    }
  }
}

const handleEdit = () => {
  router.push(`/cases/${route.params.id}`)
}

const handleLike = () => {
  caseData.value.likeCount++
  ElMessage.success('点赞成功')
}

const handleDislike = () => {
  caseData.value.dislikeCount++
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
.case-detail {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .title-area {
    h2 {
      margin: 0 0 10px 0;
    }

    .tags {
      display: flex;
      gap: 8px;
    }
  }

  .meta-info {
    display: flex;
    gap: 20px;
    color: $text-secondary;
    font-size: 14px;

    span {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .content {
    min-height: 300px;

    .content-text {
      white-space: pre-wrap;
      line-height: 1.8;
    }
  }

  .footer-actions {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid $border-light;
  }
}
</style>
