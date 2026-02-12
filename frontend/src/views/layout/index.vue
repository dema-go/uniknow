<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="240px" class="sidebar">
        <div class="logo">
          <div class="logo-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <h1>UniKnow</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#1f2937"
          text-color="#9ca3af"
          active-text-color="#ffffff"
          class="sidebar-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/cases">
            <el-icon><Document /></el-icon>
            <span>案例管理</span>
          </el-menu-item>
          <el-menu-item index="/search">
            <el-icon><Search /></el-icon>
            <span>案例搜索</span>
          </el-menu-item>
          <el-menu-item index="/qa">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能问答</span>
          </el-menu-item>
          <el-sub-menu index="operation">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>运营管理</span>
            </template>
            <el-menu-item index="/approvals">审批管理</el-menu-item>
            <el-menu-item index="/operation">运营统计</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      <el-container class="main-container">
        <el-header class="header">
          <div class="header-left">
            <!-- Breadcrumb could go here -->
          </div>
          <div class="header-right">
            <div class="search-bar-header">
              <el-input
                placeholder="全局搜索..."
                prefix-icon="Search"
                v-model="searchKeyword"
                @keyup.enter="handleSearch"
                class="header-search"
              />
            </div>
            <div class="action-icons">
               <el-badge :value="5" class="item">
                 <el-icon class="header-icon"><Bell /></el-icon>
               </el-badge>
            </div>
            <el-dropdown trigger="click">
              <span class="user-info">
                <el-avatar :size="36" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                <span class="username">管理员</span>
                <el-icon><CaretBottom /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu class="user-dropdown">
                  <el-dropdown-item><el-icon><User /></el-icon> 个人中心</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout"><el-icon><SwitchButton /></el-icon> 退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <component :is="Component" />
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const searchKeyword = ref('')

const activeMenu = computed(() => route.path)

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/search', query: { q: searchKeyword.value } })
    searchKeyword.value = '' // Clear after navigation
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  display: flex;
}

.sidebar {
  background: #111827; // Darker slate
  transition: width 0.3s;
  overflow-x: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  display: flex;
  flex-direction: column;

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    background: linear-gradient(90deg, #1f2937 0%, #111827 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    
    .logo-icon {
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 12px;
      color: white;
      font-size: 18px;
    }

    h1 {
      color: #f3f4f6;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
  }

  .sidebar-menu {
    border-right: none;
    flex: 1;
    padding-top: 10px;

    :deep(.el-menu-item) {
      margin: 4px 12px;
      border-radius: 8px;
      height: 48px;
      line-height: 48px;
      
      &:hover {
        background-color: rgba(255, 255, 255, 0.08);
      }
      
      &.is-active {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
        font-weight: 500;
        
        .el-icon {
          color: white;
        }
      }
      
      .el-icon {
        font-size: 18px;
        margin-right: 12px;
      }
    }
    
    :deep(.el-sub-menu__title) {
       margin: 4px 12px;
       border-radius: 8px;
       &:hover {
         background-color: rgba(255, 255, 255, 0.08);
       }
    }
  }
}

.main-container {
  height: 100vh;
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f3f4f6;
}

.header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  z-index: 1000;
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 24px;
  }
  
  .header-search {
    width: 240px;
    transition: width 0.3s;
    
    &:focus-within {
      width: 300px;
    }
    
    :deep(.el-input__wrapper) {
      border-radius: 20px;
      background-color: #f3f4f6;
      box-shadow: none !important;
      
      &.is-focus {
        background-color: #fff;
        box-shadow: 0 0 0 1px #764ba2 !important;
      }
    }
  }
  
  .action-icons {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .header-icon {
      font-size: 20px;
      color: #6b7280;
      cursor: pointer;
      &:hover { color: #111827; }
    }
  }
  
  .user-info {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 20px;
    transition: background 0.2s;
    
    &:hover {
      background: rgba(0,0,0,0.03);
    }
    
    .username {
      margin: 0 8px;
      font-weight: 500;
      color: #374151;
    }
  }
}

.main-content {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Transitions */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
