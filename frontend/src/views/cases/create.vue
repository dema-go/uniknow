<template>
  <div class="case-create">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>创建案例</span>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="case-form"
      >
        <el-form-item label="案例标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入案例标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="所属分类" prop="categoryId">
          <el-select v-model="form.categoryId" placeholder="请选择分类">
            <el-option label="账户安全" value="1" />
            <el-option label="财务管理" value="2" />
            <el-option label="产品介绍" value="3" />
            <el-option label="常见问题" value="4" />
          </el-select>
        </el-form-item>

        <el-form-item label="案例类型" prop="caseType">
          <el-radio-group v-model="form.caseType">
            <el-radio value="external">对外案例</el-radio>
            <el-radio value="internal">对内案例</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="案例标签">
          <el-select
            v-model="form.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请输入标签"
          >
            <el-option label="热门" value="hot" />
            <el-option label="新功能" value="new" />
            <el-option label="重要" value="important" />
          </el-select>
        </el-form-item>

        <el-form-item label="使用模板">
          <el-select
            v-model="form.templateId"
            placeholder="不适用模板"
            clearable
          >
            <el-option label="标准案例模板" value="1" />
            <el-option label="FAQ 模板" value="2" />
            <el-option label="操作指南模板" value="3" />
          </el-select>
        </el-form-item>

        <el-form-item label="案例内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="15"
            placeholder="请输入案例详细内容"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSave('draft')" :loading="saving">
            保存草稿
          </el-button>
          <el-button type="primary" @click="handleSubmit" :loading="saving">
            提交审批
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
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

const form = reactive({
  title: '',
  categoryId: '',
  caseType: 'external',
  tags: [],
  templateId: null,
  content: ''
})

const rules = {
  title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1-200 个字符', trigger: 'blur' }
  ],
  categoryId: [
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
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  await handleSave('pending_approval')
}
</script>

<style lang="scss" scoped>
.case-create {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .case-form {
    max-width: 800px;
  }
}
</style>
