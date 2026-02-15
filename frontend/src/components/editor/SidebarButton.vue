<template>
  <div class="sidebar-button" @click="$emit('click')">
    <div class="button-icon">
      <el-icon :size="20">
        <component :is="icon" />
      </el-icon>
    </div>
    <span class="button-label">{{ label }}</span>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: [String, Object],
    required: true
  },
  label: {
    type: String,
    required: true
  }
})

defineEmits(['click'])
</script>

<style lang="scss" scoped>
.sidebar-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;

  &:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);

    .button-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
  }

  &:active {
    transform: scale(0.98);
  }

  .button-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6b7280;
    transition: all 0.2s;
  }

  .button-label {
    font-size: 14px;
    font-weight: 500;
    color: #374151;
  }
}
</style>
