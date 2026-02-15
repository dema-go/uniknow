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

            <!-- 案例形式选择 -->
            <el-form-item label="案例形式" prop="case_form">
              <el-radio-group v-model="form.case_form" size="large" class="form-type-radio" :disabled="isEdit">
                <el-radio-button value="faq" label="faq">
                  <el-icon><ChatDotRound /></el-icon>
                  FAQ 问答
                </el-radio-button>
                <el-radio-button value="document" label="document">
                  <el-icon><Document /></el-icon>
                  文档上传
                </el-radio-button>
              </el-radio-group>
            </el-form-item>

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

          <!-- FAQ 类型：显示编辑器 -->
          <div class="form-section" v-if="form.case_form === 'faq'">
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
               <div v-else class="quill-editor-wrapper">
                 <QuillEditor
                   v-model:content="form.content"
                   contentType="html"
                   theme="snow"
                   :toolbar="quillToolbar"
                 />
               </div>
             </el-form-item>
          </div>

          <!-- 文档类型：显示文件上传 -->
          <div class="form-section" v-if="form.case_form === 'document'">
            <h3 class="section-title">文档上传</h3>

            <el-form-item prop="file">
              <el-upload
                ref="uploadRef"
                class="document-uploader"
                drag
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :file-list="fileList"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.md"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 PDF、Word、Excel、PPT、TXT、Markdown 格式，最大 50MB
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <!-- 文档描述 -->
            <el-form-item label="文档描述">
              <el-input
                v-model="form.content"
                type="textarea"
                :rows="3"
                placeholder="请输入文档的简要描述..."
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

    <!-- 编辑器侧边栏 -->
    <EditorSidebar
      v-if="form.case_form === 'faq'"
      :editor-mode="editorMode"
      @template-select="handleTemplateInsert"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Document, UploadFilled } from '@element-plus/icons-vue'
import { caseApi, fileApi } from '@/services/case'
import 'md-editor-v3/lib/style.css'
import { useUserStore } from '@/stores/user'
import { MdEditor } from 'md-editor-v3'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import EditorSidebar from '@/components/editor/EditorSidebar.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const uploadRef = ref(null)
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

// 表单数据
const form = reactive({
  title: '',
  category_id: '',
  case_type: 'external',
  case_form: 'faq',  // 默认 FAQ 类型
  tags: [],
  content: '',
  // 文档相关
  file_name: '',
  file_path: '',
  file_size: 0,
  file_type: ''
})

// 文件上传相关
const selectedFile = ref(null)
const fileList = ref([])

const rules = {
  title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2-100 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  content: [
    {
      required: true,
      message: '请输入案例内容',
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.case_form === 'faq' && !value) {
          callback(new Error('请输入案例内容'))
        } else {
          callback()
        }
      }
    }
  ]
}

// 文件上传处理
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  form.file_name = file.name
  form.file_size = file.size
}

const handleFileRemove = () => {
  selectedFile.value = null
  form.file_name = ''
  form.file_path = ''
  form.file_size = 0
  form.file_type = ''
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

// 处理模版插入
const handleTemplateInsert = (template) => {
  // 如果当前有内容，询问是否覆盖
  if (form.content && form.content.trim()) {
    // 直接追加模版内容
    form.content = form.content + '\n\n' + template.content
  } else {
    // 直接使用模版内容
    form.content = template.content
  }
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
    form.case_form = caseData.case_form || 'faq'
    form.tags = caseData.tags || []
    form.content = caseData.content || ''

    // 文档类型：填充文件信息
    if (caseData.case_form === 'document' && caseData.file_name) {
      form.file_name = caseData.file_name
      form.file_path = caseData.file_path
      form.file_size = caseData.file_size
      form.file_type = caseData.file_type
      fileList.value = [{ name: caseData.file_name }]
    }
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

    // 如果是文档类型且有选择新文件，先上传文件
    if (form.case_form === 'document' && selectedFile.value) {
      const formData = new FormData()
      formData.append('file', selectedFile.value)

      try {
        const uploadRes = await fileApi.upload(formData)
        data.file_path = uploadRes.data.file_path
        data.file_name = uploadRes.data.file_name
        data.file_size = uploadRes.data.file_size
        data.file_type = uploadRes.data.file_type
      } catch (uploadError) {
        ElMessage.error('文件上传失败')
        saving.value = false
        return
      }
    }

    // 文档类型如果没有内容，设置为空字符串
    if (form.case_form === 'document' && !data.content) {
      data.content = ''
    }

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

// 案例形式选择样式
.form-type-radio {
  width: 100%;

  :deep(.el-radio-button) {
    flex: 1;

    .el-radio-button__inner {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 12px 24px;
    }
  }
}

// 文档上传样式
.document-uploader {
  width: 100%;

  :deep(.el-upload) {
    width: 100%;
  }

  :deep(.el-upload-dragger) {
    width: 100%;
    padding: 40px;
    border-radius: 12px;
    border: 2px dashed #d1d5db;
    background: #f9fafb;

    &:hover {
      border-color: #667eea;
      background: #f3f4f6;
    }
  }

  .el-icon--upload {
    font-size: 48px;
    color: #9ca3af;
    margin-bottom: 16px;
  }

  .el-upload__text {
    color: #6b7280;
    font-size: 14px;

    em {
      color: #667eea;
      font-style: normal;
    }
  }

  .el-upload__tip {
    margin-top: 8px;
    color: #9ca3af;
    font-size: 12px;
  }
}

.markdown-editor {
  border-radius: 8px;
  overflow: hidden;
}

.quill-editor-wrapper {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  min-height: 400px;
  background: #fff;
  display: flex;
  flex-direction: column;

  :deep(.ql-toolbar) {
    border: none;
    border-bottom: 1px solid #e5e7eb;
    background: #f9fafb;
    flex-shrink: 0;
  }

  :deep(.ql-container) {
    border: none;
    min-height: 350px;
    flex: 1;
    font-size: 14px;
  }

  :deep(.ql-editor) {
    min-height: 350px;
    font-size: 14px;
    line-height: 1.6;
    padding: 16px;
  }

  // 空白状态下的 placeholder 样式
  :deep(.ql-editor.ql-blank::before) {
    font-style: normal;
    color: #9ca3af;
    font-size: 14px;
    left: 16px;
    right: 16px;
  }

  // 确保编辑器获得焦点时有明显反馈
  :deep(.ql-container:focus-within) {
    outline: 2px solid #667eea;
    outline-offset: -2px;
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
