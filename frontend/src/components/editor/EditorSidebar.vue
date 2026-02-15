<template>
  <div class="editor-sidebar" :class="{ expanded: isExpanded }">
    <!-- 切换按钮 -->
    <div class="sidebar-toggle" @click="isExpanded = !isExpanded">
      <el-icon :size="22">
        <Operation v-if="!isExpanded" />
        <Close v-else />
      </el-icon>
    </div>

    <!-- 展开内容 -->
    <transition name="slide">
      <div v-show="isExpanded" class="sidebar-content">
        <div class="action-buttons">
          <SidebarButton
            :icon="Search"
            label="搜索"
            @click="handleAction('search')"
          />
          <SidebarButton
            :icon="DocumentCopy"
            label="案例模版"
            @click="handleAction('template')"
          />
          <SidebarButton
            :icon="Star"
            label="案例评分"
            @click="handleAction('rate')"
          />
          <SidebarButton
            :icon="EditPen"
            label="案例润色"
            @click="handleAction('polish')"
          />
        </div>
      </div>
    </transition>

    <!-- 模版选择弹窗 -->
    <TemplateDialog
      v-model="showTemplateDialog"
      @select="handleTemplateSelect"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Operation, Close, Search, DocumentCopy, Star, EditPen } from '@element-plus/icons-vue'
import SidebarButton from './SidebarButton.vue'
import TemplateDialog from './TemplateDialog.vue'

const props = defineProps({
  editorMode: {
    type: String,
    default: 'markdown'
  }
})

const emit = defineEmits(['template-select'])

const isExpanded = ref(false)
const showTemplateDialog = ref(false)

const handleAction = (action) => {
  switch (action) {
    case 'search':
      ElMessage.info('搜索功能开发中...')
      break
    case 'template':
      showTemplateDialog.value = true
      break
    case 'rate':
      ElMessage.info('案例评分功能开发中...')
      break
    case 'polish':
      ElMessage.info('案例润色功能开发中...')
      break
  }
}

const handleTemplateSelect = (template) => {
  emit('template-select', template)
  ElMessage.success(`已应用模版: ${template.name}`)
}
</script>

<style lang="scss" scoped>
.editor-sidebar {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
  display: flex;
  align-items: center;

  .sidebar-toggle {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px 0 0 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: white;
    box-shadow: -2px 0 10px rgba(102, 126, 234, 0.3);
    transition: all 0.3s;

    &:hover {
      width: 56px;
      box-shadow: -4px 0 16px rgba(102, 126, 234, 0.4);
    }

    &:active {
      transform: scale(0.95);
    }
  }

  &.expanded .sidebar-toggle {
    border-radius: 12px;
  }

  .sidebar-content {
    position: absolute;
    right: 56px;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    min-width: 160px;

    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
  }
}

// 滑动动画
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(20px);
}
</style>
