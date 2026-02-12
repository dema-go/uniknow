import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')

  // 从localStorage加载用户信息
  const savedUserInfo = localStorage.getItem('userInfo')
  const userInfo = ref(savedUserInfo ? JSON.parse(savedUserInfo) : {
    id: '',
    name: '',
    avatar: '',
    role: 'user',
    tenantId: ''
  })

  function setToken(t) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function setUserInfo(info) {
    userInfo.value = {
      id: info.id || userInfo.value.id,
      name: info.name || info.username || userInfo.value.name,
      avatar: info.avatar || userInfo.value.avatar,
      role: info.role || userInfo.value.role,
      tenantId: info.tenantId || userInfo.value.tenantId
    }
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
  }

  function logout() {
    token.value = ''
    userInfo.value = { id: '', name: '', avatar: '', role: 'user', tenantId: '' }
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  // 检查是否是管理员
  function isAdmin() {
    return userInfo.value.role === 'admin'
  }

  // 检查是否可以跳过审批
  function canSkipApproval() {
    return isAdmin()
  }

  // 检查是否可以编辑
  function canEdit() {
    return ['admin', 'agent'].includes(userInfo.value.role)
  }

  // 检查是否可以审批
  function canApprove() {
    return ['admin', 'agent'].includes(userInfo.value.role)
  }

  // 初始化时加载用户信息
  function initUserInfo() {
    const saved = localStorage.getItem('userInfo')
    if (saved) {
      try {
        userInfo.value = JSON.parse(saved)
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    }
  }

  // 初始化
  initUserInfo()

  return {
    token,
    userInfo,
    setToken,
    setUserInfo,
    logout,
    isAdmin,
    canSkipApproval,
    canEdit,
    canApprove
  }
})
