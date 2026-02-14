<template>
  <div class="case-create-modern">
    <div class="page-header">
       <span class="back-link" @click="$router.back()">
         <el-icon><ArrowLeft /></el-icon> 返回
       </span>
       <h2>{{ isEdit ? '编辑案例' : '创建新案例' }}</h2>
    </div>

    <div class="form-wrapper">
      <el-card class="form-card" shadow="never">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="modern-form"
          v-loading="loading"
        >
          <div class="form-section">
            <h3 class="section-title">基本信息</h3>
            <el-form-item label="案例标题" prop="title">
              <el-input
                v-model="form.title"
                placeholder="请输入简明扼要的标题"
                size="large"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>

            <div class="form-row">
              <el-form-item label="所属分类" prop="category_id" class="half-width">
                <el-select v-model="form.category_id" placeholder="选择分类" size="large" class="full-width">
                  <el-option label="账户安全" value="1" />
                  <el-option label="财务管理" value="2" />
                  <el-option label="产品介绍" value="3" />
                  <el-option label="常见问题" value="4" />
                </el-select>
              </el-form-item>

              <el-form-item label="类型" prop="case_type" class="half-width">
                <el-radio-group v-model="form.case_type" size="large">
                  <el-radio-button value="external" label="external">对外公开</el-radio-button>
                  <el-radio-button value="internal" label="internal">内部专用</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </div>

            <el-form-item label="标签 (Tags)">
               <el-select
                v-model="form.tags"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="输入标签并回车"
                size="large"
                class="full-width"
              >
              </el-select>
            </el-form-item>
          </div>

          <div class="form-section">
             <div class="section-header">
               <h3 class="section-title">内容详情</h3>
               <el-button-group size="small">
                 <el-button
                   :type="editorMode === 'markdown' ? 'primary' : ''"
                   @click="editorMode = 'markdown'"
                 >
                   Markdown
                 </el-button>
                 <el-button
                   :type="editorMode === 'rich-text' ? 'primary' : ''"
                   @click="editorMode = 'rich-text'"
                 >
                   富文本
                 </el-button>
               </el-button-group>
             </div>

             <el-form-item prop="content">
               <!-- Markdown编辑器 -->
               <MdEditor
                 v-if="editorMode === 'markdown'"
                 v-model="form.content"
                 :toolbars="toolbars"
                 @onUploadImg="handleImageUpload"
                 class="markdown-editor"
               />
               <!-- Quill富文本编辑器 -->
               <QuillEditor
                 v-else
                 v-model:content="form.content"
                 contentType="html"
                 theme="snow"
                 :toolbar="quillToolbar"
                 class="quill-editor"
               />
             </el-form-item>
          </div>

          <div class="form-actions">
            <el-button size="large" @click="$router.back()">取消</el-button>
            <el-button size="large" type="primary" plain @click="handleSaveDraft" :loading="saving">
              {{ saveButtonText }}
            </el-button>
            <el-button size="large" type="primary" @click="handleSubmit" :loading="saving" class="submit-btn">
              {{ submitButtonText }}
            </el-button>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { caseApi } from '@/services/case'
import 'md-editor-v3/lib/style.css'
import { useUserStore } from '@/stores/user'
import { MdEditor } from 'md-editor-v3'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const saving = ref(false)
const loading = ref(false)
const editorMode = ref('markdown')

// 判断是否为编辑模式
const isEdit = computed(() => !!route.params.id)
const caseId = computed(() => route.params.id)

// 根据用户角色判断按钮文本和提交行为
const isAdmin = computed(() => userStore.isAdmin())
const submitButtonText = computed(() => {
  if (isEdit.value) return '保存修改'
  return isAdmin.value ? '直接发布' : '提交审批'
})
const saveButtonText = computed(() => isAdmin.value ? '保存为草稿' : '保存草稿')

// Markdown编辑器工具栏配置
const toolbars = [
  'bold',
  'underline',
  'italic',
  'strikeThrough',
  '-',
  'title',
  'sub',
  'sup',
  'quote',
  'unorderedList',
  'orderedList',
  'task',
  '-',
  'codeRow',
  'code',
  'link',
  'image',
  'table',
  '-',
  'revoke',
  'next',
  'save',
  '=',
  'pageFullscreen',
  'fullscreen',
  'preview',
  'htmlPreview',
  'catalog'
]

