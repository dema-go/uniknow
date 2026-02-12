import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'DataLine', requiresAuth: true }
      },
      {
        path: 'cases',
        name: 'CaseList',
        component: () => import('@/views/cases/list.vue'),
        meta: { title: '案例管理', icon: 'Document', requiresAuth: true }
      },
      {
        path: 'cases/create',
        name: 'CaseCreate',
        component: () => import('@/views/cases/create.vue'),
        meta: {
          title: '创建案例',
          icon: 'Plus',
          requiresAuth: true
        }
      },
      {
        path: 'cases/:id',
        name: 'CaseDetail',
        component: () => import('@/views/cases/detail.vue'),
        meta: { title: '案例详情', requiresAuth: true }
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import('@/views/search/index.vue'),
        meta: { title: '案例搜索', icon: 'Search', requiresAuth: true }
      },
      {
        path: 'qa',
        name: 'QA',
        component: () => import('@/views/qa/index.vue'),
        meta: { title: '智能问答', icon: 'ChatDotRound', requiresAuth: true }
      },
      {
        path: 'approvals',
        name: 'Approvals',
        component: () => import('@/views/approvals/index.vue'),
        meta: {
          title: '审批管理',
          icon: 'CircleCheck',
          requiresAuth: true
        }
      },
      {
        path: 'operation',
        name: 'Operation',
        component: () => import('@/views/operation/index.vue'),
        meta: {
          title: '运营统计',
          icon: 'TrendCharts',
          requiresAuth: true
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 简化版本
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 设置页面标题
  document.title = `${to.meta.title || 'UniKnow'} - 案例管理系统`

  // 登录页面特殊处理
  if (to.path === '/login') {
    if (token) {
      // 已登录用户访问登录页，跳转到首页
      next('/dashboard')
    } else {
      next()
    }
    return
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth !== false && !token) {
    ElMessage.warning('请先登录')
    next('/login')
    return
  }

  next()
})

export default router
