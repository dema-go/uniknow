<template>
  <el-dialog
    v-model="visible"
    title="选择案例模版"
    width="720px"
    :close-on-click-modal="false"
    class="template-dialog"
  >
    <!-- 分类标签 -->
    <el-tabs v-model="activeCategory" class="template-tabs">
      <el-tab-pane
        v-for="cat in categories"
        :key="cat.value"
        :label="cat.label"
        :name="cat.value"
      />
    </el-tabs>

    <!-- 模版网格 -->
    <div class="template-grid">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-card"
        @click="handleSelect(template)"
      >
        <div class="template-icon">
          <el-icon :size="24"><DocumentCopy /></el-icon>
        </div>
        <div class="template-info">
          <h4>{{ template.name }}</h4>
          <p>{{ template.description }}</p>
        </div>
        <el-tag size="small" :type="getTagType(template.category)">
          {{ template.category_label }}
        </el-tag>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { DocumentCopy } from '@element-plus/icons-vue'
import { builtinTemplates, templateCategories } from '@/data/templates'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['select'])

const activeCategory = ref('all')
const categories = templateCategories

const filteredTemplates = computed(() => {
  if (activeCategory.value === 'all') {
    return builtinTemplates
  }
  return builtinTemplates.filter(t => t.category === activeCategory.value)
})

const getTagType = (category) => {
  const typeMap = {
    faq: 'primary',
    process: 'success',
    announcement: 'warning',
    general: 'info'
  }
  return typeMap[category] || 'info'
}

const handleSelect = (template) => {
  emit('select', template)
  visible.value = false
}
</script>

<style lang="scss" scoped>
.template-dialog {
  :deep(.el-dialog__header) {
    padding: 20px 24px;
    border-bottom: 1px solid #f3f4f6;
  }

  :deep(.el-dialog__body) {
    padding: 0 24px 24px;
  }
}

.template-tabs {
  margin-bottom: 20px;

  :deep(.el-tabs__header) {
    margin: 0;
  }

  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 20px;
  }
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
}

.template-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  gap: 12px;

  &:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    transform: translateY(-2px);

    .template-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
  }

  .template-icon {
    width: 48px;
    height: 48px;
    background: #f3f4f6;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    transition: all 0.3s;
  }

  .template-info {
    flex: 1;

    h4 {
      margin: 0 0 4px;
      font-size: 15px;
      font-weight: 600;
      color: #111827;
    }

    p {
      margin: 0;
      font-size: 13px;
      color: #6b7280;
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  }

  .el-tag {
    align-self: flex-start;
  }
}
</style>
