<template>
  <div class="case-create-modern">
    <div class="page-header">
       <span class="back-link" @click="$router.back()">
         <el-icon><ArrowLeft /></el-icon> 返回
       </span>
       <h2>创建新案例</h2>
    </div>

    <div class="form-wrapper">
      <el-card class="form-card" shadow="never">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="modern-form"
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
             <h3 class="section-title">内容详情</h3>
             <el-form-item prop="content">
               <el-input
                v-model="form.content"
                type="textarea"
                :rows="12"
                placeholder="在此输入案例详细内容，支持 Markdown 格式..."
                resize="none"
              />
             </el-form-item>
          </div>

          <div class="form-actions">
            <el-button size="large" @click="$router.back()">取消</el-button>
            <el-button size="large" type="primary" plain @click="handleSave('draft')" :loading="saving">
              保存草稿
            </el-button>
            <el-button size="large" type="primary" @click="handleSubmit" :loading="saving" class="submit-btn">
              提交审批
            </el-button>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { caseApi } from '@/services/case'

const router = useRouter()
const formRef = ref(null)
const saving = ref(false)

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

const handleSave = async (status = 'draft') => {
  saving.value = true
  try {
    await caseApi.create({
      ...form,
      status
    })
    ElMessage.success('保存成功')
    router.push('/cases')
  } catch (e) {
    ElMessage.error('保存失败：请检查网络或必填项')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      handleSave('pending_approval')
    }
  })
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
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f3f4f6;
  }
}

.form-row {
  display: flex;
  gap: 24px;
}

.half-width { flex: 1; }
.full-width { width: 100%; }

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