// Quill 工具栏配置
const quillToolbar = [
  [{ header: [1, 2, 3, false] }],
  ['bold', 'italic', 'underline', 'strike'],
  [{ color: [] }, { background: [] }],
  [{ align: [] }],
  [{ list: 'ordered' }, { list: 'bullet' }],
  [{ indent: '-1' }, { indent: '+1' }],
  ['blockquote', 'code-block', 'link', 'image'],
  ['clean']
]

// Fixed snake_case to match backend
const form = reactive({
  title: '',
  category_id: '',
  case_type: 'external',
  tags: [],
  content: ''
})

const rules = {
  title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2-100 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入案例内容', trigger: 'blur' }
  ]
}

// 图片上传处理
const handleImageUpload = async (files, callback) => {
  // TODO: 实现图片上传功能
  // 目前使用本地预览
  const reader = new FileReader()
  reader.onload = (e) => {
    callback(e.target.result)
  }
  reader.readAsDataURL(files[0])
}

// 加载案例数据（编辑模式）
const loadCaseData = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const id = caseId.value
    const response = await caseApi.get(id)
    const caseData = response.data || {}

    // 填充表单数据
    form.title = caseData.title || ''
    form.category_id = caseData.category_id || ''
    form.case_type = caseData.case_type || 'external'
    form.tags = caseData.tags || []
    form.content = caseData.content || ''
  } catch (error) {
    ElMessage.error('加载案例数据失败')
    console.error('Load case error:', error)
    router.push('/cases')
  } finally {
    loading.value = false
  }
}

// 页面加载时执行
onMounted(() => {
  loadCaseData()
})

// 保存草稿 - 明确传递 draft 状态
const handleSaveDraft = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      saveWithStatus('draft')
    }
  })
}

// 提交案例 - 不传递 status，让后端根据用户角色决定
// 管理员会直接发布，维护员会进入审批流程
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      saveWithStatus(null) // 不传 status，由后端根据角色决定
    }
  })
}

// 统一的保存方法
const saveWithStatus = async (status) => {
  saving.value = true
  try {
    const data = { ...form }
    // 只有显式传递 status 时才添加（如 draft）
    // 提交时不传 status，由后端根据用户角色决定
    if (status) {
      data.status = status
    }

    if (isEdit.value) {
      // 编辑模式：调用更新接口
      await caseApi.update(caseId.value, data)
      ElMessage.success('案例更新成功')
    } else {
      // 创建模式：调用创建接口
      await caseApi.create(data)

      if (status === 'draft') {
        ElMessage.success('草稿保存成功')
      } else if (isAdmin.value) {
        ElMessage.success('案例发布成功')
      } else {
        ElMessage.success('案例已提交审批')
      }
    }
    router.push('/cases')
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败：请检查网络或必填项' : '保存失败：请检查网络或必填项')
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.case-create-modern {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;

  .back-link {
    cursor: pointer;
    color: #6b7280;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 8px;
    font-size: 14px;
    &:hover { color: #764ba2; }
  }

  h2 { font-size: 24px; font-weight: 700; color: #111827; margin: 0; }
}

.form-card {
  border: none;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.form-section {
  margin-bottom: 32px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f3f4f6;
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #374151;
    margin: 0;
  }
}

.form-row {
  display: flex;
  gap: 24px;
}

.half-width { flex: 1; }
.full-width { width: 100%; }

.markdown-editor {
  border-radius: 8px;
  overflow: hidden;
}

.quill-editor {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  min-height: 400px;
  background: #fff;

  :deep(.ql-toolbar) {
    border: none;
    border-bottom: 1px solid #e5e7eb;
  }

  :deep(.ql-container) {
    border: none;
    min-height: 350px;
  }

  :deep(.ql-editor) {
    min-height: 350px;
    font-size: 14px;
    line-height: 1.6;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid #f3f4f6;

  .submit-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    padding: 12px 32px;

    &:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }
  }
}
</style>
