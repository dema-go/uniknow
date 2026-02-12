<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <h1>UniKnow</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>首页</span>
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
              <el-icon><Management /></el-icon>
              <span>运营管理</span>
            </template>
            <el-menu-item index="/approvals">审批管理</el-menu-item>
            <el-menu-item index="/operation">运营统计</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-right">
            <el-input
              placeholder="搜索案例..."
              prefix-icon="Search"
              style="width: 300px"
              @keyup.enter="handleSearch"
              v-model="searchKeyword"
            />
            <el-dropdown>
              <span class="user-info">
                <el-avatar :size="32" icon="UserFilled" />
                <span style="margin-left: 8px">管理员</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人中心</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main">
          <router-view />
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
  router.push({ path: '/search', query: { q: searchKeyword.value } })
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #304156;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #263445;

    h1 {
      color: #fff;
      font-size: 20px;
    }
  }

  .el-menu {
    border-right: none;
  }
}

.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
