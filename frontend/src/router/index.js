import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'DataLine' }
      },
      {
        path: 'cases',
        name: 'CaseList',
        component: () => import('@/views/cases/list.vue'),
        meta: { title: '案例管理', icon: 'Document' }
      },
      {
        path: 'cases/create',
        name: 'CaseCreate',
        component: () => import('@/views/cases/create.vue'),
        meta: { title: '创建案例', icon: 'Plus' }
      },
      {
        path: 'cases/:id',
        name: 'CaseDetail',
        component: () => import('@/views/cases/detail.vue'),
        meta: { title: '案例详情' }
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import('@/views/search/index.vue'),
        meta: { title: '案例搜索', icon: 'Search' }
      },
      {
        path: 'qa',
        name: 'QA',
        component: () => import('@/views/qa/index.vue'),
        meta: { title: '智能问答', icon: 'ChatDotRound' }
      },
      {
        path: 'approvals',
        name: 'Approvals',
        component: () => import('@/views/approvals/index.vue'),
        meta: { title: '审批管理', icon: 'CircleCheck' }
      },
      {
        path: 'operation',
        name: 'Operation',
        component: () => import('@/views/operation/index.vue'),
        meta: { title: '运营统计', icon: 'TrendCharts' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'UniKnow'} - 案例管理系统`
  next()
})

export default router
