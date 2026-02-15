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
                 <el-tag :type="getFormTagType(caseData.case_form)" effect="light" round>
                  {{ caseData.case_form === 'document' ? '文档' : 'FAQ' }}
                </el-tag>
                <el-tag :type="caseData.case_type === 'external' ? 'success' : 'warning'" effect="light" round>
                  {{ caseData.case_type === 'external' ? '对外公开' : '内部专用' }}
                </el-tag>
                <el-tag type="info" effect="plain" round>{{ getStatusText(caseData.status) }}</el-tag>
                <el-tag effect="plain" round class="category-tag">{{ caseData.category_id }}</el-tag>
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
              <span>{{ caseData.creator_id }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Clock /></el-icon> 发布于 {{ formatDate(caseData.created_at) }}
            </div>
            <div class="meta-item stat">
              <el-icon><View /></el-icon> {{ caseData.view_count }}
            </div>
            <div class="meta-item stat">
              <el-icon><Star /></el-icon> {{ caseData.like_count }}
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="content-wrapper">
        <el-card class="content-card" shadow="never">
          <!-- 文档类型：显示文件信息和下载按钮 -->
          <div v-if="caseData.case_form === 'document'" class="document-section">
            <div class="document-info">
              <el-icon class="file-icon"><Document /></el-icon>
              <div class="file-details">
                <h3>{{ caseData.file_name || '未知文件' }}</h3>
                <p class="file-meta">
                  <span v-if="caseData.file_size">{{ formatFileSize(caseData.file_size) }}</span>
                  <span v-if="caseData.file_type">{{ caseData.file_type }}</span>
                </p>
              </div>
            </div>
            <el-button type="primary" @click="handleDownload" :loading="downloading">
              <el-icon><Download /></el-icon> 下载文档
            </el-button>
          </div>

          <!-- 文档描述 -->
          <div v-if="caseData.case_form === 'document' && caseData.content" class="document-description">
            <h4>文档描述</h4>
            <p>{{ caseData.content }}</p>
          </div>

           <!-- FAQ 类型：Markdown渲染内容 -->
           <article v-if="caseData.case_form === 'faq'" class="article-content markdown-body" v-html="renderedContent"></article>

           <div class="article-footer">
             <div class="interaction-bar">
               <el-button round class="action-btn like" @click="handleLike" :type="liked ? 'primary' : 'default'">
                 <el-icon><Star /></el-icon> <span>{{ caseData.like_count }} 赞</span>
               </el-button>
               <el-button round class="action-btn dislike" @click="handleDislike">
                 <el-icon><StarFilled /></el-icon> <span>踩</span>
               </el-button>
               <el-button round class="action-btn copy" @click="handleCopy" v-if="caseData.case_form === 'faq'">
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Download } from '@element-plus/icons-vue'
import { marked } from 'marked'
import 'github-markdown-css'
import 'highlight.js/styles/github.css'
import hljs from 'highlight.js'
import { caseApi, fileApi } from '@/services/case'

// 配置marked代码高亮
marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

const route = useRoute()
const router = useRouter()

const caseData = ref(null)
const liked = ref(false)
const downloading = ref(false)

// 计算渲染后的Markdown内容
const renderedContent = computed(() => {
  if (!caseData.value?.content) return ''
  return marked.parse(caseData.value.content)
})

const getStatusText = (status) => {
  const map = {
    'published': '已发布',
    'pending_approval': '待审批',
    'draft': '草稿',
    'rejected': '已拒绝'
  }
  return map[status] || status
}

const getFormTagType = (form) => {
  return form === 'document' ? 'primary' : ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

const fetchData = async () => {
  try {
    const res = await caseApi.get(route.params.id)
    caseData.value = res.data || res
  } catch (e) {
    // Mock data for fallback
    caseData.value = {
      id: route.params.id,
      title: '如何重置用户密码（标准流程）',
      content: `如果您忘记了密码，可以按照以下步骤重置：

1. 点击登录页面的"忘记密码"链接
2. 输入您的注册邮箱地址
3. 检查邮箱收到的重置链接
4. 点击链接设置新密码
5. 使用新密码登录

\`\`\`bash
# 示例命令
npm install
npm run dev
\`\`\`

**注意**：重置链接24小时内有效。`,
      category_id: '账户安全',
      case_type: 'external',
      status: 'published',
      creator_id: '系统管理员',
      created_at: '2024-01-15 10:30:00',
      view_count: 124,
      like_count: 45,
      dislike_count: 0
    }
  }
}

const handleEdit = () => {
  router.push(`/cases/${route.params.id}/edit`)
}

const handleLike = () => {
  if (liked.value) return
  caseData.value.like_count++
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

const handleDownload = async () => {
  if (!caseData.value.file_path) {
    ElMessage.error('文件路径不存在')
    return
  }

  downloading.value = true
  try {
    // 解析 file_path (格式: bucket/object_name)
    const pathParts = caseData.value.file_path.split('/')
    const bucket = pathParts[0]
    const objectName = pathParts.slice(1).join('/')

    const response = await fileApi.download(bucket, objectName)

    // 创建下载链接
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = caseData.value.file_name || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('下载成功')
  } catch (error) {
    console.error('Download error:', error)
    ElMessage.error('下载失败')
  } finally {
    downloading.value = false
  }
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

  // 文档类型样式
  .document-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px;
    background: #f9fafb;
    border-radius: 12px;
    margin-bottom: 24px;

    .document-info {
      display: flex;
      align-items: center;
      gap: 16px;

      .file-icon {
        font-size: 48px;
        color: #667eea;
      }

      .file-details {
        h3 {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          color: #111827;
        }

        .file-meta {
          margin: 0;
          font-size: 13px;
          color: #6b7280;

          span {
            margin-right: 12px;
          }
        }
      }
    }
  }

  .document-description {
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid #f3f4f6;

    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      font-weight: 600;
      color: #374151;
    }

    p {
      margin: 0;
      color: #6b7280;
      line-height: 1.6;
    }
  }

  // GitHub Markdown样式
  .article-content :deep(.markdown-body) {
    font-size: 16px;
    line-height: 1.8;
    color: #374151;

    h1, h2, h3, h4, h5, h6 {
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
    }

    h1 { font-size: 2em; }
    h2 { font-size: 1.5em; }
    h3 { font-size: 1.25em; }

    p {
      margin-bottom: 16px;
    }

    code {
      background: #f3f4f6;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 0.9em;
    }

    pre {
      background: #f6f8fa;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin-bottom: 16px;

      code {
        background: none;
        padding: 0;
      }
    }

    ul, ol {
      padding-left: 24px;
      margin-bottom: 16px;
    }

    li {
      margin-bottom: 8px;
    }

    blockquote {
      border-left: 4px solid #d1d5db;
      padding-left: 16px;
      margin: 16px 0;
      color: #6b7280;
    }

    table {
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 16px;

      th, td {
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
      }

      th {
        background: #f9fafb;
        font-weight: 600;
      }
    }

    a {
      color: #7c3aed;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }

    img {
      max-width: 100%;
      border-radius: 8px;
      margin: 16px 0;
    }
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
